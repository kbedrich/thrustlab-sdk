"""Vehicle YAML: airframe mass properties plus the explicit rotor geometry map.

Everything geometric in this file is expressed in the ArduPilot BODY frame,
FRD — x forward, y right, z DOWN.  A copter's rotors therefore point at
``axis: [0, 0, -1]``.  See the README's "Frames" section.

The ``servo_channel -> rotor_index`` map is REQUIRED and bijective by design:
ArduPilot lets a motor function land on any servo output, so nothing about
channel order may be assumed (spec decision 12).  Validation errors name the
YAML path that is wrong, because the alternative is a silent frame swap that
only shows up as a diverging SITL flight.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import yaml

#: ``|axis| - 1`` tolerated before the axis is rejected as non-unit.
AXIS_UNIT_TOLERANCE = 1e-6

# ─────────────────────────────────────────────────────────────────────────────
# Sign conventions.  The FIRST value of each tuple is spec decision 5 rev 2.1 —
# the normative physics — and is the default.  The second is the withdrawn rev-2
# reading, kept only so an export built against rev 2 can still be flown; it is
# never what a current export wants.
# ─────────────────────────────────────────────────────────────────────────────

#: How the bridge reads ``torque_Nm[i]`` when assembling the reaction moment.
#:
#: ``signed``    — rev 2.1: ``torque_Nm[i] = −s_i Q_i^aero`` is the SIGNED
#:                 reaction on the airframe, applied directly as the coefficient
#:                 of ``n_i``.  ``sense`` is NOT applied again.
#: ``magnitude`` — ``torque_Nm[i]`` is an unsigned aero magnitude, so the bridge
#:                 forms the reaction itself as ``−s_i |torque_Nm[i]|``.
TORQUE_CONVENTIONS = ("signed", "magnitude")

#: ``climb_positive`` — rev 2.1: ``v_axial_i = −(U_i · n̂_i)``, positive in a
#:                      climb, negative in descent/windmill.
#: ``dot_product``    — withdrawn rev-2 reading ``+(U_i · n̂_i)``, which reads a
#:                      climb as a descent.
V_AXIAL_SIGNS = ("climb_positive", "dot_product")

#: ``drag_positive`` — rev 2.1: ``F_i = T_i n̂_i + H_i ê_i``, so a positive
#:                     ``force_inplane_N`` opposes the edgewise motion.
#: ``subtracted``    — withdrawn rev-2 reading ``− H_i ê_i``, which turns the
#:                     H-force into a thrust.
INPLANE_SIGNS = ("drag_positive", "subtracted")


class VehicleConfigError(ValueError):
    """A vehicle YAML that cannot be turned into a runnable configuration."""


@dataclass(frozen=True)
class TiltConfig:
    """A servo-driven hinge that rotates a rotor's thrust axis per frame.

    ``hinge_axis`` is a unit vector in body FRD; the thrust axis is rotated
    about it by ``angle_min_rad`` at ``pwm_min`` through ``angle_max_rad`` at
    ``pwm_max`` (right-handed about the hinge). A QuadPlane front tilt is
    hinge ``[0, 1, 0]`` with angles ``0 → -pi/2``: the ``[0, 0, -1]`` axis
    swings to ``[1, 0, 0]`` — thrust forward.
    """

    servo_channel: int
    pwm_min: float
    pwm_max: float
    angle_min_rad: float
    angle_max_rad: float
    hinge_axis: np.ndarray
    reversed: bool = False

    def angle_from_pwm(self, pwm_us: float) -> float:
        span = self.pwm_max - self.pwm_min
        frac = min(1.0, max(0.0, (float(pwm_us) - self.pwm_min) / span))
        if self.reversed:
            frac = 1.0 - frac
        return self.angle_min_rad + frac * (self.angle_max_rad - self.angle_min_rad)


@dataclass(frozen=True)
class WingConfig:
    """Demo-grade fixed-wing aero so a QuadPlane transition has something to
    fly on: flat linear lift with a hard stall clamp, parabolic drag, forces
    applied at the CG. This is USER-SUPPLIED airframe scaffolding — the FMU
    stays the powertrain truth, and no fidelity claim is made for these
    numbers.
    """

    area_m2: float
    span_m: float
    cl0: float
    cl_alpha_per_rad: float
    alpha_stall_rad: float
    cd0: float
    oswald: float
    #: Static-stability and damping derivatives, standard non-dimensional
    #: convention (moments = q·S·{c|b}·coefficient; rates normalized by
    #: {c|b}/2V). All default to ZERO — a wing block without them behaves as
    #: before — but a transition demo NEEDS them: without pitch stiffness,
    #: weathervane and rate damping the airframe is neutrally stable in every
    #: axis, sideslip grows unchecked in the transition (measured 2026-08-30:
    #: groundspeed 19.5 m/s against a 10 m/s pitot read), and no autopilot
    #: tune can hold it.
    cm_alpha_per_rad: float = 0.0
    cm_q: float = 0.0
    cn_beta_per_rad: float = 0.0
    cn_r: float = 0.0
    cl_beta_per_rad: float = 0.0
    cl_p: float = 0.0
    #: Mean aerodynamic chord for pitch-moment normalization. ``None`` falls
    #: back to S/b — exact for a rectangular wing only. Cm_q scales with
    #: chord SQUARED, so a tapered or delta planform normalized by S/b
    #: understates pitch damping (44% low for a triangular planform); set
    #: this whenever the planform is not a rectangle.
    mean_aerodynamic_chord_m: float | None = None

    @property
    def induced_factor(self) -> float:
        aspect_ratio = self.span_m * self.span_m / self.area_m2
        return 1.0 / (np.pi * self.oswald * aspect_ratio)

    @property
    def chord_m(self) -> float:
        if self.mean_aerodynamic_chord_m is not None:
            return self.mean_aerodynamic_chord_m
        return self.area_m2 / self.span_m


@dataclass(frozen=True)
class ControlSurfaceConfig:
    """One aerodynamic control: deflection scales a body-axis moment by
    dynamic pressure. ``moment_coeff_m3`` is N·m per unit deflection per Pa
    of dynamic pressure (an effective volume), right-handed about
    ``moment_axis``.
    """

    name: str
    servo_channel: int
    pwm_min: float
    pwm_max: float
    moment_axis: np.ndarray
    moment_coeff_m3: float
    reversed: bool = False

    def deflection_from_pwm(self, pwm_us: float) -> float:
        center = 0.5 * (self.pwm_min + self.pwm_max)
        half = 0.5 * (self.pwm_max - self.pwm_min)
        deflection = min(1.0, max(-1.0, (float(pwm_us) - center) / half))
        return -deflection if self.reversed else deflection


@dataclass(frozen=True)
class RotorConfig:
    """One rotor: which servo drives it, where it is, and which way it points."""

    rotor_index: int
    servo_channel: int
    pwm_min: float
    pwm_max: float
    reversed: bool
    spin_arm_threshold: float
    position_m: np.ndarray
    axis: np.ndarray
    sense: int
    name: str | None = None
    tilt: TiltConfig | None = None

    def throttle_from_pwm(self, pwm_us: float) -> float:
        """Map a servo PWM in microseconds to the FMU's ``throttle`` in [0, 1].

        Spec decision 6 / 12: normalise against the channel's calibration,
        clamp, flip if the channel is reversed, then drop anything below the
        spin-arm threshold to a hard zero so a disarmed-but-idling PWM does not
        spin the rotor.
        """
        span = self.pwm_max - self.pwm_min
        throttle = (float(pwm_us) - self.pwm_min) / span
        throttle = min(1.0, max(0.0, throttle))
        if self.reversed:
            throttle = 1.0 - throttle
        if throttle < self.spin_arm_threshold:
            return 0.0
        return throttle


@dataclass(frozen=True)
class VehicleConfig:
    """Airframe + rotor set + environment, validated."""

    mass_kg: float
    inertia_kg_m2: np.ndarray
    inverse_inertia: np.ndarray
    drag_area_m2: np.ndarray
    wind_ned_m_s: np.ndarray
    air_density_kg_m3: float
    ambient_temp_C: float
    rotors: tuple[RotorConfig, ...]
    torque_convention: str
    negate_reaction_torque: bool
    v_axial_sign: str
    inplane_sign: str
    ground_enabled: bool
    ground_z_ned_m: float
    name: str | None = None
    wing: WingConfig | None = None
    control_surfaces: tuple[ControlSurfaceConfig, ...] = ()

    @property
    def rotor_count(self) -> int:
        return len(self.rotors)

    @property
    def has_tilt(self) -> bool:
        return any(rotor.tilt is not None for rotor in self.rotors)

    def axes_for(self, pwm_for_channel) -> np.ndarray:
        """``(N, 3)`` thrust directions with every tilt hinge applied.

        Identical to :attr:`axes` for a vehicle with no tilting rotors; the
        Rodrigues rotation runs only for rotors that declare a ``tilt``.
        """
        out = self.axes
        for rotor in self.rotors:
            if rotor.tilt is None:
                continue
            angle = rotor.tilt.angle_from_pwm(pwm_for_channel(rotor.tilt.servo_channel))
            k = rotor.tilt.hinge_axis
            v = rotor.axis
            out[rotor.rotor_index] = (
                v * np.cos(angle)
                + np.cross(k, v) * np.sin(angle)
                + k * float(np.dot(k, v)) * (1.0 - np.cos(angle))
            )
        return out

    def control_moment_m3(self, pwm_for_channel) -> np.ndarray:
        """Σ deflection · coeff · axis over the control surfaces, body FRD.

        The rigid body multiplies this by the CURRENT dynamic pressure inside
        the integrator, so the deflections are ZOH per frame while the moment
        stays state-dependent.
        """
        moment = np.zeros(3)
        for surface in self.control_surfaces:
            deflection = surface.deflection_from_pwm(
                pwm_for_channel(surface.servo_channel)
            )
            moment += deflection * surface.moment_coeff_m3 * surface.moment_axis
        return moment

    @property
    def max_servo_channel(self) -> int:
        return max(rotor.servo_channel for rotor in self.rotors)

    def throttles(self, pwm_for_channel) -> np.ndarray:
        """Per-rotor throttle vector, indexed by ``rotor_index``.

        ``pwm_for_channel`` is a callable taking a 1-based servo channel — in
        practice :meth:`~thrustlab.sitl.protocol.ServoPacket.pwm_for_channel`.
        """
        out = np.zeros(self.rotor_count, dtype=float)
        for rotor in self.rotors:
            out[rotor.rotor_index] = rotor.throttle_from_pwm(pwm_for_channel(rotor.servo_channel))
        return out

    @property
    def positions_m(self) -> np.ndarray:
        """``(N, 3)`` rotor positions in body FRD, rotor-index major."""
        return np.array([r.position_m for r in self.rotors], dtype=float)

    @property
    def axes(self) -> np.ndarray:
        """``(N, 3)`` unit thrust directions in body FRD, rotor-index major."""
        return np.array([r.axis for r in self.rotors], dtype=float)

    @property
    def senses(self) -> np.ndarray:
        """``(N,)`` rotation senses ``s_i`` per spec decision 5."""
        return np.array([r.sense for r in self.rotors], dtype=float)


def _require(mapping: Mapping[str, Any], key: str, path: str) -> Any:
    if key not in mapping:
        raise VehicleConfigError(f"{path}: required key '{key}' is missing")
    return mapping[key]


def _as_float(
    value: Any, path: str, *, positive: bool = False, non_negative: bool = False
) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise VehicleConfigError(f"{path}: expected a number, got {value!r}") from exc
    if not np.isfinite(number):
        raise VehicleConfigError(f"{path}: must be finite, got {number}")
    if positive and number <= 0.0:
        raise VehicleConfigError(f"{path}: must be > 0, got {number}")
    if non_negative and number < 0.0:
        raise VehicleConfigError(f"{path}: must be >= 0, got {number}")
    return number


def _as_vector3(value: Any, path: str) -> np.ndarray:
    if isinstance(value, (Mapping, str, bytes)):
        raise VehicleConfigError(f"{path}: expected a 3-element list, got {value!r}")
    if not isinstance(value, Sequence) or len(value) != 3:
        raise VehicleConfigError(f"{path}: expected a 3-element list, got {value!r}")
    return np.array([_as_float(v, f"{path}[{i}]") for i, v in enumerate(value)], dtype=float)


def _as_bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise VehicleConfigError(f"{path}: expected true or false, got {value!r}")
    return value


def _parse_inertia(block: Mapping[str, Any]) -> np.ndarray:
    """Accept either a full 3x3 matrix or a principal-axis triple."""
    has_matrix = "inertia" in block
    has_principal = "inertia_principal" in block
    if has_matrix and has_principal:
        raise VehicleConfigError(
            "vehicle: give either 'inertia' (3x3) or 'inertia_principal' (3 values), not both"
        )
    if has_principal:
        principal = _as_vector3(block["inertia_principal"], "vehicle.inertia_principal")
        for i, value in enumerate(principal):
            if value <= 0.0:
                raise VehicleConfigError(
                    f"vehicle.inertia_principal[{i}]: principal moments must be > 0, got {value}"
                )
        return np.diag(principal)
    if not has_matrix:
        raise VehicleConfigError(
            "vehicle: required key 'inertia' (3x3 kg m^2) or 'inertia_principal' is missing"
        )
    rows = block["inertia"]
    if not isinstance(rows, Sequence) or len(rows) != 3:
        raise VehicleConfigError("vehicle.inertia: expected 3 rows of 3 numbers")
    matrix = np.array(
        [_as_vector3(row, f"vehicle.inertia[{i}]") for i, row in enumerate(rows)], dtype=float
    )
    if not np.allclose(matrix, matrix.T, atol=1e-12, rtol=0.0):
        raise VehicleConfigError("vehicle.inertia: inertia tensor must be symmetric")
    eigenvalues = np.linalg.eigvalsh(matrix)
    if float(eigenvalues.min()) <= 0.0:
        raise VehicleConfigError(
            "vehicle.inertia: inertia tensor must be positive definite "
            f"(smallest eigenvalue {eigenvalues.min():.6g})"
        )
    return matrix


def _parse_drag_area(value: Any) -> np.ndarray:
    if value is None:
        return np.zeros(3, dtype=float)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return np.full(3, _as_float(value, "vehicle.drag_area_m2", non_negative=True))
    vector = _as_vector3(value, "vehicle.drag_area_m2")
    if float(vector.min()) < 0.0:
        raise VehicleConfigError("vehicle.drag_area_m2: drag areas must be >= 0")
    return vector


def _parse_rotor(entry: Any, ordinal: int) -> RotorConfig:
    path = f"rotors[{ordinal}]"
    if not isinstance(entry, Mapping):
        raise VehicleConfigError(f"{path}: expected a mapping, got {entry!r}")

    rotor_index = _require(entry, "rotor_index", path)
    if not isinstance(rotor_index, int) or isinstance(rotor_index, bool) or rotor_index < 0:
        raise VehicleConfigError(f"{path}.rotor_index: expected a non-negative integer")

    servo_channel = _require(entry, "servo_channel", path)
    if not isinstance(servo_channel, int) or isinstance(servo_channel, bool):
        raise VehicleConfigError(f"{path}.servo_channel: expected an integer")
    if not 1 <= servo_channel <= 32:
        raise VehicleConfigError(
            f"{path}.servo_channel: ArduPilot servo channels are 1-32 (1-based, "
            f"matching SERVOn_FUNCTION); got {servo_channel}"
        )

    pwm_min = _as_float(_require(entry, "pwm_min", path), f"{path}.pwm_min")
    pwm_max = _as_float(_require(entry, "pwm_max", path), f"{path}.pwm_max")
    if pwm_max <= pwm_min:
        raise VehicleConfigError(
            f"{path}: pwm_max ({pwm_max}) must be greater than pwm_min ({pwm_min})"
        )

    threshold = _as_float(
        entry.get("spin_arm_threshold", 0.0), f"{path}.spin_arm_threshold", non_negative=True
    )
    if threshold > 1.0:
        raise VehicleConfigError(
            f"{path}.spin_arm_threshold: a throttle threshold lives in [0, 1], got {threshold}"
        )

    position = _as_vector3(_require(entry, "position", path), f"{path}.position")
    axis = _as_vector3(_require(entry, "axis", path), f"{path}.axis")
    norm = float(np.linalg.norm(axis))
    if abs(norm - 1.0) > AXIS_UNIT_TOLERANCE:
        raise VehicleConfigError(
            f"{path}.axis: thrust axis must be a UNIT vector in body FRD "
            f"(|axis| = {norm:.9g}); a copter rotor is [0, 0, -1]"
        )

    sense = _require(entry, "sense", path)
    # `True == 1` in Python, so booleans have to be excluded explicitly.
    if isinstance(sense, bool) or sense not in (1, -1):
        raise VehicleConfigError(
            f"{path}.sense: rotation sense is +1 (CCW viewed against the thrust "
            f"direction, spec decision 5) or -1; got {sense!r}"
        )

    name = entry.get("name")
    if name is not None and not isinstance(name, str):
        raise VehicleConfigError(f"{path}.name: expected a string")

    tilt = None
    tilt_block = entry.get("tilt")
    if tilt_block is not None:
        if not isinstance(tilt_block, Mapping):
            raise VehicleConfigError(f"{path}.tilt: expected a mapping")
        tpath = f"{path}.tilt"
        t_channel = _require(tilt_block, "servo_channel", tpath)
        if not isinstance(t_channel, int) or isinstance(t_channel, bool) \
                or not 1 <= t_channel <= 32:
            raise VehicleConfigError(
                f"{tpath}.servo_channel: ArduPilot servo channels are 1-32"
            )
        t_pwm_min = _as_float(_require(tilt_block, "pwm_min", tpath), f"{tpath}.pwm_min")
        t_pwm_max = _as_float(_require(tilt_block, "pwm_max", tpath), f"{tpath}.pwm_max")
        if t_pwm_max <= t_pwm_min:
            raise VehicleConfigError(f"{tpath}: pwm_max must be greater than pwm_min")
        hinge = _as_vector3(_require(tilt_block, "hinge_axis", tpath), f"{tpath}.hinge_axis")
        norm = float(np.linalg.norm(hinge))
        if abs(norm - 1.0) > AXIS_UNIT_TOLERANCE:
            raise VehicleConfigError(
                f"{tpath}.hinge_axis: hinge axis must be a UNIT vector in body "
                f"FRD (|axis| = {norm:.9g})"
            )
        tilt = TiltConfig(
            servo_channel=t_channel,
            pwm_min=t_pwm_min,
            pwm_max=t_pwm_max,
            angle_min_rad=math.radians(
                _as_float(_require(tilt_block, "angle_min_deg", tpath),
                          f"{tpath}.angle_min_deg")
            ),
            angle_max_rad=math.radians(
                _as_float(_require(tilt_block, "angle_max_deg", tpath),
                          f"{tpath}.angle_max_deg")
            ),
            hinge_axis=hinge,
            reversed=_as_bool(tilt_block.get("reversed", False), f"{tpath}.reversed"),
        )

    return RotorConfig(
        rotor_index=rotor_index,
        servo_channel=servo_channel,
        pwm_min=pwm_min,
        pwm_max=pwm_max,
        reversed=_as_bool(entry.get("reversed", False), f"{path}.reversed"),
        spin_arm_threshold=threshold,
        position_m=position,
        axis=axis,
        sense=int(sense),
        name=name,
        tilt=tilt,
    )


def _parse_wing(block: Any) -> WingConfig | None:
    if block is None:
        return None
    if not isinstance(block, Mapping):
        raise VehicleConfigError("wing: expected a mapping")
    area = _as_float(_require(block, "area_m2", "wing"), "wing.area_m2", positive=True)
    span = _as_float(_require(block, "span_m", "wing"), "wing.span_m", positive=True)
    return WingConfig(
        area_m2=area,
        span_m=span,
        cl0=_as_float(block.get("cl0", 0.2), "wing.cl0"),
        cl_alpha_per_rad=_as_float(
            block.get("cl_alpha_per_rad", 5.0), "wing.cl_alpha_per_rad", positive=True
        ),
        alpha_stall_rad=math.radians(
            _as_float(block.get("alpha_stall_deg", 12.0), "wing.alpha_stall_deg",
                      positive=True)
        ),
        cd0=_as_float(block.get("cd0", 0.03), "wing.cd0", non_negative=True),
        oswald=_as_float(block.get("oswald", 0.8), "wing.oswald", positive=True),
        cm_alpha_per_rad=_as_float(
            block.get("cm_alpha_per_rad", 0.0), "wing.cm_alpha_per_rad"
        ),
        cm_q=_as_float(block.get("cm_q", 0.0), "wing.cm_q"),
        cn_beta_per_rad=_as_float(
            block.get("cn_beta_per_rad", 0.0), "wing.cn_beta_per_rad"
        ),
        cn_r=_as_float(block.get("cn_r", 0.0), "wing.cn_r"),
        cl_beta_per_rad=_as_float(
            block.get("cl_beta_per_rad", 0.0), "wing.cl_beta_per_rad"
        ),
        cl_p=_as_float(block.get("cl_p", 0.0), "wing.cl_p"),
        mean_aerodynamic_chord_m=(
            _as_float(block["mean_aerodynamic_chord_m"],
                      "wing.mean_aerodynamic_chord_m", positive=True)
            if "mean_aerodynamic_chord_m" in block else None
        ),
    )


def _parse_control_surfaces(block: Any) -> tuple[ControlSurfaceConfig, ...]:
    if block is None:
        return ()
    if not isinstance(block, Sequence) or isinstance(block, (str, bytes)):
        raise VehicleConfigError("control_surfaces: expected a list")
    surfaces = []
    channels = set()
    for i, entry in enumerate(block):
        path = f"control_surfaces[{i}]"
        if not isinstance(entry, Mapping):
            raise VehicleConfigError(f"{path}: expected a mapping")
        name = _require(entry, "name", path)
        if not isinstance(name, str):
            raise VehicleConfigError(f"{path}.name: expected a string")
        channel = _require(entry, "servo_channel", path)
        if not isinstance(channel, int) or isinstance(channel, bool) \
                or not 1 <= channel <= 32:
            raise VehicleConfigError(
                f"{path}.servo_channel: ArduPilot servo channels are 1-32"
            )
        if channel in channels:
            raise VehicleConfigError(
                f"{path}.servo_channel: channel {channel} is used twice"
            )
        channels.add(channel)
        pwm_min = _as_float(_require(entry, "pwm_min", path), f"{path}.pwm_min")
        pwm_max = _as_float(_require(entry, "pwm_max", path), f"{path}.pwm_max")
        if pwm_max <= pwm_min:
            raise VehicleConfigError(f"{path}: pwm_max must be greater than pwm_min")
        axis = _as_vector3(_require(entry, "moment_axis", path), f"{path}.moment_axis")
        norm = float(np.linalg.norm(axis))
        if abs(norm - 1.0) > AXIS_UNIT_TOLERANCE:
            raise VehicleConfigError(
                f"{path}.moment_axis: must be a UNIT vector (|axis| = {norm:.9g})"
            )
        surfaces.append(ControlSurfaceConfig(
            name=name,
            servo_channel=channel,
            pwm_min=pwm_min,
            pwm_max=pwm_max,
            moment_axis=axis,
            moment_coeff_m3=_as_float(
                _require(entry, "moment_coeff_m3", path), f"{path}.moment_coeff_m3"
            ),
            reversed=_as_bool(entry.get("reversed", False), f"{path}.reversed"),
        ))
    return tuple(surfaces)


def parse_vehicle_config(document: Mapping[str, Any]) -> VehicleConfig:
    """Validate a parsed YAML document into a :class:`VehicleConfig`."""
    if not isinstance(document, Mapping):
        raise VehicleConfigError("vehicle YAML must be a mapping at the top level")

    vehicle = document.get("vehicle")
    if not isinstance(vehicle, Mapping):
        raise VehicleConfigError("vehicle: required top-level 'vehicle' block is missing")

    mass = _as_float(_require(vehicle, "mass_kg", "vehicle"), "vehicle.mass_kg", positive=True)
    inertia = _parse_inertia(vehicle)
    drag_area = _parse_drag_area(vehicle.get("drag_area_m2"))

    environment = document.get("environment") or {}
    if not isinstance(environment, Mapping):
        raise VehicleConfigError("environment: expected a mapping")
    air_density = _as_float(
        environment.get("air_density_kg_m3", 1.225),
        "environment.air_density_kg_m3",
        positive=True,
    )
    ambient_temp = _as_float(
        environment.get("ambient_temp_C", 25.0), "environment.ambient_temp_C"
    )
    wind = environment.get("wind_ned_m_s")
    wind_vector = np.zeros(3) if wind is None else _as_vector3(wind, "environment.wind_ned_m_s")

    ground = document.get("ground") or {}
    if not isinstance(ground, Mapping):
        raise VehicleConfigError("ground: expected a mapping")
    ground_enabled = _as_bool(ground.get("enabled", True), "ground.enabled")
    ground_z = _as_float(ground.get("z_ned_m", 0.0), "ground.z_ned_m")

    fmu_block = document.get("fmu") or {}
    if not isinstance(fmu_block, Mapping):
        raise VehicleConfigError("fmu: expected a mapping")
    torque_convention = fmu_block.get("torque_convention", TORQUE_CONVENTIONS[0])
    if torque_convention not in TORQUE_CONVENTIONS:
        raise VehicleConfigError(
            f"fmu.torque_convention: expected one of {TORQUE_CONVENTIONS}, "
            f"got {torque_convention!r}"
        )
    negate_reaction_torque = _as_bool(
        fmu_block.get("negate_reaction_torque", False), "fmu.negate_reaction_torque"
    )
    v_axial_sign = fmu_block.get("v_axial_sign", V_AXIAL_SIGNS[0])
    if v_axial_sign not in V_AXIAL_SIGNS:
        raise VehicleConfigError(
            f"fmu.v_axial_sign: expected one of {V_AXIAL_SIGNS}, got {v_axial_sign!r}"
        )
    inplane_sign = fmu_block.get("inplane_sign", INPLANE_SIGNS[0])
    if inplane_sign not in INPLANE_SIGNS:
        raise VehicleConfigError(
            f"fmu.inplane_sign: expected one of {INPLANE_SIGNS}, got {inplane_sign!r}"
        )

    raw_rotors = document.get("rotors")
    if not isinstance(raw_rotors, Sequence) or isinstance(raw_rotors, (str, bytes)):
        raise VehicleConfigError("rotors: required top-level 'rotors' list is missing")
    if len(raw_rotors) == 0:
        raise VehicleConfigError("rotors: at least one rotor is required")

    rotors = [_parse_rotor(entry, i) for i, entry in enumerate(raw_rotors)]
    _validate_bijection(rotors)
    rotors.sort(key=lambda r: r.rotor_index)

    return VehicleConfig(
        mass_kg=mass,
        inertia_kg_m2=inertia,
        inverse_inertia=np.linalg.inv(inertia),
        drag_area_m2=drag_area,
        wind_ned_m_s=wind_vector,
        air_density_kg_m3=air_density,
        ambient_temp_C=ambient_temp,
        rotors=tuple(rotors),
        torque_convention=torque_convention,
        negate_reaction_torque=negate_reaction_torque,
        v_axial_sign=v_axial_sign,
        inplane_sign=inplane_sign,
        ground_enabled=ground_enabled,
        ground_z_ned_m=ground_z,
        name=vehicle.get("name"),
        wing=_parse_wing(document.get("wing")),
        control_surfaces=_parse_control_surfaces(document.get("control_surfaces")),
    )


def _validate_bijection(rotors: Sequence[RotorConfig]) -> None:
    """``rotor_index`` must be exactly ``0..N-1`` and ``servo_channel`` unique."""
    indices = [r.rotor_index for r in rotors]
    expected = set(range(len(rotors)))
    if set(indices) != expected or len(indices) != len(set(indices)):
        raise VehicleConfigError(
            "rotors: rotor_index must cover 0.."
            f"{len(rotors) - 1} exactly once (the FMU's rotor array is a flat "
            f"0..N-1 index, spec decision 1); got {sorted(indices)}"
        )
    channels = [r.servo_channel for r in rotors]
    if len(channels) != len(set(channels)):
        duplicates = sorted({c for c in channels if channels.count(c) > 1})
        raise VehicleConfigError(
            f"rotors: servo_channel must be unique — the servo_channel -> rotor_index "
            f"map is bijective (spec decision 12); duplicated channels {duplicates}"
        )


def load_vehicle_config(path: str | Path) -> VehicleConfig:
    """Read and validate a vehicle YAML file."""
    text = Path(path).read_text(encoding="utf-8")
    try:
        document = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise VehicleConfigError(f"{path}: not valid YAML — {exc}") from exc
    try:
        return parse_vehicle_config(document)
    except VehicleConfigError as exc:
        raise VehicleConfigError(f"{path}: {exc}") from exc
