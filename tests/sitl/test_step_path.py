"""The whole frame path over a stub FMI 3 slave.

This exercises the REAL :class:`~thrustlab.sitl.fmu.FmuRotorModel` — its
by-name variable resolution, its Initialization Mode sequence, and its
set-then-step-then-get discipline — plus the wrench mapping, the battery
feedback and the rotor CSV.  What it cannot prove is anything about a real
export's physics; that is unit U5's integration run.
"""

from __future__ import annotations

import numpy as np
import pytest

from thrustlab.sitl.bridge import Bridge
from thrustlab.sitl.fmu import (
    OPTIONAL_VARIABLES,
    REQUIRED_VARIABLES,
    FmuError,
    FmuRotorModel,
    build_variable_map,
)
from thrustlab.sitl.model import RotorModel
from thrustlab.sitl.protocol import MAGIC_16, ServoPacket
from thrustlab.sitl.rpmlog import RotorLog

from . import mock_fmu
from .ardupilot_parser import parse_sensors
from .mock_fmu import StubVariable, build_model_description


def packet(frame_count: int, pwm: int, *, frame_rate: int = 400) -> ServoPacket:
    return ServoPacket(
        magic=MAGIC_16, frame_rate=frame_rate, frame_count=frame_count, pwm=(pwm,) * 16
    )


# -------------------------------------------------------- variable resolution


def test_variable_map_is_built_by_name(quad):
    variables = build_variable_map(build_model_description(quad.rotor_count))
    assert variables["throttle"].value_reference == 1
    assert variables["throttle"].extent == quad.rotor_count
    assert variables["air_density_kg_m3"].extent == 1
    assert variables["rotor_in_envelope"].type_name == "Boolean"


def test_duplicate_variable_names_are_refused(quad):
    description = build_model_description(quad.rotor_count)
    description.modelVariables.append(StubVariable("throttle", 99, "Float64", (4,)))
    with pytest.raises(FmuError, match="more than once"):
        build_variable_map(description)


@pytest.mark.parametrize("name", REQUIRED_VARIABLES)
def test_every_contracted_variable_is_required_and_named_when_absent(quad, stub_slave, name):
    """Decision 9 makes Appendix A normative: no fabricated fallbacks.

    A zero ``force_inplane_N`` would silently delete the H-force from every
    wrench and an all-true ``rotor_in_envelope`` would report a clamped solve as
    trustworthy — both would fly, and both would lie. So each contracted name is
    refused at LOAD, and the message says which one is missing.
    """
    description = build_model_description(quad.rotor_count)
    description.modelVariables = [v for v in description.modelVariables if v.name != name]
    variables = build_variable_map(description)
    with pytest.raises(FmuError) as raised:
        FmuRotorModel(stub_slave, variables, quad.rotor_count)

    # The message also lists the whole contract, so assert against the part
    # naming what is ACTUALLY missing rather than the recital that follows.
    named_missing = str(raised.value).split("Appendix A")[0]
    assert name in named_missing
    for other in REQUIRED_VARIABLES:
        if other != name and other not in name and name not in other:
            assert other not in named_missing


def test_nothing_is_marked_optional_yet():
    """Guards the fallback path from creeping back in without a spec change."""
    assert OPTIONAL_VARIABLES == ()


def test_a_per_rotor_extent_mismatch_is_refused(quad, stub_slave):
    variables = build_variable_map(build_model_description(6))
    with pytest.raises(FmuError, match="different aircraft"):
        FmuRotorModel(stub_slave, variables, quad.rotor_count)


def test_a_scalar_declared_as_an_array_is_refused(quad, stub_slave):
    """Reading element 0 of an unexpected array would hide the mismatch."""
    description = build_model_description(quad.rotor_count)
    for variable in description.modelVariables:
        if variable.name == "voltage_bus_V":
            variable.shape = (3,)
    variables = build_variable_map(description)
    with pytest.raises(FmuError, match="scalar"):
        FmuRotorModel(stub_slave, variables, quad.rotor_count)


def test_the_model_satisfies_the_rotor_model_protocol(stub_model):
    assert isinstance(stub_model, RotorModel)


# ------------------------------------------------------------ batched reads


