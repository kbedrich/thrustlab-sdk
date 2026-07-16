from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="ComponentWriteWarning")


@_attrs_define
class ComponentWriteWarning:
    """Non-blocking plausibility warning attached to a create/patch response.

    2026-07-16 R audit Phase C: the write succeeded — a warning never blocks —
    but a spec value looks physically implausible (e.g. spec_json.R far outside
    the R(kv, weight) band, the signature of a mOhm/Ohm slip or a per-phase
    value entered where phase-to-phase is expected).

        Attributes:
            code (str):
            message (str):
            param (str):
            object_ (str | Unset):  Default: 'warning'.
    """

    code: str
    message: str
    param: str
    object_: str | Unset = "warning"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        code = self.code

        message = self.message

        param = self.param

        object_ = self.object_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "code": code,
                "message": message,
                "param": param,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        code = d.pop("code")

        message = d.pop("message")

        param = d.pop("param")

        object_ = d.pop("object", UNSET)

        component_write_warning = cls(
            code=code,
            message=message,
            param=param,
            object_=object_,
        )

        component_write_warning.additional_properties = d
        return component_write_warning

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
