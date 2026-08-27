from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="EntitlementsResource")


@_attrs_define
class EntitlementsResource:
    """The tier -> capability bundle serialized onto /v1/users/me.

    Sourced from ``entitlement_for(user.tier)`` (default-down), so the
    frontend has ONE authoritative entitlement source and never re-hardcodes
    tier sets. A plain declared model (NOT a ``@computed_field``) so it appears
    in the OpenAPI schema that codegen consumes.

        Attributes:
            api_access (bool):
            cad_export (bool):
            creator_edit (bool):
            daily_cap (int | None): Rolling daily usage cap, or null when no daily cap applies.
            db_access (str):
            fmi_export (bool):
            max_concurrent_runs (int): Account-wide simulations that may execute simultaneously across dashboard sessions
                and every API key. Additional work stays queued.
            sim_types (list[str]):
            weekly_cap (int | None): Compatibility field for a rolling weekly usage cap; null for current tiers.
    """

    api_access: bool
    cad_export: bool
    creator_edit: bool
    daily_cap: int | None
    db_access: str
    fmi_export: bool
    max_concurrent_runs: int
    sim_types: list[str]
    weekly_cap: int | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        api_access = self.api_access

        cad_export = self.cad_export

        creator_edit = self.creator_edit

        daily_cap: int | None
        daily_cap = self.daily_cap

        db_access = self.db_access

        fmi_export = self.fmi_export

        max_concurrent_runs = self.max_concurrent_runs

        sim_types = self.sim_types

        weekly_cap: int | None
        weekly_cap = self.weekly_cap

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "api_access": api_access,
                "cad_export": cad_export,
                "creator_edit": creator_edit,
                "daily_cap": daily_cap,
                "db_access": db_access,
                "fmi_export": fmi_export,
                "max_concurrent_runs": max_concurrent_runs,
                "sim_types": sim_types,
                "weekly_cap": weekly_cap,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        api_access = d.pop("api_access")

        cad_export = d.pop("cad_export")

        creator_edit = d.pop("creator_edit")

        def _parse_daily_cap(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        daily_cap = _parse_daily_cap(d.pop("daily_cap"))

        db_access = d.pop("db_access")

        fmi_export = d.pop("fmi_export")

        max_concurrent_runs = d.pop("max_concurrent_runs")

        sim_types = cast(list[str], d.pop("sim_types"))

        def _parse_weekly_cap(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        weekly_cap = _parse_weekly_cap(d.pop("weekly_cap"))

        entitlements_resource = cls(
            api_access=api_access,
            cad_export=cad_export,
            creator_edit=creator_edit,
            daily_cap=daily_cap,
            db_access=db_access,
            fmi_export=fmi_export,
            max_concurrent_runs=max_concurrent_runs,
            sim_types=sim_types,
            weekly_cap=weekly_cap,
        )

        entitlements_resource.additional_properties = d
        return entitlements_resource

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
