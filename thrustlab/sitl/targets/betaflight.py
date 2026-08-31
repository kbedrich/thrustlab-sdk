"""Betaflight SITL: the binary UDP triple, the frame conversions, the bridge.

Every claim below was read out of Betaflight master ``6aeffc36``:

  * ``src/platform/SIMULATOR/target/SITL/target.h`` — the four packet structs,
    ``USE_VIRTUAL_GPS``, ``ENABLE_GAZEBO_BRIDGE`` (defaults to 1, so a bare
    ``TARGET=SITL`` build behaves like ``SITL_GAZEBO``);
  * ``src/platform/SIMULATOR/sitl.c`` — the port numbers, ``updateState``
    (accelerometer, gyro, baro, quaternion, virtual GPS, ``simRate``) and
    ``pwmCompleteMotorUpdate`` / ``servoWrite`` (the outbound raw PWM packet);
  * ``src/platform/SIMULATOR/sitl_gyro.h`` — the gyro axis mapping, pinned by
    ``src/test/unit/sitl_gyro_unittest.cc``.

────────────────────────────────────────────────────────────────────────────────
PORTS
────────────────────────────────────────────────────────────────────────────────
``sitl.c`` lines 201-204, and the two servers it binds:

    9001  SITL -> sim   servo_packet_raw   RAW PWM microseconds, 16 channels
    9002  SITL -> sim   servo_packet       4 floats, NORMALISED, hard 4-motor cap
    9003  sim -> SITL   fdm_packet         18 doubles           (SITL binds)
    9004  sim -> SITL   rc_packet          timestamp + 16 uint16 (SITL binds)
    5761  TCP           MSP / CLI on UART1 (BASE_PORT 5760 + id 0 + 1)

This module uses 9001, NOT 9002: ``servo_packet`` carries four normalised
floats and cannot describe a hexacopter, a servo, or a real PWM value.

────────────────────────────────────────────────────────────────────────────────
STRUCT LAYOUTS
────────────────────────────────────────────────────────────────────────────────
``servo_packet_raw`` is ``{ uint16_t motorCount; float pwm_output_raw[16]; }``.
``float`` needs 4-byte alignment, so the natural C layout pads two bytes after
``motorCount``: ``<H2x16f``, 68 bytes.  ``sitl.c`` fills ``pwm_output_raw`` with
motors at ``[0, motorCount)`` (``pwmWriteMotor``) and servos immediately after,
at ``index + motorCount`` (``servoWrite``).

``fdm_packet`` is 18 doubles with no padding: ``<18d``, 144 bytes.
``rc_packet`` is ``{ double timestamp; uint16_t channels[16]; }`` — the doubles
force 8-byte alignment and 32 bytes of ``uint16_t`` land on a multiple of 8, so
there is no tail padding: ``<d16H``, 40 bytes.

────────────────────────────────────────────────────────────────────────────────
FRAME CONVERSIONS — the load-bearing part
────────────────────────────────────────────────────────────────────────────────
The bridge's own frames are world NED, body FRD, ``(w, x, y, z)`` body->NED
quaternion, accelerometer as specific force.  The ``fdm_packet`` wants the
Gazebo ``BetaflightPlugin``'s conventions, which ``sitl.c`` then undoes:

GYRO (``imu_angular_velocity_rpy``).  ``sitlGyroBodyFromSim`` maps
``roll = +wx, pitch = -wy, yaw = +wz`` and documents the sensor frame as FRD,
so roll and pitch go on the wire as the bridge's own FRD rates.  YAW IS
NEGATED: ``r_packet = -r_FRD``.

  The negation is NOT what ``sitl_gyro.h``'s header comment reads like — it
  annotates the ``+wz`` line "CW viewed from above", and it is easy to conclude
  from that (as this module first did) that Betaflight's internal yaw is
  clockwise-positive and the FRD rate should pass through untouched.  It is
  not.  Betaflight's yaw axis is COUNTER-CLOCKWISE-positive at the point the
  rate loop closes: ``mixer.c`` negates the yaw PID sum
  (``scaledAxisPidYaw = -pidData[FD_YAW].Sum`` unless ``yaw_motors_reversed``),
  and the ``mixerQuadX`` yaw column then drives a right-stick command onto the
  counter-clockwise diagonal, which torques the airframe clockwise.  For that
  loop to be NEGATIVE feedback, a clockwise turn has to arrive as a negative
  reading.

  Measured 2026-08-30 with the un-negated rate, which is what makes this
  paragraph evidence rather than argument: a three-second right-yaw command
  left the mixer saturated at PWM ``[1055, 1811, 1811, 1055]`` and HELD there
  after the stick was centred, while the true yaw rate climbed monotonically
  through 45 rad/s and the airframe departed to 142 m.  Negating yaw — which
  is what ``src/test/sitl/sitl_harness.py`` has always emitted — the same probe
  turns the airframe about 100° right and stops.

ACCELEROMETER (``imu_linear_acceleration_xyz``).  ``sitl.c`` NEGATES all three
axes on read.  The plugin's body frame is FLU (Betaflight's internal NWU body),
and FLU is FRD with y and z negated, so:

    packet = -f_FLU = -(f_x, -f_y, -f_z)_FRD = (-f_x, +f_y, +f_z)_FRD

A level vehicle at rest has ``f_FRD = (0, 0, -9.80665)`` and therefore puts
``(0, 0, -9.80665)`` on the wire; ``sitl.c`` negates it to ``+1 g`` on the
flight controller's Z-up accelerometer.  ``sitl_harness.py`` computes the same
vector the long way round and agrees.

QUATERNION (``imu_orientation_quat``).  ``sitl.c`` reconstructs

    q_att = Rz(π/2) ⊗ conj_x180(q_packet)          conj_x180 negates y and z

so, to have the flight controller recover the true FLU->NWU attitude,

    q_packet = conj_x180( Rz(-π/2) ⊗ q_nwu )

and ``q_nwu`` follows from the bridge's ``q_ned`` by the very same y/z negation,
because NWU is NED with y and z negated exactly as FLU is FRD:

    q_nwu = (w, x, -y, -z) of q_ned

VELOCITY and POSITION.  ``USE_VIRTUAL_GPS`` is defined for this target, so
``velocity_xyz`` is ENU ``(Ve, Vn, Vup)`` and ``position_xyz`` is
``(longitude, latitude, altitude_m)`` — degrees and metres, NOT metres NED.
Gazebo Harmonic inverts horizontal deltas, so ``sitl.c`` mirrors lat/lon about
the FIRST packet's values: ``corrected = 2·origin − value``.  Sending
``2·home − true`` makes the first packet equal ``home`` (the flight controller
latches ``home`` as its origin) and every later packet decode back to ``true``.

BARO.  ``pkt->pressure`` is IGNORED under the Gazebo bridge; the pressure comes
from ``position_xyz[2]`` through the ISA formula.  The field is still filled
with sea-level pressure so a legacy-bridge build reads something sane.

────────────────────────────────────────────────────────────────────────────────
TIMING — soft real time, NOT lockstep
────────────────────────────────────────────────────────────────────────────────
``updateState`` only refreshes ``simRate`` when ``0 < deltaSim < 0.02``, so the
FDM feed must advance sim time by LESS than 20 ms per packet: keep it above
50 Hz of SIM time.  500 ms of wall silence resets the flight controller's clock
(``realtime_now > last_realtime + 500e3``).  There is no barrier: the motor
packet comes back on a ``pthread_mutex_trylock``, one per FDM packet at best,
so the bridge steps its own clock and uses the most recent PWM it has heard.
"""

