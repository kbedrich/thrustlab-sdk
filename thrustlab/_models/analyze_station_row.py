from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="AnalyzeStationRow")


@_attrs_define
class AnalyzeStationRow:
    """One radial-station row of the per-station table. Aero quantities only.

    Attributes:
        cd (float):
        cl (float):
        mach (float):
        re (float):
        beta_deg (float):
        chord (float):
        d_q_dr (float):
        d_t_dr (float):
        eta_local (float):
        r_over_r (float):
        va (float):
        vt (float):
    """

    cd: float
    cl: float
    mach: float
    re: float
    beta_deg: float
    chord: float
    d_q_dr: float
    d_t_dr: float
    eta_local: float
    r_over_r: float
    va: float
    vt: float
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cd = self.cd

        cl = self.cl

        mach = self.mach

        re = self.re

        beta_deg = self.beta_deg

        chord = self.chord

        d_q_dr = self.d_q_dr

        d_t_dr = self.d_t_dr

        eta_local = self.eta_local

        r_over_r = self.r_over_r

        va = self.va

        vt = self.vt

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "Cd": cd,
                "Cl": cl,
                "Mach": mach,
                "Re": re,
                "beta_deg": beta_deg,
                "chord": chord,
                "dQ_dr": d_q_dr,
                "dT_dr": d_t_dr,
                "eta_local": eta_local,
                "r_over_R": r_over_r,
                "va": va,
                "vt": vt,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        cd = d.pop("Cd")

        cl = d.pop("Cl")

        mach = d.pop("Mach")

        re = d.pop("Re")

        beta_deg = d.pop("beta_deg")

        chord = d.pop("chord")

        d_q_dr = d.pop("dQ_dr")

        d_t_dr = d.pop("dT_dr")

        eta_local = d.pop("eta_local")

        r_over_r = d.pop("r_over_R")

        va = d.pop("va")

        vt = d.pop("vt")

        analyze_station_row = cls(
            cd=cd,
            cl=cl,
            mach=mach,
            re=re,
            beta_deg=beta_deg,
            chord=chord,
            d_q_dr=d_q_dr,
            d_t_dr=d_t_dr,
            eta_local=eta_local,
            r_over_r=r_over_r,
            va=va,
            vt=vt,
        )

        analyze_station_row.additional_properties = d
        return analyze_station_row

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
