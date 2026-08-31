"""The Betaflight bridge's clock and motor latch.

Betaflight SITL is soft real time and never asks for a step, so the bridge owns
its own clock and uses the most recent PWM it has heard.  These tests pin that
behaviour — including the two failure modes that matter on a real flight: a step
that would stall ``simRate``, and PWM held from a packet that never arrived.
"""

from __future__ import annotations

import math
import struct

import numpy as np
import pytest

from thrustlab.sitl.targets.betaflight import (
    FDM_PACKET_BYTES,
    MAX_SIM_STEP_S,
    BetaflightBridge,
    HomeOrigin,
    MotorPacket,
    encode_motor_packet,
)

from . import betaflight_fc as fc


def motor_datagram(pwm_us: float, *, motor_count: int = 4) -> bytes:
    channels = tuple([pwm_us] * motor_count + [0.0] * (16 - motor_count))
    return encode_motor_packet(MotorPacket(motor_count=motor_count, pwm_us=channels))


@pytest.fixture
def bridge(quad, stub_model) -> BetaflightBridge:
    return BetaflightBridge(quad, stub_model, home=HomeOrigin())


def test_it_holds_motor_minimum_before_the_first_packet(bridge):
    """``sitl.c`` sends nothing until its mixer has run.  The vehicle must sit
    on the ground rather than free-fall or leap."""
    assert bridge.motor_packets_seen == 0
    assert bridge.pwm.pwm_for_channel(1) == BetaflightBridge.IDLE_PWM_US
    for _ in range(50):
        bridge.advance(0.004)
    assert bridge.state.position_ned_m[2] == pytest.approx(0.0)
    assert np.allclose(bridge.state.velocity_ned_m_s, 0.0)


def test_a_motor_packet_is_latched_and_reused_until_the_next_one(bridge):
    """Loose pairing: one motor packet per FDM packet AT BEST, because
    ``pwmCompleteMotorUpdate`` gives up on a ``trylock``."""
    assert bridge.handle_motor_datagram(motor_datagram(1600.0))
    assert bridge.pwm.pwm_for_channel(1) == 1600.0
    bridge.advance(0.004)
    bridge.advance(0.004)
    assert bridge.pwm.pwm_for_channel(1) == 1600.0
    assert bridge.counters.frames_advanced == 2
    assert bridge.counters.packets_received == 1


def test_a_malformed_datagram_is_counted_and_dropped(bridge):
    """The port-9002 ``servo_packet`` is the datagram that actually turns up."""
    assert not bridge.handle_motor_datagram(struct.pack("<4f", 0.5, 0.5, 0.5, 0.5))
    assert bridge.counters.malformed_packets == 1
    assert bridge.counters.packets_received == 0
    assert bridge.pwm.pwm_for_channel(1) == BetaflightBridge.IDLE_PWM_US


def test_a_step_at_or_beyond_the_sim_rate_window_is_capped(bridge):
    """``sitl.c`` refreshes ``simRate`` only while ``deltaSim < 0.02``; a step
    that lands on or past the boundary silently stops the flight controller's
    clock from tracking the simulation."""
    before = bridge.sim_time_s
    bridge.advance(0.05)
    delta = bridge.sim_time_s - before
    assert bridge.counters.steps_capped == 1
    assert delta < MAX_SIM_STEP_S
    assert fc.fc_updates_sim_rate(delta)


def test_full_throttle_climbs_and_the_packet_reports_it(bridge):
    """End to end: PWM in, 6DOF out, and the flight controller's own decoders
    read a climb out of the packet."""
    bridge.handle_motor_datagram(motor_datagram(2000.0))
    packet = b""
    for _ in range(400):  # 1.6 s of sim time
        packet = bridge.advance(0.004)

    assert len(packet) == FDM_PACKET_BYTES
    values = struct.unpack("<18d", packet)
    assert bridge.state.position_ned_m[2] < -0.5  # NED z negative is up

    velocity_ned = fc.fc_velocity_ned(values[11:14])
    assert velocity_ned[2] < 0.0  # climbing: NED down-velocity negative
    assert values[16] > HomeOrigin().altitude_m  # GPS altitude above home

    # Climbing under thrust: the accelerometer must read MORE than 1 g up.
    assert fc.fc_accel(values[4:7])[2] > 9.9


def test_the_truth_feed_reports_altitude_and_heading(bridge):
    bridge.handle_motor_datagram(motor_datagram(2000.0))
    for _ in range(200):
        bridge.advance(0.004)
    truth = bridge.truth()
    assert truth["altitude_m"] == pytest.approx(-bridge.state.position_ned_m[2])
    assert 0.0 <= truth["heading_deg"] < 360.0
    assert truth["motor_packets"] == 1
    assert truth["frames"] == 200
    assert len(truth["pwm_us"]) == 4
    # The propulsion lane the wire protocol has nowhere to put.
    assert truth["voltage_bus_V"] is not None
    assert truth["battery_soc"] is not None
    assert isinstance(truth["all_in_envelope"], bool)


def test_the_truth_feed_has_no_propulsion_lane_before_the_first_step(quad, stub_model):
    truth = BetaflightBridge(quad, stub_model).truth()
    assert truth["voltage_bus_V"] is None
    assert truth["all_in_envelope"] is None


def test_a_restart_re_seeds_the_physics_and_the_clock(bridge):
    bridge.handle_motor_datagram(motor_datagram(2000.0))
    for _ in range(100):
        bridge.advance(0.004)
    assert bridge.sim_time_s > 0.0

    bridge.restart()
    assert bridge.sim_time_s == 0.0
    assert bridge.counters.restarts == 1
    assert np.allclose(bridge.state.position_ned_m, 0.0)


def test_the_quaternion_survives_a_yawed_state(bridge):
    """A heading the flight controller must read back exactly, because the
    virtual mag is synthesised from this quaternion and fights the estimator if
    it disagrees."""
    from thrustlab.sitl.rigidbody import BodyState, quaternion_from_euler

    bridge.state = BodyState.at_rest(yaw_rad=math.radians(135.0))
    values = struct.unpack("<18d", bridge.advance(0.004))
    recovered = fc.fc_attitude_quaternion(values[7:11])
    expected = quaternion_from_euler(0.0, 0.0, math.radians(135.0))
    expected_nwu = (expected[0], expected[1], -expected[2], -expected[3])
    assert np.allclose(recovered, expected_nwu) or np.allclose(
        recovered, -np.array(expected_nwu)
    )