from __future__ import annotations

import json
import logging
import math
import socket
import struct
import time
from collections.abc import Sequence
from dataclasses import dataclass, field

import numpy as np

from ..rigidbody import GRAVITY_MSS, quaternion_yaw
from ..rpmlog import RotorLog
from ..vehicle import VehicleConfig
from .base import BridgeCounters, PhysicsCore, StateSample

logger = logging.getLogger(__name__)

# ───────────────────────────────────────────────────────────────── ports

PORT_PWM_RAW = 9001
PORT_PWM = 9002
PORT_STATE = 9003
PORT_RC = 9004
PORT_MSP = 5761

# ─────────────────────────────────────────────────────────── wire formats

SIMULATOR_MAX_PWM_CHANNELS = 16
SIMULATOR_MAX_RC_CHANNELS = 16

_SERVO_RAW_FORMAT = "<H2x16f"
_FDM_FORMAT = "<18d"
_RC_FORMAT = "<d16H"

SERVO_PACKET_RAW_BYTES = struct.calcsize(_SERVO_RAW_FORMAT)  # 68
FDM_PACKET_BYTES = struct.calcsize(_FDM_FORMAT)  # 144
RC_PACKET_BYTES = struct.calcsize(_RC_FORMAT)  # 40

#: What ``sitl.c`` puts in ``fdm_packet.pressure``'s place is ignored under the
#: Gazebo bridge; this is only for a legacy-bridge build.
SEA_LEVEL_PRESSURE_PA = 101325.0

