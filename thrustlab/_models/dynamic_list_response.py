from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.dynamic_resource import DynamicResource


T = TypeVar("T", bound="DynamicListResponse")


@_attrs_define
class DynamicListResponse:
    """Cursor-paginated list of dynamic simulations (mirrors SweepListResponse) so
    the project page + queue strip can surface dynamic runs like steady/sweep runs.

        Attributes:
            data (list[DynamicResource]):
            has_more (bool | Unset):  Default: False.
            next_cursor (None | str | Unset):
            object_ (Literal['list'] | Unset):  Default: 'list'.
    """

    data: list[DynamicResource]
    has_more: bool | Unset = False
    next_cursor: None | str | Unset = UNSET
    object_: Literal["list"] | Unset = "list"

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        has_more = self.has_more

        next_cursor: None | str | Unset
        if isinstance(self.next_cursor, Unset):
            next_cursor = UNSET
        else:
            next_cursor = self.next_cursor

        object_ = self.object_

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "data": data,
            }
        )
        if has_more is not UNSET:
            field_dict["has_more"] = has_more
        if next_cursor is not UNSET:
            field_dict["next_cursor"] = next_cursor
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.dynamic_resource import DynamicResource

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = DynamicResource.from_dict(data_item_data)

            data.append(data_item)

        has_more = d.pop("has_more", UNSET)

        def _parse_next_cursor(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        next_cursor = _parse_next_cursor(d.pop("next_cursor", UNSET))

        object_ = cast(Literal["list"] | Unset, d.pop("object", UNSET))
        if object_ != "list" and not isinstance(object_, Unset):
            raise ValueError(f"object must match const 'list', got '{object_}'")

        dynamic_list_response = cls(
            data=data,
            has_more=has_more,
            next_cursor=next_cursor,
            object_=object_,
        )

        return dynamic_list_response
