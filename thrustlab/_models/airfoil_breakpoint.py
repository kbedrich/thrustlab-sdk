from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

T = TypeVar("T", bound="AirfoilBreakpoint")


@_attrs_define
class AirfoilBreakpoint:
    """One per-station airfoil assignment in an ``airfoil_layout``.

    ``r_over_R`` is the normalized radial station the breakpoint applies at;
    ``airfoil_ref`` is either an aerosandbox library name (e.g. ``"clarky"``) or
    an ``afl_<ksuid>`` reference to the caller's custom airfoil. Custom refs are
    resolved caller-scoped at the route and the resolved Kulfan
    weights are passed inline to the stateless service.

        Attributes:
            airfoil_ref (str):
            r_over_r (float):
    """

    airfoil_ref: str
    r_over_r: float

    def to_dict(self) -> dict[str, Any]:
        airfoil_ref = self.airfoil_ref

        r_over_r = self.r_over_r

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "airfoil_ref": airfoil_ref,
                "r_over_R": r_over_r,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        airfoil_ref = d.pop("airfoil_ref")

        r_over_r = d.pop("r_over_R")

        airfoil_breakpoint = cls(
            airfoil_ref=airfoil_ref,
            r_over_r=r_over_r,
        )

        return airfoil_breakpoint
