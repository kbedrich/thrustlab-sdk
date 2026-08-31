from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="FmuExportAcceptedResponse")


@_attrs_define
class FmuExportAcceptedResponse:
    """202 body — the FMU export job was queued.

    Attributes:
        id (str):
        object_ (str | Unset):  Default: 'fmu_export'.
        status (str | Unset):  Default: 'queued'.
    """

    id: str
    object_: str | Unset = "fmu_export"
    status: str | Unset = "queued"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        object_ = self.object_

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        object_ = d.pop("object", UNSET)

        status = d.pop("status", UNSET)

        fmu_export_accepted_response = cls(
            id=id,
            object_=object_,
            status=status,
        )

        fmu_export_accepted_response.additional_properties = d
        return fmu_export_accepted_response

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
