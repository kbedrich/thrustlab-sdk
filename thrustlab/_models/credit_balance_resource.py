from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.credit_bucket_breakdown import CreditBucketBreakdown


T = TypeVar("T", bound="CreditBalanceResource")


@_attrs_define
class CreditBalanceResource:
    """
    Attributes:
        as_of (str):
        breakdown (list[CreditBucketBreakdown]):
        total (int):
        currency (Literal['credit'] | Unset):  Default: 'credit'.
        low_balance_threshold (int | None | Unset):
        object_ (Literal['credit_balance'] | Unset):  Default: 'credit_balance'.
    """

    as_of: str
    breakdown: list[CreditBucketBreakdown]
    total: int
    currency: Literal["credit"] | Unset = "credit"
    low_balance_threshold: int | None | Unset = UNSET
    object_: Literal["credit_balance"] | Unset = "credit_balance"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        as_of = self.as_of

        breakdown = []
        for breakdown_item_data in self.breakdown:
            breakdown_item = breakdown_item_data.to_dict()
            breakdown.append(breakdown_item)

        total = self.total

        currency = self.currency

        low_balance_threshold: int | None | Unset
        if isinstance(self.low_balance_threshold, Unset):
            low_balance_threshold = UNSET
        else:
            low_balance_threshold = self.low_balance_threshold

        object_ = self.object_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "as_of": as_of,
                "breakdown": breakdown,
                "total": total,
            }
        )
        if currency is not UNSET:
            field_dict["currency"] = currency
        if low_balance_threshold is not UNSET:
            field_dict["low_balance_threshold"] = low_balance_threshold
        if object_ is not UNSET:
            field_dict["object"] = object_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.credit_bucket_breakdown import CreditBucketBreakdown

        d = dict(src_dict)
        as_of = d.pop("as_of")

        breakdown = []
        _breakdown = d.pop("breakdown")
        for breakdown_item_data in _breakdown:
            breakdown_item = CreditBucketBreakdown.from_dict(breakdown_item_data)

            breakdown.append(breakdown_item)

        total = d.pop("total")

        currency = cast(Literal["credit"] | Unset, d.pop("currency", UNSET))
        if currency != "credit" and not isinstance(currency, Unset):
            raise ValueError(f"currency must match const 'credit', got '{currency}'")

        def _parse_low_balance_threshold(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        low_balance_threshold = _parse_low_balance_threshold(d.pop("low_balance_threshold", UNSET))

        object_ = cast(Literal["credit_balance"] | Unset, d.pop("object", UNSET))
        if object_ != "credit_balance" and not isinstance(object_, Unset):
            raise ValueError(f"object must match const 'credit_balance', got '{object_}'")

        credit_balance_resource = cls(
            as_of=as_of,
            breakdown=breakdown,
            total=total,
            currency=currency,
            low_balance_threshold=low_balance_threshold,
            object_=object_,
        )

        credit_balance_resource.additional_properties = d
        return credit_balance_resource

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
