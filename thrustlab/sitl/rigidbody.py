"""6DOF rigid body in ArduPilot's frames: NED world, FRD body.

FRAMES — the single most load-bearing paragraph in this package:

  * World is NED: x North, y East, z DOWN.  Gravity is ``(0, 0, +9.80665)``.
    ``position`` is metres from the SITL home origin, ``velocity`` is m/s NED.
    Both go on the wire unchanged (``SIM_JSON.cpp`` reads ``state.position``
    and ``state.velocity`` straight into ``position`` / ``velocity_ef``).
  * Body is FRD: x forward, y right, z DOWN.  A copter's rotors therefore point
    along ``[0, 0, -1]`` and produce a NEGATIVE-z body force.
  * The quaternion is ``(w, x, y, z)`` for the body->NED rotation, matching
    ArduPilot's ``Quaternion`` (q1..q4) filling the body-to-earth ``dcm``.

THE ACCELEROMETER.  ``accel_body`` on the wire is SPECIFIC FORCE, not kinematic
acceleration.  ``SIM_Aircraft::update_dynamics`` on ArduPilot master::

    Vector3f accel_earth = dcm * accel_body;
    accel_earth += Vector3f(0.0f, 0.0f, GRAVITY_MSS);
    ...
    accel_body = dcm.transposed() * (accel_earth + Vector3f(0.0f, 0.0f, -GRAVITY_MSS));

so the reading is ``R_ned->body (a_kinematic_NED - g_NED)`` and a level vehicle
at rest reports ``(0, 0, -9.80665)``.  :meth:`RigidBody.specific_force_body`
implements exactly that.

COUPLING.  The rotor wrench is held constant across the frame (one-sample
partitioned ZOH, spec decision 12).  Aerodynamic drag and the gyroscopic term
are functions of state, so they are re-evaluated inside the integrator; only the
propulsion wrench is frozen.

GROUND.  The JSON backend gives ArduPilot no ground model of its own — the
physics backend owns it, and without one the vehicle free-falls before it can
arm.  :class:`RigidBody` therefore carries a deliberately minimal plane contact
mirroring ArduPilot's own ``GROUND_BEHAVIOR_NO_MOVEMENT`` for copters: while
resting on the plane the downward acceleration is clipped, roll and pitch are
levelled, yaw is kept, and the rates are zeroed.  It is enough to arm, lift off
and land; it is not a landing-gear model.  The spec does not cover this — see
the README's "Limitations".
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace

import numpy as np

#: ArduPilot's ``GRAVITY_MSS``.
GRAVITY_MSS = 9.80665

#: ISA sea-level density — the reference for equivalent airspeed.
RHO0_KG_M3 = 1.225

#: The pitot captures the full flow magnitude up to this off-axis angle,
#: then follows ArduPilot's cosine law to zero at 90° (SIM_Aircraft.cpp,
#: ``update_eas_airspeed`` on master) — the same model the autopilot's own
#: SITL backends present, so EKF/TECS see familiar sensor behaviour.
PITOT_MAX_AOA_RAD = math.radians(20.0)

#: Wing aero fades in over this forward-speed band: zero at u ≤ 0, full at
#: u ≥ this, smoothstep between. A hard on/off gate at fixed thresholds
#: injected finite force/moment STEPS into the integrator (measured: the
#: old ``u <= 0.1`` gate with 5 m/s of vertical flow switched 0.7 N·m of
#: pitch moment — 11.6 rad/s² on the demo airframe — across one float ulp
#: of forward speed).
WING_FADE_U_M_S = 2.0

GRAVITY_NED = np.array([0.0, 0.0, GRAVITY_MSS])

#: Largest integrator sub-step.  At SIM_RATE_HZ = 400 a frame is 2.5 ms, so the
#: default gives one RK4 sub-step per frame and a 100 ms catch-up frame gets 40.
DEFAULT_MAX_SUBSTEP_S = 2.5e-3


def quaternion_to_matrix(q: np.ndarray) -> np.ndarray:
    """Body->NED rotation matrix from a ``(w, x, y, z)`` quaternion."""
    w, x, y, z = (float(v) for v in np.asarray(q, dtype=float).reshape(4))
    return np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
            [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
            [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)],
        ]
    )


def quaternion_from_euler(roll: float, pitch: float, yaw: float) -> np.ndarray:
    """``(w, x, y, z)`` body->NED quaternion from a 3-2-1 Euler triple."""
    half_roll, half_pitch, half_yaw = roll / 2.0, pitch / 2.0, yaw / 2.0
    cr, sr = np.cos(half_roll), np.sin(half_roll)
    cp, sp = np.cos(half_pitch), np.sin(half_pitch)
    cy, sy = np.cos(half_yaw), np.sin(half_yaw)
    return np.array(
        [
            cr * cp * cy + sr * sp * sy,
            sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy,
        ]
    )


def quaternion_yaw(q: np.ndarray) -> float:
    """Heading of a ``(w, x, y, z)`` body->NED quaternion, radians."""
    matrix = quaternion_to_matrix(q)
    return float(np.arctan2(matrix[1, 0], matrix[0, 0]))


def _normalise(q: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(q))
    if norm <= 0.0 or not np.isfinite(norm):
        return np.array([1.0, 0.0, 0.0, 0.0])
    return q / norm


@dataclass(frozen=True)
class BodyState:
    """The full 6DOF state.  Immutable: every advance returns a new one."""

    position_ned_m: np.ndarray
    velocity_ned_m_s: np.ndarray
    quaternion: np.ndarray  # (w, x, y, z), body -> NED
    omega_body_rad_s: np.ndarray

    @classmethod
    def at_rest(
        cls,
        *,
        position_ned_m: np.ndarray | None = None,
        yaw_rad: float = 0.0,
    ) -> BodyState:
        return cls(
            position_ned_m=(
                np.zeros(3) if position_ned_m is None else np.asarray(position_ned_m, dtype=float)
            ),
            velocity_ned_m_s=np.zeros(3),
            quaternion=quaternion_from_euler(0.0, 0.0, yaw_rad),
            omega_body_rad_s=np.zeros(3),
        )

    def to_vector(self) -> np.ndarray:
        return np.concatenate(
            [
                self.position_ned_m,
                self.velocity_ned_m_s,
                self.quaternion,
                self.omega_body_rad_s,
            ]
        )

    @classmethod
    def from_vector(cls, vector: np.ndarray) -> BodyState:
        return cls(
            position_ned_m=vector[0:3].copy(),
            velocity_ned_m_s=vector[3:6].copy(),
            quaternion=_normalise(vector[6:10].copy()),
            omega_body_rad_s=vector[10:13].copy(),
        )

    @property
    def rotation_body_to_ned(self) -> np.ndarray:
        return quaternion_to_matrix(self.quaternion)


class RigidBody:
    """Mass properties, drag, gravity, ground — everything but the rotors."""

    def __init__(
        self,
        *,
        mass_kg: float,
        inertia_kg_m2: np.ndarray,
        inverse_inertia: np.ndarray,
        drag_area_m2: np.ndarray,
        air_density_kg_m3: float,
        wind_ned_m_s: np.ndarray,
        ground_enabled: bool = True,
        ground_z_ned_m: float = 0.0,
        max_substep_s: float = DEFAULT_MAX_SUBSTEP_S,
        wing=None,
    ) -> None:
        self.mass_kg = float(mass_kg)
        self.inertia_kg_m2 = np.asarray(inertia_kg_m2, dtype=float).reshape(3, 3)
        self.inverse_inertia = np.asarray(inverse_inertia, dtype=float).reshape(3, 3)
        self.drag_area_m2 = np.asarray(drag_area_m2, dtype=float).reshape(3)
        self.air_density_kg_m3 = float(air_density_kg_m3)
        self.wind_ned_m_s = np.asarray(wind_ned_m_s, dtype=float).reshape(3)
        self.ground_enabled = bool(ground_enabled)
        self.ground_z_ned_m = float(ground_z_ned_m)
        self.max_substep_s = float(max_substep_s)
        #: Optional :class:`~thrustlab.sitl.vehicle.WingConfig` — demo
        #: wing aero, state-dependent like drag, re-evaluated per substep.
        self.wing = wing

    # ----------------------------------------------------------- air-relative

    def air_velocity_body(self, state: BodyState) -> np.ndarray:
        """Vehicle velocity through the air, body FRD."""
        relative_ned = state.velocity_ned_m_s - self.wind_ned_m_s
        return state.rotation_body_to_ned.T @ relative_ned

    def airspeed(self, state: BodyState) -> float:
        """What the simulated pitot reads, as EQUIVALENT airspeed.

        Mirrors ArduPilot's own SITL pitot (``SIM_Aircraft.cpp``,
        ``update_eas_airspeed``): the full flow magnitude within 20° of the
        nose, a cosine taper to zero at 90° off-axis, zero in reverse flow —
        and the wire field is EAS, so the true-airspeed reading scales by
        ``sqrt(ρ/ρ₀)``. The naive 3-D magnitude once fed ArduPilot 5 m/s of
        phantom airspeed in a 5 m/s descent ('Transition airspeed reached
        54.6' during a descent whose groundspeed never passed 14, measured
        2026-08-30); the bare forward component that replaced it under-read
        combined forward/vertical flow by ~8-11% against a real pitot's
        acceptance cone."""
        v_air = self.air_velocity_body(state)
        u = float(v_air[0])
        aoa = math.atan2(math.hypot(float(v_air[1]), float(v_air[2])), u)
        if aoa >= math.pi / 2:
            return 0.0
        speed = float(np.linalg.norm(v_air))
        if aoa > PITOT_MAX_AOA_RAD:
            gain = (math.pi / 2) / (math.pi / 2 - PITOT_MAX_AOA_RAD)
            speed *= math.cos((aoa - PITOT_MAX_AOA_RAD) * gain)
        return speed * math.sqrt(self.air_density_kg_m3 / RHO0_KG_M3)

    def drag_force_body(self, state: BodyState) -> np.ndarray:
        """``F = -0.5 ρ (CdA)_i |v_i| v_i`` per body axis.

        A per-axis drag AREA (Cd·A, m^2) is the airframe input the spec asks
        for; the force is quadratic in speed, evaluated component-wise so the
        three body axes can carry different frontal areas.
        """
        v_air = self.air_velocity_body(state)
        return -0.5 * self.air_density_kg_m3 * self.drag_area_m2 * np.abs(v_air) * v_air

    def _wing_fade(self, u: float) -> float:
        """Smoothstep 0→1 over forward speed ``[0, WING_FADE_U_M_S]``.

        The wing model — linear lift AND the linear stability derivatives —
        is a small-disturbance model around forward flight; near-vertical
        flow is outside its domain, and switching it with a hard threshold
        put finite force/moment steps into the integrator.
        """
        s = min(max(u / WING_FADE_U_M_S, 0.0), 1.0)
        return s * s * (3.0 - 2.0 * s)

    def wing_force_body(self, state: BodyState) -> np.ndarray:
        """Demo wing lift and drag in body FRD; zero without a ``wing`` block.

        Angle of attack comes from the body-frame air velocity's x-z plane
        (``alpha = atan2(w, u)`` in FRD), lift is linear in alpha and CLAMPED
        at the stall angle, drag is ``cd0 + k·CL²``. Forces act at the CG;
        stability and damping MOMENTS live in :meth:`wing_moment_body`. The
        whole model fades in smoothly with forward speed (:meth:`_wing_fade`)
        — reverse flow reads zero, and there is no on/off step.
        """
        if self.wing is None:
            return np.zeros(3)
        v_air = self.air_velocity_body(state)
        u, w = float(v_air[0]), float(v_air[2])
        fade = self._wing_fade(u)
        if fade == 0.0:
            return np.zeros(3)
        speed_sq = u * u + w * w
        alpha = np.arctan2(w, u)
        alpha_eff = float(np.clip(alpha, -self.wing.alpha_stall_rad,
                                  self.wing.alpha_stall_rad))
        cl = self.wing.cl0 + self.wing.cl_alpha_per_rad * alpha_eff
        cd = self.wing.cd0 + self.wing.induced_factor * cl * cl
        q_s = 0.5 * self.air_density_kg_m3 * speed_sq * self.wing.area_m2
        lift, drag = q_s * cl, q_s * cd
        cos_a, sin_a = np.cos(alpha), np.sin(alpha)
        # Wind axes back to body FRD: drag along −v̂, lift ⊥ v̂ toward −z.
        return fade * np.array(
            [lift * sin_a - drag * cos_a, 0.0, -lift * cos_a - drag * sin_a]
        )

    def dynamic_pressure(self, state: BodyState) -> float:
        v_air = self.air_velocity_body(state)
        return 0.5 * self.air_density_kg_m3 * float(np.dot(v_air, v_air))

    def wing_moment_body(self, state: BodyState) -> np.ndarray:
        """Static stability and rate damping, standard derivative form.

        ``[L, M, N] = q·S·[b·(Clβ·β + Clp·p̂), c·(Cmα·α + Cmq·q̂),
        b·(Cnβ·β + Cnr·r̂)]`` with rates normalized by ``{b|c}/2V``. Without
        these the airframe is neutrally stable in every axis — the measured
        failure mode is sideslip growing unchecked through the QuadPlane
        transition until the wing departs — so the demo wing carries the
        derivatives every real airframe has. Zero with an all-zero derivative
        set (the pre-2026-08-30 behaviour); fades in smoothly with forward
        speed like the wing force, and the small-disturbance angles α and β
        are clamped to the wing's own linear range (the stall angle) instead
        of extrapolating a near-vertical flow angle into a huge restoring
        moment.
        """
        if self.wing is None:
            return np.zeros(3)
        wing = self.wing
        if not (wing.cm_alpha_per_rad or wing.cm_q or wing.cn_beta_per_rad
                or wing.cn_r or wing.cl_beta_per_rad or wing.cl_p):
            return np.zeros(3)
        v_air = self.air_velocity_body(state)
        u = float(v_air[0])
        fade = self._wing_fade(u)
        if fade == 0.0:
            return np.zeros(3)
        speed = float(np.linalg.norm(v_air))
        bound = wing.alpha_stall_rad
        alpha = float(np.clip(np.arctan2(v_air[2], u), -bound, bound))
        beta = float(np.clip(
            np.arcsin(np.clip(v_air[1] / speed, -1.0, 1.0)), -bound, bound))
        p, q_rate, r = (float(x) for x in state.omega_body_rad_s)
        q_dyn = 0.5 * self.air_density_kg_m3 * speed * speed
        b, c = wing.span_m, wing.chord_m
        p_hat = p * b / (2.0 * speed)
        q_hat = q_rate * c / (2.0 * speed)
        r_hat = r * b / (2.0 * speed)
        return fade * q_dyn * wing.area_m2 * np.array([
            b * (wing.cl_beta_per_rad * beta + wing.cl_p * p_hat),
            c * (wing.cm_alpha_per_rad * alpha + wing.cm_q * q_hat),
            b * (wing.cn_beta_per_rad * beta + wing.cn_r * r_hat),
        ])

    # --------------------------------------------------------------- dynamics

    def _on_ground(self, state: BodyState) -> bool:
        return self.ground_enabled and state.position_ned_m[2] >= self.ground_z_ned_m - 1e-3

    def acceleration_ned(
        self, state: BodyState, rotor_force_body_N: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray]:
        """Kinematic NED acceleration and the non-gravitational body force.

        Mirrors ArduPilot: gravity is added in the earth frame and the ground
        clips a downward earth-frame acceleration.
        """
        force_body = np.asarray(rotor_force_body_N, dtype=float).reshape(3)
        force_body = force_body + self.drag_force_body(state) + self.wing_force_body(state)
        accel_ned = state.rotation_body_to_ned @ (force_body / self.mass_kg) + GRAVITY_NED
        if self._on_ground(state) and accel_ned[2] > 0.0:
            accel_ned = accel_ned.copy()
            accel_ned[2] = 0.0
        return accel_ned, force_body

    def specific_force_body(self, state: BodyState, rotor_force_body_N: np.ndarray) -> np.ndarray:
        """The accelerometer reading ArduPilot expects in ``imu.accel_body``."""
        accel_ned, _ = self.acceleration_ned(state, rotor_force_body_N)
        return state.rotation_body_to_ned.T @ (accel_ned - GRAVITY_NED)

    def _derivative(
        self,
        state: BodyState,
        rotor_force_body_N: np.ndarray,
        rotor_moment_body_Nm: np.ndarray,
        control_moment_m3: np.ndarray | None = None,
    ) -> np.ndarray:
        accel_ned, _ = self.acceleration_ned(state, rotor_force_body_N)
        omega = state.omega_body_rad_s
        moment = np.asarray(rotor_moment_body_Nm, dtype=float).reshape(3)
        moment = moment + self.wing_moment_body(state)
        if control_moment_m3 is not None:
            # Surface deflections are ZOH per frame; the moment they produce
            # scales with the CURRENT dynamic pressure, like drag.
            moment = moment + self.dynamic_pressure(state) * control_moment_m3
        omega_dot = self.inverse_inertia @ (moment - np.cross(omega, self.inertia_kg_m2 @ omega))

        w, x, y, z = state.quaternion
        p, q, r = omega
        q_dot = 0.5 * np.array(
            [
                -x * p - y * q - z * r,
                w * p + y * r - z * q,
                w * q - x * r + z * p,
                w * r + x * q - y * p,
            ]
        )
        return np.concatenate([state.velocity_ned_m_s, accel_ned, q_dot, omega_dot])

    def advance(
        self,
        state: BodyState,
        rotor_force_body_N: np.ndarray,
        rotor_moment_body_Nm: np.ndarray,
        dt_s: float,
        control_moment_m3: np.ndarray | None = None,
    ) -> BodyState:
        """Integrate ``dt_s`` with the rotor wrench held (ZOH), then apply ground."""
        if dt_s <= 0.0:
            return state
        substeps = max(1, int(np.ceil(dt_s / self.max_substep_s)))
        h = dt_s / substeps
        current = state
        for _ in range(substeps):
            y0 = current.to_vector()
            k1 = self._derivative(
                current, rotor_force_body_N, rotor_moment_body_Nm, control_moment_m3
            )
            k2 = self._derivative(
                BodyState.from_vector(y0 + 0.5 * h * k1),
                rotor_force_body_N, rotor_moment_body_Nm, control_moment_m3,
            )
            k3 = self._derivative(
                BodyState.from_vector(y0 + 0.5 * h * k2),
                rotor_force_body_N, rotor_moment_body_Nm, control_moment_m3,
            )
            k4 = self._derivative(
                BodyState.from_vector(y0 + h * k3),
                rotor_force_body_N, rotor_moment_body_Nm, control_moment_m3,
            )
            current = BodyState.from_vector(y0 + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4))
        return self.apply_ground(current)

    def apply_ground(self, state: BodyState) -> BodyState:
        """ArduPilot's copter ``GROUND_BEHAVIOR_NO_MOVEMENT``, minimally.

        Below the plane: pin the altitude, stop any downward motion, stop
        sliding and rotating, level roll and pitch but keep the heading.  A
        vehicle whose rotors can lift it leaves the plane on the next frame
        because :meth:`acceleration_ned` only clips DOWNWARD acceleration.
        """
        if not self.ground_enabled:
            return state
        if state.position_ned_m[2] < self.ground_z_ned_m:
            return state
        position = state.position_ned_m.copy()
        position[2] = self.ground_z_ned_m
        velocity = state.velocity_ned_m_s.copy()
        if velocity[2] > 0.0:
            velocity[2] = 0.0
        velocity[0] = 0.0
        velocity[1] = 0.0
        return replace(
            state,
            position_ned_m=position,
            velocity_ned_m_s=velocity,
            quaternion=quaternion_from_euler(0.0, 0.0, quaternion_yaw(state.quaternion)),
            omega_body_rad_s=np.zeros(3),
        )
