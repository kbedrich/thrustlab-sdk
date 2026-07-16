from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.credit_usage_related_resource_object import CreditUsageRelatedResourceObject

T = TypeVar("T", bound="CreditUsageRelatedResource")


@_attrs_define
class CreditUsageRelatedResource:
    """
    Attributes:
        id (str):
        object_ (CreditUsageRelatedResourceObject):
    """

    id: str
    object_: CreditUsageRelatedResourceObject
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        object_ = self.object_.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "object": object_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        object_ = CreditUsageRelatedResourceObject(d.pop("object"))

        credit_usage_related_resource = cls(
            id=id,
            object_=object_,
        )

        credit_usage_related_resource.additional_properties = d
        return credit_usage_related_resource

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
