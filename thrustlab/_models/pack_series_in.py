from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.pack_leaf_in import PackLeafIn
    from thrustlab._models.pack_parallel_in import PackParallelIn


T = TypeVar("T", bound="PackSeriesIn")


@_attrs_define
class PackSeriesIn:
    """
    Attributes:
        children (list[PackLeafIn | PackParallelIn | PackSeriesIn]):
        kind (Literal['series'] | Unset):  Default: 'series'.
    """

    children: list[PackLeafIn | PackParallelIn | PackSeriesIn]
    kind: Literal["series"] | Unset = "series"

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.pack_leaf_in import PackLeafIn

        children = []
        for children_item_data in self.children:
            children_item: dict[str, Any]
            if isinstance(children_item_data, PackLeafIn):
                children_item = children_item_data.to_dict()
            elif isinstance(children_item_data, PackSeriesIn):
                children_item = children_item_data.to_dict()
            else:
                children_item = children_item_data.to_dict()

            children.append(children_item)

        kind = self.kind

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "children": children,
            }
        )
        if kind is not UNSET:
            field_dict["kind"] = kind

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.pack_leaf_in import PackLeafIn
        from thrustlab._models.pack_parallel_in import PackParallelIn

        d = dict(src_dict)
        children = []
        _children = d.pop("children")
        for children_item_data in _children:

            def _parse_children_item(data: object) -> PackLeafIn | PackParallelIn | PackSeriesIn:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    children_item_type_0 = PackLeafIn.from_dict(data)

                    return children_item_type_0
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    children_item_type_1 = PackSeriesIn.from_dict(data)

                    return children_item_type_1
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                children_item_type_2 = PackParallelIn.from_dict(data)

                return children_item_type_2

            children_item = _parse_children_item(children_item_data)

            children.append(children_item)

        kind = cast(Literal["series"] | Unset, d.pop("kind", UNSET))
        if kind != "series" and not isinstance(kind, Unset):
            raise ValueError(f"kind must match const 'series', got '{kind}'")

        pack_series_in = cls(
            children=children,
            kind=kind,
        )

        return pack_series_in
