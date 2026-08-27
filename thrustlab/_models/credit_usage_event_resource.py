from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.credit_usage_event_resource_type import CreditUsageEventResourceType
from thrustlab._models.credit_usage_event_resource_unit_type import CreditUsageEventResourceUnitType
from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.credit_usage_related_resource import CreditUsageRelatedResource


T = TypeVar("T", bound="CreditUsageEventResource")


@_attrs_define
class CreditUsageEventResource:
    """
    Attributes:
        amount (int):
        balance_after (int | None): Remaining Free allowance after this event, or null for unlimited Hobbyist and Pro
            accounts.
        created_at (str):
        id (str):
        type_ (CreditUsageEventResourceType):
        unit_type (CreditUsageEventResourceUnitType):
        object_ (Literal['credit_usage_event'] | Unset):  Default: 'credit_usage_event'.
        resource (CreditUsageRelatedResource | None | Unset):
    """

    amount: int
    balance_after: int | None
    created_at: str
    id: str
    type_: CreditUsageEventResourceType
    unit_type: CreditUsageEventResourceUnitType
    object_: Literal["credit_usage_event"] | Unset = "credit_usage_event"
    resource: CreditUsageRelatedResource | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.credit_usage_related_resource import CreditUsageRelatedResource

        amount = self.amount

        balance_after: int | None
        balance_after = self.balance_after

        created_at = self.created_at

        id = self.id

        type_ = self.type_.value

        unit_type = self.unit_type.value

        object_ = self.object_

        resource: dict[str, Any] | None | Unset
        if isinstance(self.resource, Unset):
            resource = UNSET
        elif isinstance(self.resource, CreditUsageRelatedResource):
            resource = self.resource.to_dict()
        else:
            resource = self.resource

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "amount": amount,
                "balance_after": balance_after,
                "created_at": created_at,
                "id": id,
                "type": type_,
                "unit_type": unit_type,
            }
        )
        if object_ is not UNSET:
            field_dict["object"] = object_
        if resource is not UNSET:
            field_dict["resource"] = resource

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.credit_usage_related_resource import CreditUsageRelatedResource

        d = dict(src_dict)
        amount = d.pop("amount")

        def _parse_balance_after(data: object) -> int | None:
            if data is None:
                return data
            return cast(int | None, data)

        balance_after = _parse_balance_after(d.pop("balance_after"))

        created_at = d.pop("created_at")

        id = d.pop("id")

        type_ = CreditUsageEventResourceType(d.pop("type"))

        unit_type = CreditUsageEventResourceUnitType(d.pop("unit_type"))

        object_ = cast(Literal["credit_usage_event"] | Unset, d.pop("object", UNSET))
        if object_ != "credit_usage_event" and not isinstance(object_, Unset):
            raise ValueError(f"object must match const 'credit_usage_event', got '{object_}'")

        def _parse_resource(data: object) -> CreditUsageRelatedResource | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                resource_type_0 = CreditUsageRelatedResource.from_dict(data)

                return resource_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(CreditUsageRelatedResource | None | Unset, data)

        resource = _parse_resource(d.pop("resource", UNSET))

        credit_usage_event_resource = cls(
            amount=amount,
            balance_after=balance_after,
            created_at=created_at,
            id=id,
            type_=type_,
            unit_type=unit_type,
            object_=object_,
            resource=resource,
        )

        credit_usage_event_resource.additional_properties = d
        return credit_usage_event_resource

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