#: Metres per degree of latitude, and of longitude at the equator.  The demo
#: only needs a locally-flat mapping around home, which is all the flight
#: controller's virtual GPS gets from Gazebo either.
METRES_PER_DEGREE = 111319.49

#: ``sitl.c``: ``simRate`` is only refreshed while ``deltaSim < 0.02``.
MAX_SIM_STEP_S = 0.02

#: 500 ms of wall silence resets the flight controller's clock.
SITL_SILENCE_TIMEOUT_S = 0.5


class BetaflightProtocolError(ValueError):
    """A datagram that is not a well-formed Betaflight SITL packet."""


@dataclass(frozen=True)
class HomeOrigin:
    """Where ``position_ned_m == (0, 0, 0)`` sits on the globe."""

    latitude_deg: float = -27.5
    longitude_deg: float = 153.0
    altitude_m: float = 30.0


# ───────────────────────────────────────────────────── SITL -> bridge (9001)


@dataclass(frozen=True)
class MotorPacket:
    """One decoded ``servo_packet_raw``: raw PWM microseconds, 16 channels."""

    motor_count: int
    pwm_us: tuple[float, ...]

    def pwm_for_channel(self, channel: int) -> float:
        """PWM for a 1-BASED output channel, motors first then servos.

        ``pwmWriteMotor`` fills ``pwm_output_raw[index]`` for motor ``index``
        and ``servoWrite`` fills ``[index + motorCount]``, so a vehicle YAML
        that numbers its rotors 1..N and its servos N+1.. lines up exactly.
        """
        if channel < 1 or channel > SIMULATOR_MAX_PWM_CHANNELS:
            raise BetaflightProtocolError(
                f"output channel {channel} is outside the "
                f"{SIMULATOR_MAX_PWM_CHANNELS} channels a servo_packet_raw carries"
            )
        return self.pwm_us[channel - 1]


def decode_motor_packet(data: bytes) -> MotorPacket:
    """Decode a ``servo_packet_raw``, raising on anything else."""
    if len(data) != SERVO_PACKET_RAW_BYTES:
        raise BetaflightProtocolError(
            f"servo_packet_raw is {SERVO_PACKET_RAW_BYTES} bytes "
            f"(uint16 motorCount + 2 pad + 16 floats); got {len(data)}. A "
            f"{struct.calcsize('<4f')}-byte datagram is the port-9002 "
            f"servo_packet, which this bridge does not use"
        )
    fields = struct.unpack(_SERVO_RAW_FORMAT, data)
    motor_count = int(fields[0])
    if motor_count > SIMULATOR_MAX_PWM_CHANNELS:
        raise BetaflightProtocolError(
            f"servo_packet_raw claims {motor_count} motors; the struct carries "
            f"{SIMULATOR_MAX_PWM_CHANNELS} channels in total"
        )
    return MotorPacket(motor_count=motor_count, pwm_us=tuple(float(v) for v in fields[1:]))


