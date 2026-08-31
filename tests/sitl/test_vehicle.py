"""Vehicle YAML validation and the PWM -> throttle map."""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest

from thrustlab.sitl.vehicle import (
    RotorConfig,
    VehicleConfigError,
    load_vehicle_config,
    parse_vehicle_config,
)

from .conftest import QUAD_YAML


def rotor(**overrides: Any) -> RotorConfig:
    base: dict[str, Any] = {
        "rotor_index": 0,
        "servo_channel": 1,
        "pwm_min": 1000.0,
        "pwm_max": 2000.0,
        "reversed": False,
        "spin_arm_threshold": 0.0,
        "position_m": np.zeros(3),
        "axis": np.array([0.0, 0.0, -1.0]),
        "sense": 1,
    }
    base.update(overrides)
    return RotorConfig(**base)


# ----------------------------------------------------------- PWM -> throttle


@pytest.mark.parametrize(
    ("pwm", "expected"),
    [(1000, 0.0), (1500, 0.5), (2000, 1.0), (1250, 0.25), (900, 0.0), (2500, 1.0)],
)
def test_throttle_normalises_and_clamps(pwm: float, expected: float):
    assert rotor().throttle_from_pwm(pwm) == pytest.approx(expected)


def test_throttle_honours_a_non_default_calibration():
    channel = rotor(pwm_min=1100.0, pwm_max=1900.0)
    assert channel.throttle_from_pwm(1100) == pytest.approx(0.0)
    assert channel.throttle_from_pwm(1500) == pytest.approx(0.5)
    assert channel.throttle_from_pwm(1900) == pytest.approx(1.0)


def test_reversed_flips_the_throttle():
    channel = rotor(reversed=True)
    assert channel.throttle_from_pwm(1000) == pytest.approx(1.0)
    assert channel.throttle_from_pwm(2000) == pytest.approx(0.0)
    assert channel.throttle_from_pwm(1250) == pytest.approx(0.75)


def test_spin_arm_threshold_snaps_to_zero():
    channel = rotor(spin_arm_threshold=0.1)
    assert channel.throttle_from_pwm(1050) == 0.0  # 0.05 < 0.1
    assert channel.throttle_from_pwm(1100) == pytest.approx(0.1)  # at the threshold
    assert channel.throttle_from_pwm(1200) == pytest.approx(0.2)


def test_spin_arm_threshold_applies_after_the_reversal():
    channel = rotor(reversed=True, spin_arm_threshold=0.1)
    # 1950 us normalises to 0.95, reverses to 0.05, which is below the threshold.
    assert channel.throttle_from_pwm(1950) == 0.0
    assert channel.throttle_from_pwm(1050) == pytest.approx(0.95)


def test_throttles_are_indexed_by_rotor_index_not_list_order(quad_document):
    # Wire servo 1 to rotor 3 and servo 4 to rotor 0, leaving the rest alone.
    quad_document["rotors"][0]["rotor_index"] = 3
    quad_document["rotors"][3]["rotor_index"] = 0
    vehicle = parse_vehicle_config(quad_document)

    pwm = {1: 2000, 2: 1000, 3: 1000, 4: 1500}
    throttles = vehicle.throttles(lambda channel: pwm[channel])
    assert throttles[3] == pytest.approx(1.0)  # servo 1 -> rotor 3
    assert throttles[0] == pytest.approx(0.5)  # servo 4 -> rotor 0
    assert throttles[1] == pytest.approx(0.0)
    assert throttles[2] == pytest.approx(0.0)


# ------------------------------------------------------------------ example


def test_example_quad_loads():
    vehicle = load_vehicle_config(QUAD_YAML)
    assert vehicle.rotor_count == 4
    assert [r.rotor_index for r in vehicle.rotors] == [0, 1, 2, 3]
    assert [r.servo_channel for r in vehicle.rotors] == [1, 2, 3, 4]
    # ArduPilot quad X: motors 1 and 2 are CCW, motors 3 and 4 are CW.
    assert list(vehicle.senses) == [1.0, 1.0, -1.0, -1.0]
    # All rotors thrust up, i.e. -z in body FRD.
    assert np.allclose(vehicle.axes, np.array([[0.0, 0.0, -1.0]] * 4))
    # Motor 1 front-right, 2 rear-left, 3 front-left, 4 rear-right.
    signs = np.sign(vehicle.positions_m[:, :2])
    assert signs.tolist() == [[1, 1], [-1, -1], [1, -1], [-1, 1]]


def test_config_defaults_are_decision_5_rev_2_1(quad):
    assert quad.v_axial_sign == "climb_positive"
    assert quad.inplane_sign == "drag_positive"
    assert quad.torque_convention == "signed"
    assert quad.negate_reaction_torque is False


def test_the_fmu_block_is_optional_and_defaults_to_rev_2_1(quad_document):
    del quad_document["fmu"]
    vehicle = parse_vehicle_config(quad_document)
    assert vehicle.v_axial_sign == "climb_positive"
    assert vehicle.inplane_sign == "drag_positive"
    assert vehicle.torque_convention == "signed"


def test_the_withdrawn_rev_2_readings_remain_selectable(quad_document):
    quad_document["fmu"]["v_axial_sign"] = "dot_product"
    quad_document["fmu"]["inplane_sign"] = "subtracted"
    vehicle = parse_vehicle_config(quad_document)
    assert vehicle.v_axial_sign == "dot_product"
    assert vehicle.inplane_sign == "subtracted"


def test_rotors_are_sorted_by_rotor_index(quad_document):
    quad_document["rotors"].reverse()
    vehicle = parse_vehicle_config(quad_document)
    assert [r.rotor_index for r in vehicle.rotors] == [0, 1, 2, 3]


