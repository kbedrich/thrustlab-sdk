from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="SweepPointPatch")


@_attrs_define
class SweepPointPatch:
    """
    Attributes:
        is_starred (bool):
    """

    is_starred: bool

    def to_dict(self) -> dict[str, Any]:
        is_starred = self.is_starred

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "is_starred": is_starred,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        is_starred = d.pop("is_starred")

        sweep_point_patch = cls(
            is_starred=is_starred,
        )

        return sweep_point_patch
