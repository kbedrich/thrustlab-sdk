from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="ComponentIdsResponse")


@_attrs_define
class ComponentIdsResponse:
    """The Select-all id list.

    Returns EVERY component id matching the current search + filters in the
    requested ``sort_by``/``sort_order`` (the SAME primary ordering the paginated
    list uses), bounded by a documented hard cap. This sidesteps the cursor-keyset
    bug — the cursor keyset is ``(created_at, public_id)`` and so cannot honor a
    non-default ``sort_by``; a single sorted ``.limit(cap)`` query can. ``total``
    is the count returned (== matches when not truncated); ``truncated`` is true
    when the matching set exceeded the cap (the first ``cap`` ids, in sort order,
    are returned).

        Attributes:
            data (list[str]):
            total (int):
            truncated (bool):
            object_ (str | Unset):  Default: 'list'.
    """

    data: list[str]
    total: int
    truncated: bool
    object_: str | Unset = "list"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = self.data

        total = self.total

        truncated = self.truncated

        object_ = self.object_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "total": total,
                "truncated": truncated,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        data = cast(list[str], d.pop("data"))

        total = d.pop("total")

        truncated = d.pop("truncated")

        object_ = d.pop("object", UNSET)

        component_ids_response = cls(
            data=data,
            total=total,
            truncated=truncated,
            object_=object_,
        )

        component_ids_response.additional_properties = d
        return component_ids_response

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
