from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="ProjectResource")


@_attrs_define
class ProjectResource:
    """
    Attributes:
        aircraft_type_tag (None | str):
        created_at (datetime.datetime):
        id (str):
        name (str):
        notes (None | str):
        updated_at (datetime.datetime):
        completed_count (int | Unset):  Default: 0.
        failed_count (int | Unset):  Default: 0.
        last_activity_at (datetime.datetime | None | Unset):
        object_ (str | Unset):  Default: 'project'.
        run_count (int | Unset):  Default: 0.
        running_count (int | Unset):  Default: 0.
    """

    aircraft_type_tag: None | str
    created_at: datetime.datetime
    id: str
    name: str
    notes: None | str
    updated_at: datetime.datetime
    completed_count: int | Unset = 0
    failed_count: int | Unset = 0
    last_activity_at: datetime.datetime | None | Unset = UNSET
    object_: str | Unset = "project"
    run_count: int | Unset = 0
    running_count: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        aircraft_type_tag: None | str
        aircraft_type_tag = self.aircraft_type_tag

        created_at = self.created_at.isoformat()

        id = self.id

        name = self.name

        notes: None | str
        notes = self.notes

        updated_at = self.updated_at.isoformat()

        completed_count = self.completed_count

        failed_count = self.failed_count

        last_activity_at: None | str | Unset
        if isinstance(self.last_activity_at, Unset):
            last_activity_at = UNSET
        elif isinstance(self.last_activity_at, datetime.datetime):
            last_activity_at = self.last_activity_at.isoformat()
        else:
            last_activity_at = self.last_activity_at

        object_ = self.object_

        run_count = self.run_count

        running_count = self.running_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "aircraft_type_tag": aircraft_type_tag,
                "created_at": created_at,
                "id": id,
                "name": name,
                "notes": notes,
                "updated_at": updated_at,
            }
        )
        if completed_count is not UNSET:
            field_dict["completed_count"] = completed_count
        if failed_count is not UNSET:
            field_dict["failed_count"] = failed_count
        if last_activity_at is not UNSET:
            field_dict["last_activity_at"] = last_activity_at
        if object_ is not UNSET:
            field_dict["object"] = object_
        if run_count is not UNSET:
            field_dict["run_count"] = run_count
        if running_count is not UNSET:
            field_dict["running_count"] = running_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_aircraft_type_tag(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        aircraft_type_tag = _parse_aircraft_type_tag(d.pop("aircraft_type_tag"))

        created_at = isoparse(d.pop("created_at"))

        id = d.pop("id")

        name = d.pop("name")

        def _parse_notes(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        notes = _parse_notes(d.pop("notes"))

        updated_at = isoparse(d.pop("updated_at"))

        completed_count = d.pop("completed_count", UNSET)

        failed_count = d.pop("failed_count", UNSET)

        def _parse_last_activity_at(data: object) -> datetime.datetime | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_activity_at_type_0 = isoparse(data)

                return last_activity_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None | Unset, data)

        last_activity_at = _parse_last_activity_at(d.pop("last_activity_at", UNSET))

        object_ = d.pop("object", UNSET)

        run_count = d.pop("run_count", UNSET)

        running_count = d.pop("running_count", UNSET)

        project_resource = cls(
            aircraft_type_tag=aircraft_type_tag,
            created_at=created_at,
            id=id,
            name=name,
            notes=notes,
            updated_at=updated_at,
            completed_count=completed_count,
            failed_count=failed_count,
            last_activity_at=last_activity_at,
            object_=object_,
            run_count=run_count,
            running_count=running_count,
        )

        project_resource.additional_properties = d
        return project_resource

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
