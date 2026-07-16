from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.termination_in_mode import TerminationInMode
from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="TerminationIn")


@_attrs_define
class TerminationIn:
    """Run-termination policy: the SOC / cell-voltage depletion cutoffs and the
    fixed-duration vs until-depleted run mode.

        Attributes:
            cell_voltage_cutoff_v (float | None | Unset):
            max_duration_s (float | None | Unset):
            mode (TerminationInMode | Unset):  Default: TerminationInMode.UNTIL_DEPLETED.
            soc_cutoff_pct (float | Unset):  Default: 20.0.
    """

    cell_voltage_cutoff_v: float | None | Unset = UNSET
    max_duration_s: float | None | Unset = UNSET
    mode: TerminationInMode | Unset = TerminationInMode.UNTIL_DEPLETED
    soc_cutoff_pct: float | Unset = 20.0

    def to_dict(self) -> dict[str, Any]:
        cell_voltage_cutoff_v: float | None | Unset
        if isinstance(self.cell_voltage_cutoff_v, Unset):
            cell_voltage_cutoff_v = UNSET
        else:
            cell_voltage_cutoff_v = self.cell_voltage_cutoff_v

        max_duration_s: float | None | Unset
        if isinstance(self.max_duration_s, Unset):
            max_duration_s = UNSET
        else:
            max_duration_s = self.max_duration_s

        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode.value

        soc_cutoff_pct = self.soc_cutoff_pct

        field_dict: dict[str, Any] = {}

        field_dict.update({})
        if cell_voltage_cutoff_v is not UNSET:
            field_dict["cell_voltage_cutoff_v"] = cell_voltage_cutoff_v
        if max_duration_s is not UNSET:
            field_dict["max_duration_s"] = max_duration_s
        if mode is not UNSET:
            field_dict["mode"] = mode
        if soc_cutoff_pct is not UNSET:
            field_dict["soc_cutoff_pct"] = soc_cutoff_pct

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_cell_voltage_cutoff_v(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        cell_voltage_cutoff_v = _parse_cell_voltage_cutoff_v(d.pop("cell_voltage_cutoff_v", UNSET))

        def _parse_max_duration_s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        max_duration_s = _parse_max_duration_s(d.pop("max_duration_s", UNSET))

        _mode = d.pop("mode", UNSET)
        mode: TerminationInMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = TerminationInMode(_mode)

        soc_cutoff_pct = d.pop("soc_cutoff_pct", UNSET)

        termination_in = cls(
            cell_voltage_cutoff_v=cell_voltage_cutoff_v,
            max_duration_s=max_duration_s,
            mode=mode,
            soc_cutoff_pct=soc_cutoff_pct,
        )

        return termination_in
