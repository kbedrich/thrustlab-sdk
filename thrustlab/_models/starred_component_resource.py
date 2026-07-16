from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="StarredComponentResource")


@_attrs_define
class StarredComponentResource:
    """
    Attributes:
        component_id (str):
        component_type (str):
        created_at (datetime.datetime):
        id (str):
        project_id (str):
        object_ (str | Unset):  Default: 'starred_component'.
    """

    component_id: str
    component_type: str
    created_at: datetime.datetime
    id: str
    project_id: str
    object_: str | Unset = "starred_component"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        component_id = self.component_id

        component_type = self.component_type

        created_at = self.created_at.isoformat()

        id = self.id

        project_id = self.project_id

        object_ = self.object_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "component_id": component_id,
                "component_type": component_type,
                "created_at": created_at,
                "id": id,
                "project_id": project_id,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        component_id = d.pop("component_id")

        component_type = d.pop("component_type")

        created_at = isoparse(d.pop("created_at"))

        id = d.pop("id")

        project_id = d.pop("project_id")

        object_ = d.pop("object", UNSET)

        starred_component_resource = cls(
            component_id=component_id,
            component_type=component_type,
            created_at=created_at,
            id=id,
            project_id=project_id,
            object_=object_,
        )

        starred_component_resource.additional_properties = d
        return starred_component_resource

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