def test_outputs_are_read_in_one_call_per_data_type(quad, stub_model, stub_slave):
    """The DLL pays one lazy bus solve per fmi3GetFloat64 REQUEST.

    A request costs the same however many variables it names, so the whole
    Float64 output block goes in ONE call and the envelope flags in one
    getBoolean. Reading lane by lane would multiply the per-frame solve cost by
    the number of output lanes.
    """
    bridge = Bridge(quad, stub_model)
    stub_slave.get_float64_calls = 0
    stub_slave.get_boolean_calls = 0
    stub_slave.bus_solves = 0

    frames = 25
    for frame in range(1, frames + 1):
        bridge.handle_packet(packet(frame, 1500))

    assert stub_slave.step_count == frames
    assert stub_slave.get_float64_calls == frames
    assert stub_slave.get_boolean_calls == frames
    assert stub_slave.bus_solves == frames


def test_a_duplicate_frame_costs_no_extra_read(quad, stub_model, stub_slave):
    bridge = Bridge(quad, stub_model)
    bridge.handle_packet(packet(1, 1500))
    reads = stub_slave.get_float64_calls
    for _ in range(5):
        bridge.handle_packet(packet(1, 1500))  # duplicates resend, never re-read
    assert stub_slave.get_float64_calls == reads


def test_the_batched_read_requests_every_float_output_at_once(quad, stub_model, stub_slave):
    seen: list[tuple[list[int], int]] = []
    original = stub_slave.getFloat64

    def spy(vr, nValues=None):
        seen.append((list(vr), nValues))
        return original(vr, nValues)

    stub_slave.getFloat64 = spy
    Bridge(quad, stub_model).handle_packet(packet(1, 1500))

    assert len(seen) == 1, "the whole Float64 output block must be one request"
    value_references, n_values = seen[0]
    # thrust, torque, force_inplane, rpm (4 rotors each) + voltage, current, soc.
    assert value_references == [10, 11, 12, 13, 20, 21, 22]
    assert n_values == 4 * 4 + 3


def test_batched_slices_attribute_to_the_right_rotor(quad, stub_model):
    """A wrong offset in the batched read would silently permute the rotors.

    Distinct PWM per channel, so every lane and every rotor index carries a
    different number and any mis-slice shows up.
    """
    bridge = Bridge(quad, stub_model)
    pwm = [1000] * 16
    pwm[0], pwm[1], pwm[2], pwm[3] = 1200, 1400, 1600, 1800
    result = bridge.handle_packet(ServoPacket(MAGIC_16, 400, 1, tuple(pwm)))

    expected_throttle = np.array([0.2, 0.4, 0.6, 0.8])
    assert result.throttle == pytest.approx(expected_throttle)
    outputs = result.outputs
    assert outputs.thrust_N == pytest.approx(mock_fmu.THRUST_PER_THROTTLE * expected_throttle)
    assert outputs.rpm == pytest.approx(mock_fmu.RPM_PER_THROTTLE * expected_throttle)
    assert outputs.torque_Nm == pytest.approx(
        -quad.senses * mock_fmu.TORQUE_PER_THROTTLE * expected_throttle
    )
    assert outputs.current_bus_A == pytest.approx(
        mock_fmu.CURRENT_PER_THROTTLE * expected_throttle.sum()
    )
    assert outputs.rotor_in_envelope.tolist() == [True] * 4
    assert outputs.all_in_envelope is True


def test_the_inplane_lane_reaches_the_wrench_rather_than_defaulting_to_zero(quad, stub_model):
    """The lane a fabricated zero used to silently delete.

    In forward flight the stub produces a real ``force_inplane_N``, and under
    rev 2.1 it must land as a DRAG on the body x axis.
    """
    from thrustlab.sitl.rigidbody import BodyState

    cruising = BodyState(
        position_ned_m=np.array([0.0, 0.0, -10.0]),
        velocity_ned_m_s=np.array([12.0, 0.0, 0.0]),
        quaternion=np.array([1.0, 0.0, 0.0, 0.0]),
        omega_body_rad_s=np.zeros(3),
    )
    bridge = Bridge(quad, stub_model, initial_state=cruising)
    result = bridge.handle_packet(packet(1, 1500))

    expected = mock_fmu.INPLANE_PER_THROTTLE_EDGE * 0.5 * 12.0
    assert result.outputs.force_inplane_N == pytest.approx([expected] * 4)
    assert expected > 0.0
    # Four rotors of drag, decelerating the vehicle along body +x.
    assert bridge.state.velocity_ned_m_s[0] < 12.0


