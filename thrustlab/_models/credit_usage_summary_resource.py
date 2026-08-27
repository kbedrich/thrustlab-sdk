from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.credit_usage_summary_resource_window import CreditUsageSummaryResourceWindow
from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="CreditUsageSummaryResource")


@_attrs_define
class CreditUsageSummaryResource:
    """The usage meter's single owner-scoped read.

    ``used`` is in COMPUTE UNITS (per physical rotor) — inherited from
    ``metering.used_in_window`` which SUMs ``abs(amount)`` (a 4-rotor static
    counts 4). ``cap``/``remaining`` are None for Hobbyist/Pro because paid
    usage is unlimited. ``resets_at`` is the ROLLING reporting window's next
    age-out instant (oldest in-window debit + window length), NEVER
    ``since + window`` (which always equals ``now``).

        Attributes:
            resets_at (str):
            tier (str):
            used (int):
            window (CreditUsageSummaryResourceWindow):
            cap (int | None | Unset):
            object_ (Literal['credit_usage_summary'] | Unset):  Default: 'credit_usage_summary'.
            remaining (int | None | Unset):
    """

    resets_at: str
    tier: str
    used: int
    window: CreditUsageSummaryResourceWindow
    cap: int | None | Unset = UNSET
    object_: Literal["credit_usage_summary"] | Unset = "credit_usage_summary"
    remaining: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        resets_at = self.resets_at

        tier = self.tier

        used = self.used

        window = self.window.value

        cap: int | None | Unset
        if isinstance(self.cap, Unset):
            cap = UNSET
        else:
            cap = self.cap

        object_ = self.object_

        remaining: int | None | Unset
        if isinstance(self.remaining, Unset):
            remaining = UNSET
        else:
            remaining = self.remaining

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "resets_at": resets_at,
                "tier": tier,
                "used": used,
                "window": window,
            }
        )
        if cap is not UNSET:
            field_dict["cap"] = cap
        if object_ is not UNSET:
            field_dict["object"] = object_
        if remaining is not UNSET:
            field_dict["remaining"] = remaining

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        resets_at = d.pop("resets_at")

        tier = d.pop("tier")

        used = d.pop("used")

        window = CreditUsageSummaryResourceWindow(d.pop("window"))

        def _parse_cap(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        cap = _parse_cap(d.pop("cap", UNSET))

        object_ = cast(Literal["credit_usage_summary"] | Unset, d.pop("object", UNSET))
        if object_ != "credit_usage_summary" and not isinstance(object_, Unset):
            raise ValueError(f"object must match const 'credit_usage_summary', got '{object_}'")

        def _parse_remaining(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        remaining = _parse_remaining(d.pop("remaining", UNSET))

        credit_usage_summary_resource = cls(
            resets_at=resets_at,
            tier=tier,
            used=used,
            window=window,
            cap=cap,
            object_=object_,
            remaining=remaining,
        )

        credit_usage_summary_resource.additional_properties = d
        return credit_usage_summary_resource

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
