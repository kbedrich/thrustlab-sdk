"""Betaflight SITL wire format and frame conversions.

Golden bytes are written out from the struct layout by hand, not from the
encoder, so a change to either side of the wire fails here.  The frame
conversions are checked by round-tripping through :mod:`tests.betaflight_fc`,
which is Betaflight's own receive side transcribed from the flight-controller
source — the encoder is correct exactly when the flight controller recovers the
truth from it.
"""

from __future__ import annotations

import math
import struct

import numpy as np
import pytest

from thrustlab.sitl.rigidbody import BodyState, quaternion_from_euler
from thrustlab.sitl.targets.base import StateSample
from thrustlab.sitl.targets.betaflight import (
    FDM_PACKET_BYTES,
    PORT_MSP,
    PORT_PWM_RAW,
    PORT_RC,
    PORT_STATE,
    RC_PACKET_BYTES,
    SERVO_PACKET_RAW_BYTES,
    BetaflightProtocolError,
    BetaflightStateEncoder,
    HomeOrigin,
    MotorPacket,
    accel_packet_from_specific_force,
    decode_motor_packet,
    decode_rc_packet,
    encode_motor_packet,
    encode_rc_packet,
    geodetic_packet_from_ned,
    gyro_packet_from_body,
    quaternion_nwu_from_ned,
    quaternion_packet_from_ned,
    velocity_enu_from_ned,
)

from . import betaflight_fc as fc

GRAVITY = 9.80665
HOME = HomeOrigin(latitude_deg=-27.5, longitude_deg=153.0, altitude_m=30.0)


# ─────────────────────────────────────────────────────────── struct layouts


def test_the_ports_are_the_ones_sitl_c_binds():
    """``sitl.c`` lines 201-204, plus BASE_PORT 5760 + UART1."""
    assert (PORT_PWM_RAW, PORT_STATE, PORT_RC, PORT_MSP) == (9001, 9003, 9004, 5761)


def test_packet_sizes_match_the_c_structs():
    # servo_packet_raw: uint16 + 2 pad (float alignment) + 16 floats
    assert SERVO_PACKET_RAW_BYTES == 2 + 2 + 16 * 4 == 68
    # fdm_packet: 18 doubles, no padding
    assert FDM_PACKET_BYTES == 18 * 8 == 144
    # rc_packet: double + 16 uint16, no tail padding
    assert RC_PACKET_BYTES == 8 + 16 * 2 == 40


def test_servo_packet_raw_golden_bytes_carry_two_pad_bytes():
    """The two bytes after ``motorCount`` are PADDING, not data.

    Reading the struct as ``<H16f`` instead of ``<H2x16f`` shifts every float by
    two bytes and turns a hovering quad into noise, so the layout is pinned to a
    literal here.
    """
    golden = (
        b"\x04\x00"          # uint16 motorCount = 4
        b"\x00\x00"          # 2 bytes of alignment padding
        b"\x00\x00\xfaD"     # float 2000.0
        b"\x00\x00zD"        # float 1000.0
        b"\x00\x80\xbbD"     # float 1500.0
        b"\x00\x00\x00\x00"  # float 0.0
    ) + b"\x00" * (12 * 4)   # channels 5-16 untouched
    assert len(golden) == SERVO_PACKET_RAW_BYTES

    packet = decode_motor_packet(golden)
    assert packet.motor_count == 4
    assert packet.pwm_us[:4] == (2000.0, 1000.0, 1500.0, 0.0)
    assert encode_motor_packet(packet) == golden


def test_motor_packet_round_trips():
    pwm = tuple(1000.0 + 10.0 * i for i in range(16))
    packet = MotorPacket(motor_count=6, pwm_us=pwm)
    assert decode_motor_packet(encode_motor_packet(packet)) == packet


