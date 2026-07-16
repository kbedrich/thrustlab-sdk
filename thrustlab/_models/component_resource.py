from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.component_resource_spec_json import ComponentResourceSpecJson


T = TypeVar("T", bound="ComponentResource")


@_attrs_define
class ComponentResource:
    """
    Attributes:
        base_component_id (None | UUID):
        created_at (datetime.datetime):
        id (str):
        name (str):
        source (str):
        spec_json (ComponentResourceSpecJson):
        type_ (str):
        updated_at (datetime.datetime):
        user_id (None | UUID):
        visibility (str):
        object_ (str | Unset):  Default: 'component'.
    """

    base_component_id: None | UUID
    created_at: datetime.datetime
    id: str
    name: str
    source: str
    spec_json: ComponentResourceSpecJson
    type_: str
    updated_at: datetime.datetime
    user_id: None | UUID
    visibility: str
    object_: str | Unset = "component"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        base_component_id: None | str
        if isinstance(self.base_component_id, UUID):
            base_component_id = str(self.base_component_id)
        else:
            base_component_id = self.base_component_id

        created_at = self.created_at.isoformat()

        id = self.id

        name = self.name

        source = self.source

        spec_json = self.spec_json.to_dict()

        type_ = self.type_

        updated_at = self.updated_at.isoformat()

        user_id: None | str
        if isinstance(self.user_id, UUID):
            user_id = str(self.user_id)
        else:
            user_id = self.user_id

        visibility = self.visibility

        object_ = self.object_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "base_component_id": base_component_id,
                "created_at": created_at,
                "id": id,
                "name": name,
                "source": source,
                "spec_json": spec_json,
                "type": type_,
                "updated_at": updated_at,
                "user_id": user_id,
                "visibility": visibility,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.component_resource_spec_json import ComponentResourceSpecJson

        d = dict(src_dict)

        def _parse_base_component_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                base_component_id_type_0 = UUID(data)

                return base_component_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        base_component_id = _parse_base_component_id(d.pop("base_component_id"))

        created_at = isoparse(d.pop("created_at"))

        id = d.pop("id")

        name = d.pop("name")

        source = d.pop("source")

        spec_json = ComponentResourceSpecJson.from_dict(d.pop("spec_json"))

        type_ = d.pop("type")

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_user_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                user_id_type_0 = UUID(data)

                return user_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        user_id = _parse_user_id(d.pop("user_id"))

        visibility = d.pop("visibility")

        object_ = d.pop("object", UNSET)

        component_resource = cls(
            base_component_id=base_component_id,
            created_at=created_at,
            id=id,
            name=name,
            source=source,
            spec_json=spec_json,
            type_=type_,
            updated_at=updated_at,
            user_id=user_id,
            visibility=visibility,
            object_=object_,
        )

        component_resource.additional_properties = d
        return component_resource

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
