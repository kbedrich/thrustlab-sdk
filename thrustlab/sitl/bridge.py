"""The ArduPilot bridge: physics core + ArduPilot frame clock + JSON encoder.

This module is the public ArduPilot entry point and its surface has not moved.
What used to live here inline now lives behind the three seams in
:mod:`thrustlab.sitl.targets`:

  * the physics — FMU step, disc kinematics, wrench, 6DOF, rotor log — is
    :class:`thrustlab.sitl.targets.base.PhysicsCore`;
  * spec decision 12's ``frame_count`` state machine is
    :class:`~thrustlab.sitl.targets.ardupilot.ArduPilotFrameClock`;
  * the JSON reply is
    :class:`~thrustlab.sitl.targets.ardupilot.ArduPilotStateEncoder`.

Read :mod:`thrustlab.sitl.targets.ardupilot` for the timing rules
(``MAX_STEP_S`` and why it is strictly below ArduPilot's own ceiling) — they are
unchanged and are documented at their new home.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from .model import RotorModel, RotorOutputs
from .protocol import ProtocolError, ServoPacket, StateReply, decode_servo_packet
from .rigidbody import BodyState
from .rpmlog import RotorLog
from .targets.ardupilot import (
    ARDUPILOT_MAX_DELTAT_S,
    DEFAULT_FRAME_RATE_HZ,
    MAX_STEP_S,
    ArduPilotFrameClock,
    ArduPilotStateEncoder,
    BridgeServer,
)
from .targets.base import BridgeCounters, PhysicsCore
from .vehicle import VehicleConfig

logger = logging.getLogger(__name__)

__all__ = [
    "ARDUPILOT_MAX_DELTAT_S",
    "DEFAULT_FRAME_RATE_HZ",
    "MAX_STEP_S",
    "Bridge",
    "BridgeCounters",
    "BridgeServer",
    "FrameResult",
]


@dataclass
class FrameResult:
    """One handled packet: what was done and what went back on the wire."""

    reply: bytes
    advanced: bool
    duplicate: bool
    restarted: bool
    dt_s: float
    timestamp_s: float
    frame_count: int
    outputs: RotorOutputs | None = None
    throttle: np.ndarray | None = None


class Bridge(PhysicsCore):
    """Stateful, transport-free.  Feed it datagrams; it returns replies."""

    def __init__(
        self,
        vehicle: VehicleConfig,
        model: RotorModel,
        *,
        initial_state: BodyState | None = None,
        rotor_log: RotorLog | None = None,
        max_substep_s: float | None = None,
    ) -> None:
        super().__init__(
            vehicle,
            model,
            initial_state=initial_state,
            rotor_log=rotor_log,
            max_substep_s=max_substep_s,
        )
        self.clock = ArduPilotFrameClock(self.counters)
        self.encoder = ArduPilotStateEncoder(self.counters)
        self._last_reply = b""

    # ------------------------------------------------------------ wire entry

    def handle_datagram(self, data: bytes) -> bytes | None:
        """Decode one datagram and produce the reply, or ``None`` if unusable."""
        try:
            packet = decode_servo_packet(data)
        except ProtocolError as exc:
            self.counters.malformed_packets += 1
            logger.warning("dropping datagram: %s", exc)
            return None
        self.counters.packets_received += 1
        return self.handle_packet(packet).reply

    def handle_packet(self, packet: ServoPacket) -> FrameResult:
        """Run spec decision 12's state machine for one servo packet."""
        tick = self.clock.tick(packet)
        if not tick.advance:
            return FrameResult(
                reply=self._last_reply,
                advanced=False,
                duplicate=tick.duplicate,
                restarted=False,
                dt_s=0.0,
                timestamp_s=self.sim_time_s,
                frame_count=packet.frame_count,
            )

        if tick.restart:
            self.restart()

        result = self.step(
            packet.pwm_for_channel, tick.dt_s, frame_count=packet.frame_count
        )
        reply = self.encoder.encode(result.sample)
        self.clock.commit()
        self._last_reply = reply
        return FrameResult(
            reply=reply,
            advanced=True,
            duplicate=False,
            restarted=tick.restart,
            dt_s=result.dt_s,
            timestamp_s=result.timestamp_s,
            frame_count=packet.frame_count,
            outputs=result.outputs,
            throttle=result.throttle,
        )

    # ---------------------------------------------------------------- restart

    def restart(self) -> None:
        """Full restart: FMU reset + re-init, 6DOF re-seeded, clock back to zero."""
        super().restart()
        self.clock.reset()
        self._last_reply = b""

    # ------------------------------------------------------ compatibility API

    def _state_reply(
        self, rotor_force_body_N: np.ndarray, outputs: RotorOutputs
    ) -> StateReply:
        """End-of-step sensor sample, in ArduPilot's own fields.

        Kept as a method because it is the readable name for "what goes on the
        wire this frame"; the sample it wraps is the target-neutral
        :class:`~thrustlab.sitl.targets.base.StateSample`.
        """
        from .targets.base import StateSample

        return self.encoder.state_reply(
            StateSample(
                timestamp_s=self.sim_time_s,
                state=self.state,
                accel_body_m_s2=self.body.specific_force_body(
                    self.state, rotor_force_body_N
                ),
                airspeed_m_s=self.body.airspeed(self.state),
                voltage_bus_V=outputs.voltage_bus_V,
                current_bus_A=outputs.current_bus_A,
                battery_soc=outputs.battery_soc,
            )
        )
