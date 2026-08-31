"""Spec decision 5, against cases worked out by hand.

Frames throughout: body FRD (x forward, y right, z DOWN), so a copter rotor
thrusts along ``[0, 0, -1]``.
"""

from __future__ import annotations

import numpy as np
import pytest

from thrustlab.sitl.kinematics import assemble_wrench, disc_inflow

UP = np.array([0.0, 0.0, -1.0])
ARM = 0.0778  # example quad half-diagonal component


def quad_geometry() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    positions = np.array(
        [
            [ARM, ARM, 0.0],  # motor 1 front-right, CCW
            [-ARM, -ARM, 0.0],  # motor 2 rear-left,  CCW
            [ARM, -ARM, 0.0],  # motor 3 front-left,  CW
            [-ARM, ARM, 0.0],  # motor 4 rear-right,  CW
        ]
    )
    axes = np.tile(UP, (4, 1))
    senses = np.array([1.0, 1.0, -1.0, -1.0])
    return positions, axes, senses


# ------------------------------------------------------------------ inflow


def test_hover_has_no_inflow_and_no_edge_direction():
    positions, axes, _ = quad_geometry()
    inflow = disc_inflow(positions, axes, np.zeros(3), np.zeros(3))
    assert np.allclose(inflow.v_axial_m_s, 0.0)
    assert np.allclose(inflow.v_edge_m_s, 0.0)
    # H must vanish as v_edge -> 0 with no singularity (decision 5).
    assert np.allclose(inflow.edge_unit, 0.0)


def test_a_climb_gives_a_positive_axial_inflow():
    """Decision 5 rev 2.1: ``v_axial = -(U . n)``, positive in a climb.

    Climbing at 2 m/s: ``v_air_body = (0, 0, -2)`` FRD, so
    ``U = -(0,0,-2) = (0,0,+2)`` and ``U . n = (0,0,2).(0,0,-1) = -2``; negating
    that gives +2.  The withdrawn rev-2 reading is the raw dot product, which
    would hand the aero tables a descent.
    """
    positions, axes, _ = quad_geometry()
    climbing = np.array([0.0, 0.0, -2.0])

    inflow = disc_inflow(positions, axes, climbing, np.zeros(3))
    assert np.allclose(inflow.v_axial_m_s, 2.0)
    assert np.allclose(inflow.v_edge_m_s, 0.0)

    withdrawn = disc_inflow(positions, axes, climbing, np.zeros(3), v_axial_sign="dot_product")
    assert np.allclose(withdrawn.v_axial_m_s, -2.0)


def test_a_descent_gives_a_negative_axial_inflow():
    positions, axes, _ = quad_geometry()
    inflow = disc_inflow(positions, axes, np.array([0.0, 0.0, 1.5]), np.zeros(3))
    assert np.allclose(inflow.v_axial_m_s, -1.5)


def test_forward_flight_is_pure_edgewise():
    positions, axes, _ = quad_geometry()
    inflow = disc_inflow(positions, axes, np.array([10.0, 0.0, 0.0]), np.zeros(3))
    assert np.allclose(inflow.v_axial_m_s, 0.0)
    assert np.allclose(inflow.v_edge_m_s, 10.0)
    # The air moves aft relative to the rotor, so e_hat points aft.
    assert np.allclose(inflow.edge_unit, np.tile([-1.0, 0.0, 0.0], (4, 1)))


def test_pure_yaw_rate_gives_each_rotor_a_tangential_inflow():
    """omega = (0,0,2) rad/s, rotor at (0.1, 0, 0):

    ``omega x r = (0,0,2) x (0.1,0,0) = (0, 0.2, 0)``, so the hub moves right at
    0.2 m/s and the air comes at it from the right: ``U = (0, -0.2, 0)``.  The
    rotor axis is vertical, so all of it is edgewise.
    """
    positions = np.array([[0.1, 0.0, 0.0]])
    axes = np.array([UP])
    inflow = disc_inflow(positions, axes, np.zeros(3), np.array([0.0, 0.0, 2.0]))
    assert inflow.v_axial_m_s[0] == pytest.approx(0.0)
    assert inflow.v_edge_m_s[0] == pytest.approx(0.2)
    assert np.allclose(inflow.edge_unit[0], [0.0, -1.0, 0.0])


