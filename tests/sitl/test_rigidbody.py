"""6DOF: NED/FRD frames, the accelerometer convention, drag, ground."""

from __future__ import annotations

import numpy as np
import pytest

from thrustlab.sitl.rigidbody import (
    GRAVITY_MSS,
    BodyState,
    RigidBody,
    quaternion_from_euler,
    quaternion_to_matrix,
    quaternion_yaw,
)

MASS = 0.68
INERTIA = np.diag([0.0033, 0.0033, 0.0060])


def make_body(**overrides) -> RigidBody:
    kwargs = {
        "mass_kg": MASS,
        "inertia_kg_m2": INERTIA,
        "inverse_inertia": np.linalg.inv(INERTIA),
        "drag_area_m2": np.zeros(3),
        "air_density_kg_m3": 1.225,
        "wind_ned_m_s": np.zeros(3),
        "ground_enabled": False,
        "ground_z_ned_m": 0.0,
    }
    kwargs.update(overrides)
    return RigidBody(**kwargs)


# -------------------------------------------------------------- quaternions


def test_identity_quaternion_is_the_identity_rotation():
    assert np.allclose(quaternion_to_matrix([1.0, 0.0, 0.0, 0.0]), np.eye(3))


def test_yaw_rotates_body_forward_towards_east():
    q = quaternion_from_euler(0.0, 0.0, np.pi / 2)
    forward_ned = quaternion_to_matrix(q) @ np.array([1.0, 0.0, 0.0])
    assert np.allclose(forward_ned, [0.0, 1.0, 0.0], atol=1e-12)
    assert quaternion_yaw(q) == pytest.approx(np.pi / 2)


def test_pitch_up_points_body_forward_upwards():
    # Positive pitch is nose up, and up is NEGATIVE z in NED.
    q = quaternion_from_euler(0.0, np.radians(30.0), 0.0)
    forward_ned = quaternion_to_matrix(q) @ np.array([1.0, 0.0, 0.0])
    assert forward_ned[2] == pytest.approx(-np.sin(np.radians(30.0)))


# ----------------------------------------------------------- accelerometer


def test_stationary_level_accelerometer_reads_one_g_up():
    """``SIM_Aircraft``: accel_body is SPECIFIC FORCE, so at rest it is -g in z."""
    body = make_body()
    state = BodyState.at_rest()
    # No rotor force: the vehicle is in free fall, and an accelerometer in free
    # fall reads zero.
    assert np.allclose(body.specific_force_body(state, np.zeros(3)), 0.0)
    # Held up by exactly its own weight (thrust along body -z):
    hover_force = np.array([0.0, 0.0, -MASS * GRAVITY_MSS])
    assert np.allclose(
        body.specific_force_body(state, hover_force), [0.0, 0.0, -GRAVITY_MSS], atol=1e-12
    )


def test_hover_thrust_produces_no_kinematic_acceleration():
    body = make_body()
    state = BodyState.at_rest()
    accel_ned, _ = body.acceleration_ned(state, np.array([0.0, 0.0, -MASS * GRAVITY_MSS]))
    assert np.allclose(accel_ned, 0.0, atol=1e-12)


def test_free_fall_accelerates_downwards_at_g():
    body = make_body()
    accel_ned, _ = body.acceleration_ned(BodyState.at_rest(), np.zeros(3))
    assert np.allclose(accel_ned, [0.0, 0.0, GRAVITY_MSS])


def test_accelerometer_rotates_with_the_body():
    body = make_body()
    state = BodyState(
        position_ned_m=np.zeros(3),
        velocity_ned_m_s=np.zeros(3),
        quaternion=quaternion_from_euler(0.0, np.radians(90.0), 0.0),
        omega_body_rad_s=np.zeros(3),
    )
    # Pitched 90 deg nose-up and in free fall: gravity now shows on body x.
    reading = body.specific_force_body(state, np.zeros(3))
    assert np.allclose(reading, 0.0, atol=1e-12)
    # Held stationary by a thrust that exactly opposes gravity in the EARTH
    # frame — which, pitched up, means a body +x force.
    hold = quaternion_to_matrix(state.quaternion).T @ np.array([0.0, 0.0, -MASS * GRAVITY_MSS])
    assert np.allclose(body.specific_force_body(state, hold), [GRAVITY_MSS, 0.0, 0.0], atol=1e-9)


# --------------------------------------------------------------- integration


def test_free_fall_matches_the_closed_form():
    body = make_body()
    state = BodyState.at_rest()
    dt = 1.0
    state = body.advance(state, np.zeros(3), np.zeros(3), dt)
    assert state.velocity_ned_m_s[2] == pytest.approx(GRAVITY_MSS * dt, rel=1e-9)
    assert state.position_ned_m[2] == pytest.approx(0.5 * GRAVITY_MSS * dt**2, rel=1e-9)


def test_hover_holds_position():
    body = make_body()
    state = BodyState.at_rest()
    for _ in range(400):
        state = body.advance(
            state, np.array([0.0, 0.0, -MASS * GRAVITY_MSS]), np.zeros(3), 1 / 400
        )
    assert np.allclose(state.position_ned_m, 0.0, atol=1e-9)
    assert np.allclose(state.velocity_ned_m_s, 0.0, atol=1e-9)


def test_yaw_moment_spins_up_the_yaw_rate():
    body = make_body()
    state = BodyState.at_rest()
    moment = np.array([0.0, 0.0, 0.01])
    state = body.advance(state, np.zeros(3), moment, 0.1)
    # I_zz * omega_dot = M for a body starting at rest about a principal axis.
    assert state.omega_body_rad_s[2] == pytest.approx(0.01 / 0.0060 * 0.1, rel=1e-6)
    assert np.allclose(state.omega_body_rad_s[:2], 0.0, atol=1e-12)
    assert quaternion_yaw(state.quaternion) > 0.0


