"""ArduPilot SITL JSON-backend wire format: servo packets in, state JSON out.

Every claim in this module was checked against ArduPilot master on 2026-08-29:

  * ``libraries/SITL/SIM_JSON.h``   — packet structs, ``keytable[36]``
  * ``libraries/SITL/SIM_JSON.cpp`` — ``parse_sensors``, ``recv_fdm``
  * ``libraries/SITL/examples/JSON/readme.md``

────────────────────────────────────────────────────────────────────────────────
SITL -> bridge (binary, little endian, no padding)
────────────────────────────────────────────────────────────────────────────────
``SIM_JSON.h``::

    struct servo_packet_16 { uint16_t magic = 18458; uint16_t frame_rate;
                             uint32_t frame_count; uint16_t pwm[16]; };   // 40 B
    struct servo_packet_32 { uint16_t magic = 29569; uint16_t frame_rate;
                             uint32_t frame_count; uint16_t pwm[32]; };   // 72 B

``uint32_t`` sits at offset 4 and both structs are a multiple of 4 bytes long, so
the natural C layout has no padding and ``<HHI16H`` / ``<HHI32H`` are exact.
SITL emits the 32-channel form when ``SERVO_32_ENABLE = 1``.

────────────────────────────────────────────────────────────────────────────────
bridge -> SITL (plain text JSON)
────────────────────────────────────────────────────────────────────────────────
TWO framing rules follow from ``recv_fdm`` and are easy to get wrong:

1. Every ``'\\n'`` in the datagram is turned into a NUL, then the parser takes
   the text between the LAST two NULs.  A datagram carrying only a trailing
   newline has one NUL, so ``memrchr`` for the second one returns ``nullptr``
   and the frame is silently dropped.  The payload must therefore be
   ``b"\\n" + json + b"\\n"`` — leading newline included.
2. ``parse_sensors`` is a ``strstr`` scanner, not a JSON parser.  For each
   keytable row it finds ``section`` anywhere in the buffer, then ``key`` after
   it, then skips ``strlen(key) + 2`` bytes (past ``":``) and runs ``strtod``.
   Consequences the encoder below is built around:

   * separators must be compact (``"key":value``) — a space after the colon
     survives ``strtod`` but not the ``+2`` skip for every type;
   * a key that is a PREFIX of another key wins by position in the string, not
     by keytable order.  ``velocity`` is a prefix of ``velocity_wind``, so this
     encoder never emits ``velocity_wind``; if that ever changes, ``velocity``
     must still be serialised first.  ``_KEYTABLE_PREFIX_HAZARDS`` documents the
     full set and ``tests/test_protocol.py`` re-implements the ArduPilot scanner
     to prove our payload resolves correctly.

Mandatory fields (``required = true`` in ``keytable``): ``timestamp``,
``imu/gyro``, ``imu/accel_body``, ``velocity``.  ``recv_fdm`` additionally
refuses a frame carrying neither ``attitude`` nor ``quaternion``; when both are
present the quaternion wins.
"""

from __future__ import annotations

import json
import math
import struct
from collections.abc import Sequence
from dataclasses import dataclass

MAGIC_16 = 18458
MAGIC_32 = 29569

_FORMAT_16 = "<HHI16H"
_FORMAT_32 = "<HHI32H"
SERVO_PACKET_16_BYTES = struct.calcsize(_FORMAT_16)  # 40
SERVO_PACKET_32_BYTES = struct.calcsize(_FORMAT_32)  # 72

_BY_SIZE: dict[int, tuple[int, str, int]] = {
    SERVO_PACKET_16_BYTES: (MAGIC_16, _FORMAT_16, 16),
    SERVO_PACKET_32_BYTES: (MAGIC_32, _FORMAT_32, 32),
}

# Pairs from ArduPilot's keytable where the first member is a substring of the
# second.  parse_sensors matches by POSITION in the buffer, so emitting the
# longer member first makes SITL read the wrong value into the shorter key.
# (short_key, long_key_that_contains_it)
_KEYTABLE_PREFIX_HAZARDS = (
    ("velocity", "velocity_wind"),
    ("rc_1", "rc_10"),
    ("rc_1", "rc_11"),
    ("rc_1", "rc_12"),
)


class ProtocolError(ValueError):
    """A datagram that is not a well-formed ArduPilot servo packet."""


@dataclass(frozen=True)
class ServoPacket:
    """One decoded ``servo_packet_16`` / ``servo_packet_32``."""

    magic: int
    frame_rate: int
    frame_count: int
    pwm: tuple[int, ...]

    @property
    def channel_count(self) -> int:
        return len(self.pwm)

    def pwm_for_channel(self, servo_channel: int) -> int:
        """PWM (microseconds) for a 1-based ArduPilot servo channel.

        ``SERVO1_FUNCTION`` drives ``input.servos[0]`` which SITL copies to
        ``pwm[0]`` (``SIM_JSON.cpp::output_servos``), so channel *n* is
        ``pwm[n - 1]``.
        """
        if servo_channel < 1 or servo_channel > self.channel_count:
            raise ProtocolError(
                f"servo channel {servo_channel} is outside the {self.channel_count} "
                f"channels carried by this packet (magic {self.magic}); enable "
                f"SERVO_32_ENABLE in ArduPilot if you need channels 17-32"
            )
        return self.pwm[servo_channel - 1]


