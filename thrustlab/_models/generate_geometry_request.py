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
        chord_stations (list[float] | None | Unset): Chord per station, normalized c/R.
        hub_r_over_r (float | None | Unset): The blade's own hub as a fraction of tip radius. Absent => the legacy APC
            diameter regression.
        num_blades (int | Unset):  Default: 2.
        station_r_over_r (list[float] | None | Unset): Station r/R column — strictly increasing within (0, 1]. Its
            presence switches chord/twist/thickness/sweep from spline evaluation to radius interpolation.
        sweep (list[float] | None | Unset):
        sweep_stations (list[float] | None | Unset): Swept c/4 leading-edge locus per station, x_le/R.
        thickness_scale (float | Unset):  Default: 1.0.
        thickness_stations (list[float] | None | Unset): Thickness per station, t/c.
        twist_spline (None | SplineData | Unset):
        twist_stations (list[float] | None | Unset): Twist per station, degrees.
    """

    chord_spline: SplineData
    diameter: float
    pitch: float
    thickness_spline: SplineData
    airfoil: str | Unset = "naca4412"
    airfoil_layout: list[AirfoilBreakpoint] | None | Unset = UNSET
    chord_stations: list[float] | None | Unset = UNSET
    hub_r_over_r: float | None | Unset = UNSET
    num_blades: int | Unset = 2
    station_r_over_r: list[float] | None | Unset = UNSET
    sweep: list[float] | None | Unset = UNSET
    sweep_stations: list[float] | None | Unset = UNSET
    thickness_scale: float | Unset = 1.0
    thickness_stations: list[float] | None | Unset = UNSET
    twist_spline: None | SplineData | Unset = UNSET
    twist_stations: list[float] | None | Unset = UNSET

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

        chord_stations: list[float] | None | Unset
        if isinstance(self.chord_stations, Unset):
            chord_stations = UNSET
        elif isinstance(self.chord_stations, list):
            chord_stations = self.chord_stations

        else:
            chord_stations = self.chord_stations

        hub_r_over_r: float | None | Unset
        if isinstance(self.hub_r_over_r, Unset):
            hub_r_over_r = UNSET
        else:
            hub_r_over_r = self.hub_r_over_r

        num_blades = self.num_blades

        station_r_over_r: list[float] | None | Unset
        if isinstance(self.station_r_over_r, Unset):
            station_r_over_r = UNSET
        elif isinstance(self.station_r_over_r, list):
            station_r_over_r = self.station_r_over_r

        else:
            station_r_over_r = self.station_r_over_r

        sweep: list[float] | None | Unset
        if isinstance(self.sweep, Unset):
            sweep = UNSET
        elif isinstance(self.sweep, list):
            sweep = self.sweep

        else:
            sweep = self.sweep

        sweep_stations: list[float] | None | Unset
        if isinstance(self.sweep_stations, Unset):
            sweep_stations = UNSET
        elif isinstance(self.sweep_stations, list):
            sweep_stations = self.sweep_stations

        else:
            sweep_stations = self.sweep_stations

        thickness_scale = self.thickness_scale

        thickness_stations: list[float] | None | Unset
        if isinstance(self.thickness_stations, Unset):
            thickness_stations = UNSET
        elif isinstance(self.thickness_stations, list):
            thickness_stations = self.thickness_stations

        else:
            thickness_stations = self.thickness_stations

        twist_spline: dict[str, Any] | None | Unset
        if isinstance(self.twist_spline, Unset):
            twist_spline = UNSET
        elif isinstance(self.twist_spline, SplineData):
            twist_spline = self.twist_spline.to_dict()
        else:
            twist_spline = self.twist_spline

        twist_stations: list[float] | None | Unset
        if isinstance(self.twist_stations, Unset):
            twist_stations = UNSET
        elif isinstance(self.twist_stations, list):
            twist_stations = self.twist_stations

        else:
            twist_stations = self.twist_stations

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
        if chord_stations is not UNSET:
            field_dict["chord_stations"] = chord_stations
        if hub_r_over_r is not UNSET:
            field_dict["hub_r_over_R"] = hub_r_over_r
        if num_blades is not UNSET:
            field_dict["num_blades"] = num_blades
        if station_r_over_r is not UNSET:
            field_dict["station_r_over_R"] = station_r_over_r
        if sweep is not UNSET:
            field_dict["sweep"] = sweep
        if sweep_stations is not UNSET:
            field_dict["sweep_stations"] = sweep_stations
        if thickness_scale is not UNSET:
            field_dict["thickness_scale"] = thickness_scale
        if thickness_stations is not UNSET:
            field_dict["thickness_stations"] = thickness_stations
        if twist_spline is not UNSET:
            field_dict["twist_spline"] = twist_spline
        if twist_stations is not UNSET:
            field_dict["twist_stations"] = twist_stations

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

        def _parse_chord_stations(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                chord_stations_type_0 = cast(list[float], data)

                return chord_stations_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        chord_stations = _parse_chord_stations(d.pop("chord_stations", UNSET))

        def _parse_hub_r_over_r(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        hub_r_over_r = _parse_hub_r_over_r(d.pop("hub_r_over_R", UNSET))

        num_blades = d.pop("num_blades", UNSET)

        def _parse_station_r_over_r(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                station_r_over_r_type_0 = cast(list[float], data)

                return station_r_over_r_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        station_r_over_r = _parse_station_r_over_r(d.pop("station_r_over_R", UNSET))

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

        def _parse_sweep_stations(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                sweep_stations_type_0 = cast(list[float], data)

                return sweep_stations_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        sweep_stations = _parse_sweep_stations(d.pop("sweep_stations", UNSET))

        thickness_scale = d.pop("thickness_scale", UNSET)

        def _parse_thickness_stations(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                thickness_stations_type_0 = cast(list[float], data)

                return thickness_stations_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        thickness_stations = _parse_thickness_stations(d.pop("thickness_stations", UNSET))

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

        def _parse_twist_stations(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                twist_stations_type_0 = cast(list[float], data)

                return twist_stations_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        twist_stations = _parse_twist_stations(d.pop("twist_stations", UNSET))

        generate_geometry_request = cls(
            chord_spline=chord_spline,
            diameter=diameter,
            pitch=pitch,
            thickness_spline=thickness_spline,
            airfoil=airfoil,
            airfoil_layout=airfoil_layout,
            chord_stations=chord_stations,
            hub_r_over_r=hub_r_over_r,
            num_blades=num_blades,
            station_r_over_r=station_r_over_r,
            sweep=sweep,
            sweep_stations=sweep_stations,
            thickness_scale=thickness_scale,
            thickness_stations=thickness_stations,
            twist_spline=twist_spline,
            twist_stations=twist_stations,
        )

        return generate_geometry_request