def test_quaternion_stays_normalised_under_a_long_tumble():
    body = make_body()
    state = BodyState(
        position_ned_m=np.zeros(3),
        velocity_ned_m_s=np.zeros(3),
        quaternion=quaternion_from_euler(0.1, -0.2, 0.3),
        omega_body_rad_s=np.array([3.0, -2.0, 1.5]),
    )
    for _ in range(2000):
        state = body.advance(state, np.zeros(3), np.zeros(3), 1 / 400)
    assert np.linalg.norm(state.quaternion) == pytest.approx(1.0, abs=1e-12)


def test_gyroscopic_coupling_appears_for_an_asymmetric_body():
    inertia = np.diag([0.002, 0.004, 0.007])
    body = make_body(inertia_kg_m2=inertia, inverse_inertia=np.linalg.inv(inertia))
    state = BodyState(
        position_ned_m=np.zeros(3),
        velocity_ned_m_s=np.zeros(3),
        quaternion=np.array([1.0, 0.0, 0.0, 0.0]),
        omega_body_rad_s=np.array([5.0, 3.0, 0.0]),
    )
    state = body.advance(state, np.zeros(3), np.zeros(3), 0.01)
    # -omega x (I omega) is non-zero about z when Ixx != Iyy.
    assert abs(state.omega_body_rad_s[2]) > 1e-6


# ---------------------------------------------------------------- drag/wind


def test_drag_opposes_the_air_relative_velocity():
    body = make_body(drag_area_m2=np.array([0.01, 0.01, 0.02]))
    state = BodyState(
        position_ned_m=np.zeros(3),
        velocity_ned_m_s=np.array([10.0, 0.0, 0.0]),
        quaternion=np.array([1.0, 0.0, 0.0, 0.0]),
        omega_body_rad_s=np.zeros(3),
    )
    drag = body.drag_force_body(state)
    assert drag[0] == pytest.approx(-0.5 * 1.225 * 0.01 * 10.0 * 10.0)
    assert np.allclose(drag[1:], 0.0)


def test_a_matching_tailwind_cancels_the_airspeed():
    body = make_body(
        drag_area_m2=np.array([0.01, 0.01, 0.02]),
        wind_ned_m_s=np.array([10.0, 0.0, 0.0]),
    )
    state = BodyState(
        position_ned_m=np.zeros(3),
        velocity_ned_m_s=np.array([10.0, 0.0, 0.0]),
        quaternion=np.array([1.0, 0.0, 0.0, 0.0]),
        omega_body_rad_s=np.zeros(3),
    )
    assert body.airspeed(state) == pytest.approx(0.0)
    assert np.allclose(body.drag_force_body(state), 0.0)


def test_airspeed_is_air_relative_not_ground_relative():
    body = make_body(wind_ned_m_s=np.array([-5.0, 0.0, 0.0]))
    state = BodyState(
        position_ned_m=np.zeros(3),
        velocity_ned_m_s=np.array([5.0, 0.0, 0.0]),
        quaternion=np.array([1.0, 0.0, 0.0, 0.0]),
        omega_body_rad_s=np.zeros(3),
    )
    assert body.airspeed(state) == pytest.approx(10.0)


# ------------------------------------------------------------------- ground


def test_the_ground_catches_a_falling_vehicle():
    body = make_body(ground_enabled=True, ground_z_ned_m=0.0)
    state = BodyState.at_rest(position_ned_m=np.array([0.0, 0.0, -1.0]))
    for _ in range(400):
        state = body.advance(state, np.zeros(3), np.zeros(3), 1 / 100)
    assert state.position_ned_m[2] == pytest.approx(0.0)
    assert state.velocity_ned_m_s[2] == pytest.approx(0.0)


def test_a_vehicle_on_the_ground_levels_and_stops_rotating():
    body = make_body(ground_enabled=True)
    state = BodyState(
        position_ned_m=np.array([0.0, 0.0, 0.5]),
        velocity_ned_m_s=np.array([1.0, 2.0, 3.0]),
        quaternion=quaternion_from_euler(0.3, -0.2, 1.1),
        omega_body_rad_s=np.array([1.0, 1.0, 1.0]),
    )
    landed = body.apply_ground(state)
    assert landed.position_ned_m[2] == pytest.approx(0.0)
    assert np.allclose(landed.velocity_ned_m_s, 0.0)
    assert np.allclose(landed.omega_body_rad_s, 0.0)
    # Heading is preserved, roll and pitch are not.
    assert quaternion_yaw(landed.quaternion) == pytest.approx(1.1)
    matrix = quaternion_to_matrix(landed.quaternion)
    assert matrix[2, 2] == pytest.approx(1.0)


def test_enough_thrust_lifts_off_the_ground():
    body = make_body(ground_enabled=True)
    state = BodyState.at_rest()
    lift = np.array([0.0, 0.0, -2.0 * MASS * GRAVITY_MSS])
    for _ in range(50):
        state = body.advance(state, lift, np.zeros(3), 1 / 100)
    assert state.position_ned_m[2] < -0.5  # airborne, NED z is negative up


def test_disabled_ground_lets_the_vehicle_fall_through():
    body = make_body(ground_enabled=False)
    state = BodyState.at_rest()
    state = body.advance(state, np.zeros(3), np.zeros(3), 1.0)
    assert state.position_ned_m[2] > 1.0
