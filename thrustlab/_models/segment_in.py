from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.segment_in_airspeed_ramp import SegmentInAirspeedRamp
from thrustlab._models.segment_in_throttle_ramp import SegmentInThrottleRamp
from thrustlab._models.segment_in_vertical_speed_ramp import SegmentInVerticalSpeedRamp
from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.segment_in_per_group import SegmentInPerGroup


T = TypeVar("T", bound="SegmentIn")


@_attrs_define
class SegmentIn:
    """One schedule segment: a per-group throttle command + an airspeed target
    (+ vertical-speed target) held for ``duration_s`` (or until depletion
    when ``until_depleted``).

        Attributes:
            per_group (SegmentInPerGroup):
            airspeed_ramp (SegmentInAirspeedRamp | Unset):  Default: SegmentInAirspeedRamp.STEP.
            airspeed_target (float | Unset):  Default: 0.0.
            duration_s (float | None | Unset):
            throttle_ramp (SegmentInThrottleRamp | Unset):  Default: SegmentInThrottleRamp.STEP.
            until_depleted (bool | Unset):  Default: False.
            vertical_speed_ramp (SegmentInVerticalSpeedRamp | Unset):  Default: SegmentInVerticalSpeedRamp.STEP.
            vertical_speed_target (float | Unset):  Default: 0.0.
    """

    per_group: SegmentInPerGroup
    airspeed_ramp: SegmentInAirspeedRamp | Unset = SegmentInAirspeedRamp.STEP
    airspeed_target: float | Unset = 0.0
    duration_s: float | None | Unset = UNSET
    throttle_ramp: SegmentInThrottleRamp | Unset = SegmentInThrottleRamp.STEP
    until_depleted: bool | Unset = False
    vertical_speed_ramp: SegmentInVerticalSpeedRamp | Unset = SegmentInVerticalSpeedRamp.STEP
    vertical_speed_target: float | Unset = 0.0

    def to_dict(self) -> dict[str, Any]:
        per_group = self.per_group.to_dict()

        airspeed_ramp: str | Unset = UNSET
        if not isinstance(self.airspeed_ramp, Unset):
            airspeed_ramp = self.airspeed_ramp.value

        airspeed_target = self.airspeed_target

        duration_s: float | None | Unset
        if isinstance(self.duration_s, Unset):
            duration_s = UNSET
        else:
            duration_s = self.duration_s

        throttle_ramp: str | Unset = UNSET
        if not isinstance(self.throttle_ramp, Unset):
            throttle_ramp = self.throttle_ramp.value

        until_depleted = self.until_depleted

        vertical_speed_ramp: str | Unset = UNSET
        if not isinstance(self.vertical_speed_ramp, Unset):
            vertical_speed_ramp = self.vertical_speed_ramp.value

        vertical_speed_target = self.vertical_speed_target

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "per_group": per_group,
            }
        )
        if airspeed_ramp is not UNSET:
            field_dict["airspeed_ramp"] = airspeed_ramp
        if airspeed_target is not UNSET:
            field_dict["airspeed_target"] = airspeed_target
        if duration_s is not UNSET:
            field_dict["duration_s"] = duration_s
        if throttle_ramp is not UNSET:
            field_dict["throttle_ramp"] = throttle_ramp
        if until_depleted is not UNSET:
            field_dict["until_depleted"] = until_depleted
        if vertical_speed_ramp is not UNSET:
            field_dict["vertical_speed_ramp"] = vertical_speed_ramp
        if vertical_speed_target is not UNSET:
            field_dict["vertical_speed_target"] = vertical_speed_target

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.segment_in_per_group import SegmentInPerGroup

        d = dict(src_dict)
        per_group = SegmentInPerGroup.from_dict(d.pop("per_group"))

        _airspeed_ramp = d.pop("airspeed_ramp", UNSET)
        airspeed_ramp: SegmentInAirspeedRamp | Unset
        if isinstance(_airspeed_ramp, Unset):
            airspeed_ramp = UNSET
        else:
            airspeed_ramp = SegmentInAirspeedRamp(_airspeed_ramp)

        airspeed_target = d.pop("airspeed_target", UNSET)

        def _parse_duration_s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        duration_s = _parse_duration_s(d.pop("duration_s", UNSET))

        _throttle_ramp = d.pop("throttle_ramp", UNSET)
        throttle_ramp: SegmentInThrottleRamp | Unset
        if isinstance(_throttle_ramp, Unset):
            throttle_ramp = UNSET
        else:
            throttle_ramp = SegmentInThrottleRamp(_throttle_ramp)

        until_depleted = d.pop("until_depleted", UNSET)

        _vertical_speed_ramp = d.pop("vertical_speed_ramp", UNSET)
        vertical_speed_ramp: SegmentInVerticalSpeedRamp | Unset
        if isinstance(_vertical_speed_ramp, Unset):
            vertical_speed_ramp = UNSET
        else:
            vertical_speed_ramp = SegmentInVerticalSpeedRamp(_vertical_speed_ramp)

        vertical_speed_target = d.pop("vertical_speed_target", UNSET)

        segment_in = cls(
            per_group=per_group,
            airspeed_ramp=airspeed_ramp,
            airspeed_target=airspeed_target,
            duration_s=duration_s,
            throttle_ramp=throttle_ramp,
            until_depleted=until_depleted,
            vertical_speed_ramp=vertical_speed_ramp,
            vertical_speed_target=vertical_speed_target,
        )

        return segment_in
