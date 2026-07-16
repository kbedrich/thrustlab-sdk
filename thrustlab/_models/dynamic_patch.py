from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="DynamicPatch")


@_attrs_define
class DynamicPatch:
    """
    Attributes:
        is_starred (bool | None | Unset):
        name (None | str | Unset):
    """

    is_starred: bool | None | Unset = UNSET
    name: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        is_starred: bool | None | Unset
        if isinstance(self.is_starred, Unset):
            is_starred = UNSET
        else:
            is_starred = self.is_starred

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if is_starred is not UNSET:
            field_dict["is_starred"] = is_starred
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_is_starred(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_starred = _parse_is_starred(d.pop("is_starred", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        dynamic_patch = cls(
            is_starred=is_starred,
            name=name,
        )

        return dynamic_patch
