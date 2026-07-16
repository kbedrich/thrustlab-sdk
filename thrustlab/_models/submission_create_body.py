from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.submission_create_body_data_json import SubmissionCreateBodyDataJson


T = TypeVar("T", bound="SubmissionCreateBody")


@_attrs_define
class SubmissionCreateBody:
    """
    Attributes:
        component_type (str):
        data_json (SubmissionCreateBodyDataJson):
        manufacturer (str):
        name (str):
        source_url (str):
        notes (None | str | Unset):
    """

    component_type: str
    data_json: SubmissionCreateBodyDataJson
    manufacturer: str
    name: str
    source_url: str
    notes: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        component_type = self.component_type

        data_json = self.data_json.to_dict()

        manufacturer = self.manufacturer

        name = self.name

        source_url = self.source_url

        notes: None | str | Unset
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "component_type": component_type,
                "data_json": data_json,
                "manufacturer": manufacturer,
                "name": name,
                "source_url": source_url,
            }
        )
        if notes is not UNSET:
            field_dict["notes"] = notes

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.submission_create_body_data_json import SubmissionCreateBodyDataJson

        d = dict(src_dict)
        component_type = d.pop("component_type")

        data_json = SubmissionCreateBodyDataJson.from_dict(d.pop("data_json"))

        manufacturer = d.pop("manufacturer")

        name = d.pop("name")

        source_url = d.pop("source_url")

        def _parse_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        notes = _parse_notes(d.pop("notes", UNSET))

        submission_create_body = cls(
            component_type=component_type,
            data_json=data_json,
            manufacturer=manufacturer,
            name=name,
            source_url=source_url,
            notes=notes,
        )

        submission_create_body.additional_properties = d
        return submission_create_body

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
