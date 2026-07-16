from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.component_brand import ComponentBrand


T = TypeVar("T", bound="ComponentBrandsResponse")


@_attrs_define
class ComponentBrandsResponse:
    """
    Attributes:
        data (list[ComponentBrand]):
        has_more (bool):
        next_cursor (None | str):
        object_ (str | Unset):  Default: 'list'.
    """

    data: list[ComponentBrand]
    has_more: bool
    next_cursor: None | str
    object_: str | Unset = "list"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

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
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "has_more": has_more,
                "next_cursor": next_cursor,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.component_brand import ComponentBrand

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = ComponentBrand.from_dict(data_item_data)

            data.append(data_item)

        has_more = d.pop("has_more")

        def _parse_next_cursor(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        next_cursor = _parse_next_cursor(d.pop("next_cursor"))

        object_ = d.pop("object", UNSET)

        component_brands_response = cls(
            data=data,
            has_more=has_more,
            next_cursor=next_cursor,
            object_=object_,
        )

        component_brands_response.additional_properties = d
        return component_brands_response

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
