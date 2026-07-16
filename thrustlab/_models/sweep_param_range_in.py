from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.sweep_param_range_in_mode import SweepParamRangeInMode
from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="SweepParamRangeIn")


@_attrs_define
class SweepParamRangeIn:
    """
    Attributes:
        mode (SweepParamRangeInMode):
        start (float | None | Unset):
        steps (int | None | Unset):
        stop (float | None | Unset):
        values (list[float] | None | Unset):
    """

    mode: SweepParamRangeInMode
    start: float | None | Unset = UNSET
    steps: int | None | Unset = UNSET
    stop: float | None | Unset = UNSET
    values: list[float] | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        mode = self.mode.value

        start: float | None | Unset
        if isinstance(self.start, Unset):
            start = UNSET
        else:
            start = self.start

        steps: int | None | Unset
        if isinstance(self.steps, Unset):
            steps = UNSET
        else:
            steps = self.steps

        stop: float | None | Unset
        if isinstance(self.stop, Unset):
            stop = UNSET
        else:
            stop = self.stop

        values: list[float] | None | Unset
        if isinstance(self.values, Unset):
            values = UNSET
        elif isinstance(self.values, list):
            values = self.values

        else:
            values = self.values

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "mode": mode,
            }
        )
        if start is not UNSET:
            field_dict["start"] = start
        if steps is not UNSET:
            field_dict["steps"] = steps
        if stop is not UNSET:
            field_dict["stop"] = stop
        if values is not UNSET:
            field_dict["values"] = values

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        mode = SweepParamRangeInMode(d.pop("mode"))

        def _parse_start(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        start = _parse_start(d.pop("start", UNSET))

        def _parse_steps(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        steps = _parse_steps(d.pop("steps", UNSET))

        def _parse_stop(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        stop = _parse_stop(d.pop("stop", UNSET))

        def _parse_values(data: object) -> list[float] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                values_type_0 = cast(list[float], data)

                return values_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[float] | None | Unset, data)

        values = _parse_values(d.pop("values", UNSET))

        sweep_param_range_in = cls(
            mode=mode,
            start=start,
            steps=steps,
            stop=stop,
            values=values,
        )

        return sweep_param_range_in
