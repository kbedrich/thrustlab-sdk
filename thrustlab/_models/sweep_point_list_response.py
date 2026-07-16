from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.sweep_point_list_response_display_labels_type_0 import SweepPointListResponseDisplayLabelsType0
    from thrustlab._models.sweep_point_resource import SweepPointResource


T = TypeVar("T", bound="SweepPointListResponse")


@_attrs_define
class SweepPointListResponse:
    """
    Attributes:
        data (list[SweepPointResource]):
        has_more (bool):
        next_cursor (None | str):
        object_ (Literal['list']):
        display_labels (None | SweepPointListResponseDisplayLabelsType0 | Unset):
    """

    data: list[SweepPointResource]
    has_more: bool
    next_cursor: None | str
    object_: Literal["list"]
    display_labels: None | SweepPointListResponseDisplayLabelsType0 | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.sweep_point_list_response_display_labels_type_0 import SweepPointListResponseDisplayLabelsType0

        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        has_more = self.has_more

        next_cursor: None | str
        next_cursor = self.next_cursor

        object_ = self.object_

        display_labels: dict[str, Any] | None | Unset
        if isinstance(self.display_labels, Unset):
            display_labels = UNSET
        elif isinstance(self.display_labels, SweepPointListResponseDisplayLabelsType0):
            display_labels = self.display_labels.to_dict()
        else:
            display_labels = self.display_labels

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "data": data,
                "has_more": has_more,
                "next_cursor": next_cursor,
                "object": object_,
            }
        )
        if display_labels is not UNSET:
            field_dict["display_labels"] = display_labels

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.sweep_point_list_response_display_labels_type_0 import SweepPointListResponseDisplayLabelsType0
        from thrustlab._models.sweep_point_resource import SweepPointResource

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = SweepPointResource.from_dict(data_item_data)

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

        def _parse_display_labels(data: object) -> None | SweepPointListResponseDisplayLabelsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                display_labels_type_0 = SweepPointListResponseDisplayLabelsType0.from_dict(data)

                return display_labels_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SweepPointListResponseDisplayLabelsType0 | Unset, data)

        display_labels = _parse_display_labels(d.pop("display_labels", UNSET))

        sweep_point_list_response = cls(
            data=data,
            has_more=has_more,
            next_cursor=next_cursor,
            object_=object_,
            display_labels=display_labels,
        )

        return sweep_point_list_response