def encode_motor_packet(packet: MotorPacket) -> bytes:
    """Re-encode a motor packet.  Used by the tests and by fixture capture."""
    if len(packet.pwm_us) != SIMULATOR_MAX_PWM_CHANNELS:
        raise BetaflightProtocolError(
            f"servo_packet_raw carries {SIMULATOR_MAX_PWM_CHANNELS} channels, "
            f"not {len(packet.pwm_us)}"
        )
    return struct.pack(_SERVO_RAW_FORMAT, packet.motor_count, *packet.pwm_us)


# ───────────────────────────────────────────────────── bridge -> SITL (9004)


def encode_rc_packet(timestamp_s: float, channels: Sequence[int]) -> bytes:
    """Encode an ``rc_packet``: a timestamp and 16 channels in microseconds.

    ``FEATURE_RX_UDP`` is the default receiver for a bare ``TARGET=SITL`` build,
    so this IS the transmitter.  Stop sending and the flight controller's
    failsafe trips, which is how the upstream harness simulates RX loss.
    """
    values = list(channels)
    if len(values) > SIMULATOR_MAX_RC_CHANNELS:
        raise BetaflightProtocolError(
            f"rc_packet carries {SIMULATOR_MAX_RC_CHANNELS} channels, not {len(values)}"
        )
    values += [0] * (SIMULATOR_MAX_RC_CHANNELS - len(values))
    return struct.pack(_RC_FORMAT, float(timestamp_s), *(int(v) for v in values))


def decode_rc_packet(data: bytes) -> tuple[float, tuple[int, ...]]:
    """Decode an ``rc_packet``.  Used by the tests."""
    if len(data) != RC_PACKET_BYTES:
        raise BetaflightProtocolError(
            f"rc_packet is {RC_PACKET_BYTES} bytes; got {len(data)}"
        )
    fields = struct.unpack(_RC_FORMAT, data)
    return float(fields[0]), tuple(int(v) for v in fields[1:])


# ────────────────────────────────────────────── frame conversions (pure)


def gyro_packet_from_body(omega_body_rad_s: Sequence[float]) -> tuple[float, float, float]:
    """Body FRD rates -> ``imu_angular_velocity_rpy``.

    Roll and pitch pass through: ``sitlGyroBodyFromSim`` reads the packet as
    FRD and negates y itself to reach Betaflight's nose-down-positive pitch.

    YAW IS NEGATED.  Betaflight's yaw axis is counter-clockwise-positive where
    the rate loop closes, so a nose-right (FRD ``r`` positive) turn has to
    arrive negative or the loop is POSITIVE feedback — measured as a saturated
    mixer and a monotonically diverging spin.  The module docstring carries the
    log lines and the ``mixer.c`` reasoning.
    """
    p, q, r = (float(v) for v in np.asarray(omega_body_rad_s, dtype=float).reshape(3))
    return (p, q, -r)


def accel_packet_from_specific_force(
    accel_body_m_s2: Sequence[float],
) -> tuple[float, float, float]:
    """Body FRD specific force -> ``imu_linear_acceleration_xyz``.

    ``packet = -f_FLU``, and FLU is FRD with y and z negated, so the x axis
    flips and y and z survive.  Level at rest: ``(0, 0, -9.80665)`` in, the same
    out, and ``sitl.c``'s negation makes it ``+1 g`` up on the flight
    controller.
    """
    fx, fy, fz = (float(v) for v in np.asarray(accel_body_m_s2, dtype=float).reshape(3))
    return (-fx, fy, fz)


def _quaternion_multiply(a: Sequence[float], b: Sequence[float]) -> tuple[float, float, float, float]:
    aw, ax, ay, az = (float(v) for v in a)
    bw, bx, by, bz = (float(v) for v in b)
    return (
        aw * bw - ax * bx - ay * by - az * bz,
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
    )


