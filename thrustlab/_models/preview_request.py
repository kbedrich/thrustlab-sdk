from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="PreviewRequest")


@_attrs_define
class PreviewRequest:
    """
    Attributes:
        diameter (float): Diameter in inches
        geometry_style_id (str):
        pitch (float): Pitch in inches
        num_blades (int | Unset):  Default: 2.
    """

    diameter: float
    geometry_style_id: str
    pitch: float
    num_blades: int | Unset = 2
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        diameter = self.diameter

        geometry_style_id = self.geometry_style_id

        pitch = self.pitch

        num_blades = self.num_blades

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "diameter": diameter,
                "geometry_style_id": geometry_style_id,
                "pitch": pitch,
            }
        )
        if num_blades is not UNSET:
            field_dict["num_blades"] = num_blades

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        diameter = d.pop("diameter")

        geometry_style_id = d.pop("geometry_style_id")

        pitch = d.pop("pitch")

        num_blades = d.pop("num_blades", UNSET)

        preview_request = cls(
            diameter=diameter,
            geometry_style_id=geometry_style_id,
            pitch=pitch,
            num_blades=num_blades,
        )

        preview_request.additional_properties = d
        return preview_request

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
