from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar(
    "T",
    bound="ListDeliveriesV1WebhookEndpointsPublicIdDeliveriesGetResponseListDeliveriesV1WebhookEndpointsPublicIdDeliveriesGet",
)


@_attrs_define
class ListDeliveriesV1WebhookEndpointsPublicIdDeliveriesGetResponseListDeliveriesV1WebhookEndpointsPublicIdDeliveriesGet:
    """ """

    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        list_deliveries_v1_webhook_endpoints_public_id_deliveries_get_response_list_deliveries_v1_webhook_endpoints_public_id_deliveries_get = cls()

        list_deliveries_v1_webhook_endpoints_public_id_deliveries_get_response_list_deliveries_v1_webhook_endpoints_public_id_deliveries_get.additional_properties = d
        return list_deliveries_v1_webhook_endpoints_public_id_deliveries_get_response_list_deliveries_v1_webhook_endpoints_public_id_deliveries_get

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