def test_the_envelope_flags_come_from_the_fmu_not_a_default(quad, stub_model, stub_slave):
    """A fabricated all-true flag would report a clamped solve as trustworthy."""
    bridge = Bridge(quad, stub_model)
    assert bridge.handle_packet(packet(1, 1500)).outputs.all_in_envelope is True

    # Force the stub out of envelope on one rotor and watch it propagate.
    original = stub_slave.doStep

    def clamped(*args, **kwargs):
        result = original(*args, **kwargs)
        stub_slave.values[14] = [False, True, True, True]
        stub_slave.values[23] = [False]
        return result

    stub_slave.doStep = clamped
    outputs = bridge.handle_packet(packet(2, 1500)).outputs
    assert outputs.all_in_envelope is False
    assert outputs.rotor_in_envelope.tolist() == [False, True, True, True]


def test_initialization_pins_disc_mode_before_leaving_init(quad, stub_slave):
    variables = build_variable_map(build_model_description(quad.rotor_count))
    FmuRotorModel(stub_slave, variables, quad.rotor_count)
    assert stub_slave.calls[0] == "enterInitializationMode"
    assert stub_slave.calls[-1] == "exitInitializationMode"
    # use_vehicle_frame is variability=fixed; the stub raises if it is written
    # outside Initialization Mode.
    assert stub_slave.values[30] == [False]


def test_terminate_frees_the_instance(stub_model, stub_slave):
    stub_model.terminate()
    assert stub_slave.terminated and stub_slave.freed


# --------------------------------------------------------------- step path


def test_throttle_reaches_the_fmu_per_rotor(quad, stub_model, stub_slave):
    bridge = Bridge(quad, stub_model)
    # 1500 us on every channel -> 0.5 throttle on every rotor.
    bridge.handle_packet(packet(1, 1500))
    assert stub_slave.values[1] == pytest.approx([0.5] * 4)


def test_the_spin_arm_threshold_zeroes_idling_channels(quad, stub_model, stub_slave):
    bridge = Bridge(quad, stub_model)
    # 1010 us normalises to 0.01, below the example's 0.02 threshold.
    bridge.handle_packet(packet(1, 1010))
    assert stub_slave.values[1] == pytest.approx([0.0] * 4)
    assert stub_slave.values[10] == pytest.approx([0.0] * 4)


def test_hover_thrust_lifts_the_vehicle(quad, stub_model):
    """Stub thrust is 6 N per unit throttle per rotor; 0.68 kg needs 6.67 N."""
    bridge = Bridge(quad, stub_model)
    hover_throttle = quad.mass_kg * 9.80665 / (4 * mock_fmu.THRUST_PER_THROTTLE)
    pwm = round(1000 + 1000 * hover_throttle)
    for frame in range(1, 401):
        bridge.handle_packet(packet(frame, pwm))
    # One second of near-exact hover thrust from a standing start.
    assert abs(bridge.state.position_ned_m[2]) < 0.02
    assert abs(bridge.state.velocity_ned_m_s[2]) < 0.05


def test_full_throttle_climbs_and_idle_stays_on_the_ground(quad, stub_model):
    bridge = Bridge(quad, stub_model)
    for frame in range(1, 401):
        bridge.handle_packet(packet(frame, 2000))
    assert bridge.state.position_ned_m[2] < -1.0  # NED z negative is up


def test_idle_throttle_leaves_the_vehicle_on_the_ground(quad, stub_model):
    bridge = Bridge(quad, stub_model)
    for frame in range(1, 401):
        bridge.handle_packet(packet(frame, 1000))
    assert bridge.state.position_ned_m[2] == pytest.approx(0.0)
    assert np.allclose(bridge.state.velocity_ned_m_s, 0.0)


def test_a_symmetric_quad_does_not_yaw_or_roll(quad, stub_model):
    bridge = Bridge(quad, stub_model)
    for frame in range(1, 401):
        bridge.handle_packet(packet(frame, 2000))
    # Equal thrust on two CCW and two CW rotors: the reaction torques cancel.
    assert np.allclose(bridge.state.omega_body_rad_s, 0.0, atol=1e-12)
    assert np.allclose(bridge.state.position_ned_m[:2], 0.0, atol=1e-9)


