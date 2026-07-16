from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define

from thrustlab._models.segment_group_command_in_throttle_ramp import SegmentGroupCommandInThrottleRamp
from thrustlab._models.segment_group_command_in_tilt_ramp import SegmentGroupCommandInTiltRamp
from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="SegmentGroupCommandIn")


@_attrs_define
class SegmentGroupCommandIn:
    """A single rotor-group's throttle (+ tilt) command inside a segment.

    Attributes:
        throttle_target (float):
        throttle_ramp (SegmentGroupCommandInThrottleRamp | Unset):  Default: SegmentGroupCommandInThrottleRamp.STEP.
        tilt_ramp (SegmentGroupCommandInTiltRamp | Unset):  Default: SegmentGroupCommandInTiltRamp.STEP.
        tilt_target (float | Unset):  Default: 0.0.
    """

    throttle_target: float
    throttle_ramp: SegmentGroupCommandInThrottleRamp | Unset = SegmentGroupCommandInThrottleRamp.STEP
    tilt_ramp: SegmentGroupCommandInTiltRamp | Unset = SegmentGroupCommandInTiltRamp.STEP
    tilt_target: float | Unset = 0.0

    def to_dict(self) -> dict[str, Any]:
        throttle_target = self.throttle_target

        throttle_ramp: str | Unset = UNSET
        if not isinstance(self.throttle_ramp, Unset):
            throttle_ramp = self.throttle_ramp.value

        tilt_ramp: str | Unset = UNSET
        if not isinstance(self.tilt_ramp, Unset):
            tilt_ramp = self.tilt_ramp.value

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

        _throttle_ramp = d.pop("throttle_ramp", UNSET)
        throttle_ramp: SegmentGroupCommandInThrottleRamp | Unset
        if isinstance(_throttle_ramp, Unset):
            throttle_ramp = UNSET
        else:
            throttle_ramp = SegmentGroupCommandInThrottleRamp(_throttle_ramp)

        _tilt_ramp = d.pop("tilt_ramp", UNSET)
        tilt_ramp: SegmentGroupCommandInTiltRamp | Unset
        if isinstance(_tilt_ramp, Unset):
            tilt_ramp = UNSET
        else:
            tilt_ramp = SegmentGroupCommandInTiltRamp(_tilt_ramp)

        tilt_target = d.pop("tilt_target", UNSET)

        segment_group_command_in = cls(
            throttle_target=throttle_target,
            throttle_ramp=throttle_ramp,
            tilt_ramp=tilt_ramp,
            tilt_target=tilt_target,
        )

        return segment_group_command_in
