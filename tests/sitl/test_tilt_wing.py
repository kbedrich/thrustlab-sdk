"""Tilt hinges, demo wing aero, and q-scaled control-surface moments."""
import math
from dataclasses import replace

import numpy as np
import pytest

from thrustlab.sitl.rigidbody import BodyState, RigidBody
from thrustlab.sitl.vehicle import (
    ControlSurfaceConfig,
    TiltConfig,
    VehicleConfigError,
    WingConfig,
    parse_vehicle_config,
)


def vehicle_doc(**overrides):
    doc = {
        "vehicle": {
            "mass_kg": 1.35,
            "inertia_principal": [0.02, 0.02, 0.03],
            "drag_area_m2": 0.02,
        },
        "rotors": [
            {
                "rotor_index": 0,
                "servo_channel": 5,
                "pwm_min": 1000,
                "pwm_max": 2000,
                "position": [0.2, 0.3, 0.0],
                "axis": [0.0, 0.0, -1.0],
                "sense": 1,
                "tilt": {
                    "servo_channel": 12,
                    "pwm_min": 1000,
                    "pwm_max": 2000,
                    "angle_min_deg": 0.0,
                    "angle_max_deg": -90.0,
                    "hinge_axis": [0.0, 1.0, 0.0],
                },
            },
            {
                "rotor_index": 1,
                "servo_channel": 6,
                "pwm_min": 1000,
                "pwm_max": 2000,
                "position": [-0.35, 0.0, 0.0],
                "axis": [0.0, 0.0, -1.0],
                "sense": -1,
            },
        ],
    }
    doc.update(overrides)
    return doc


class TheTiltHinge:
    pass


def test_the_tilt_swings_the_thrust_axis_from_up_to_forward():
    config = parse_vehicle_config(vehicle_doc())
    pwm = {5: 1500, 6: 1500, 12: 1000}
    axes = config.axes_for(lambda ch: pwm[ch])
    np.testing.assert_allclose(axes[0], [0.0, 0.0, -1.0], atol=1e-12)

    pwm[12] = 2000  # full forward tilt: -90 deg about +y
    axes = config.axes_for(lambda ch: pwm[ch])
    np.testing.assert_allclose(axes[0], [1.0, 0.0, 0.0], atol=1e-12)

    pwm[12] = 1500  # halfway: 45 deg forward, still lifting
    axes = config.axes_for(lambda ch: pwm[ch])
    np.testing.assert_allclose(
        axes[0], [math.sqrt(0.5), 0.0, -math.sqrt(0.5)], atol=1e-12
    )


def test_the_untilted_rotor_keeps_its_axis_at_every_tilt_pwm():
    config = parse_vehicle_config(vehicle_doc())
    for tilt_pwm in (1000, 1400, 2000):
        axes = config.axes_for(lambda ch, p=tilt_pwm: {5: 1500, 6: 1500, 12: p}[ch])
        np.testing.assert_allclose(axes[1], [0.0, 0.0, -1.0], atol=1e-15)


def test_a_non_unit_hinge_axis_is_refused_by_name():
    doc = vehicle_doc()
    doc["rotors"][0]["tilt"]["hinge_axis"] = [0.0, 2.0, 0.0]
    with pytest.raises(VehicleConfigError, match="hinge_axis"):
        parse_vehicle_config(doc)


def wing_body(**wing_overrides):
    wing = dict(area_m2=0.32, span_m=1.4, cl0=0.2, cl_alpha_per_rad=5.0,
                alpha_stall_rad=math.radians(12.0), cd0=0.03, oswald=0.8)
    wing.update(wing_overrides)
    return RigidBody(
        mass_kg=1.35,
        inertia_kg_m2=np.diag([0.02, 0.02, 0.03]),
        inverse_inertia=np.linalg.inv(np.diag([0.02, 0.02, 0.03])),
        drag_area_m2=np.zeros(3),
        air_density_kg_m3=1.225,
        wind_ned_m_s=np.zeros(3),
        ground_enabled=False,
        wing=WingConfig(**wing),
    )


def forward_state(u_m_s, w_m_s=0.0):
    return BodyState(
        position_ned_m=np.zeros(3),
        velocity_ned_m_s=np.array([u_m_s, 0.0, w_m_s]),
        quaternion=np.array([1.0, 0.0, 0.0, 0.0]),
        omega_body_rad_s=np.zeros(3),
    )


def stable_wing_body():
    return wing_body(cm_alpha_per_rad=-0.4, cm_q=-6.0, cn_beta_per_rad=0.08,
                     cn_r=-0.15, cl_beta_per_rad=-0.05, cl_p=-0.5)