def test_channels_are_one_based_with_servos_after_the_motors():
    """``pwmWriteMotor`` fills ``[index]``; ``servoWrite`` fills
    ``[index + motorCount]``."""
    pwm = tuple(float(1000 + i) for i in range(16))
    packet = MotorPacket(motor_count=4, pwm_us=pwm)
    assert packet.pwm_for_channel(1) == 1000.0   # motor 0
    assert packet.pwm_for_channel(4) == 1003.0   # motor 3
    assert packet.pwm_for_channel(5) == 1004.0   # servo 0 sits at index 4
    with pytest.raises(BetaflightProtocolError):
        packet.pwm_for_channel(0)
    with pytest.raises(BetaflightProtocolError):
        packet.pwm_for_channel(17)


def test_the_port_9002_packet_is_rejected_with_a_pointed_message():
    """``servo_packet`` is 4 normalised floats and cannot describe a hex."""
    with pytest.raises(BetaflightProtocolError, match="servo_packet"):
        decode_motor_packet(struct.pack("<4f", 0.5, 0.5, 0.5, 0.5))


def test_a_motor_count_beyond_the_struct_is_rejected():
    with pytest.raises(BetaflightProtocolError, match="17 motors"):
        decode_motor_packet(struct.pack("<H2x16f", 17, *([1000.0] * 16)))


def test_rc_packet_golden_bytes():
    golden = struct.pack("<d", 1.5) + struct.pack(
        "<16H", 1500, 1500, 1000, 1500, 2000, 1000, 1000, 1000,
        0, 0, 0, 0, 0, 0, 0, 0,
    )
    assert len(golden) == RC_PACKET_BYTES
    encoded = encode_rc_packet(1.5, [1500, 1500, 1000, 1500, 2000, 1000, 1000, 1000])
    assert encoded == golden
    timestamp, channels = decode_rc_packet(encoded)
    assert timestamp == 1.5
    assert channels[:5] == (1500, 1500, 1000, 1500, 2000)


def test_rc_packet_rejects_more_than_sixteen_channels():
    with pytest.raises(BetaflightProtocolError, match="16 channels"):
        encode_rc_packet(0.0, [1500] * 17)


# ────────────────────────────────────────────────────── frame conversions


def test_roll_and_pitch_go_on_the_wire_as_body_frd_rates():
    """``sitlGyroBodyFromSim`` reads the packet as FRD, so roll passes through
    and the flight controller negates pitch itself to reach its
    nose-down-positive convention."""
    assert gyro_packet_from_body([0.1, -0.2, 0.0])[:2] == (0.1, -0.2)
    assert fc.fc_gyro(gyro_packet_from_body([0.1, -0.2, 0.0]))[:2] == (0.1, 0.2)


def test_a_nose_right_turn_reaches_the_flight_controller_negative():
    """Betaflight's yaw axis is COUNTER-CLOCKWISE-positive where the rate loop
    closes, so a nose-right (FRD ``r`` positive) turn must arrive negative.

    Get this backwards and the yaw loop is POSITIVE feedback.  Measured
    2026-08-30 on the un-negated version: a three-second right-yaw command left
    the mixer saturated at ``[1055, 1811, 1811, 1055]`` and holding after the
    stick centred, with the true yaw rate climbing monotonically through
    45 rad/s.  ``sitl_gyro.h``'s "CW viewed from above" annotation is what makes
    this easy to get backwards; ``mixer.c``'s ``scaledAxisPidYaw = -pidSum`` is
    what actually decides it.
    """
    assert gyro_packet_from_body([0.0, 0.0, 1.0])[2] == -1.0
    assert fc.fc_gyro(gyro_packet_from_body([0.0, 0.0, 1.0]))[2] < 0.0


def test_the_accelerometer_reaches_the_flight_controller_as_one_g_up():
    """A level vehicle at rest reads ``(0, 0, -g)`` in FRD; the flight
    controller must see ``+1 g`` on its Z-up axis."""
    packet = accel_packet_from_specific_force([0.0, 0.0, -GRAVITY])
    assert packet == pytest.approx((0.0, 0.0, -GRAVITY))
    assert fc.fc_accel(packet) == pytest.approx((0.0, 0.0, GRAVITY))


