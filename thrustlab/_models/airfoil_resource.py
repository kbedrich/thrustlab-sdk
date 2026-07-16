from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="AirfoilResource")


@_attrs_define
class AirfoilResource:
    """
    Attributes:
        id (str):
        name (str):
        source (str):
        camber (float | None | Unset):
        family (None | str | Unset):
        max_thickness (float | None | Unset):
        object_ (str | Unset):  Default: 'airfoil'.
    """

    id: str
    name: str
    source: str
    camber: float | None | Unset = UNSET
    family: None | str | Unset = UNSET
    max_thickness: float | None | Unset = UNSET
    object_: str | Unset = "airfoil"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        source = self.source

        camber: float | None | Unset
        if isinstance(self.camber, Unset):
            camber = UNSET
        else:
            camber = self.camber

        family: None | str | Unset
        if isinstance(self.family, Unset):
            family = UNSET
        else:
            family = self.family

        max_thickness: float | None | Unset
        if isinstance(self.max_thickness, Unset):
            max_thickness = UNSET
        else:
            max_thickness = self.max_thickness

        object_ = self.object_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "source": source,
            }
        )
        if camber is not UNSET:
            field_dict["camber"] = camber
        if family is not UNSET:
            field_dict["family"] = family
        if max_thickness is not UNSET:
            field_dict["max_thickness"] = max_thickness
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        source = d.pop("source")

        def _parse_camber(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        camber = _parse_camber(d.pop("camber", UNSET))

        def _parse_family(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        family = _parse_family(d.pop("family", UNSET))

        def _parse_max_thickness(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        max_thickness = _parse_max_thickness(d.pop("max_thickness", UNSET))

        object_ = d.pop("object", UNSET)

        airfoil_resource = cls(
            id=id,
            name=name,
            source=source,
            camber=camber,
            family=family,
            max_thickness=max_thickness,
            object_=object_,
        )

        airfoil_resource.additional_properties = d
        return airfoil_resource

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
