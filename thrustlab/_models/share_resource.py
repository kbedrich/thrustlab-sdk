from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="ShareResource")


@_attrs_define
class ShareResource:
    """
    Attributes:
        share_token (str):
        share_url (str):
        object_ (str | Unset):  Default: 'simulation_share'.
    """

    share_token: str
    share_url: str
    object_: str | Unset = "simulation_share"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        share_token = self.share_token

        share_url = self.share_url

        object_ = self.object_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "share_token": share_token,
                "share_url": share_url,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        share_token = d.pop("share_token")

        share_url = d.pop("share_url")

        object_ = d.pop("object", UNSET)

        share_resource = cls(
            share_token=share_token,
            share_url=share_url,
            object_=object_,
        )

        share_resource.additional_properties = d
        return share_resource

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
