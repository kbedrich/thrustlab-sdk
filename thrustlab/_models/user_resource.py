from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from thrustlab._models.user_resource_unit_system import UserResourceUnitSystem
from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.entitlements_resource import EntitlementsResource


T = TypeVar("T", bound="UserResource")


@_attrs_define
class UserResource:
    """
    Attributes:
        created_at (datetime.datetime):
        email (str):
        email_verified (bool):
        entitlements (EntitlementsResource): The tier -> capability bundle serialized onto /v1/users/me.

            Sourced from ``entitlement_for(user.tier)`` (default-down), so the
            frontend has ONE authoritative entitlement source and never re-hardcodes
            tier sets. A plain declared model (NOT a ``@computed_field``) so it appears
            in the OpenAPI schema that codegen consumes.
        id (str):
        tier (str):
        trial_days_remaining (int | None):
        trial_end (datetime.datetime | None):
        trial_start (datetime.datetime | None):
        unit_system (UserResourceUnitSystem):
        object_ (str | Unset):  Default: 'user'.
    """

    created_at: datetime.datetime
    email: str
    email_verified: bool
    entitlements: EntitlementsResource
    id: str
    tier: str
    trial_days_remaining: int | None
    trial_end: datetime.datetime | None
    trial_start: datetime.datetime | None
    unit_system: UserResourceUnitSystem
    object_: str | Unset = "user"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        created_at = self.created_at.isoformat()

        email = self.email

        email_verified = self.email_verified

        entitlements = self.entitlements.to_dict()

        id = self.id

        tier = self.tier

        trial_days_remaining: int | None
        trial_days_remaining = self.trial_days_remaining

        trial_end: None | str
        if isinstance(self.trial_end, datetime.datetime):
            trial_end = self.trial_end.isoformat()
        else:
            trial_end = self.trial_end

        trial_start: None | str
        if isinstance(self.trial_start, datetime.datetime):
            trial_start = self.trial_start.isoformat()
        else:
            trial_start = self.trial_start

        unit_system = self.unit_system.value

        object_ = self.object_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "created_at": created_at,
                "email": email,
                "email_verified": email_verified,
                "entitlements": entitlements,
                "id": id,
                "tier": tier,
                "trial_days_remaining": trial_days_remaining,
                "trial_end": trial_end,
                "trial_start": trial_start,
                "unit_system": unit_system,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.entitlements_resource import EntitlementsResource

        d = dict(src_dict)
        created_at = isoparse(d.pop("created_at"))

        email = d.pop("email")

        email_verified = d.pop("email_verified")

        entitlements = EntitlementsResource.from_dict(d.pop("entitlements"))

        id = d.pop("id")

        tier = d.pop("tier")

        def _parse_trial_days_remaining(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        trial_days_remaining = _parse_trial_days_remaining(d.pop("trial_days_remaining"))

        def _parse_trial_end(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                trial_end_type_0 = isoparse(data)

                return trial_end_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        trial_end = _parse_trial_end(d.pop("trial_end"))

        def _parse_trial_start(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                trial_start_type_0 = isoparse(data)

                return trial_start_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        trial_start = _parse_trial_start(d.pop("trial_start"))

        unit_system = UserResourceUnitSystem(d.pop("unit_system"))

        object_ = d.pop("object", UNSET)

        user_resource = cls(
            created_at=created_at,
            email=email,
            email_verified=email_verified,
            entitlements=entitlements,
            id=id,
            tier=tier,
            trial_days_remaining=trial_days_remaining,
            trial_end=trial_end,
            trial_start=trial_start,
            unit_system=unit_system,
            object_=object_,
        )

        user_resource.additional_properties = d
        return user_resource

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