#: ``Rz(-90°)`` as a ``(w, x, y, z)`` quaternion.  ``sitl.c`` re-applies
#: ``Rz(+90°)``, so the packet carries the attitude pre-rotated by its inverse.
_RZ_NEG_90 = (math.sqrt(0.5), 0.0, 0.0, -math.sqrt(0.5))


def quaternion_nwu_from_ned(quaternion_ned: Sequence[float]) -> tuple[float, float, float, float]:
    """``(w, x, y, z)`` body(FRD)->NED  ->  body(FLU)->NWU.

    NWU is NED with y and z negated, and FLU is FRD with y and z negated — the
    SAME similarity transform on both sides — and conjugating a rotation by
    ``Rx(180°)`` is exactly ``(w, x, y, z) -> (w, x, -y, -z)``.
    """
    w, x, y, z = (float(v) for v in np.asarray(quaternion_ned, dtype=float).reshape(4))
    return (w, x, -y, -z)


def quaternion_packet_from_ned(
    quaternion_ned: Sequence[float],
) -> tuple[float, float, float, float]:
    """``(w, x, y, z)`` body->NED -> ``imu_orientation_quat``.

    ``sitl.c`` computes ``q_att = Rz(π/2) ⊗ conj_x180(q_packet)``; this is its
    inverse, so the flight controller reconstructs the true FLU->NWU attitude
    exactly.  ``conj_x180`` (negate y and z) is an involution, which is why it
    appears on both sides.
    """
    nwu = quaternion_nwu_from_ned(quaternion_ned)
    w, x, y, z = _quaternion_multiply(_RZ_NEG_90, nwu)
    return (w, x, -y, -z)


def velocity_enu_from_ned(velocity_ned_m_s: Sequence[float]) -> tuple[float, float, float]:
    """NED velocity -> ``velocity_xyz`` ENU ``(Ve, Vn, Vup)``.

    ``sitl.c`` reads ``velN = [1]``, ``velE = [0]``, ``velD = -[2]`` and takes
    the course as ``atan2([0], [1])``, which is only a bearing from north if
    ``[0]`` is East and ``[1]`` is North.
    """
    vn, ve, vd = (float(v) for v in np.asarray(velocity_ned_m_s, dtype=float).reshape(3))
    return (ve, vn, -vd)


def geodetic_packet_from_ned(
    position_ned_m: Sequence[float], home: HomeOrigin
) -> tuple[float, float, float]:
    """NED position -> ``position_xyz`` ``(longitude, latitude, altitude_m)``.

    The lat/lon pair is MIRRORED about home, because ``sitl.c`` un-mirrors it:
    ``corrected = 2·origin − value``, with ``origin`` latched from the FIRST
    packet.  The first packet of a run sits at home, mirrors to home, and so
    latches home — after which every packet decodes back to the truth.
    """
    north, east, down = (float(v) for v in np.asarray(position_ned_m, dtype=float).reshape(3))
    latitude = home.latitude_deg + north / METRES_PER_DEGREE
    longitude = home.longitude_deg + east / (
        METRES_PER_DEGREE * math.cos(math.radians(home.latitude_deg))
    )
    altitude = home.altitude_m - down
    return (
        2.0 * home.longitude_deg - longitude,
        2.0 * home.latitude_deg - latitude,
        altitude,
    )