# --------------------------------------------------------------- rejections


def test_duplicate_servo_channel_is_rejected(quad_document):
    quad_document["rotors"][1]["servo_channel"] = 1
    with pytest.raises(VehicleConfigError, match="bijective"):
        parse_vehicle_config(quad_document)


def test_rotor_index_gap_is_rejected(quad_document):
    quad_document["rotors"][2]["rotor_index"] = 7
    with pytest.raises(VehicleConfigError, match="rotor_index"):
        parse_vehicle_config(quad_document)


def test_duplicate_rotor_index_is_rejected(quad_document):
    quad_document["rotors"][2]["rotor_index"] = 1
    with pytest.raises(VehicleConfigError, match="rotor_index"):
        parse_vehicle_config(quad_document)


def test_non_unit_axis_is_rejected(quad_document):
    quad_document["rotors"][0]["axis"] = [0.0, 0.0, -2.0]
    with pytest.raises(VehicleConfigError, match="UNIT vector"):
        parse_vehicle_config(quad_document)


def test_a_canted_unit_axis_is_accepted(quad_document):
    quad_document["rotors"][0]["axis"] = [0.0, np.sin(0.2), -np.cos(0.2)]
    vehicle = parse_vehicle_config(quad_document)
    assert np.linalg.norm(vehicle.axes[0]) == pytest.approx(1.0)


@pytest.mark.parametrize("sense", [0, 2, -2, "cw", True])
def test_bad_sense_is_rejected(quad_document, sense):
    quad_document["rotors"][0]["sense"] = sense
    with pytest.raises(VehicleConfigError, match="sense"):
        parse_vehicle_config(quad_document)


def test_inverted_pwm_range_is_rejected(quad_document):
    quad_document["rotors"][0]["pwm_max"] = 900
    with pytest.raises(VehicleConfigError, match="pwm_max"):
        parse_vehicle_config(quad_document)


def test_out_of_range_servo_channel_is_rejected(quad_document):
    quad_document["rotors"][0]["servo_channel"] = 33
    with pytest.raises(VehicleConfigError, match="1-32"):
        parse_vehicle_config(quad_document)


def test_missing_mass_is_rejected(quad_document):
    del quad_document["vehicle"]["mass_kg"]
    with pytest.raises(VehicleConfigError, match="mass_kg"):
        parse_vehicle_config(quad_document)


def test_zero_mass_is_rejected(quad_document):
    quad_document["vehicle"]["mass_kg"] = 0.0
    with pytest.raises(VehicleConfigError, match="> 0"):
        parse_vehicle_config(quad_document)


def test_missing_inertia_is_rejected(quad_document):
    del quad_document["vehicle"]["inertia_principal"]
    with pytest.raises(VehicleConfigError, match="inertia"):
        parse_vehicle_config(quad_document)


def test_full_inertia_tensor_is_accepted(quad_document):
    del quad_document["vehicle"]["inertia_principal"]
    quad_document["vehicle"]["inertia"] = [
        [0.0033, 0.0001, 0.0],
        [0.0001, 0.0033, 0.0],
        [0.0, 0.0, 0.0060],
    ]
    vehicle = parse_vehicle_config(quad_document)
    assert vehicle.inertia_kg_m2[0, 1] == pytest.approx(0.0001)
    assert np.allclose(vehicle.inverse_inertia @ vehicle.inertia_kg_m2, np.eye(3))


def test_asymmetric_inertia_is_rejected(quad_document):
    del quad_document["vehicle"]["inertia_principal"]
    quad_document["vehicle"]["inertia"] = [
        [0.0033, 0.0010, 0.0],
        [0.0000, 0.0033, 0.0],
        [0.0, 0.0, 0.0060],
    ]
    with pytest.raises(VehicleConfigError, match="symmetric"):
        parse_vehicle_config(quad_document)


def test_non_positive_definite_inertia_is_rejected(quad_document):
    del quad_document["vehicle"]["inertia_principal"]
    quad_document["vehicle"]["inertia"] = [
        [0.0033, 0.0, 0.0],
        [0.0, -0.0033, 0.0],
        [0.0, 0.0, 0.0060],
    ]
    with pytest.raises(VehicleConfigError, match="positive definite"):
        parse_vehicle_config(quad_document)


def test_both_inertia_forms_is_rejected(quad_document):
    quad_document["vehicle"]["inertia"] = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    with pytest.raises(VehicleConfigError, match="not both"):
        parse_vehicle_config(quad_document)


def test_empty_rotor_list_is_rejected(quad_document):
    quad_document["rotors"] = []
    with pytest.raises(VehicleConfigError, match="at least one rotor"):
        parse_vehicle_config(quad_document)


def test_unknown_sign_convention_is_rejected(quad_document):
    quad_document["fmu"]["v_axial_sign"] = "whatever"
    with pytest.raises(VehicleConfigError, match="v_axial_sign"):
        parse_vehicle_config(quad_document)


def test_scalar_drag_area_broadcasts(quad_document):
    quad_document["vehicle"]["drag_area_m2"] = 0.01
    vehicle = parse_vehicle_config(quad_document)
    assert np.allclose(vehicle.drag_area_m2, 0.01)


def test_error_message_names_the_offending_path(quad_document):
    quad_document["rotors"][2]["position"] = [0.0, 0.0]
    with pytest.raises(VehicleConfigError, match=r"rotors\[2\]\.position"):
        parse_vehicle_config(quad_document)


def test_file_errors_carry_the_filename(tmp_path):
    path = tmp_path / "broken.yaml"
    path.write_text("vehicle: {}\n", encoding="utf-8")
    with pytest.raises(VehicleConfigError, match=r"broken\.yaml"):
        load_vehicle_config(path)
