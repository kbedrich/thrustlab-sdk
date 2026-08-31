from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.component_specs_response_spec_json import ComponentSpecsResponseSpecJson


T = TypeVar("T", bound="ComponentSpecsResponse")


@_attrs_define
class ComponentSpecsResponse:
    """The Turnstile-leased datasheet readout (spec gating, 2026-08-30).

    ``spec_json`` is the DATASHEET projection (``_CATALOG_DATASHEET_KEYS``) for
    a catalog motor/battery, the headline projection for other catalog types,
    and the raw spec for the caller's own custom row. Never carries a catalog
    row's ``inertia`` / ``L`` / battery resistances — those are absent from
    every allowlist this response can be built from.

        Attributes:
            id (str):
            spec_json (ComponentSpecsResponseSpecJson):
            type_ (str):
            object_ (str | Unset):  Default: 'component_specs'.
    """

    id: str
    spec_json: ComponentSpecsResponseSpecJson
    type_: str
    object_: str | Unset = "component_specs"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        spec_json = self.spec_json.to_dict()

        type_ = self.type_

        object_ = self.object_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "spec_json": spec_json,
                "type": type_,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.component_specs_response_spec_json import ComponentSpecsResponseSpecJson

        d = dict(src_dict)
        id = d.pop("id")

        spec_json = ComponentSpecsResponseSpecJson.from_dict(d.pop("spec_json"))

        type_ = d.pop("type")

        object_ = d.pop("object", UNSET)

        component_specs_response = cls(
            id=id,
            spec_json=spec_json,
            type_=type_,
            object_=object_,
        )

        component_specs_response.additional_properties = d
        return component_specs_response

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