class BetaflightStateEncoder:
    """:class:`StateSample` -> the 144-byte ``fdm_packet``."""

    def __init__(self, home: HomeOrigin, counters: BridgeCounters | None = None) -> None:
        self.home = home
        self.counters = counters

    def encode(self, sample: StateSample) -> bytes:
        gyro = gyro_packet_from_body(sample.state.omega_body_rad_s)
        accel = accel_packet_from_specific_force(sample.accel_body_m_s2)
        quaternion = quaternion_packet_from_ned(sample.state.quaternion)
        velocity = velocity_enu_from_ned(sample.state.velocity_ned_m_s)
        position = geodetic_packet_from_ned(sample.state.position_ned_m, self.home)

        values = [
            float(sample.timestamp_s),
            *gyro,
            *accel,
            *quaternion,
            *velocity,
            *position,
            SEA_LEVEL_PRESSURE_PA,
        ]
        substitutions = sum(1 for v in values if not math.isfinite(v))
        if substitutions:
            # A NaN reaching the flight controller poisons its estimator for the
            # rest of the run and the failure surfaces far from its cause. The
            # binary wire has no way to omit a field, so substitute and shout.
            if self.counters is not None:
                self.counters.non_finite_substitutions += substitutions
            logger.error(
                "%d non-finite value(s) in the FDM packet at t=%.4f s were sent as 0.0; "
                "the 6DOF or the FMU has diverged",
                substitutions,
                sample.timestamp_s,
            )
            values = [v if math.isfinite(v) else 0.0 for v in values]
        return struct.pack(_FDM_FORMAT, *values)


# ──────────────────────────────────────────────────────────────── the bridge


class BetaflightBridge(PhysicsCore):
    """Physics core plus the Betaflight motor decode and FDM encode.

    Transport-free, like :class:`thrustlab.sitl.bridge.Bridge`.  The
    difference is the clock: Betaflight SITL is soft real time and never asks
    for a step, so :class:`BetaflightServer` drives ``advance`` on a fixed sim
    step and this class only remembers the most recent PWM it was told.
    """

    #: PWM held before the first motor packet arrives.  ``sitl.c`` sends nothing
    #: until its mixer has run, and a disarmed flight controller commands the
    #: motor minimum anyway, so the vehicle sits on the ground.
    IDLE_PWM_US = 1000.0

    def __init__(
        self,
        vehicle: VehicleConfig,
        model,
        *,
        home: HomeOrigin | None = None,
        rotor_log: RotorLog | None = None,
        max_substep_s: float | None = None,
        initial_state=None,
    ) -> None:
        super().__init__(
            vehicle,
            model,
            initial_state=initial_state,
            rotor_log=rotor_log,
            max_substep_s=max_substep_s,
        )
        self.home = home or HomeOrigin()
        self.encoder = BetaflightStateEncoder(self.home, self.counters)
        self._pwm = MotorPacket(
            motor_count=vehicle.rotor_count,
            pwm_us=(self.IDLE_PWM_US,) * SIMULATOR_MAX_PWM_CHANNELS,
        )
        self.motor_packets_seen = 0
        self.frame_count = 0
        self.last_outputs: RotorOutputs | None = None

    @property
    def pwm(self) -> MotorPacket:
        """The most recent motor packet, or the idle hold before the first."""
        return self._pwm

    def handle_motor_datagram(self, data: bytes) -> bool:
        """Latch one ``servo_packet_raw``.  Returns whether it was usable."""
        try:
            packet = decode_motor_packet(data)
        except BetaflightProtocolError as exc:
            self.counters.malformed_packets += 1
            logger.warning("dropping datagram: %s", exc)
            return False
        self.counters.packets_received += 1
        self.motor_packets_seen += 1
        self._pwm = packet
        return True

    def advance(self, dt_s: float) -> bytes:
        """Step ``dt_s`` on the latched PWM and return the ``fdm_packet``."""
        if dt_s >= MAX_SIM_STEP_S:
            self.counters.steps_capped += 1
            dt_s = MAX_SIM_STEP_S * 0.99
        self.frame_count += 1
        result = self.step(
            self._pwm.pwm_for_channel, dt_s, frame_count=self.frame_count
        )
        self.last_outputs = result.outputs
        return self.encoder.encode(result.sample)

    # -------------------------------------------------------------- truth

    def truth(self) -> dict[str, object]:
        """Ground truth for a mission driver's assertions.

        The flight controller's own estimate is available over MSP; this is what
        actually happened, which is the only honest thing to assert a hover band
        against.
        """
        state = self.state
        outputs = self.last_outputs
        return {
            "t": self.sim_time_s,
            "position_ned_m": [float(v) for v in state.position_ned_m],
            "velocity_ned_m_s": [float(v) for v in state.velocity_ned_m_s],
            "altitude_m": float(-state.position_ned_m[2]),
            "heading_deg": math.degrees(quaternion_yaw(state.quaternion)) % 360.0,
            "quaternion": [float(v) for v in state.quaternion],
            "omega_body_rad_s": [float(v) for v in state.omega_body_rad_s],
            "pwm_us": list(self._pwm.pwm_us[: self.vehicle.rotor_count]),
            "motor_packets": self.motor_packets_seen,
            "frames": self.counters.frames_advanced,
            # The propulsion lane the wire protocol has nowhere to put. The full
            # per-rotor record is the rotor log; this is enough for a mission
            # driver to report and assert on without parsing it.
            "voltage_bus_V": float(outputs.voltage_bus_V) if outputs else None,
            "current_bus_A": float(outputs.current_bus_A) if outputs else None,
            "battery_soc": float(outputs.battery_soc) if outputs else None,
            "all_in_envelope": bool(outputs.all_in_envelope) if outputs else None,
        }


