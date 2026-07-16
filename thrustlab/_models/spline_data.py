from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="SplineData")


@_attrs_define
class SplineData:
    """
    Attributes:
        control_points (list[float]):
        knots (list[float]):
        degree (int | Unset):  Default: 3.
    """

    control_points: list[float]
    knots: list[float]
    degree: int | Unset = 3
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        control_points = self.control_points

        knots = self.knots

        degree = self.degree

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "control_points": control_points,
                "knots": knots,
            }
        )
        if degree is not UNSET:
            field_dict["degree"] = degree

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        control_points = cast(list[float], d.pop("control_points"))

        knots = cast(list[float], d.pop("knots"))

        degree = d.pop("degree", UNSET)

        spline_data = cls(
            control_points=control_points,
            knots=knots,
            degree=degree,
        )

        spline_data.additional_properties = d
        return spline_data

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
