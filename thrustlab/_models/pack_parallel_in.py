from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.pack_leaf_in import PackLeafIn
    from thrustlab._models.pack_series_in import PackSeriesIn


T = TypeVar("T", bound="PackParallelIn")


@_attrs_define
class PackParallelIn:
    """
    Attributes:
        branches (list[PackLeafIn | PackParallelIn | PackSeriesIn]):
        voltage_match_tolerance_v (float):
        kind (Literal['parallel'] | Unset):  Default: 'parallel'.
    """

    branches: list[PackLeafIn | PackParallelIn | PackSeriesIn]
    voltage_match_tolerance_v: float
    kind: Literal["parallel"] | Unset = "parallel"

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.pack_leaf_in import PackLeafIn
        from thrustlab._models.pack_series_in import PackSeriesIn

        branches = []
        for branches_item_data in self.branches:
            branches_item: dict[str, Any]
            if isinstance(branches_item_data, PackLeafIn):
                branches_item = branches_item_data.to_dict()
            elif isinstance(branches_item_data, PackSeriesIn):
                branches_item = branches_item_data.to_dict()
            else:
                branches_item = branches_item_data.to_dict()

            branches.append(branches_item)

        voltage_match_tolerance_v = self.voltage_match_tolerance_v

        kind = self.kind

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "branches": branches,
                "voltage_match_tolerance_v": voltage_match_tolerance_v,
            }
        )
        if kind is not UNSET:
            field_dict["kind"] = kind

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.pack_leaf_in import PackLeafIn
        from thrustlab._models.pack_series_in import PackSeriesIn

        d = dict(src_dict)
        branches = []
        _branches = d.pop("branches")
        for branches_item_data in _branches:

            def _parse_branches_item(data: object) -> PackLeafIn | PackParallelIn | PackSeriesIn:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    branches_item_type_0 = PackLeafIn.from_dict(data)

                    return branches_item_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    branches_item_type_1 = PackSeriesIn.from_dict(data)

                    return branches_item_type_1
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                branches_item_type_2 = PackParallelIn.from_dict(data)

                return branches_item_type_2

            branches_item = _parse_branches_item(branches_item_data)

            branches.append(branches_item)

        voltage_match_tolerance_v = d.pop("voltage_match_tolerance_v")

        kind = cast(Literal["parallel"] | Unset, d.pop("kind", UNSET))
        if kind != "parallel" and not isinstance(kind, Unset):
            raise ValueError(f"kind must match const 'parallel', got '{kind}'")

        pack_parallel_in = cls(
            branches=branches,
            voltage_match_tolerance_v=voltage_match_tolerance_v,
            kind=kind,
        )

        return pack_parallel_in
