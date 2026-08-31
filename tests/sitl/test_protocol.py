"""Wire format: servo packet codec both sizes, and state JSON ArduPilot can read."""

from __future__ import annotations

import json
import struct

import pytest

from thrustlab.sitl.protocol import (
    MAGIC_16,
    MAGIC_32,
    SERVO_PACKET_16_BYTES,
    SERVO_PACKET_32_BYTES,
    ProtocolError,
    ServoPacket,
    StateReply,
    decode_servo_packet,
    encode_servo_packet,
    encode_state_json,
)

from .ardupilot_parser import FramingError, frame_payload, parse_sensors


def make_packet(channels: int = 16, *, frame_count: int = 7, frame_rate: int = 400) -> ServoPacket:
    magic = MAGIC_16 if channels == 16 else MAGIC_32
    return ServoPacket(
        magic=magic,
        frame_rate=frame_rate,
        frame_count=frame_count,
        pwm=tuple(1000 + 10 * i for i in range(channels)),
    )


# ------------------------------------------------------------------ codec


def test_packet_sizes_match_the_c_structs():
    # servo_packet_16: 2 + 2 + 4 + 32; servo_packet_32: 2 + 2 + 4 + 64. The
    # uint32 is naturally aligned at offset 4 and both totals are multiples of
    # 4, so the C layout has no padding.
    assert SERVO_PACKET_16_BYTES == 40
    assert SERVO_PACKET_32_BYTES == 72


@pytest.mark.parametrize("channels", [16, 32])
def test_servo_packet_round_trips(channels: int):
    packet = make_packet(channels)
    encoded = encode_servo_packet(packet)
    assert len(encoded) == (SERVO_PACKET_16_BYTES if channels == 16 else SERVO_PACKET_32_BYTES)
    assert decode_servo_packet(encoded) == packet


@pytest.mark.parametrize(
    ("channels", "magic", "fmt"),
    [(16, MAGIC_16, "<HHI16H"), (32, MAGIC_32, "<HHI32H")],
)
def test_decode_matches_a_hand_built_packet(channels: int, magic: int, fmt: str):
    pwm = [1500] * channels
    raw = struct.pack(fmt, magic, 400, 12345, *pwm)
    packet = decode_servo_packet(raw)
    assert packet.magic == magic
    assert packet.frame_rate == 400
    assert packet.frame_count == 12345
    assert packet.channel_count == channels
    assert packet.pwm == tuple(pwm)


def test_pwm_lookup_is_one_based_on_the_servo_channel():
    packet = make_packet(16)
    # SERVO1_FUNCTION drives input.servos[0] -> pwm[0].
    assert packet.pwm_for_channel(1) == packet.pwm[0]
    assert packet.pwm_for_channel(16) == packet.pwm[15]


@pytest.mark.parametrize("channel", [0, -1, 17])
def test_pwm_lookup_rejects_channels_outside_the_packet(channel: int):
    with pytest.raises(ProtocolError):
        make_packet(16).pwm_for_channel(channel)


def test_channel_17_needs_the_32_channel_packet():
    assert make_packet(32).pwm_for_channel(17) == 1000 + 10 * 16
    with pytest.raises(ProtocolError, match="SERVO_32_ENABLE"):
        make_packet(16).pwm_for_channel(17)


@pytest.mark.parametrize("length", [0, 1, 39, 41, 71, 73, 4096])
def test_wrong_length_is_rejected(length: int):
    with pytest.raises(ProtocolError, match="bytes"):
        decode_servo_packet(b"\x00" * length)


def test_wrong_magic_for_the_length_is_rejected():
    # The 32-channel magic in a 16-channel-sized packet: right size, wrong
    # protocol version.
    raw = struct.pack("<HHI16H", MAGIC_32, 400, 1, *([1500] * 16))
    with pytest.raises(ProtocolError, match="magic"):
        decode_servo_packet(raw)


def test_encode_rejects_a_mismatched_magic():
    bad = ServoPacket(magic=MAGIC_32, frame_rate=400, frame_count=1, pwm=(1500,) * 16)
    with pytest.raises(ProtocolError):
        encode_servo_packet(bad)


# ------------------------------------------------------------- state reply