def decode_servo_packet(data: bytes) -> ServoPacket:
    """Decode a servo packet, raising :class:`ProtocolError` on anything else."""
    entry = _BY_SIZE.get(len(data))
    if entry is None:
        raise ProtocolError(
            f"servo packet is {len(data)} bytes; expected {SERVO_PACKET_16_BYTES} "
            f"(16 channels) or {SERVO_PACKET_32_BYTES} (32 channels)"
        )
    expected_magic, fmt, channels = entry
    fields = struct.unpack(fmt, data)
    magic = fields[0]
    if magic != expected_magic:
        raise ProtocolError(
            f"servo packet magic {magic} does not match {expected_magic} expected "
            f"for a {channels}-channel packet"
        )
    return ServoPacket(
        magic=magic,
        frame_rate=fields[1],
        frame_count=fields[2],
        pwm=tuple(fields[3:]),
    )


def encode_servo_packet(packet: ServoPacket) -> bytes:
    """Re-encode a servo packet.  Used by the tests and by fixture capture."""
    channels = packet.channel_count
    if channels == 16:
        fmt, expected_magic = _FORMAT_16, MAGIC_16
    elif channels == 32:
        fmt, expected_magic = _FORMAT_32, MAGIC_32
    else:
        raise ProtocolError(f"servo packets carry 16 or 32 channels, not {channels}")
    if packet.magic != expected_magic:
        raise ProtocolError(
            f"magic {packet.magic} does not match {expected_magic} for {channels} channels"
        )
    return struct.pack(fmt, packet.magic, packet.frame_rate, packet.frame_count, *packet.pwm)


@dataclass(frozen=True)
class StateReply:
    """The physics state ArduPilot reads back, in ArduPilot's own frames.

    ``position``/``velocity`` are NED metres and m/s relative to the SITL home
    origin.  ``gyro`` is body FRD rad/s.  ``accel_body`` is the ACCELEROMETER
    reading — specific force, not kinematic acceleration.  ``SIM_Aircraft.cpp``
    is explicit about it::

        accel_body = dcm.transposed() * (accel_earth + Vector3f(0, 0, -GRAVITY_MSS));

    so a level vehicle at rest reports ``(0, 0, -9.80665)``.  See
    :mod:`thrustlab.sitl.rigidbody`.

    ``quaternion`` is ``(q1, q2, q3, q4) = (w, x, y, z)`` for the body->NED
    rotation, matching ``Quaternion::rotation_matrix`` filling ArduPilot's
    body-to-earth ``dcm``.
    """

    timestamp_s: float
    gyro_rad_s: Sequence[float]
    accel_body_m_s2: Sequence[float]
    position_ned_m: Sequence[float]
    velocity_ned_m_s: Sequence[float]
    quaternion: Sequence[float]
    airspeed_m_s: float | None = None
    battery_voltage_V: float | None = None
    battery_current_A: float | None = None


def _finite(value: float) -> float:
    """Replace a non-finite number with 0.0.

    A NaN reaching SITL poisons the EKF for the rest of the run and the failure
    surfaces far from its cause, so the bridge substitutes zero and lets the
    caller log it (:func:`encode_state_json` reports the substitution count).
    """
    number = float(value)
    return number if math.isfinite(number) else 0.0


def encode_state_json(state: StateReply) -> tuple[bytes, int]:
    """Serialise ``state`` into the exact bytes to put on the wire.

    Returns ``(payload, non_finite_count)``.  The payload carries the leading
    AND trailing newline required by ``recv_fdm`` (see the module docstring).
    Key order is deliberate — do not reorder without re-reading
    ``_KEYTABLE_PREFIX_HAZARDS``.
    """
    substitutions = 0

    def scalar(value: float) -> float:
        nonlocal substitutions
        if not math.isfinite(float(value)):
            substitutions += 1
        return _finite(value)

    def vector(values: Sequence[float]) -> list[float]:
        return [scalar(v) for v in values]

    body: dict[str, object] = {
        "timestamp": scalar(state.timestamp_s),
        "imu": {
            "gyro": vector(state.gyro_rad_s),
            "accel_body": vector(state.accel_body_m_s2),
        },
        "position": vector(state.position_ned_m),
        "velocity": vector(state.velocity_ned_m_s),
        "quaternion": vector(state.quaternion),
    }
    if state.airspeed_m_s is not None:
        body["airspeed"] = scalar(state.airspeed_m_s)
    if state.battery_voltage_V is not None or state.battery_current_A is not None:
        battery: dict[str, float] = {}
        if state.battery_voltage_V is not None:
            battery["voltage"] = scalar(state.battery_voltage_V)
        if state.battery_current_A is not None:
            battery["current"] = scalar(state.battery_current_A)
        body["battery"] = battery

    text = json.dumps(body, separators=(",", ":"), allow_nan=False)
    return b"\n" + text.encode("ascii") + b"\n", substitutions
