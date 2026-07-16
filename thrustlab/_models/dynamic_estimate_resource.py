from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="DynamicEstimateResource")


@_attrs_define
class DynamicEstimateResource:
    """
    Attributes:
        estimated_credits (int):
        estimated_duration_s (float):
        object_ (Literal['dynamic_estimate'] | Unset):  Default: 'dynamic_estimate'.
    """

    estimated_credits: int
    estimated_duration_s: float
    object_: Literal["dynamic_estimate"] | Unset = "dynamic_estimate"

    def to_dict(self) -> dict[str, Any]:
        estimated_credits = self.estimated_credits

        estimated_duration_s = self.estimated_duration_s

        object_ = self.object_

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "estimated_credits": estimated_credits,
                "estimated_duration_s": estimated_duration_s,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        estimated_credits = d.pop("estimated_credits")

        estimated_duration_s = d.pop("estimated_duration_s")

        object_ = cast(Literal["dynamic_estimate"] | Unset, d.pop("object", UNSET))
        if object_ != "dynamic_estimate" and not isinstance(object_, Unset):
            raise ValueError(f"object must match const 'dynamic_estimate', got '{object_}'")

        dynamic_estimate_resource = cls(
            estimated_credits=estimated_credits,
            estimated_duration_s=estimated_duration_s,
            object_=object_,
        )

        return dynamic_estimate_resource
