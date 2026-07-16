from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.component_patch_spec_json_type_0 import ComponentPatchSpecJsonType0


T = TypeVar("T", bound="ComponentPatch")


@_attrs_define
class ComponentPatch:
    """
    Attributes:
        name (None | str | Unset):
        spec_json (ComponentPatchSpecJsonType0 | None | Unset):
    """

    name: None | str | Unset = UNSET
    spec_json: ComponentPatchSpecJsonType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.component_patch_spec_json_type_0 import ComponentPatchSpecJsonType0

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        spec_json: dict[str, Any] | None | Unset
        if isinstance(self.spec_json, Unset):
            spec_json = UNSET
        elif isinstance(self.spec_json, ComponentPatchSpecJsonType0):
            spec_json = self.spec_json.to_dict()
        else:
            spec_json = self.spec_json

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if spec_json is not UNSET:
            field_dict["spec_json"] = spec_json

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.component_patch_spec_json_type_0 import ComponentPatchSpecJsonType0

        d = dict(src_dict)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_spec_json(data: object) -> ComponentPatchSpecJsonType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                spec_json_type_0 = ComponentPatchSpecJsonType0.from_dict(data)

                return spec_json_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ComponentPatchSpecJsonType0 | None | Unset, data)

        spec_json = _parse_spec_json(d.pop("spec_json", UNSET))

        component_patch = cls(
            name=name,
            spec_json=spec_json,
        )

        component_patch.additional_properties = d
        return component_patch

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