def test_commanding_the_ccw_pair_yaws_the_nose_right(quad, stub_model):
    """End-to-end check of the rev-2.1 reaction sign, PWM to gyro.

    Rotors 0 and 1 (servos 1 and 2) are the CCW pair and are DIAGONAL, so equal
    thrust on them contributes no net roll or pitch — a clean yaw command.
    ArduPilot's ``AP_MOTORS_MATRIX_YAW_FACTOR_CCW = +1`` says this must yaw the
    nose RIGHT, i.e. positive body z in FRD.
    """
    from thrustlab.sitl.rigidbody import BodyState

    airborne = BodyState.at_rest(position_ned_m=np.array([0.0, 0.0, -10.0]))
    bridge = Bridge(quad, stub_model, initial_state=airborne)

    def mixed(frame_count: int) -> ServoPacket:
        pwm = [1000] * 16
        pwm[0] = pwm[1] = 1800  # servos 1 and 2 -> rotors 0 and 1, both CCW
        pwm[2] = pwm[3] = 1200  # servos 3 and 4 -> rotors 2 and 3, both CW
        return ServoPacket(MAGIC_16, 400, frame_count, tuple(pwm))

    for frame in range(1, 101):
        bridge.handle_packet(mixed(frame))

    omega = bridge.state.omega_body_rad_s
    assert omega[2] > 0.0, "harder CCW rotors must yaw the nose right"
    assert np.allclose(omega[:2], 0.0, atol=1e-12), "a diagonal pair adds no roll or pitch"


def test_battery_feedback_reaches_the_wire(quad, stub_model):
    bridge = Bridge(quad, stub_model)
    result = bridge.handle_packet(packet(1, 2000))
    parsed = parse_sensors(result.reply)
    expected_current = 4 * mock_fmu.CURRENT_PER_THROTTLE
    assert parsed["battery/current"] == pytest.approx(expected_current, rel=1e-6)
    assert parsed["battery/voltage"] == pytest.approx(
        mock_fmu.OPEN_CIRCUIT_V - mock_fmu.PACK_RESISTANCE_OHM * expected_current, rel=1e-6
    )


def test_battery_sags_under_load_and_recovers(quad, stub_model):
    bridge = Bridge(quad, stub_model)
    idle = parse_sensors(bridge.handle_packet(packet(1, 1000)).reply)
    loaded = parse_sensors(bridge.handle_packet(packet(2, 2000)).reply)
    assert loaded["battery/voltage"] < idle["battery/voltage"]
    assert loaded["battery/current"] > idle["battery/current"]


def test_soc_falls_monotonically_under_load(quad, stub_model):
    bridge = Bridge(quad, stub_model)
    soc = []
    for frame in range(1, 51):
        result = bridge.handle_packet(packet(frame, 2000))
        soc.append(result.outputs.battery_soc)
    assert soc == sorted(soc, reverse=True)
    assert soc[-1] < soc[0]


def test_non_finite_battery_values_are_omitted_from_the_payload(quad, stub_model, stub_slave):
    """A diverged bus solve must not be reported to SITL as a real reading.

    The lanes are contracted, so they are always READ; the remaining question is
    what to put on the wire when the value is not finite. Omitting the field
    makes SIM_JSON.cpp fall back to ``sitl->batt_voltage``, which beats sending a
    fabricated 0 V that the firmware would act on as a dead pack.
    """
    bridge = Bridge(quad, stub_model)
    original = stub_slave.doStep

    def diverged(*args, **kwargs):
        result = original(*args, **kwargs)
        stub_slave.values[20] = [float("nan")]
        stub_slave.values[21] = [float("inf")]
        return result

    stub_slave.doStep = diverged
    parsed = parse_sensors(bridge.handle_packet(packet(1, 1500)).reply)
    assert "battery/voltage" not in parsed
    assert "battery/current" not in parsed
    # The rest of the frame is still well-formed.
    assert parsed["/timestamp"] == pytest.approx(1 / 400)


def test_airspeed_reflects_configured_wind(quad_document, stub_slave):
    from thrustlab.sitl.vehicle import parse_vehicle_config

    quad_document["environment"]["wind_ned_m_s"] = [-8.0, 0.0, 0.0]
    vehicle = parse_vehicle_config(quad_document)
    model = FmuRotorModel(
        stub_slave, build_variable_map(build_model_description(4)), vehicle.rotor_count
    )
    bridge = Bridge(vehicle, model)
    parsed = parse_sensors(bridge.handle_packet(packet(1, 1000)).reply)
    # Stationary over the ground in an 8 m/s headwind.
    assert parsed["/airspeed"] == pytest.approx(8.0, rel=1e-6)


