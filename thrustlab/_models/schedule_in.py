from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.schedule_in_interpolation_type_0 import ScheduleInInterpolationType0
from thrustlab._models.schedule_in_mode import ScheduleInMode
from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.segment_in import SegmentIn


T = TypeVar("T", bound="ScheduleIn")


@_attrs_define
class ScheduleIn:
    """The control schedule — a ``segments`` list OR a per-rotor ``csv_text``.

    ``mode`` is the discriminator. ``segments`` is required for ``mode=segments``;
    ``csv_text`` (+ optional ``interpolation``) for ``mode=csv``. The cross-field
    requirement is enforced server-side by the schedule compiler (``validate_schedule``) so a malformed schedule 4xx's
    BEFORE any reservation.

        Attributes:
            mode (ScheduleInMode):
            csv_text (None | str | Unset):
            interpolation (None | ScheduleInInterpolationType0 | Unset):
            segments (list[SegmentIn] | None | Unset):
    """

    mode: ScheduleInMode
    csv_text: None | str | Unset = UNSET
    interpolation: None | ScheduleInInterpolationType0 | Unset = UNSET
    segments: list[SegmentIn] | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        mode = self.mode.value

        csv_text: None | str | Unset
        if isinstance(self.csv_text, Unset):
            csv_text = UNSET
        else:
            csv_text = self.csv_text

        interpolation: None | str | Unset
        if isinstance(self.interpolation, Unset):
            interpolation = UNSET
        elif isinstance(self.interpolation, ScheduleInInterpolationType0):
            interpolation = self.interpolation.value
        else:
            interpolation = self.interpolation

        segments: list[dict[str, Any]] | None | Unset
        if isinstance(self.segments, Unset):
            segments = UNSET
        elif isinstance(self.segments, list):
            segments = []
            for segments_type_0_item_data in self.segments:
                segments_type_0_item = segments_type_0_item_data.to_dict()
                segments.append(segments_type_0_item)

        else:
            segments = self.segments

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "mode": mode,
            }
        )
        if csv_text is not UNSET:
            field_dict["csv_text"] = csv_text
        if interpolation is not UNSET:
            field_dict["interpolation"] = interpolation
        if segments is not UNSET:
            field_dict["segments"] = segments

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.segment_in import SegmentIn

        d = dict(src_dict)
        mode = ScheduleInMode(d.pop("mode"))

        def _parse_csv_text(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        csv_text = _parse_csv_text(d.pop("csv_text", UNSET))

        def _parse_interpolation(data: object) -> None | ScheduleInInterpolationType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                interpolation_type_0 = ScheduleInInterpolationType0(data)

                return interpolation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ScheduleInInterpolationType0 | Unset, data)

        interpolation = _parse_interpolation(d.pop("interpolation", UNSET))

        def _parse_segments(data: object) -> list[SegmentIn] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                segments_type_0 = []
                _segments_type_0 = data
                for segments_type_0_item_data in _segments_type_0:
                    segments_type_0_item = SegmentIn.from_dict(segments_type_0_item_data)

                    segments_type_0.append(segments_type_0_item)

                return segments_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[SegmentIn] | None | Unset, data)

        segments = _parse_segments(d.pop("segments", UNSET))

        schedule_in = cls(
            mode=mode,
            csv_text=csv_text,
            interpolation=interpolation,
            segments=segments,
        )

        return schedule_in
