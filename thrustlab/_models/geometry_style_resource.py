from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="GeometryStyleResource")


@_attrs_define
class GeometryStyleResource:
    """Identity/metadata-only view of a curated catalog geometry style.

    The calibrated geometry arrays — ``thickness_spline``, ``thickness_scale``,
    ``chord_spline_coefficients``, ``chord_spline_reference`` — are the curated
    trade-secret geometry the anti-scrape moat protects, so they are NOT
    serialized here. The catalog stays browsable by IDENTITY (id/manufacturer/
    label/display_name/description/airfoil/source) so the editor can let a user
    PICK a style by name; the calibrated numbers are server-side only (read by
    ``/v1/geometry/generate`` to produce the user's OWN-design geometry output,
    never returned raw). ``from_attributes`` ignores the model's extra calibrated
    columns — they simply do not appear in the response.

        Attributes:
            airfoil (str):
            description (str):
            display_name (str):
            id (str):
            label (str):
            manufacturer (str):
            source (str):
            object_ (str | Unset):  Default: 'geometry_style'.
    """

    airfoil: str
    description: str
    display_name: str
    id: str
    label: str
    manufacturer: str
    source: str
    object_: str | Unset = "geometry_style"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        airfoil = self.airfoil

        description = self.description

        display_name = self.display_name

        id = self.id

        label = self.label

        manufacturer = self.manufacturer

        source = self.source

        object_ = self.object_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "airfoil": airfoil,
                "description": description,
                "display_name": display_name,
                "id": id,
                "label": label,
                "manufacturer": manufacturer,
                "source": source,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        airfoil = d.pop("airfoil")

        description = d.pop("description")

        display_name = d.pop("display_name")

        id = d.pop("id")

        label = d.pop("label")

        manufacturer = d.pop("manufacturer")

        source = d.pop("source")

        object_ = d.pop("object", UNSET)

        geometry_style_resource = cls(
            airfoil=airfoil,
            description=description,
            display_name=display_name,
            id=id,
            label=label,
            manufacturer=manufacturer,
            source=source,
            object_=object_,
        )

        geometry_style_resource.additional_properties = d
        return geometry_style_resource

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