def test_edgewise_inflow_reaches_the_fmu_in_forward_flight(quad, stub_model, stub_slave):
    from thrustlab.sitl.rigidbody import BodyState

    bridge = Bridge(
        quad,
        stub_model,
        initial_state=BodyState(
            position_ned_m=np.array([0.0, 0.0, -10.0]),
            velocity_ned_m_s=np.array([12.0, 0.0, 0.0]),
            quaternion=np.array([1.0, 0.0, 0.0, 0.0]),
            omega_body_rad_s=np.zeros(3),
        ),
    )
    bridge.handle_packet(packet(1, 1500))
    assert stub_slave.values[5] == pytest.approx([12.0] * 4)  # v_edge_m_s
    assert stub_slave.values[2] == pytest.approx([0.0] * 4)  # v_axial_m_s


@pytest.mark.parametrize(
    ("sign", "expected"), [(None, 3.0), ("climb_positive", 3.0), ("dot_product", -3.0)]
)
def test_climb_axial_inflow_uses_the_configured_sign(quad_document, stub_slave, sign, expected):
    """The default hands the FMU a POSITIVE v_axial in a climb (rev 2.1)."""
    from thrustlab.sitl.rigidbody import BodyState
    from thrustlab.sitl.vehicle import parse_vehicle_config

    climbing = BodyState(
        position_ned_m=np.array([0.0, 0.0, -10.0]),
        velocity_ned_m_s=np.array([0.0, 0.0, -3.0]),
        quaternion=np.array([1.0, 0.0, 0.0, 0.0]),
        omega_body_rad_s=np.zeros(3),
    )
    if sign is None:
        del quad_document["fmu"]["v_axial_sign"]
    else:
        quad_document["fmu"]["v_axial_sign"] = sign
    vehicle = parse_vehicle_config(quad_document)
    model = FmuRotorModel(
        stub_slave, build_variable_map(build_model_description(4)), vehicle.rotor_count
    )
    Bridge(vehicle, model, initial_state=climbing).handle_packet(packet(1, 1500))
    assert stub_slave.values[2] == pytest.approx([expected] * 4)


def test_the_wrench_is_held_across_sub_steps(quad, stub_model, stub_slave):
    """One DoStep per frame no matter how many 6DOF sub-steps it takes."""
    bridge = Bridge(quad, stub_model, max_substep_s=1e-4)
    bridge.handle_packet(packet(1, 1500))
    bridge.handle_packet(packet(41, frame_rate=400, pwm=1500))  # 0.1 s catch-up
    assert stub_slave.step_count == 2


# ------------------------------------------------------------------- logging


def test_the_rotor_log_records_one_row_per_advance(quad, stub_model, tmp_path):
    path = tmp_path / "rotors.csv"
    with RotorLog(path, quad.rotor_count) as log:
        bridge = Bridge(quad, stub_model, rotor_log=log)
        for frame in range(1, 6):
            bridge.handle_packet(packet(frame, 1800))
        bridge.handle_packet(packet(5, 1800))  # duplicate: must not add a row
        assert log.rows_written == 5

    lines = path.read_text(encoding="utf-8").strip().splitlines()
    header = lines[0].split(",")
    assert len(lines) == 6
    assert "rpm_0" in header and "rpm_3" in header
    assert "thrust_N_2" in header and "v_edge_m_s_1" in header

    row = dict(zip(header, lines[-1].split(","), strict=True))
    expected_rpm = 0.8 * mock_fmu.RPM_PER_THROTTLE
    assert float(row["rpm_0"]) == pytest.approx(expected_rpm, rel=1e-4)
    assert float(row["throttle_3"]) == pytest.approx(0.8, rel=1e-6)
    assert int(row["all_in_envelope"]) == 1


def test_the_log_survives_a_restart(quad, stub_model, tmp_path):
    path = tmp_path / "rotors.csv"
    with RotorLog(path, quad.rotor_count) as log:
        bridge = Bridge(quad, stub_model, rotor_log=log)
        bridge.handle_packet(packet(9, 1500))
        bridge.handle_packet(packet(0, 1500))  # regression -> restart
        assert log.rows_written == 2
    assert len(path.read_text(encoding="utf-8").strip().splitlines()) == 3


def test_stub_slave_refuses_a_step_before_reinitialisation(quad, stub_slave):
    """The stub enforces decision 8, so a reset without re-init would fail."""
    model = FmuRotorModel(stub_slave, build_variable_map(build_model_description(4)), 4)
    stub_slave.reset()  # bypass FmuRotorModel.reset, which re-initialises
    with pytest.raises(Exception, match="doStep in mode instantiated"):
        model.do_step(0.0, 0.0025)
    model.reset()  # the real path: reset AND re-initialise
    model.do_step(0.0, 0.0025)