def test_yaw_rate_inflow_is_antisymmetric_across_the_hub():
    positions = np.array([[0.1, 0.0, 0.0], [-0.1, 0.0, 0.0]])
    axes = np.array([UP, UP])
    inflow = disc_inflow(positions, axes, np.zeros(3), np.array([0.0, 0.0, 2.0]))
    assert np.allclose(inflow.v_edge_m_s, 0.2)
    assert np.allclose(inflow.edge_unit[0], -inflow.edge_unit[1])


def test_canted_rotor_splits_a_climb_between_axial_and_edgewise():
    """20 deg of forward cant, climbing at 2 m/s.

    ``n = (sin20, 0, -cos20)``, ``U = (0, 0, 2)`` so ``U.n = -2 cos20`` and
    ``v_axial = +2 cos20`` (rev 2.1), while the edge speed is ``2 sin20``.
    """
    cant = np.radians(20.0)
    axis = np.array([np.sin(cant), 0.0, -np.cos(cant)])
    inflow = disc_inflow(
        np.array([[0.1, 0.0, 0.0]]),
        np.array([axis]),
        np.array([0.0, 0.0, -2.0]),
        np.zeros(3),
    )
    assert inflow.v_axial_m_s[0] == pytest.approx(2.0 * np.cos(cant))
    assert inflow.v_edge_m_s[0] == pytest.approx(2.0 * np.sin(cant))
    # e_hat is perpendicular to the axis and unit length.
    assert np.dot(inflow.edge_unit[0], axis) == pytest.approx(0.0, abs=1e-12)
    assert np.linalg.norm(inflow.edge_unit[0]) == pytest.approx(1.0)


def test_wind_enters_through_the_air_relative_velocity():
    """The caller passes AIR-relative body velocity, so a tailwind cancels it."""
    positions, axes, _ = quad_geometry()
    still = disc_inflow(positions, axes, np.zeros(3), np.zeros(3))
    assert np.allclose(still.v_edge_m_s, 0.0)
    headwind = disc_inflow(positions, axes, np.array([5.0, 0.0, 0.0]), np.zeros(3))
    assert np.allclose(headwind.v_edge_m_s, 5.0)


# ------------------------------------------------------------------ wrench


def test_symmetric_quad_hover_produces_pure_lift():
    positions, axes, senses = quad_geometry()
    thrust = np.full(4, 2.0)
    # torque_Nm = -s_i Q_aero, equal aero torque on all four rotors.
    torque = np.array([-1.0, -1.0, 1.0, 1.0]) * 0.09
    force, moment = assemble_wrench(
        positions, axes, senses, thrust, torque, np.zeros(4), np.zeros((4, 3))
    )
    assert np.allclose(force, [0.0, 0.0, -8.0])
    assert np.allclose(moment, 0.0, atol=1e-15)


def test_front_rotor_thrust_pitches_the_nose_up():
    positions = np.array([[0.1, 0.0, 0.0]])
    force, moment = assemble_wrench(
        np.array(positions),
        np.array([UP]),
        np.array([1.0]),
        np.array([1.0]),
        np.array([0.0]),
        np.array([0.0]),
        np.zeros((1, 3)),
    )
    assert np.allclose(force, [0.0, 0.0, -1.0])
    # r x F = (0.1,0,0) x (0,0,-1) = (0, +0.1, 0); +y in FRD is nose up.
    assert np.allclose(moment, [0.0, 0.1, 0.0])


def test_right_rotor_thrust_rolls_left():
    force, moment = assemble_wrench(
        np.array([[0.0, 0.1, 0.0]]),
        np.array([UP]),
        np.array([1.0]),
        np.array([1.0]),
        np.array([0.0]),
        np.array([0.0]),
        np.zeros((1, 3)),
    )
    assert np.allclose(force, [0.0, 0.0, -1.0])
    # (0,0.1,0) x (0,0,-1) = (-0.1, 0, 0); negative roll is left wing down.
    assert np.allclose(moment, [-0.1, 0.0, 0.0])


