from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.segment_group_command_in_throttle_ramp_type_0 import SegmentGroupCommandInThrottleRampType0
from thrustlab._models.segment_group_command_in_tilt_ramp_type_0 import SegmentGroupCommandInTiltRampType0
from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="SegmentGroupCommandIn")


@_attrs_define
class SegmentGroupCommandIn:
    """A single rotor-group's throttle (+ tilt) command inside a segment.

    Attributes:
        throttle_target (float):
        throttle_ramp (None | SegmentGroupCommandInThrottleRampType0 | Unset): Ramp shape for THIS group's throttle
            across the segment. Omit to inherit the segment-level `throttle_ramp` (itself defaulting to `step`). Each rotor
            group's ramp is honoured independently.
        tilt_ramp (None | SegmentGroupCommandInTiltRampType0 | Unset): Ramp shape for THIS group's tilt. Omit for
            `step`.
        tilt_target (float | Unset):  Default: 0.0.
    """

    throttle_target: float
    throttle_ramp: None | SegmentGroupCommandInThrottleRampType0 | Unset = UNSET
    tilt_ramp: None | SegmentGroupCommandInTiltRampType0 | Unset = UNSET
    tilt_target: float | Unset = 0.0

    def to_dict(self) -> dict[str, Any]:
        throttle_target = self.throttle_target

        throttle_ramp: None | str | Unset
        if isinstance(self.throttle_ramp, Unset):
            throttle_ramp = UNSET
        elif isinstance(self.throttle_ramp, SegmentGroupCommandInThrottleRampType0):
            throttle_ramp = self.throttle_ramp.value
        else:
            throttle_ramp = self.throttle_ramp

        tilt_ramp: None | str | Unset
        if isinstance(self.tilt_ramp, Unset):
            tilt_ramp = UNSET
        elif isinstance(self.tilt_ramp, SegmentGroupCommandInTiltRampType0):
            tilt_ramp = self.tilt_ramp.value
        else:
            tilt_ramp = self.tilt_ramp

        tilt_target = self.tilt_target

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "throttle_target": throttle_target,
            }
        )
        if throttle_ramp is not UNSET:
            field_dict["throttle_ramp"] = throttle_ramp
        if tilt_ramp is not UNSET:
            field_dict["tilt_ramp"] = tilt_ramp
        if tilt_target is not UNSET:
            field_dict["tilt_target"] = tilt_target

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        throttle_target = d.pop("throttle_target")

        def _parse_throttle_ramp(data: object) -> None | SegmentGroupCommandInThrottleRampType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                throttle_ramp_type_0 = SegmentGroupCommandInThrottleRampType0(data)

                return throttle_ramp_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SegmentGroupCommandInThrottleRampType0 | Unset, data)

        throttle_ramp = _parse_throttle_ramp(d.pop("throttle_ramp", UNSET))

        def _parse_tilt_ramp(data: object) -> None | SegmentGroupCommandInTiltRampType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                tilt_ramp_type_0 = SegmentGroupCommandInTiltRampType0(data)

                return tilt_ramp_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SegmentGroupCommandInTiltRampType0 | Unset, data)

        tilt_ramp = _parse_tilt_ramp(d.pop("tilt_ramp", UNSET))

        tilt_target = d.pop("tilt_target", UNSET)

        segment_group_command_in = cls(
            throttle_target=throttle_target,
            throttle_ramp=throttle_ramp,
            tilt_ramp=tilt_ramp,
            tilt_target=tilt_target,
        )

        return segment_group_command_in
