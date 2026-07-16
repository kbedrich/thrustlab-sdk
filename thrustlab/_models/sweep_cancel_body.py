from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="SweepCancelBody")


@_attrs_define
class SweepCancelBody:
    """
    Attributes:
        save_partial (bool | Unset):  Default: False.
    """

    save_partial: bool | Unset = False

    def to_dict(self) -> dict[str, Any]:
        save_partial = self.save_partial

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if save_partial is not UNSET:
            field_dict["save_partial"] = save_partial

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        save_partial = d.pop("save_partial", UNSET)

        sweep_cancel_body = cls(
            save_partial=save_partial,
        )

        return sweep_cancel_body
