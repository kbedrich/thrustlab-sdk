from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.submission_patch_data_json_type_0 import SubmissionPatchDataJsonType0


T = TypeVar("T", bound="SubmissionPatch")


@_attrs_define
class SubmissionPatch:
    """Withdraw/edit-before-review fields. component_type excluded —
    structural classifier; changing it would invalidate downstream
    review pipelines.

        Attributes:
            data_json (None | SubmissionPatchDataJsonType0 | Unset):
            manufacturer (None | str | Unset):
            name (None | str | Unset):
            notes (None | str | Unset):
            source_url (None | str | Unset):
    """

    data_json: None | SubmissionPatchDataJsonType0 | Unset = UNSET
    manufacturer: None | str | Unset = UNSET
    name: None | str | Unset = UNSET
    notes: None | str | Unset = UNSET
    source_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.submission_patch_data_json_type_0 import SubmissionPatchDataJsonType0

        data_json: dict[str, Any] | None | Unset
        if isinstance(self.data_json, Unset):
            data_json = UNSET
        elif isinstance(self.data_json, SubmissionPatchDataJsonType0):
            data_json = self.data_json.to_dict()
        else:
            data_json = self.data_json

        manufacturer: None | str | Unset
        if isinstance(self.manufacturer, Unset):
            manufacturer = UNSET
        else:
            manufacturer = self.manufacturer

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        notes: None | str | Unset
        if isinstance(self.notes, Unset):
            notes = UNSET
        else:
            notes = self.notes

        source_url: None | str | Unset
        if isinstance(self.source_url, Unset):
            source_url = UNSET
        else:
            source_url = self.source_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if data_json is not UNSET:
            field_dict["data_json"] = data_json
        if manufacturer is not UNSET:
            field_dict["manufacturer"] = manufacturer
        if name is not UNSET:
            field_dict["name"] = name
        if notes is not UNSET:
            field_dict["notes"] = notes
        if source_url is not UNSET:
            field_dict["source_url"] = source_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.submission_patch_data_json_type_0 import SubmissionPatchDataJsonType0

        d = dict(src_dict)

        def _parse_data_json(data: object) -> None | SubmissionPatchDataJsonType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                data_json_type_0 = SubmissionPatchDataJsonType0.from_dict(data)

                return data_json_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SubmissionPatchDataJsonType0 | Unset, data)

        data_json = _parse_data_json(d.pop("data_json", UNSET))

        def _parse_manufacturer(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        manufacturer = _parse_manufacturer(d.pop("manufacturer", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_notes(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        notes = _parse_notes(d.pop("notes", UNSET))

        def _parse_source_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_url = _parse_source_url(d.pop("source_url", UNSET))

        submission_patch = cls(
            data_json=data_json,
            manufacturer=manufacturer,
            name=name,
            notes=notes,
            source_url=source_url,
        )

        submission_patch.additional_properties = d
        return submission_patch

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
