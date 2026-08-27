from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.design_request_target_mode import DesignRequestTargetMode
from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.airfoil_breakpoint import AirfoilBreakpoint


T = TypeVar("T", bound="DesignRequest")


@_attrs_define
class DesignRequest:
    """Generate an optimal MIL starting blade from design targets.

    Strict (``extra="forbid"``) with numeric bounds on every field. The fields are the Generate-form inputs: blade
    count, diameter
    (-> tip radius), hub radius, design RPM (-> Omega), design airspeed (``0`` =
    static — the kernel is static-valid), a thrust *or* power target, and the
    per-station airfoil layout. The server computes the optimum design-Cl
    distribution itself (the constant Cl that maximizes blade efficiency). There
    are NO polar coefficients (hard contract) — the geometry + Re/M
    determine the section physics via NeuralFoil.

        Attributes:
            design_rpm (float): Design RPM (-> Omega)
            diameter (float): Diameter in inches (-> tip radius R)
            hub_radius (float): Hub radius as a fraction of the tip radius (0..1)
            target_mode (DesignRequestTargetMode): Drive to a thrust OR power target
            target_value (float): Thrust (gf) or power (W) target — unit swaps with target_mode
            air_density (float | Unset): Air density kg/m^3 Default: 1.225.
            airfoil (str | Unset):  Default: 'naca4412'.
            airfoil_layout (list[AirfoilBreakpoint] | None | Unset): Per-station airfoil breakpoints. Only the rootmost
                entry is used — a MIL design flies one section for the whole blade.
            airspeed (float | Unset): Design airspeed m/s; 0 = static Default: 0.0.
            num_blades (int | Unset): Blade count Default: 2.
            section_airfoils (list[list[list[float]]] | Unset): Optional per-station Kulfan CST weight pairs [[lower_w,
                upper_w], ...]. Prefer 'airfoil_layout' — that is what the picker emits.
    """

    design_rpm: float
    diameter: float
    hub_radius: float
    target_mode: DesignRequestTargetMode
    target_value: float
    air_density: float | Unset = 1.225
    airfoil: str | Unset = "naca4412"
    airfoil_layout: list[AirfoilBreakpoint] | None | Unset = UNSET
    airspeed: float | Unset = 0.0
    num_blades: int | Unset = 2
    section_airfoils: list[list[list[float]]] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        design_rpm = self.design_rpm

        diameter = self.diameter

        hub_radius = self.hub_radius

        target_mode = self.target_mode.value

        target_value = self.target_value

        air_density = self.air_density

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

        airspeed = self.airspeed

        num_blades = self.num_blades

        section_airfoils: list[list[list[float]]] | Unset = UNSET
        if not isinstance(self.section_airfoils, Unset):
            section_airfoils = []
            for section_airfoils_item_data in self.section_airfoils:
                section_airfoils_item = []
                for section_airfoils_item_item_data in section_airfoils_item_data:
                    section_airfoils_item_item = section_airfoils_item_item_data

                    section_airfoils_item.append(section_airfoils_item_item)

                section_airfoils.append(section_airfoils_item)

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "design_rpm": design_rpm,
                "diameter": diameter,
                "hub_radius": hub_radius,
                "target_mode": target_mode,
                "target_value": target_value,
            }
        )
        if air_density is not UNSET:
            field_dict["air_density"] = air_density
        if airfoil is not UNSET:
            field_dict["airfoil"] = airfoil
        if airfoil_layout is not UNSET:
            field_dict["airfoil_layout"] = airfoil_layout
        if airspeed is not UNSET:
            field_dict["airspeed"] = airspeed
        if num_blades is not UNSET:
            field_dict["num_blades"] = num_blades
        if section_airfoils is not UNSET:
            field_dict["section_airfoils"] = section_airfoils

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.airfoil_breakpoint import AirfoilBreakpoint

        d = dict(src_dict)
        design_rpm = d.pop("design_rpm")

        diameter = d.pop("diameter")

        hub_radius = d.pop("hub_radius")

        target_mode = DesignRequestTargetMode(d.pop("target_mode"))

        target_value = d.pop("target_value")

        air_density = d.pop("air_density", UNSET)

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

        airspeed = d.pop("airspeed", UNSET)

        num_blades = d.pop("num_blades", UNSET)

        _section_airfoils = d.pop("section_airfoils", UNSET)
        section_airfoils: list[list[list[float]]] | Unset = UNSET
        if _section_airfoils is not UNSET:
            section_airfoils = []
            for section_airfoils_item_data in _section_airfoils:
                section_airfoils_item = []
                _section_airfoils_item = section_airfoils_item_data
                for section_airfoils_item_item_data in _section_airfoils_item:
                    section_airfoils_item_item = cast(list[float], section_airfoils_item_item_data)

                    section_airfoils_item.append(section_airfoils_item_item)

                section_airfoils.append(section_airfoils_item)

        design_request = cls(
            design_rpm=design_rpm,
            diameter=diameter,
            hub_radius=hub_radius,
            target_mode=target_mode,
            target_value=target_value,
            air_density=air_density,
            airfoil=airfoil,
            airfoil_layout=airfoil_layout,
            airspeed=airspeed,
            num_blades=num_blades,
            section_airfoils=section_airfoils,
        )

        return design_request
