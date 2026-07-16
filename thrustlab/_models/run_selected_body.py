from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

T = TypeVar("T", bound="RunSelectedBody")


@_attrs_define
class RunSelectedBody:
    """
    Attributes:
        simulation_ids (list[str]):
    """

    simulation_ids: list[str]

    def to_dict(self) -> dict[str, Any]:
        simulation_ids = self.simulation_ids

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "simulation_ids": simulation_ids,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        simulation_ids = cast(list[str], d.pop("simulation_ids"))

        run_selected_body = cls(
            simulation_ids=simulation_ids,
        )

        return run_selected_body
