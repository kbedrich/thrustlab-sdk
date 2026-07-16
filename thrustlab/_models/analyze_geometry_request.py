from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.analyze_geometry_request_mode import AnalyzeGeometryRequestMode
from thrustlab._models.analyze_geometry_request_target_type_type_0 import AnalyzeGeometryRequestTargetTypeType0
from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="AnalyzeGeometryRequest")


@_attrs_define
class AnalyzeGeometryRequest:
    """Aero-only operating-point analysis request (point / sweep / solve-to-target).

    Mirrors ``CalibrateRequest``'s geometry block + ``extra="forbid"`` so an
    unknown field (e.g. a stray ``motor_id``) is rejected at the boundary — the
    schema itself is the aero-only guard. Every scalar carries numeric
    bounds and the sweep ``j_steps`` is capped at 200.

        Attributes:
            chord (list[float]):
            diameter (float): Diameter in inches
            radius (list[float]):
            twist (list[float]): Twist in degrees
            air_density (float | Unset): Air density kg/m^3 Default: 1.225.
            airfoil (str | Unset):  Default: 'naca4412'.
            airspeed (float | Unset): Freestream m/s Default: 0.0.
            hub_radius (float | None | Unset):
            j_from (float | None | Unset):
            j_steps (int | None | Unset): Sweep point count (DoS bound — each step is a full solve)
            j_to (float | None | Unset):
            mode (AnalyzeGeometryRequestMode | Unset):  Default: AnalyzeGeometryRequestMode.POINT.
            num_blades (int | Unset):  Default: 2.
            rpm (float | Unset):  Default: 5000.0.
            section_airfoils (list[Any] | Unset): [[lower_w, upper_w], ...] Kulfan pairs per station
            sweep (list[float] | None | Unset):
            target_type (AnalyzeGeometryRequestTargetTypeType0 | None | Unset):
            target_value (float | None | Unset):
            thickness (list[float] | None | Unset):
    """

    chord: list[float]
    diameter: float
    radius: list[float]
    twist: list[float]
    air_density: float | Unset = 1.225
    airfoil: str | Unset = "naca4412"
    airspeed: float | Unset = 0.0
    hub_radius: float | None | Unset = UNSET
    j_from: float | None | Unset = UNSET
    j_steps: int | None | Unset = UNSET
    j_to: float | None | Unset = UNSET
    mode: AnalyzeGeometryRequestMode | Unset = AnalyzeGeometryRequestMode.POINT
    num_blades: int | Unset = 2
    rpm: float | Unset = 5000.0
    section_airfoils: list[Any] | Unset = UNSET
    sweep: list[float] | None | Unset = UNSET
    target_type: AnalyzeGeometryRequestTargetTypeType0 | None | Unset = UNSET
    target_value: float | None | Unset = UNSET
    thickness: list[float] | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        chord = self.chord

        diameter = self.diameter

        radius = self.radius

        twist = self.twist

        air_density = self.air_density

        airfoil = self.airfoil

        airspeed = self.airspeed

        hub_radius: float | None | Unset
        if isinstance(self.hub_radius, Unset):
            hub_radius = UNSET
        else:
            hub_radius = self.hub_radius

        j_from: float | None | Unset
        if isinstance(self.j_from, Unset):
            j_from = UNSET
        else:
            j_from = self.j_from

        j_steps: int | None | Unset
        if isinstance(self.j_steps, Unset):
            j_steps = UNSET
        else:
            j_steps = self.j_steps

        j_to: float | None | Unset
        if isinstance(self.j_to, Unset):
            j_to = UNSET
        else:
            j_to = self.j_to

        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode.value

        num_blades = self.num_blades

        rpm = self.rpm

        section_airfoils: list[Any] | Unset = UNSET
        if not isinstance(self.section_airfoils, Unset):
            section_airfoils = self.section_airfoils

        sweep: list[float] | None | Unset
        if isinstance(self.sweep, Unset):
            sweep = UNSET
        elif isinstance(self.sweep, list):
            sweep = self.sweep

        else:
            sweep = self.sweep

        target_type: None | str | Unset
        if isinstance(self.target_type, Unset):
            target_type = UNSET
        elif isinstance(self.target_type, AnalyzeGeometryRequestTargetTypeType0):
            target_type = self.target_type.value
        else:
            target_type = self.target_type

        target_value: float | None | Unset
        if isinstance(self.target_value, Unset):
            target_value = UNSET
        else:
            target_value = self.target_value

        thickness: list[float] | None | Unset
        if isinstance(self.thickness, Unset):
            thickness = UNSET
        elif isinstance(self.thickness, list):
            thickness = self.thickness

        else:
            thickness = self.thickness

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "chord": chord,
                "diameter": diameter,
                "radius": radius,
                "twist": twist,
            }
        )
        if air_density is not UNSET:
            field_dict["air_density"] = air_density
        if airfoil is not UNSET:
            field_dict["airfoil"] = airfoil
        if airspeed is not UNSET:
            field_dict["airspeed"] = airspeed
        if hub_radius is not UNSET:
            field_dict["hub_radius"] = hub_radius
        if j_from is not UNSET:
            field_dict["j_from"] = j_from
        if j_steps is not UNSET:
            field_dict["j_steps"] = j_steps
        if j_to is not UNSET:
            field_dict["j_to"] = j_to
        if mode is not UNSET:
            field_dict["mode"] = mode
        if num_blades is not UNSET:
            field_dict["num_blades"] = num_blades
        if rpm is not UNSET:
            field_dict["rpm"] = rpm
        if section_airfoils is not UNSET:
            field_dict["section_airfoils"] = section_airfoils
        if sweep is not UNSET:
            field_dict["sweep"] = sweep
        if target_type is not UNSET:
            field_dict["target_type"] = target_type
        if target_value is not UNSET:
            field_dict["target_value"] = target_value
        if thickness is not UNSET:
            field_dict["thickness"] = thickness

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        chord = cast(list[float], d.pop("chord"))

        diameter = d.pop("diameter")

        radius = cast(list[float], d.pop("radius"))

        twist = cast(list[float], d.pop("twist"))

        air_density = d.pop("air_density", UNSET)

        airfoil = d.pop("airfoil", UNSET)

        airspeed = d.pop("airspeed", UNSET)

        def _parse_hub_radius(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        hub_radius = _parse_hub_radius(d.pop("hub_radius", UNSET))

        def _parse_j_from(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        j_from = _parse_j_from(d.pop("j_from", UNSET))

        def _parse_j_steps(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        j_steps = _parse_j_steps(d.pop("j_steps", UNSET))

        def _parse_j_to(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        j_to = _parse_j_to(d.pop("j_to", UNSET))

        _mode = d.pop("mode", UNSET)
        mode: AnalyzeGeometryRequestMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = AnalyzeGeometryRequestMode(_mode)

        num_blades = d.pop("num_blades", UNSET)

        rpm = d.pop("rpm", UNSET)

        section_airfoils = cast(list[Any], d.pop("section_airfoils", UNSET))

        def _parse_sweep(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                sweep_type_0 = cast(list[float], data)

                return sweep_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        sweep = _parse_sweep(d.pop("sweep", UNSET))

        def _parse_target_type(data: object) -> AnalyzeGeometryRequestTargetTypeType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                target_type_type_0 = AnalyzeGeometryRequestTargetTypeType0(data)

                return target_type_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(AnalyzeGeometryRequestTargetTypeType0 | None | Unset, data)

        target_type = _parse_target_type(d.pop("target_type", UNSET))

        def _parse_target_value(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        target_value = _parse_target_value(d.pop("target_value", UNSET))

        def _parse_thickness(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                thickness_type_0 = cast(list[float], data)

                return thickness_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        thickness = _parse_thickness(d.pop("thickness", UNSET))

        analyze_geometry_request = cls(
            chord=chord,
            diameter=diameter,
            radius=radius,
            twist=twist,
            air_density=air_density,
            airfoil=airfoil,
            airspeed=airspeed,
            hub_radius=hub_radius,
            j_from=j_from,
            j_steps=j_steps,
            j_to=j_to,
            mode=mode,
            num_blades=num_blades,
            rpm=rpm,
            section_airfoils=section_airfoils,
            sweep=sweep,
            target_type=target_type,
            target_value=target_value,
            thickness=thickness,
        )

        return analyze_geometry_request