def test_the_stability_derivatives_restore_and_damp():
    body = stable_wing_body()
    v = 13.0
    # Nose-up alpha (w > 0 in FRD): the pitch moment must push nose DOWN.
    a = math.radians(6.0)
    m = body.wing_moment_body(forward_state(v * math.cos(a), v * math.sin(a)))
    assert m[1] < 0.0, f"pitch stiffness must restore, got {m}"
    # Sideslip from the right (v_y > 0): weathervane yaws nose-right (+N),
    # dihedral rolls away (-L).
    state = BodyState(
        position_ned_m=np.zeros(3),
        velocity_ned_m_s=np.array([v, 2.0, 0.0]),
        quaternion=np.array([1.0, 0.0, 0.0, 0.0]),
        omega_body_rad_s=np.zeros(3),
    )
    m = body.wing_moment_body(state)
    assert m[2] > 0.0 and m[0] < 0.0, f"weathervane +N, dihedral -L, got {m}"
    # Every rate is damped: moment opposes the rate, axis by axis.
    for axis in range(3):
        omega = np.zeros(3)
        omega[axis] = 1.0
        spinning = BodyState(
            position_ned_m=np.zeros(3),
            velocity_ned_m_s=np.array([v, 0.0, 0.0]),
            quaternion=np.array([1.0, 0.0, 0.0, 0.0]),
            omega_body_rad_s=omega,
        )
        assert body.wing_moment_body(spinning)[axis] < 0.0, f"axis {axis} undamped"


def test_a_wing_without_derivatives_makes_no_moment():
    body = wing_body()  # all derivatives default to zero
    np.testing.assert_allclose(
        body.wing_moment_body(forward_state(13.0, 2.0)), 0.0
    )


def test_the_pitot_reads_through_ardupilots_acceptance_cone():
    """The `airspeed` JSON field feeds ArduPilot's simulated pitot, which
    captures the full flow within 20° of the nose and follows a cosine law
    to zero at 90° (SIM_Aircraft.cpp, update_eas_airspeed). The 3-D
    magnitude once fed TECS phantom airspeed in every climb and descent;
    a bare forward component under-read combined flow by ~8-11%."""
    body = wing_body()
    assert body.airspeed(forward_state(13.0)) == pytest.approx(13.0)
    # Pure 5 m/s descent (+z is down in FRD): 90° off-axis, the pitot reads 0.
    assert body.airspeed(forward_state(0.0, 5.0)) == 0.0
    # Descending WHILE flying forward: 22.6° off-axis — nearly the full
    # 13 m/s magnitude, tapered by cos((22.62°-20°)·90/70).
    assert body.airspeed(forward_state(12.0, 5.0)) == pytest.approx(12.978, abs=2e-3)
    # 30° off-axis at V=13: cos((30°-20°)·90/70) = 0.9749.
    v = 13.0
    assert body.airspeed(
        forward_state(v * math.cos(math.radians(30)), v * math.sin(math.radians(30)))
    ) == pytest.approx(12.674, abs=2e-3)
    # Inside the 20° cone the magnitude passes through untapered.
    assert body.airspeed(
        forward_state(v * math.cos(math.radians(19)), v * math.sin(math.radians(19)))
    ) == pytest.approx(v, abs=1e-9)
    # Reverse flow reads zero, not negative.
    assert body.airspeed(forward_state(-4.0)) == 0.0


def test_the_pitot_reports_equivalent_airspeed():
    """The wire field is EAS: at off-standard density the true airspeed
    scales by sqrt(rho/rho0), exactly as ArduPilot's eas2tas divides."""
    thin = RigidBody(
        mass_kg=1.0, inertia_kg_m2=np.eye(3), inverse_inertia=np.eye(3),
        drag_area_m2=np.zeros(3), air_density_kg_m3=0.9,
        wind_ned_m_s=np.zeros(3),
    )
    assert thin.airspeed(forward_state(13.0)) == pytest.approx(
        13.0 * math.sqrt(0.9 / 1.225)
    )


def test_wing_aero_is_continuous_across_the_old_gate_thresholds():
    """The hard u<=0.1 / V<1 switches once flipped 0.7 N·m of pitch moment
    across one float ulp of forward speed (11.6 rad/s² on the demo
    airframe). The fade must make force and moment continuous everywhere."""
    body = stable_wing_body()
    for u in (0.1, 1.0, 2.0):
        lo, hi = forward_state(u - 1e-6, 5.0), forward_state(u + 1e-6, 5.0)
        np.testing.assert_allclose(
            body.wing_moment_body(lo), body.wing_moment_body(hi), atol=1e-4
        )
        np.testing.assert_allclose(
            body.wing_force_body(lo), body.wing_force_body(hi), atol=1e-4
        )
    # No forward flow, no wing aero — same as before.
    np.testing.assert_allclose(body.wing_moment_body(forward_state(0.0, 5.0)), 0.0)


def test_the_moment_angles_clamp_at_the_linear_range():
    """Near-vertical flow must not extrapolate the linear Cm_alpha model:
    alpha in the moment is clamped at the stall angle, so a steeper flow
    angle at the same airspeed cannot produce a larger restoring moment."""
    body = stable_wing_body()
    v = 13.0
    at_stall = body.wing_moment_body(forward_state(
        v * math.cos(math.radians(12)), v * math.sin(math.radians(12))))
    steeper = body.wing_moment_body(forward_state(
        v * math.cos(math.radians(60)), v * math.sin(math.radians(60))))
    assert abs(steeper[1]) <= abs(at_stall[1]) + 1e-9


