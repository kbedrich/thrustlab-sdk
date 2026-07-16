from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.submission_resource_data_json import SubmissionResourceDataJson


T = TypeVar("T", bound="SubmissionResource")


@_attrs_define
class SubmissionResource:
    """
    Attributes:
        component_type (str):
        created_at (datetime.datetime):
        credit_reward (int):
        data_json (SubmissionResourceDataJson):
        id (str):
        manufacturer (str):
        name (str):
        notes (None | str):
        reviewed_at (datetime.datetime | None):
        reviewer_notes (None | str):
        source_url (str):
        status (str):
        object_ (str | Unset):  Default: 'submission'.
    """

    component_type: str
    created_at: datetime.datetime
    credit_reward: int
    data_json: SubmissionResourceDataJson
    id: str
    manufacturer: str
    name: str
    notes: None | str
    reviewed_at: datetime.datetime | None
    reviewer_notes: None | str
    source_url: str
    status: str
    object_: str | Unset = "submission"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        component_type = self.component_type

        created_at = self.created_at.isoformat()

        credit_reward = self.credit_reward

        data_json = self.data_json.to_dict()

        id = self.id

        manufacturer = self.manufacturer

        name = self.name

        notes: None | str
        notes = self.notes

        reviewed_at: None | str
        if isinstance(self.reviewed_at, datetime.datetime):
            reviewed_at = self.reviewed_at.isoformat()
        else:
            reviewed_at = self.reviewed_at

        reviewer_notes: None | str
        reviewer_notes = self.reviewer_notes

        source_url = self.source_url

        status = self.status

        object_ = self.object_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "component_type": component_type,
                "created_at": created_at,
                "credit_reward": credit_reward,
                "data_json": data_json,
                "id": id,
                "manufacturer": manufacturer,
                "name": name,
                "notes": notes,
                "reviewed_at": reviewed_at,
                "reviewer_notes": reviewer_notes,
                "source_url": source_url,
                "status": status,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.submission_resource_data_json import SubmissionResourceDataJson

        d = dict(src_dict)
        component_type = d.pop("component_type")

        created_at = isoparse(d.pop("created_at"))

        credit_reward = d.pop("credit_reward")

        data_json = SubmissionResourceDataJson.from_dict(d.pop("data_json"))

        id = d.pop("id")

        manufacturer = d.pop("manufacturer")

        name = d.pop("name")

        def _parse_notes(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        notes = _parse_notes(d.pop("notes"))

        def _parse_reviewed_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                reviewed_at_type_0 = isoparse(data)

                return reviewed_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        reviewed_at = _parse_reviewed_at(d.pop("reviewed_at"))

        def _parse_reviewer_notes(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        reviewer_notes = _parse_reviewer_notes(d.pop("reviewer_notes"))

        source_url = d.pop("source_url")

        status = d.pop("status")

        object_ = d.pop("object", UNSET)

        submission_resource = cls(
            component_type=component_type,
            created_at=created_at,
            credit_reward=credit_reward,
            data_json=data_json,
            id=id,
            manufacturer=manufacturer,
            name=name,
            notes=notes,
            reviewed_at=reviewed_at,
            reviewer_notes=reviewer_notes,
            source_url=source_url,
            status=status,
            object_=object_,
        )

        submission_resource.additional_properties = d
        return submission_resource

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
