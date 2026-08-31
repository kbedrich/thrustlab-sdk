"""Spec decision 12's protocol state machine, clause by clause."""

from __future__ import annotations

import numpy as np
import pytest

# MAX_STEP_S is deliberately NOT imported: the cap is asserted against
# ArduPilot's consumer predicate, never against our own constant.
from thrustlab.sitl.bridge import ARDUPILOT_MAX_DELTAT_S, DEFAULT_FRAME_RATE_HZ, Bridge
from thrustlab.sitl.protocol import MAGIC_16, MAGIC_32, ServoPacket, encode_servo_packet

from .ardupilot_parser import parse_sensors


def packet(
    frame_count: int,
    *,
    frame_rate: int = 400,
    pwm: int = 1000,
    channels: int = 16,
) -> ServoPacket:
    return ServoPacket(
        magic=MAGIC_16 if channels == 16 else MAGIC_32,
        frame_rate=frame_rate,
        frame_count=frame_count,
        pwm=(pwm,) * channels,
    )


@pytest.fixture
def bridge(quad, stub_model) -> Bridge:
    return Bridge(quad, stub_model)


# ------------------------------------------------------ one advance per frame


def test_each_new_frame_count_advances_exactly_once(bridge, stub_slave):
    for frame in range(1, 11):
        bridge.handle_packet(packet(frame))
    assert stub_slave.step_count == 10
    assert bridge.counters.frames_advanced == 10
    assert bridge.counters.duplicates_resent == 0


def test_first_frame_steps_one_nominal_period(bridge, stub_slave):
    result = bridge.handle_packet(packet(0, frame_rate=400))
    assert result.advanced is True
    assert result.dt_s == pytest.approx(1 / 400)
    assert stub_slave.last_step == (0.0, pytest.approx(1 / 400))
    assert result.timestamp_s == pytest.approx(1 / 400)


def test_reply_timestamps_are_end_of_step_and_monotone(bridge):
    timestamps = []
    for frame in range(1, 6):
        result = bridge.handle_packet(packet(frame))
        parsed = parse_sensors(result.reply)
        timestamps.append(parsed["/timestamp"])
        assert parsed["/timestamp"] == pytest.approx(result.timestamp_s)
    assert timestamps == sorted(timestamps)
    assert timestamps[0] == pytest.approx(1 / 400)
    assert timestamps[-1] == pytest.approx(5 / 400)


# ---------------------------------------------------------------- duplicates


def test_duplicate_packet_resends_the_identical_bytes_and_advances_nothing(bridge, stub_slave):
    first = bridge.handle_packet(packet(5))
    steps_after_first = stub_slave.step_count
    time_after_first = bridge.sim_time_s

    duplicate = bridge.handle_packet(packet(5))
    assert duplicate.duplicate is True
    assert duplicate.advanced is False
    assert duplicate.reply == first.reply  # byte for byte
    assert stub_slave.step_count == steps_after_first
    assert bridge.sim_time_s == time_after_first
    assert bridge.counters.duplicates_resent == 1


def test_repeated_duplicates_keep_resending_the_same_reply(bridge, stub_slave):
    first = bridge.handle_packet(packet(3))
    for _ in range(5):
        assert bridge.handle_packet(packet(3)).reply == first.reply
    assert stub_slave.step_count == 1
    assert bridge.counters.duplicates_resent == 5


def test_a_duplicate_with_a_different_pwm_still_resends_the_old_reply(bridge):
    """ArduPilot re-sends the SAME frame; the counter is the identity."""
    first = bridge.handle_packet(packet(3, pwm=1000))
    resent = bridge.handle_packet(packet(3, pwm=1900))
    assert resent.reply == first.reply


# ----------------------------------------------------------------- regression


def test_frame_count_regression_restarts_everything(bridge, stub_slave):
    for frame in range(1, 21):
        bridge.handle_packet(packet(frame, pwm=1800))
    assert bridge.sim_time_s > 0.0
    assert not np.allclose(bridge.state.position_ned_m, 0.0)
    resets_before = stub_slave.reset_count

    result = bridge.handle_packet(packet(0))
    assert result.restarted is True
    assert bridge.counters.restarts == 1
    assert stub_slave.reset_count == resets_before + 1
    # 6DOF re-seeded, clock restarted, and this packet still got its one step.
    assert np.allclose(bridge.state.position_ned_m, 0.0)
    assert bridge.sim_time_s == pytest.approx(1 / 400)
    assert result.dt_s == pytest.approx(1 / 400)


def test_restart_re_enters_initialization_mode(bridge, stub_slave):
    bridge.handle_packet(packet(9))
    stub_slave.calls.clear()
    bridge.handle_packet(packet(0))
    # fmi3Reset REQUIRES re-initialisation before the next step (decision 8).
    assert stub_slave.calls[:3] == ["reset", "enterInitializationMode", "exitInitializationMode"]
    assert "doStep" in stub_slave.calls


def test_after_a_restart_the_counter_tracking_starts_over(bridge, stub_slave):
    bridge.handle_packet(packet(50))
    bridge.handle_packet(packet(0))
    bridge.handle_packet(packet(1))
    assert bridge.counters.restarts == 1
    assert stub_slave.step_count == 3
    assert bridge.sim_time_s == pytest.approx(2 / 400)


def test_a_forward_jump_is_not_a_restart(bridge):
    bridge.handle_packet(packet(1))
    result = bridge.handle_packet(packet(9999))
    assert result.restarted is False
    assert bridge.counters.restarts == 0