def test_the_accelerometer_x_axis_flips_and_y_z_survive():
    """``packet = -f_FLU`` and FLU is FRD with y and z negated."""
    assert accel_packet_from_specific_force([1.0, 2.0, 3.0]) == (-1.0, 2.0, 3.0)
    # Forward acceleration: FRD +x specific force must reach the flight
    # controller's nose-forward axis positive.
    assert fc.fc_accel(accel_packet_from_specific_force([2.0, 0.0, 0.0]))[0] == 2.0


def test_nwu_quaternion_is_the_ned_one_with_y_and_z_negated():
    """Heading east: NED yaw +90° is NWU yaw -90° (NWU counts CCW)."""
    q_ned = quaternion_from_euler(0.0, 0.0, math.pi / 2)
    assert quaternion_nwu_from_ned(q_ned) == pytest.approx(
        (math.sqrt(0.5), 0.0, 0.0, -math.sqrt(0.5))
    )


@pytest.mark.parametrize(
    ("roll", "pitch", "yaw"),
    [
        (0.0, 0.0, 0.0),
        (0.0, 0.0, math.pi / 2),
        (0.0, 0.0, -2.5),
        (0.3, -0.2, 1.1),
        (-0.7, 0.4, -3.0),
    ],
)
def test_the_flight_controller_reconstructs_our_attitude_exactly(roll, pitch, yaw):
    """``sitl.c`` applies ``Rz(π/2) ⊗ conj_x180(·)``; the encoder pre-applies
    the inverse, so the round trip is the identity on the NWU attitude."""
    q_ned = quaternion_from_euler(roll, pitch, yaw)
    recovered = fc.fc_attitude_quaternion(quaternion_packet_from_ned(q_ned))
    expected = quaternion_nwu_from_ned(q_ned)
    # A quaternion and its negation are the same rotation.
    assert np.allclose(recovered, expected) or np.allclose(recovered, -np.array(expected))


def test_the_level_attitude_packet_is_the_golden_rz_minus_90():
    """Level, heading north: the packet carries ``Rz(-90°)`` pre-rotation."""
    packet = quaternion_packet_from_ned([1.0, 0.0, 0.0, 0.0])
    assert packet == pytest.approx((math.sqrt(0.5), 0.0, 0.0, math.sqrt(0.5)))


def test_velocity_goes_out_enu_and_comes_back_ned():
    """``velocity_xyz`` is ``(Ve, Vn, Vup)`` under ``USE_VIRTUAL_GPS``."""
    ned = [3.0, -4.0, 2.0]  # north, east, down
    packet = velocity_enu_from_ned(ned)
    assert packet == (-4.0, 3.0, -2.0)
    assert fc.fc_velocity_ned(packet) == pytest.approx(tuple(ned))


def test_ground_course_is_a_bearing_from_north():
    """Flying due east must read 090°, which only works if ``[0]`` is East."""
    assert fc.fc_ground_course_deg(velocity_enu_from_ned([0.0, 5.0, 0.0])) == pytest.approx(90.0)
    assert fc.fc_ground_course_deg(velocity_enu_from_ned([5.0, 0.0, 0.0])) == pytest.approx(0.0)


def test_the_first_packet_sits_at_home_so_the_flight_controller_latches_home():
    """The mirroring is only self-consistent if the origin the flight
    controller latches is home itself."""
    lon, lat, alt = geodetic_packet_from_ned([0.0, 0.0, 0.0], HOME)
    assert lon == pytest.approx(HOME.longitude_deg)
    assert lat == pytest.approx(HOME.latitude_deg)
    assert alt == pytest.approx(HOME.altitude_m)


def test_the_mirrored_position_decodes_back_to_the_truth():
    """``sitl.c`` un-mirrors with ``2·origin − value`` against the latched
    origin, which the first packet made equal to home."""
    north, east, down = 100.0, -40.0, -25.0
    lon, lat, alt = geodetic_packet_from_ned([north, east, down], HOME)
    assert fc.fc_gps_is_valid(lon, lat)
    got_lon, got_lat = fc.fc_gps_degrees(lon, lat, HOME.longitude_deg, HOME.latitude_deg)

    true_lat = HOME.latitude_deg + north / 111319.49
    true_lon = HOME.longitude_deg + east / (
        111319.49 * math.cos(math.radians(HOME.latitude_deg))
    )
    assert got_lat == pytest.approx(true_lat, abs=1e-12)
    assert got_lon == pytest.approx(true_lon, abs=1e-12)
    assert alt == pytest.approx(HOME.altitude_m + 25.0)