def test_harder_ccw_rotors_yaw_the_nose_right():
    """The ArduPilot cross-check on the reaction sign.

    ``AP_MOTORS_MATRIX_YAW_FACTOR_CCW = +1`` means commanding the CCW rotors
    harder must yaw a copter NOSE-RIGHT, i.e. positive body z in FRD.  Under
    decision 5 rev 2.1 the FMU emits ``torque_Nm[i] = -s_i Q_i^aero``, so the
    two CCW rotors (``s_i = +1``) carry NEGATIVE torque_Nm and the sum lands on
    +z as it must.
    """
    positions, axes, senses = quad_geometry()
    # Q_aero = 0.18 on the CCW pair, 0.09 on the CW pair -> torque_Nm = -s*Q.
    torque = np.array([-0.18, -0.18, 0.09, 0.09])
    _, moment = assemble_wrench(
        positions, axes, senses, np.zeros(4), torque, np.zeros(4), np.zeros((4, 3))
    )
    assert moment[2] == pytest.approx(0.18)  # nose right


def test_negate_reaction_torque_flips_the_axial_moment():
    positions, axes, senses = quad_geometry()
    torque = np.array([-0.18, -0.18, 0.09, 0.09])
    _, moment = assemble_wrench(
        positions,
        axes,
        senses,
        np.zeros(4),
        torque,
        np.zeros(4),
        np.zeros((4, 3)),
        negate_reaction_torque=True,
    )
    assert moment[2] == pytest.approx(-0.18)


def test_magnitude_convention_forms_the_reaction_from_the_yaml_sense():
    """``magnitude``: the FMU gives |Q_aero|, the bridge forms ``-s_i |Q|``."""
    positions, axes, senses = quad_geometry()
    magnitudes = np.full(4, 0.09)
    _, moment = assemble_wrench(
        positions,
        axes,
        senses,
        np.zeros(4),
        magnitudes,
        np.zeros(4),
        np.zeros((4, 3)),
        torque_convention="magnitude",
    )
    # senses sum to zero, so a uniform magnitude yields no net yaw.
    assert np.allclose(moment, 0.0, atol=1e-15)

    lopsided = np.array([0.18, 0.09, 0.09, 0.09])
    _, moment = assemble_wrench(
        positions,
        axes,
        senses,
        np.zeros(4),
        lopsided,
        np.zeros(4),
        np.zeros((4, 3)),
        torque_convention="magnitude",
    )
    # A CCW rotor pulling more aero torque yaws the nose right, same as above.
    assert moment[2] == pytest.approx(0.09)


def test_the_inplane_force_is_a_drag_in_forward_flight():
    """Forward flight at 10 m/s: e_hat is aft, so ``+H e`` opposes the motion."""
    inflow = disc_inflow(
        np.array([[0.0, 0.0, 0.0]]),
        np.array([UP]),
        np.array([10.0, 0.0, 0.0]),
        np.zeros(3),
    )
    args = (
        np.array([[0.0, 0.0, 0.0]]),
        np.array([UP]),
        np.array([1.0]),
        np.array([0.0]),
        np.array([0.0]),
        np.array([0.5]),
        inflow.edge_unit,
    )
    force_default, _ = assemble_wrench(*args)
    force_withdrawn, _ = assemble_wrench(*args, inplane_sign="subtracted")
    # Rev 2.1: F = T n + H e with e = (-1,0,0), so H opposes the motion.
    assert np.allclose(force_default, [-0.5, 0.0, 0.0])
    # The withdrawn rev-2 reading would push the vehicle FORWARD instead.
    assert np.allclose(force_withdrawn, [0.5, 0.0, 0.0])


def test_canted_rotor_wrench_has_a_horizontal_component():
    cant = np.radians(20.0)
    axis = np.array([np.sin(cant), 0.0, -np.cos(cant)])
    force, moment = assemble_wrench(
        np.array([[0.0, 0.0, 0.0]]),
        np.array([axis]),
        np.array([1.0]),
        np.array([10.0]),
        np.array([0.09]),
        np.array([0.0]),
        np.zeros((1, 3)),
    )
    assert force[0] == pytest.approx(10.0 * np.sin(cant))
    assert force[2] == pytest.approx(-10.0 * np.cos(cant))
    # A rotor at the origin contributes only its axial reaction, along the axis.
    assert np.allclose(moment, 0.09 * axis)
