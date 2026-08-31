"""Per-rotor disc kinematics and wrench assembly.

The sign and wrench conventions live here, in one place, so every consumer
cites the same equations:

    ``n̂_i`` is the thrust direction (unit).  ``U_i`` is the AIR velocity
    relative to the rotor (``U_i = −(v_body + ω_body × r_i)`` in vehicle mode).
    ``v_axial_i = −(U_i · n̂_i)`` — POSITIVE in normal advance/climb, negative in
    descent/windmill.
    ``U_⊥ = U_i − (U_i·n̂_i) n̂_i``; ``v_edge_i = |U_⊥|``;
    ``ê_i = U_⊥ / v_edge_i`` (H ≡ 0 as ``v_edge → 0``, no singularity).
    Per-rotor wrench: ``F_i = T_i n̂_i + H_i ê_i`` — ``ê_i`` is the
    air-relative in-plane direction, so a positive ``H_i`` is a DRAG opposing
    the edgewise motion.
    ``M_total = Σ_i ( r_i × F_i + Q_i n̂_i )`` where ``Q_i`` is the FMU output
    ``torque_Nm[i] = −s_i Q_i^aero``, i.e. the SIGNED REACTION on the airframe,
    applied directly — ``s_i`` does NOT appear again in the moment sum.

Rev 2.1 corrected all four of these signs; rev 2 had ``v_axial = +U·n̂``,
``F = T n̂ − H ê`` and an ``s_i`` in the moment sum, which respectively made a
climb read as a descent, turned the H-force into a thrust, and double-applied
the rotation sense.  The rev-2 readings survive only as non-default escape
hatches in the vehicle YAML (``fmu.v_axial_sign: dot_product``,
``fmu.inplane_sign: subtracted``) so a mismatched older export can still be
flown; see :mod:`thrustlab.sitl.vehicle`.

The reaction sign is independently confirmed by ArduPilot: a rotor turning
right-handed about ``n̂`` puts ``−Q^aero n̂`` on the airframe, and
``AP_MOTORS_MATRIX_YAW_FACTOR_CCW = +1`` says a CCW rotor must yaw a copter
nose-right (``+Z`` FRD) — which is what ``−Q^aero n̂`` gives for
``n̂ = (0,0,−1)``.

Frames: everything here is body FRD.  ``v_body`` is the vehicle's velocity
THROUGH THE AIR in body axes — the caller subtracts wind in NED and rotates,
which is why this module takes ``v_air_body`` rather than ground velocity.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

#: ``v_edge`` below this is treated as exactly zero, so ``ê_i`` is zero and the
#: in-plane force drops out instead of dividing by a vanishing norm.
EDGE_VELOCITY_EPS = 1e-9


@dataclass(frozen=True)
class DiscInflow:
    """Per-rotor inflow, ready to hand to the FMU's disc-mode inputs."""

    v_axial_m_s: np.ndarray  # (N,)
    v_edge_m_s: np.ndarray  # (N,)
    edge_unit: np.ndarray  # (N, 3) ê_i, zero where v_edge is negligible


def disc_inflow(
    positions_m: np.ndarray,
    axes: np.ndarray,
    v_air_body_m_s: np.ndarray,
    omega_body_rad_s: np.ndarray,
    *,
    v_axial_sign: str = "climb_positive",
) -> DiscInflow:
    """``U_i = −(v_air_body + ω_body × r_i)``, decomposed on each rotor's axis.

    ``positions_m`` and ``axes`` are ``(N, 3)`` rotor-major body-FRD arrays.
    ``v_axial_sign`` is ``climb_positive`` for decision 5 rev 2.1's
    ``v_axial = −(U·n̂)``, or ``dot_product`` for the withdrawn rev-2 reading.
    """
    positions = np.asarray(positions_m, dtype=float).reshape(-1, 3)
    unit_axes = np.asarray(axes, dtype=float).reshape(-1, 3)
    v_air = np.asarray(v_air_body_m_s, dtype=float).reshape(3)
    omega = np.asarray(omega_body_rad_s, dtype=float).reshape(3)

    # Velocity of each rotor hub through the air, in body axes.
    hub_velocity = v_air[None, :] + np.cross(omega[None, :], positions)
    inflow = -hub_velocity  # U_i

    v_axial = np.einsum("ij,ij->i", inflow, unit_axes)
    perpendicular = inflow - v_axial[:, None] * unit_axes
    v_edge = np.linalg.norm(perpendicular, axis=1)

    edge_unit = np.zeros_like(perpendicular)
    significant = v_edge > EDGE_VELOCITY_EPS
    edge_unit[significant] = perpendicular[significant] / v_edge[significant, None]

    # Decision 5 rev 2.1: v_axial = −(U·n̂), positive in a climb. U_⊥ above is
    # built from the TRUE dot product, so the flip must come last.
    if v_axial_sign == "climb_positive":
        v_axial = -v_axial
    elif v_axial_sign != "dot_product":  # pragma: no cover - guarded by vehicle.py
        raise ValueError(f"unknown v_axial_sign {v_axial_sign!r}")

    return DiscInflow(v_axial_m_s=v_axial, v_edge_m_s=v_edge, edge_unit=edge_unit)


def assemble_wrench(
    positions_m: np.ndarray,
    axes: np.ndarray,
    senses: np.ndarray,
    thrust_N: np.ndarray,
    torque_Nm: np.ndarray,
    force_inplane_N: np.ndarray,
    edge_unit: np.ndarray,
    *,
    torque_convention: str = "signed",
    negate_reaction_torque: bool = False,
    inplane_sign: str = "drag_positive",
) -> tuple[np.ndarray, np.ndarray]:
    """Spec decision 5 rev 2.1's ``F_i`` and ``M_total``, in body FRD.

    Returns ``(force_body_N, moment_body_Nm)``, each a ``(3,)`` array.
    """
    positions = np.asarray(positions_m, dtype=float).reshape(-1, 3)
    unit_axes = np.asarray(axes, dtype=float).reshape(-1, 3)
    thrust = np.asarray(thrust_N, dtype=float).reshape(-1)
    torque = np.asarray(torque_Nm, dtype=float).reshape(-1)
    inplane = np.asarray(force_inplane_N, dtype=float).reshape(-1)
    edge = np.asarray(edge_unit, dtype=float).reshape(-1, 3)

    # F_i = T_i n̂_i + H_i ê_i (rev 2.1): ê_i is the air-relative in-plane
    # direction, so a positive H_i opposes the edgewise motion.
    if inplane_sign == "drag_positive":
        inplane_scale = 1.0
    elif inplane_sign == "subtracted":
        inplane_scale = -1.0
    else:  # pragma: no cover - guarded by vehicle.py validation
        raise ValueError(f"unknown inplane_sign {inplane_sign!r}")
    per_rotor_force = thrust[:, None] * unit_axes + inplane_scale * inplane[:, None] * edge

    # torque_Nm[i] is the SIGNED reaction on the airframe; s_i is already in it.
    if torque_convention == "signed":
        axial_moment = torque
    elif torque_convention == "magnitude":
        axial_moment = -np.asarray(senses, dtype=float).reshape(-1) * np.abs(torque)
    else:  # pragma: no cover - guarded by vehicle.py validation
        raise ValueError(f"unknown torque_convention {torque_convention!r}")
    if negate_reaction_torque:
        axial_moment = -axial_moment

    # M_total = Σ_i ( r_i × F_i + Q_i n̂_i )
    moment = np.cross(positions, per_rotor_force).sum(axis=0)
    moment = moment + (axial_moment[:, None] * unit_axes).sum(axis=0)

    return per_rotor_force.sum(axis=0), moment