def test_altitude_drives_the_barometer_not_the_pressure_field():
    """The Gazebo bridge derives pressure from ``position_xyz[2]``; a 100 m
    climb must show up as roughly 12 hPa less."""
    _, _, ground = geodetic_packet_from_ned([0.0, 0.0, 0.0], HomeOrigin(altitude_m=0.0))
    _, _, up100 = geodetic_packet_from_ned([0.0, 0.0, -100.0], HomeOrigin(altitude_m=0.0))
    drop = fc.fc_baro_pressure_pa(ground) - fc.fc_baro_pressure_pa(up100)
    assert 1150 < drop < 1250


# ─────────────────────────────────────────────────────────── whole packet


def _sample(**overrides) -> StateSample:
    defaults = dict(
        timestamp_s=1.25,
        state=BodyState.at_rest(),
        accel_body_m_s2=np.array([0.0, 0.0, -GRAVITY]),
        airspeed_m_s=0.0,
        voltage_bus_V=22.2,
        current_bus_A=10.0,
        battery_soc=0.8,
    )
    defaults.update(overrides)
    return StateSample(**defaults)


def test_the_fdm_packet_is_eighteen_doubles_in_the_documented_order():
    encoder = BetaflightStateEncoder(HOME)
    state = BodyState(
        position_ned_m=np.array([10.0, 20.0, -30.0]),
        velocity_ned_m_s=np.array([1.0, 2.0, -3.0]),
        quaternion=quaternion_from_euler(0.0, 0.0, 0.0),
        omega_body_rad_s=np.array([0.1, 0.2, 0.3]),
    )
    data = encoder.encode(_sample(state=state))
    assert len(data) == FDM_PACKET_BYTES

    values = struct.unpack("<18d", data)
    assert values[0] == 1.25                                   # timestamp
    assert values[1:4] == (0.1, 0.2, -0.3)                     # gyro, FRD, yaw negated
    assert values[4:7] == pytest.approx((0.0, 0.0, -GRAVITY))  # accel
    assert values[7:11] == pytest.approx(                      # quaternion
        (math.sqrt(0.5), 0.0, 0.0, math.sqrt(0.5))
    )
    assert values[11:14] == pytest.approx((2.0, 1.0, 3.0))     # velocity ENU
    assert values[16] == pytest.approx(HOME.altitude_m + 30.0)  # altitude
    assert values[17] == 101325.0                              # pressure field


def test_a_non_finite_state_is_zeroed_and_counted_rather_than_sent():
    """A NaN reaching the flight controller poisons its estimator for the whole
    run, and the binary wire has no way to omit a field."""
    from thrustlab.sitl.targets.base import BridgeCounters

    counters = BridgeCounters()
    encoder = BetaflightStateEncoder(HOME, counters)
    state = BodyState(
        position_ned_m=np.array([np.nan, 0.0, 0.0]),
        velocity_ned_m_s=np.array([0.0, np.inf, 0.0]),
        quaternion=quaternion_from_euler(0.0, 0.0, 0.0),
        omega_body_rad_s=np.zeros(3),
    )
    values = struct.unpack("<18d", encoder.encode(_sample(state=state)))
    assert all(math.isfinite(v) for v in values)
    assert counters.non_finite_substitutions == 2


def test_the_step_size_stays_inside_the_sim_rate_window():
    """``sitl.c`` only refreshes ``simRate`` while ``0 < deltaSim < 0.02``."""
    from thrustlab.sitl.targets.betaflight import MAX_SIM_STEP_S, BetaflightServer

    assert fc.fc_updates_sim_rate(BetaflightServer.step_s)
    assert not fc.fc_updates_sim_rate(MAX_SIM_STEP_S)