# ------------------------------------------------------------------ dt rules


def test_a_gap_advances_one_catch_up_step(bridge, stub_slave):
    bridge.handle_packet(packet(10))
    result = bridge.handle_packet(packet(15, frame_rate=400))
    assert result.dt_s == pytest.approx(5 / 400)
    assert stub_slave.step_count == 2  # ONE advance, not five
    assert bridge.counters.frames_skipped == 4


def test_a_capped_frame_still_satisfies_ardupilots_deltat_predicate(bridge):
    """The consumer's rule, not our constant.

    ``SIM_JSON.cpp::recv_fdm`` gates ``time_advance()`` on
    ``is_positive(deltat) && deltat < 0.1`` — EXCLUSIVE. A capped frame whose
    timestamp delta is exactly 0.1 s would be silently dropped by the very
    consumer the cap exists to feed, so the assertion is on the delta ArduPilot
    actually differences out of two consecutive replies.
    """
    first = bridge.handle_packet(packet(1))
    capped = bridge.handle_packet(packet(1001, frame_rate=400))  # 1000/400 = 2.5 s
    assert bridge.counters.steps_capped == 1

    deltat = parse_sensors(capped.reply)["/timestamp"] - parse_sensors(first.reply)["/timestamp"]
    assert deltat > 0.0, "is_positive(deltat) must hold"
    assert deltat < ARDUPILOT_MAX_DELTAT_S, "deltat < 0.1 is exclusive in recv_fdm"
    # Still a real catch-up step, not a token one.
    assert deltat > 0.09


def test_the_cap_is_not_applied_below_the_ceiling(bridge):
    bridge.handle_packet(packet(1))
    result = bridge.handle_packet(packet(40, frame_rate=400))  # 39/400 = 0.0975 s
    assert result.dt_s == pytest.approx(39 / 400)
    assert bridge.counters.steps_capped == 0


def test_a_gap_landing_exactly_on_100_ms_is_capped_below_it(bridge):
    """40 frames at 400 Hz is exactly 0.1 s — the value ArduPilot rejects."""
    assert pytest.approx(ARDUPILOT_MAX_DELTAT_S) == 40 / 400  # the gap this frame asks for
    bridge.handle_packet(packet(1))
    result = bridge.handle_packet(packet(41, frame_rate=400))
    assert result.dt_s < ARDUPILOT_MAX_DELTAT_S
    assert bridge.counters.steps_capped == 1


@pytest.mark.parametrize("rate", [50, 100, 200, 400, 1000])
def test_frame_rate_is_honoured_per_packet(bridge, rate):
    result = bridge.handle_packet(packet(1, frame_rate=rate))
    assert result.dt_s == pytest.approx(1 / rate)


def test_a_mid_flight_rate_change_is_picked_up(bridge):
    assert bridge.handle_packet(packet(1, frame_rate=400)).dt_s == pytest.approx(1 / 400)
    assert bridge.handle_packet(packet(2, frame_rate=50)).dt_s == pytest.approx(1 / 50)
    assert bridge.handle_packet(packet(3, frame_rate=400)).dt_s == pytest.approx(1 / 400)


def test_a_zero_frame_rate_falls_back_to_the_default(bridge):
    result = bridge.handle_packet(packet(1, frame_rate=0))
    assert result.dt_s == pytest.approx(1 / DEFAULT_FRAME_RATE_HZ)


def test_the_fmu_and_the_6dof_see_the_same_dt(bridge, stub_slave):
    bridge.handle_packet(packet(1))
    bridge.handle_packet(packet(6, frame_rate=200))
    start, size = stub_slave.last_step
    assert size == pytest.approx(5 / 200)
    assert bridge.sim_time_s == pytest.approx(start + size)


# ----------------------------------------------------------------- datagrams


def test_a_full_datagram_round_trip(bridge):
    reply = bridge.handle_datagram(encode_servo_packet(packet(1)))
    assert reply is not None
    parse_sensors(reply)
    assert bridge.counters.packets_received == 1


def test_a_32_channel_datagram_is_accepted(quad, stub_model):
    bridge = Bridge(quad, stub_model)
    reply = bridge.handle_datagram(encode_servo_packet(packet(1, channels=32)))
    assert reply is not None
    assert bridge.counters.frames_advanced == 1


def test_a_malformed_datagram_is_dropped_without_a_reply(bridge, stub_slave):
    assert bridge.handle_datagram(b"garbage") is None
    assert bridge.counters.malformed_packets == 1
    assert bridge.counters.packets_received == 0
    assert stub_slave.step_count == 0


def test_a_channel_the_packet_cannot_carry_is_an_error(quad_document, stub_model):
    from thrustlab.sitl.protocol import ProtocolError
    from thrustlab.sitl.vehicle import parse_vehicle_config

    quad_document["rotors"][0]["servo_channel"] = 20
    vehicle = parse_vehicle_config(quad_document)
    bridge = Bridge(vehicle, stub_model)
    with pytest.raises(ProtocolError, match="SERVO_32_ENABLE"):
        bridge.handle_packet(packet(1, channels=16))
    # With SERVO_32_ENABLE the same frame is fine.
    assert bridge.handle_packet(packet(1, channels=32)).advanced


def test_rotor_count_mismatch_is_refused(quad, stub_model):
    stub_model.n_rotors = 6
    with pytest.raises(ValueError, match="6 rotors"):
        Bridge(quad, stub_model)
