from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.airfoil_breakpoint import AirfoilBreakpoint
    from thrustlab._models.spline_data import SplineData


T = TypeVar("T", bound="GenerateGeometryRequest")


@_attrs_define
class GenerateGeometryRequest:
    """
    Attributes:
        chord_spline (SplineData):
        diameter (float): Diameter in inches
        pitch (float): Pitch in inches
        thickness_spline (SplineData):
        airfoil (str | Unset):  Default: 'naca4412'.
        airfoil_layout (list[AirfoilBreakpoint] | None | Unset):
        num_blades (int | Unset):  Default: 2.
        sweep (list[float] | None | Unset):
        thickness_scale (float | Unset):  Default: 1.0.
        twist_spline (None | SplineData | Unset):
    """

    chord_spline: SplineData
    diameter: float
    pitch: float
    thickness_spline: SplineData
    airfoil: str | Unset = "naca4412"
    airfoil_layout: list[AirfoilBreakpoint] | None | Unset = UNSET
    num_blades: int | Unset = 2
    sweep: list[float] | None | Unset = UNSET
    thickness_scale: float | Unset = 1.0
    twist_spline: None | SplineData | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.spline_data import SplineData

        chord_spline = self.chord_spline.to_dict()

        diameter = self.diameter

        pitch = self.pitch

        thickness_spline = self.thickness_spline.to_dict()

        airfoil = self.airfoil

        airfoil_layout: list[dict[str, Any]] | None | Unset
        if isinstance(self.airfoil_layout, Unset):
            airfoil_layout = UNSET
        elif isinstance(self.airfoil_layout, list):
            airfoil_layout = []
            for airfoil_layout_type_0_item_data in self.airfoil_layout:
                airfoil_layout_type_0_item = airfoil_layout_type_0_item_data.to_dict()
                airfoil_layout.append(airfoil_layout_type_0_item)

        else:
            airfoil_layout = self.airfoil_layout

        num_blades = self.num_blades

        sweep: list[float] | None | Unset
        if isinstance(self.sweep, Unset):
            sweep = UNSET
        elif isinstance(self.sweep, list):
            sweep = self.sweep

        else:
            sweep = self.sweep

        thickness_scale = self.thickness_scale

        twist_spline: dict[str, Any] | None | Unset
        if isinstance(self.twist_spline, Unset):
            twist_spline = UNSET
        elif isinstance(self.twist_spline, SplineData):
            twist_spline = self.twist_spline.to_dict()
        else:
            twist_spline = self.twist_spline

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "chord_spline": chord_spline,
                "diameter": diameter,
                "pitch": pitch,
                "thickness_spline": thickness_spline,
            }
        )
        if airfoil is not UNSET:
            field_dict["airfoil"] = airfoil
        if airfoil_layout is not UNSET:
            field_dict["airfoil_layout"] = airfoil_layout
        if num_blades is not UNSET:
            field_dict["num_blades"] = num_blades
        if sweep is not UNSET:
            field_dict["sweep"] = sweep
        if thickness_scale is not UNSET:
            field_dict["thickness_scale"] = thickness_scale
        if twist_spline is not UNSET:
            field_dict["twist_spline"] = twist_spline

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.airfoil_breakpoint import AirfoilBreakpoint
        from thrustlab._models.spline_data import SplineData

        d = dict(src_dict)
        chord_spline = SplineData.from_dict(d.pop("chord_spline"))

        diameter = d.pop("diameter")

        pitch = d.pop("pitch")

        thickness_spline = SplineData.from_dict(d.pop("thickness_spline"))

        airfoil = d.pop("airfoil", UNSET)

        def _parse_airfoil_layout(data: object) -> list[AirfoilBreakpoint] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                airfoil_layout_type_0 = []
                _airfoil_layout_type_0 = data
                for airfoil_layout_type_0_item_data in _airfoil_layout_type_0:
                    airfoil_layout_type_0_item = AirfoilBreakpoint.from_dict(airfoil_layout_type_0_item_data)

                    airfoil_layout_type_0.append(airfoil_layout_type_0_item)

                return airfoil_layout_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[AirfoilBreakpoint] | None | Unset, data)

        airfoil_layout = _parse_airfoil_layout(d.pop("airfoil_layout", UNSET))

        num_blades = d.pop("num_blades", UNSET)

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

        thickness_scale = d.pop("thickness_scale", UNSET)

        def _parse_twist_spline(data: object) -> None | SplineData | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                twist_spline_type_0 = SplineData.from_dict(data)

                return twist_spline_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SplineData | Unset, data)

        twist_spline = _parse_twist_spline(d.pop("twist_spline", UNSET))

        generate_geometry_request = cls(
            chord_spline=chord_spline,
            diameter=diameter,
            pitch=pitch,
            thickness_spline=thickness_spline,
            airfoil=airfoil,
            airfoil_layout=airfoil_layout,
            num_blades=num_blades,
            sweep=sweep,
            thickness_scale=thickness_scale,
            twist_spline=twist_spline,
        )

        return generate_geometry_request
