"""The three protocol seams, and the physics core every target drives.

:class:`PhysicsCore` owns the whole simulation: the FMU step, the disc
kinematics, the wrench assembly, the 6DOF advance and the per-rotor log.  It
knows nothing about any autopilot — it takes a :class:`ChannelSource` and a
``dt`` and gives back a :class:`StepResult`.

A target supplies the rest:

* a :class:`ChannelSource` decoded from whatever the autopilot puts on the wire;
* a :class:`FrameClock` that turns an inbound packet into ``dt`` plus the
  advance / duplicate / restart decision;
* a :class:`StateEncoder` that turns a :class:`StateSample` into outbound bytes.

FRAMES.  A :class:`StateSample` is always in the bridge's own frames — world
NED, body FRD, ``(w, x, y, z)`` body->NED quaternion, accelerometer as SPECIFIC
FORCE (a level vehicle at rest reads ``(0, 0, -9.80665)``).  Converting those
into an autopilot's frames is the encoder's job and nobody else's; see
:mod:`thrustlab.sitl.rigidbody` for why the frames are what they are.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np

from ..kinematics import DiscInflow, assemble_wrench, disc_inflow
from ..model import RotorModel, RotorOutputs
from ..rigidbody import BodyState, RigidBody
from ..rpmlog import RotorLog
from ..vehicle import VehicleConfig

logger = logging.getLogger(__name__)


@runtime_checkable
class ChannelSource(Protocol):
    """PWM in microseconds for a 1-BASED output channel.

    ``VehicleConfig.throttles``, ``axes_for`` and ``control_moment_m3`` all take
    a callable of exactly this shape, which is why it is the seam: an ArduPilot
    ``servo_packet`` and a Betaflight ``servo_packet_raw`` differ only in how
    they answer it.
    """

    def __call__(self, channel: int) -> float: ...


@runtime_checkable
class StateEncoder(Protocol):
    """Bridge state -> the bytes that go back to the autopilot."""

    def encode(self, sample: StateSample) -> bytes: ...


@dataclass(frozen=True)
class FrameTick:
    """A frame clock's verdict for one inbound packet.

    ``advance`` false means the packet is a duplicate: answer it idempotently
    and step nothing.  ``restart`` means the autopilot restarted and the whole
    simulation must be reset before the step.
    """

    dt_s: float
    advance: bool = True
    duplicate: bool = False
    restart: bool = False


@runtime_checkable
class FrameClock(Protocol):
    """Inbound packet -> :class:`FrameTick`.  Stateful by nature."""

    def tick(self, packet: object) -> FrameTick: ...

    def reset(self) -> None: ...


@dataclass
class BridgeCounters:
    """What happened on the wire.  Cheap, and the only way to prove the gate."""

    packets_received: int = 0
    frames_advanced: int = 0
    duplicates_resent: int = 0
    restarts: int = 0
    frames_skipped: int = 0
    steps_capped: int = 0
    malformed_packets: int = 0
    non_finite_substitutions: int = 0


@dataclass(frozen=True)
class StateSample:
    """One end-of-step sensor sample, in the bridge's own frames.

    ``accel_body_m_s2`` is the ACCELEROMETER reading — specific force, not
    kinematic acceleration — evaluated at the POST-step state with the same
    held wrench, so the reading and the timestamp describe the same instant.
    """

    timestamp_s: float
    state: BodyState
    accel_body_m_s2: np.ndarray
    airspeed_m_s: float
    voltage_bus_V: float
    current_bus_A: float
    battery_soc: float


@dataclass(frozen=True)
class StepResult:
    """Everything one physics advance produced."""

    dt_s: float
    timestamp_s: float
    state: BodyState
    outputs: RotorOutputs
    throttle: np.ndarray
    inflow: DiscInflow
    force_body_N: np.ndarray
    moment_body_Nm: np.ndarray
    accel_body_m_s2: np.ndarray
    airspeed_m_s: float

    @property
    def sample(self) -> StateSample:
        return StateSample(
            timestamp_s=self.timestamp_s,
            state=self.state,
            accel_body_m_s2=self.accel_body_m_s2,
            airspeed_m_s=self.airspeed_m_s,
            voltage_bus_V=self.outputs.voltage_bus_V,
            current_bus_A=self.outputs.current_bus_A,
            battery_soc=self.outputs.battery_soc,
        )


class PhysicsCore:
    """FMU + 6DOF, driven by PWM per channel.  Transport-free, target-free.

    Per frame the coupling is: set FMU inputs -> one ``fmi3DoStep`` -> read the
    wrench -> advance the 6DOF with that wrench HELD.  RK4 stage queries back
    into the FMU would violate FMI 3 Step Mode's set-then-get rules, which is
    why the 6DOF sub-steps against a frozen wrench instead.
    """

    def __init__(
        self,
        vehicle: VehicleConfig,
        model: RotorModel,
        *,
        initial_state: BodyState | None = None,
        rotor_log: RotorLog | None = None,
        max_substep_s: float | None = None,
    ) -> None:
        if model.n_rotors != vehicle.rotor_count:
            raise ValueError(
                f"the FMU carries {model.n_rotors} rotors but the vehicle YAML declares "
                f"{vehicle.rotor_count}"
            )
        self.vehicle = vehicle
        self.model = model
        self.rotor_log = rotor_log
        self.counters = BridgeCounters()

        body_kwargs = {
            "mass_kg": vehicle.mass_kg,
            "inertia_kg_m2": vehicle.inertia_kg_m2,
            "inverse_inertia": vehicle.inverse_inertia,
            "drag_area_m2": vehicle.drag_area_m2,
            "air_density_kg_m3": vehicle.air_density_kg_m3,
            "wind_ned_m_s": vehicle.wind_ned_m_s,
            "ground_enabled": vehicle.ground_enabled,
            "ground_z_ned_m": vehicle.ground_z_ned_m,
            "wing": vehicle.wing,
        }
        if max_substep_s is not None:
            body_kwargs["max_substep_s"] = max_substep_s
        self.body = RigidBody(**body_kwargs)

        self._initial_state = initial_state or BodyState.at_rest(
            position_ned_m=np.array([0.0, 0.0, vehicle.ground_z_ned_m])
        )
        self.state = self._initial_state
        self.sim_time_s = 0.0
        self._positions = vehicle.positions_m
        self._axes = vehicle.axes
        self._senses = vehicle.senses

    # ------------------------------------------------------------- one frame

    def step(
        self, channels: ChannelSource, dt_s: float, *, frame_count: int = 0
    ) -> StepResult:
        """Set inputs, take one FMU step, advance the 6DOF, log the rotor lane."""
        vehicle = self.vehicle
        throttle = vehicle.throttles(channels)

        # Tilt hinges rotate the thrust axes per frame; static vehicles keep
        # the precomputed array. Control-surface deflections are read the same
        # way and become a q-scaled moment inside the integrator.
        axes = vehicle.axes_for(channels) if vehicle.has_tilt else self._axes
        control_m3 = (
            vehicle.control_moment_m3(channels) if vehicle.control_surfaces else None
        )

        # Disc kinematics at the START of the frame, from the current 6DOF state.
        v_air_body = self.body.air_velocity_body(self.state)
        inflow = disc_inflow(
            self._positions,
            axes,
            v_air_body,
            self.state.omega_body_rad_s,
            v_axial_sign=vehicle.v_axial_sign,
        )

        # One-sample partitioned ZOH: set -> DoStep -> get.
        self.model.set_inputs(
            throttle=throttle,
            v_axial_m_s=inflow.v_axial_m_s,
            v_edge_m_s=inflow.v_edge_m_s,
            air_density_kg_m3=vehicle.air_density_kg_m3,
            ambient_temp_C=vehicle.ambient_temp_C,
        )
        self.model.do_step(self.sim_time_s, dt_s)
        outputs = self.model.get_outputs()

        force_body, moment_body = assemble_wrench(
            self._positions,
            axes,
            self._senses,
            outputs.thrust_N,
            outputs.torque_Nm,
            outputs.force_inplane_N,
            inflow.edge_unit,
            torque_convention=vehicle.torque_convention,
            negate_reaction_torque=vehicle.negate_reaction_torque,
            inplane_sign=vehicle.inplane_sign,
        )

        # The wrench is held across the whole frame.
        self.state = self.body.advance(
            self.state, force_body, moment_body, dt_s, control_moment_m3=control_m3
        )
        self.sim_time_s += dt_s
        self.counters.frames_advanced += 1

        if self.rotor_log is not None:
            self.rotor_log.write(
                timestamp_s=self.sim_time_s,
                frame_count=frame_count,
                dt_s=dt_s,
                voltage_bus_V=outputs.voltage_bus_V,
                current_bus_A=outputs.current_bus_A,
                battery_soc=outputs.battery_soc,
                all_in_envelope=outputs.all_in_envelope,
                throttle=throttle,
                rpm=outputs.rpm,
                thrust_N=outputs.thrust_N,
                torque_Nm=outputs.torque_Nm,
                force_inplane_N=outputs.force_inplane_N,
                v_axial_m_s=inflow.v_axial_m_s,
                v_edge_m_s=inflow.v_edge_m_s,
                rotor_in_envelope=outputs.rotor_in_envelope,
            )

        return StepResult(
            dt_s=dt_s,
            timestamp_s=self.sim_time_s,
            state=self.state,
            outputs=outputs,
            throttle=throttle,
            inflow=inflow,
            force_body_N=force_body,
            moment_body_Nm=moment_body,
            accel_body_m_s2=self.body.specific_force_body(self.state, force_body),
            airspeed_m_s=self.body.airspeed(self.state),
        )

    # ---------------------------------------------------------------- restart

    def restart(self) -> None:
        """Full restart: FMU reset + re-init, 6DOF re-seeded, clock back to zero."""
        self.model.reset()
        self.state = self._initial_state
        self.sim_time_s = 0.0
        self.counters.restarts += 1
