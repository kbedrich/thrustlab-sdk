from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.design_request_target_mode import DesignRequestTargetMode
from thrustlab._models.types import UNSET, Unset

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
            airspeed (float | Unset): Design airspeed m/s; 0 = static Default: 0.0.
            num_blades (int | Unset): Blade count (min 2) Default: 2.
            section_airfoils (list[Any] | Unset): [[lower_w, upper_w]...] Kulfan pairs from the picker
    """

    design_rpm: float
    diameter: float
    hub_radius: float
    target_mode: DesignRequestTargetMode
    target_value: float
    air_density: float | Unset = 1.225
    airfoil: str | Unset = "naca4412"
    airspeed: float | Unset = 0.0
    num_blades: int | Unset = 2
    section_airfoils: list[Any] | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        design_rpm = self.design_rpm

        diameter = self.diameter

        hub_radius = self.hub_radius

        target_mode = self.target_mode.value

        target_value = self.target_value

        air_density = self.air_density

        airfoil = self.airfoil

        airspeed = self.airspeed

        num_blades = self.num_blades

        section_airfoils: list[Any] | Unset = UNSET
        if not isinstance(self.section_airfoils, Unset):
            section_airfoils = self.section_airfoils

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
        if airspeed is not UNSET:
            field_dict["airspeed"] = airspeed
        if num_blades is not UNSET:
            field_dict["num_blades"] = num_blades
        if section_airfoils is not UNSET:
            field_dict["section_airfoils"] = section_airfoils

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        design_rpm = d.pop("design_rpm")

        diameter = d.pop("diameter")

        hub_radius = d.pop("hub_radius")

        target_mode = DesignRequestTargetMode(d.pop("target_mode"))

        target_value = d.pop("target_value")

        air_density = d.pop("air_density", UNSET)

        airfoil = d.pop("airfoil", UNSET)

        airspeed = d.pop("airspeed", UNSET)

        num_blades = d.pop("num_blades", UNSET)

        section_airfoils = cast(list[Any], d.pop("section_airfoils", UNSET))

        design_request = cls(
            design_rpm=design_rpm,
            diameter=diameter,
            hub_radius=hub_radius,
            target_mode=target_mode,
            target_value=target_value,
            air_density=air_density,
            airfoil=airfoil,
            airspeed=airspeed,
            num_blades=num_blades,
            section_airfoils=section_airfoils,
        )

        return design_request
