from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="GeometryPreviewResponse")


@_attrs_define
class GeometryPreviewResponse:
    """
    Attributes:
        chord (list[float]):
        hub_radius (float):
        radius (list[float]):
        section_airfoils (list[Any]):
        thickness (list[float]):
        twist (list[float]):
        object_ (str | Unset):  Default: 'geometry_preview'.
    """

    chord: list[float]
    hub_radius: float
    radius: list[float]
    section_airfoils: list[Any]
    thickness: list[float]
    twist: list[float]
    object_: str | Unset = "geometry_preview"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chord = self.chord

        hub_radius = self.hub_radius

        radius = self.radius

        section_airfoils = self.section_airfoils

        thickness = self.thickness

        twist = self.twist

        object_ = self.object_

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

        geometry_preview_response = cls(
            chord=chord,
            hub_radius=hub_radius,
            radius=radius,
            section_airfoils=section_airfoils,
            thickness=thickness,
            twist=twist,
            object_=object_,
        )

        geometry_preview_response.additional_properties = d
        return geometry_preview_response

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
