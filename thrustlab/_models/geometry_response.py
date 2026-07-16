from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="GeometryResponse")


@_attrs_define
class GeometryResponse:
    """
    Attributes:
        chord (list[float]):
        hub_radius (float):
        radius (list[float]):
        section_airfoils (list[Any]):
        thickness (list[float]):
        twist (list[float]):
        object_ (str | Unset):  Default: 'geometry'.
        section_coords (list[Any] | None | Unset):
        x_le_over_r (list[Any] | None | Unset):
    """

    chord: list[float]
    hub_radius: float
    radius: list[float]
    section_airfoils: list[Any]
    thickness: list[float]
    twist: list[float]
    object_: str | Unset = "geometry"
    section_coords: list[Any] | None | Unset = UNSET
    x_le_over_r: list[Any] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chord = self.chord

        hub_radius = self.hub_radius

        radius = self.radius

        section_airfoils = self.section_airfoils

        thickness = self.thickness

        twist = self.twist

        object_ = self.object_

        section_coords: list[Any] | None | Unset
        if isinstance(self.section_coords, Unset):
            section_coords = UNSET
        elif isinstance(self.section_coords, list):
            section_coords = self.section_coords

        else:
            section_coords = self.section_coords

        x_le_over_r: list[Any] | None | Unset
        if isinstance(self.x_le_over_r, Unset):
            x_le_over_r = UNSET
        elif isinstance(self.x_le_over_r, list):
            x_le_over_r = self.x_le_over_r

        else:
            x_le_over_r = self.x_le_over_r

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "chord": chord,
                "hub_radius": hub_radius,
                "radius": radius,
                "section_airfoils": section_airfoils,
                "thickness": thickness,
                "twist": twist,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_
        if section_coords is not UNSET:
            field_dict["section_coords"] = section_coords
        if x_le_over_r is not UNSET:
            field_dict["x_le_over_R"] = x_le_over_r

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        chord = cast(list[float], d.pop("chord"))

        hub_radius = d.pop("hub_radius")

        radius = cast(list[float], d.pop("radius"))

        section_airfoils = cast(list[Any], d.pop("section_airfoils"))

        thickness = cast(list[float], d.pop("thickness"))

        twist = cast(list[float], d.pop("twist"))

        object_ = d.pop("object", UNSET)

        def _parse_section_coords(data: object) -> list[Any] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                section_coords_type_0 = cast(list[Any], data)

                return section_coords_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[Any] | None | Unset, data)

        section_coords = _parse_section_coords(d.pop("section_coords", UNSET))

        def _parse_x_le_over_r(data: object) -> list[Any] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                x_le_over_r_type_0 = cast(list[Any], data)

                return x_le_over_r_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[Any] | None | Unset, data)

        x_le_over_r = _parse_x_le_over_r(d.pop("x_le_over_R", UNSET))

        geometry_response = cls(
            chord=chord,
            hub_radius=hub_radius,
            radius=radius,
            section_airfoils=section_airfoils,
            thickness=thickness,
            twist=twist,
            object_=object_,
            section_coords=section_coords,
            x_le_over_r=x_le_over_r,
        )

        geometry_response.additional_properties = d
        return geometry_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
