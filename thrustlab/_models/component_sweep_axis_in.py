from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.component_sweep_axis_in_axis import ComponentSweepAxisInAxis
from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="ComponentSweepAxisIn")


@_attrs_define
class ComponentSweepAxisIn:
    """A categorical component sweep axis on the
    wire. The caller supplies component IDs (raw UUID or comp_<ksuid>); the
    handler resolves them ownership-scoped to the resolved spec_json + name and
    stores the resolved axis in config_json["sweep"]["component_axes"].

        Attributes:
            axis (ComponentSweepAxisInAxis):
            component_ids (list[str]): Component IDs (raw UUID or comp_<ksuid>) to sweep over; >=2 (a 1-value axis is not a
                sweep)
            slot (int | Unset): Rotor-group index this axis targets (ignored for battery). Back-compat single-slot; prefer
                `slots`. Default: 0.
            slots (list[int] | None | Unset): Rotor-group indices this axis targets. >1 entry → SYNCED (one shared
                dimension). Omitted → [slot]. Battery must be a single slot.
    """

    axis: ComponentSweepAxisInAxis
    component_ids: list[str]
    slot: int | Unset = 0
    slots: list[int] | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        axis = self.axis.value

        component_ids = self.component_ids

        slot = self.slot

        slots: list[int] | None | Unset
        if isinstance(self.slots, Unset):
            slots = UNSET
        elif isinstance(self.slots, list):
            slots = self.slots

        else:
            slots = self.slots

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "axis": axis,
                "component_ids": component_ids,
            }
        )
        if slot is not UNSET:
            field_dict["slot"] = slot
        if slots is not UNSET:
            field_dict["slots"] = slots

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        axis = ComponentSweepAxisInAxis(d.pop("axis"))

        component_ids = cast(list[str], d.pop("component_ids"))

        slot = d.pop("slot", UNSET)

        def _parse_slots(data: object) -> list[int] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                slots_type_0 = cast(list[int], data)

                return slots_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[int] | None | Unset, data)

        slots = _parse_slots(d.pop("slots", UNSET))

        component_sweep_axis_in = cls(
            axis=axis,
            component_ids=component_ids,
            slot=slot,
            slots=slots,
        )

        return component_sweep_axis_in
