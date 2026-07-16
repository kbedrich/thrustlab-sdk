from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="StarredComponentCreateBody")


@_attrs_define
class StarredComponentCreateBody:
    """Accepts either prefixed (``proj_<ksuid>`` / ``comp_<ksuid>``) or raw
    UUID strings — resolution happens in the handler so the same body shape
    works during the reference-app transition.

        Attributes:
            component_id (str):
            component_type (str):
            project_id (str):
    """

    component_id: str
    component_type: str
    project_id: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        component_id = self.component_id

        component_type = self.component_type

        project_id = self.project_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "component_id": component_id,
                "component_type": component_type,
                "project_id": project_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        component_id = d.pop("component_id")

        component_type = d.pop("component_type")

        project_id = d.pop("project_id")

        starred_component_create_body = cls(
            component_id=component_id,
            component_type=component_type,
            project_id=project_id,
        )

        starred_component_create_body.additional_properties = d
        return starred_component_create_body

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