@dataclass
class BetaflightServer:
    """Sockets and the soft-realtime clock around :class:`BetaflightBridge`.

    One socket bound on 9001 for the motor feed, one unbound socket that sends
    the FDM packets to 9003 and (optionally) a ground-truth JSON fan-out.  RC is
    NOT sent from here: a mission driver owns the sticks, and
    :func:`encode_rc_packet` is the seam it uses.
    """

    bridge: BetaflightBridge
    host: str = "127.0.0.1"
    motor_port: int = PORT_PWM_RAW
    sitl_host: str = "127.0.0.1"
    state_port: int = PORT_STATE
    #: Sim seconds per FDM packet.  Must stay under ``MAX_SIM_STEP_S`` or the
    #: flight controller stops refreshing ``simRate`` — and well under it, since
    #: ``simRate`` is the RATIO of this to the wall gap and a millisecond of
    #: scheduling jitter is 25% of a 4 ms period but only 10% of a 10 ms one.
    step_s: float = 0.01
    #: Sim seconds per wall second.  1.0 is real time; Betaflight's scheduler
    #: tracks the FDM clock, so above ~2 it starts losing loop iterations.
    speedup: float = 1.0
    truth_port: int | None = None
    truth_host: str = "127.0.0.1"
    #: Ground-truth fan-out rate, Hz.  Nothing needs it at the FDM rate.
    truth_rate_hz: float = 20.0
    recv_buffer_bytes: int = 512
    #: Sim steps the clock skipped rather than sprinting to catch up.  A large
    #: number means the FMU step cannot keep up with ``step_s`` and the flight
    #: controller is running in slower-than-wall time.
    steps_dropped: int = field(default=0, init=False)
    _motor_socket: socket.socket | None = field(default=None, init=False, repr=False)
    _out_socket: socket.socket | None = field(default=None, init=False, repr=False)
    _running: bool = field(default=False, init=False, repr=False)

    def open(self) -> None:
        motor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        motor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        motor.bind((self.host, self.motor_port))
        motor.setblocking(False)
        self._motor_socket = motor
        self._out_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        logger.info(
            "listening for Betaflight servo_packet_raw on %s:%d, feeding %s:%d "
            "at %.1f Hz sim (%.4f s/step, speedup %.2f)",
            self.host,
            self.motor_port,
            self.sitl_host,
            self.state_port,
            1.0 / self.step_s,
            self.step_s,
            self.speedup,
        )

    def close(self) -> None:
        for name in ("_motor_socket", "_out_socket"):
            sock = getattr(self, name)
            if sock is not None:
                sock.close()
                setattr(self, name, None)

    def stop(self) -> None:
        self._running = False

    def _drain_motor_socket(self) -> None:
        assert self._motor_socket is not None
        while True:
            try:
                data, _ = self._motor_socket.recvfrom(self.recv_buffer_bytes)
            except BlockingIOError:
                return
            except OSError:
                return
            self.bridge.handle_motor_datagram(data)

    def _send_state(self, packet: bytes) -> None:
        assert self._out_socket is not None
        try:
            self._out_socket.sendto(packet, (self.sitl_host, self.state_port))
        except OSError:
            # The flight controller has not bound 9003 yet (or has exited).
            # Linux surfaces the ICMP port-unreachable on the NEXT send, so a
            # bridge started before SITL would otherwise die on frame two.
            pass

    def serve_forever(self, duration_s: float | None = None) -> None:
        """Run the clock.  ``duration_s`` is WALL seconds; ``None`` is forever.

        THE FLIGHT CONTROLLER'S CLOCK IS THIS LOOP'S PACING, and it is not
        forgiving.  ``sitl.c`` sets ``simRate = deltaSim / wall_gap`` from ONE
        packet pair — the smoothed version is commented out — and ``micros64()``
        then advances real elapsed time TIMES ``simRate`` until the next packet
        replaces it.  ``simRate`` is therefore ``1/wall_gap``, a CONVEX function
        of the jitter: a gap half as long as intended doubles the clock, and no
        long gap ever pays that back.  A loop that sends AFTER its physics step
        turns one slow step into a long gap immediately followed by a short one,
        and the short one is the expensive half.  Measured 2026-08-30 at a
        perfectly good mean rate of 98.7 Hz: the flight controller's clock ran
        2.8x wall, its receiver declared FAILSAFE RXLOSS over an RC stream that
        never stopped, and every arm died inside two seconds.

        So the send is the FIRST thing after the sleep, carrying a packet
        computed on the PREVIOUS tick.  Nothing but ``time.monotonic()`` sits
        between waking and sending, and the FMU step's own variance no longer
        reaches Betaflight's clock.
        """
        if self._motor_socket is None:
            self.open()
        period = self.step_s / self.speedup
        truth_period = 1.0 / self.truth_rate_hz if self.truth_port else None

        self._drain_motor_socket()
        packet = self.bridge.advance(self.step_s)

        started = time.monotonic()
        next_tick = started
        next_truth = started
        self._running = True
        while self._running:
            now = time.monotonic()
            if duration_s is not None and now - started >= duration_s:
                return
            if now < next_tick:
                time.sleep(next_tick - now)
                continue

            self._send_state(packet)
            behind = next_tick + period < now
            # Never fire early to catch up, and never carry a debt that makes
            # the NEXT tick fire early either: a step that could not be
            # delivered on time is DROPPED. Sim time then falls behind wall
            # time, simRate stays at or below 1, and that is always safe.
            next_tick = max(next_tick + period, now + period)
            if behind:
                self.steps_dropped += 1

            # Everything below happens in the gap, not before the send.
            self._drain_motor_socket()
            packet = self.bridge.advance(self.step_s)

            if truth_period is not None and now >= next_truth:
                next_truth = now + truth_period
                try:
                    self._out_socket.sendto(
                        json.dumps(self.bridge.truth()).encode("ascii"),
                        (self.truth_host, int(self.truth_port)),
                    )
                except OSError:
                    pass  # fire-and-forget: a listener must never stall the sim

    def __enter__(self) -> BetaflightServer:
        self.open()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()


__all__ = [
    "FDM_PACKET_BYTES",
    "GRAVITY_MSS",
    "METRES_PER_DEGREE",
    "PORT_MSP",
    "PORT_PWM_RAW",
    "PORT_RC",
    "PORT_STATE",
    "RC_PACKET_BYTES",
    "SERVO_PACKET_RAW_BYTES",
    "BetaflightBridge",
    "BetaflightProtocolError",
    "BetaflightServer",
    "BetaflightStateEncoder",
    "HomeOrigin",
    "MotorPacket",
    "accel_packet_from_specific_force",
    "decode_motor_packet",
    "decode_rc_packet",
    "encode_motor_packet",
    "encode_rc_packet",
    "geodetic_packet_from_ned",
    "gyro_packet_from_body",
    "quaternion_nwu_from_ned",
    "quaternion_packet_from_ned",
    "velocity_enu_from_ned",
]