def test_the_mac_overrides_the_rectangular_chord():
    """S/b is a rectangular-wing default; an explicit MAC replaces it, and
    pitch damping scales with chord SQUARED through q_hat."""
    rect = WingConfig(area_m2=0.32, span_m=1.4, cl0=0.2, cl_alpha_per_rad=5.0,
                      alpha_stall_rad=math.radians(12.0), cd0=0.03, oswald=0.8)
    assert rect.chord_m == pytest.approx(0.32 / 1.4)
    mac = replace(rect, mean_aerodynamic_chord_m=0.3048)
    assert mac.chord_m == 0.3048
    body_rect = wing_body(cm_q=-6.0)
    body_mac = wing_body(cm_q=-6.0, mean_aerodynamic_chord_m=0.3048)
    pitching = BodyState(
        position_ned_m=np.zeros(3),
        velocity_ned_m_s=np.array([13.0, 0.0, 0.0]),
        quaternion=np.array([1.0, 0.0, 0.0, 0.0]),
        omega_body_rad_s=np.array([0.0, 1.0, 0.0]),
    )
    ratio = body_mac.wing_moment_body(pitching)[1] / body_rect.wing_moment_body(pitching)[1]
    assert ratio == pytest.approx((0.3048 / (0.32 / 1.4)) ** 2)


def test_the_wing_lifts_up_and_drags_backwards_in_forward_flight():
    body = wing_body()
    force = body.wing_force_body(forward_state(15.0))
    # CL0 0.2 at 15 m/s over 0.32 m^2: 0.5*1.225*225*0.32*0.2 = 8.82 N of lift.
    assert force[2] == pytest.approx(-8.82, rel=0.02), f"lift up (-z), got {force}"
    assert force[0] < 0.0, f"drag should oppose +x flight, got {force}"
    assert force[1] == 0.0


def test_the_lift_clamps_at_the_stall_angle():
    body = wing_body()
    v = 15.0
    at_stall = body.wing_force_body(
        forward_state(v * math.cos(math.radians(12)), v * math.sin(math.radians(12)))
    )
    beyond = body.wing_force_body(
        forward_state(v * math.cos(math.radians(25)), v * math.sin(math.radians(25)))
    )
    # Same airspeed, larger alpha: the clamped CL cannot grow, so the
    # magnitude of the aero force must not increase past the stall clamp.
    assert np.linalg.norm(beyond) <= np.linalg.norm(at_stall) + 1e-9


def test_the_wing_is_silent_at_rest_and_without_a_wing_block():
    body = wing_body()
    np.testing.assert_allclose(body.wing_force_body(forward_state(0.0)), 0.0)
    bare = RigidBody(
        mass_kg=1.0, inertia_kg_m2=np.eye(3), inverse_inertia=np.eye(3),
        drag_area_m2=np.zeros(3), air_density_kg_m3=1.225,
        wind_ned_m_s=np.zeros(3),
    )
    np.testing.assert_allclose(bare.wing_force_body(forward_state(20.0)), 0.0)


def test_the_control_moment_scales_with_dynamic_pressure():
    body = wing_body()
    elevator_m3 = np.array([0.0, 0.02, 0.0])  # full up-elevator about +y
    slow = body._derivative(forward_state(10.0), np.zeros(3), np.zeros(3), elevator_m3)
    fast = body._derivative(forward_state(20.0), np.zeros(3), np.zeros(3), elevator_m3)
    q_dot_slow, q_dot_fast = slow[10:13][1], fast[10:13][1]
    assert q_dot_slow > 0.0, "positive coefficient about +y must pitch up"
    # 2x speed = 4x dynamic pressure = 4x control moment (wing pitch force
    # contributes no moment: it acts at the CG).
    assert q_dot_fast == pytest.approx(4.0 * q_dot_slow, rel=1e-9)


def test_the_surface_deflection_maps_pwm_to_signed_unit_range():
    surface = ControlSurfaceConfig(
        name="elevator", servo_channel=2, pwm_min=1000, pwm_max=2000,
        moment_axis=np.array([0.0, 1.0, 0.0]), moment_coeff_m3=0.02,
    )
    assert surface.deflection_from_pwm(1500) == 0.0
    assert surface.deflection_from_pwm(2000) == 1.0
    assert surface.deflection_from_pwm(1000) == -1.0
    assert surface.deflection_from_pwm(700) == -1.0  # clamped


def test_the_tilt_pwm_maps_to_the_angle_range_clamped():
    tilt = TiltConfig(
        servo_channel=12, pwm_min=1100, pwm_max=1900,
        angle_min_rad=0.0, angle_max_rad=-math.pi / 2,
        hinge_axis=np.array([0.0, 1.0, 0.0]),
    )
    assert tilt.angle_from_pwm(1100) == 0.0
    assert tilt.angle_from_pwm(1900) == pytest.approx(-math.pi / 2)
    assert tilt.angle_from_pwm(2400) == pytest.approx(-math.pi / 2)  # clamped
    assert tilt.angle_from_pwm(1500) == pytest.approx(-math.pi / 4)
