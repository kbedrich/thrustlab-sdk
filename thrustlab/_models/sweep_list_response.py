from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

if TYPE_CHECKING:
    from thrustlab._models.sweep_resource import SweepResource


T = TypeVar("T", bound="SweepListResponse")


@_attrs_define
class SweepListResponse:
    """
    Attributes:
        data (list[SweepResource]):
        has_more (bool):
        next_cursor (None | str):
        object_ (Literal['list']):
    """

    data: list[SweepResource]
    has_more: bool
    next_cursor: None | str
    object_: Literal["list"]

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        has_more = self.has_more

        next_cursor: None | str
        next_cursor = self.next_cursor

        object_ = self.object_

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "data": data,
                "has_more": has_more,
                "next_cursor": next_cursor,
                "object": object_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.sweep_resource import SweepResource

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = SweepResource.from_dict(data_item_data)

            data.append(data_item)

        has_more = d.pop("has_more")

        def _parse_next_cursor(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        next_cursor = _parse_next_cursor(d.pop("next_cursor"))

        object_ = cast(Literal["list"], d.pop("object"))
        if object_ != "list":
            raise ValueError(f"object must match const 'list', got '{object_}'")

        sweep_list_response = cls(
            data=data,
            has_more=has_more,
            next_cursor=next_cursor,
            object_=object_,
        )

        return sweep_list_response