def sample_state() -> StateReply:
    return StateReply(
        timestamp_s=2.5,
        gyro_rad_s=[0.01, -0.02, 0.03],
        accel_body_m_s2=[0.1, 0.2, -9.80665],
        position_ned_m=[1.0, -2.0, -3.5],
        velocity_ned_m_s=[0.5, 0.25, -1.25],
        quaternion=[1.0, 0.0, 0.0, 0.0],
        airspeed_m_s=1.5,
        battery_voltage_V=24.13,
        battery_current_A=61.5,
    )


def test_payload_carries_a_leading_and_trailing_newline():
    payload, _ = encode_state_json(sample_state())
    # recv_fdm parses between the LAST TWO NULs, so a trailing newline alone
    # makes ArduPilot drop the very first frame.
    assert payload.startswith(b"\n")
    assert payload.endswith(b"\n")
    assert frame_payload(payload).startswith("{")


def test_payload_is_compact():
    payload, _ = encode_state_json(sample_state())
    # parse_sensors skips strlen(key) + 2 bytes, i.e. exactly '":'.
    assert b'": ' not in payload
    assert b", " not in payload


def test_payload_is_still_valid_json():
    payload, _ = encode_state_json(sample_state())
    assert json.loads(frame_payload(payload))["timestamp"] == 2.5


def test_ardupilot_parser_resolves_every_field_we_send():
    state = sample_state()
    payload, substitutions = encode_state_json(state)
    assert substitutions == 0

    parsed = parse_sensors(payload)
    assert parsed["/timestamp"] == pytest.approx(2.5)
    assert parsed["imu/gyro"] == pytest.approx(list(state.gyro_rad_s))
    assert parsed["imu/accel_body"] == pytest.approx(list(state.accel_body_m_s2))
    assert parsed["/position"] == pytest.approx(list(state.position_ned_m))
    assert parsed["/velocity"] == pytest.approx(list(state.velocity_ned_m_s))
    assert parsed["/quaternion"] == pytest.approx(list(state.quaternion))
    assert parsed["/airspeed"] == pytest.approx(1.5)
    assert parsed["battery/voltage"] == pytest.approx(24.13)
    assert parsed["battery/current"] == pytest.approx(61.5)


def test_no_stray_keytable_row_resolves():
    """Nothing we send may accidentally satisfy a key we do not mean to set.

    ``velocity`` inside ``velocity_wind`` is the classic one; ``rc``, ``rng_*``
    and ``windvane`` are the rest of the surface.
    """
    payload, _ = encode_state_json(sample_state())
    parsed = parse_sensors(payload)
    for absent in (
        "/velocity_wind",
        "/latitude",
        "/longitude",
        "/altitude",
        "/attitude",
        "/rng_1",
        "windvane/speed",
        "windvane/direction",
        "rc/rc_1",
        "/no_lockstep",
        "/no_time_sync",
    ):
        assert absent not in parsed, f"ArduPilot would wrongly resolve {absent}"


def test_mandatory_fields_are_always_present_even_without_optional_ones():
    minimal = StateReply(
        timestamp_s=0.0,
        gyro_rad_s=[0.0, 0.0, 0.0],
        accel_body_m_s2=[0.0, 0.0, -9.80665],
        position_ned_m=[0.0, 0.0, 0.0],
        velocity_ned_m_s=[0.0, 0.0, 0.0],
        quaternion=[1.0, 0.0, 0.0, 0.0],
    )
    payload, _ = encode_state_json(minimal)
    parsed = parse_sensors(payload)  # raises if a required row is missing
    assert "/quaternion" in parsed  # recv_fdm needs attitude OR quaternion
    assert "battery/voltage" not in parsed
    assert "/airspeed" not in parsed


def test_non_finite_values_are_substituted_and_counted():
    broken = StateReply(
        timestamp_s=0.0,
        gyro_rad_s=[float("nan"), 0.0, 0.0],
        accel_body_m_s2=[0.0, float("inf"), -9.80665],
        position_ned_m=[0.0, 0.0, 0.0],
        velocity_ned_m_s=[0.0, 0.0, 0.0],
        quaternion=[1.0, 0.0, 0.0, 0.0],
    )
    payload, substitutions = encode_state_json(broken)
    assert substitutions == 2
    assert b"NaN" not in payload and b"Infinity" not in payload
    parsed = parse_sensors(payload)
    assert parsed["imu/gyro"] == pytest.approx([0.0, 0.0, 0.0])


def test_framing_helper_rejects_a_single_newline():
    with pytest.raises(FramingError):
        frame_payload(b'{"timestamp":0}\n')
