from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="SweepInputs")


@_attrs_define
class SweepInputs:
    """
    Attributes:
        airspeed_m_s (float):
        battery_charge_pct (float):
        density_kg_m3 (float):
        solver (str):
    """

    airspeed_m_s: float
    battery_charge_pct: float
    density_kg_m3: float
    solver: str

    def to_dict(self) -> dict[str, Any]:
        airspeed_m_s = self.airspeed_m_s

        battery_charge_pct = self.battery_charge_pct

        density_kg_m3 = self.density_kg_m3

        solver = self.solver

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "airspeed_m_s": airspeed_m_s,
                "battery_charge_pct": battery_charge_pct,
                "density_kg_m3": density_kg_m3,
                "solver": solver,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        airspeed_m_s = d.pop("airspeed_m_s")

        battery_charge_pct = d.pop("battery_charge_pct")

        density_kg_m3 = d.pop("density_kg_m3")

        solver = d.pop("solver")

        sweep_inputs = cls(
            airspeed_m_s=airspeed_m_s,
            battery_charge_pct=battery_charge_pct,
            density_kg_m3=density_kg_m3,
            solver=solver,
        )

        return sweep_inputs
