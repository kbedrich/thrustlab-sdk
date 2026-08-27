from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="PackLeafIn")


@_attrs_define
class PackLeafIn:
    """
    Attributes:
        battery_component_id (str):
        id (str):
        branch_wire_resistance_mohm (float | Unset):  Default: 0.0.
        initial_soc_pct (float | None | Unset):
        kind (Literal['leaf'] | Unset):  Default: 'leaf'.
    """

    battery_component_id: str
    id: str
    branch_wire_resistance_mohm: float | Unset = 0.0
    initial_soc_pct: float | None | Unset = UNSET
    kind: Literal["leaf"] | Unset = "leaf"

    def to_dict(self) -> dict[str, Any]:
        battery_component_id = self.battery_component_id

        id = self.id

        branch_wire_resistance_mohm = self.branch_wire_resistance_mohm

        initial_soc_pct: float | None | Unset
        if isinstance(self.initial_soc_pct, Unset):
            initial_soc_pct = UNSET
        else:
            initial_soc_pct = self.initial_soc_pct

        kind = self.kind

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "battery_component_id": battery_component_id,
                "id": id,
            }
        )
        if branch_wire_resistance_mohm is not UNSET:
            field_dict["branch_wire_resistance_mohm"] = branch_wire_resistance_mohm
        if initial_soc_pct is not UNSET:
            field_dict["initial_soc_pct"] = initial_soc_pct
        if kind is not UNSET:
            field_dict["kind"] = kind

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        battery_component_id = d.pop("battery_component_id")

        id = d.pop("id")

        branch_wire_resistance_mohm = d.pop("branch_wire_resistance_mohm", UNSET)

        def _parse_initial_soc_pct(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        initial_soc_pct = _parse_initial_soc_pct(d.pop("initial_soc_pct", UNSET))

        kind = cast(Literal["leaf"] | Unset, d.pop("kind", UNSET))
        if kind != "leaf" and not isinstance(kind, Unset):
            raise ValueError(f"kind must match const 'leaf', got '{kind}'")

        pack_leaf_in = cls(
            battery_component_id=battery_component_id,
            id=id,
            branch_wire_resistance_mohm=branch_wire_resistance_mohm,
            initial_soc_pct=initial_soc_pct,
            kind=kind,
        )

        return pack_leaf_in
