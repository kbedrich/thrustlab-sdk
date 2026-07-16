from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from thrustlab._models.component_create_body_spec_json import ComponentCreateBodySpecJson


T = TypeVar("T", bound="ComponentCreateBody")


@_attrs_define
class ComponentCreateBody:
    """
    Attributes:
        name (str):
        spec_json (ComponentCreateBodySpecJson):
        type_ (str):
    """

    name: str
    spec_json: ComponentCreateBodySpecJson
    type_: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        spec_json = self.spec_json.to_dict()

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "spec_json": spec_json,
                "type": type_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.component_create_body_spec_json import ComponentCreateBodySpecJson

        d = dict(src_dict)
        name = d.pop("name")

        spec_json = ComponentCreateBodySpecJson.from_dict(d.pop("spec_json"))

        type_ = d.pop("type")

        component_create_body = cls(
            name=name,
            spec_json=spec_json,
            type_=type_,
        )

        component_create_body.additional_properties = d
        return component_create_body

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
