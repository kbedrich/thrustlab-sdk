from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.sweep_config_in_esc_timing_values_type_0_item import SweepConfigInEscTimingValuesType0Item
from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.component_sweep_axis_in import ComponentSweepAxisIn
    from thrustlab._models.sweep_param_range_in import SweepParamRangeIn


T = TypeVar("T", bound="SweepConfigIn")


@_attrs_define
class SweepConfigIn:
    """
    Attributes:
        rotor_sweep_mask (list[bool]):
        airspeed (None | SweepParamRangeIn | Unset):
        battery_charge (None | SweepParamRangeIn | Unset):
        component_axes (list[ComponentSweepAxisIn] | Unset):
        density (None | SweepParamRangeIn | Unset):
        esc_pwm_frequency_khz (None | SweepParamRangeIn | Unset):
        esc_timing_values (list[SweepConfigInEscTimingValuesType0Item] | None | Unset):
        throttle (None | SweepParamRangeIn | Unset):
        tilt (None | SweepParamRangeIn | Unset):
        tilt_sweep_mask (list[bool] | Unset):
        vertical_speed (None | SweepParamRangeIn | Unset):
    """

    rotor_sweep_mask: list[bool]
    airspeed: None | SweepParamRangeIn | Unset = UNSET
    battery_charge: None | SweepParamRangeIn | Unset = UNSET
    component_axes: list[ComponentSweepAxisIn] | Unset = UNSET
    density: None | SweepParamRangeIn | Unset = UNSET
    esc_pwm_frequency_khz: None | SweepParamRangeIn | Unset = UNSET
    esc_timing_values: list[SweepConfigInEscTimingValuesType0Item] | None | Unset = UNSET
    throttle: None | SweepParamRangeIn | Unset = UNSET
    tilt: None | SweepParamRangeIn | Unset = UNSET
    tilt_sweep_mask: list[bool] | Unset = UNSET
    vertical_speed: None | SweepParamRangeIn | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.sweep_param_range_in import SweepParamRangeIn

        rotor_sweep_mask = self.rotor_sweep_mask

        airspeed: dict[str, Any] | None | Unset
        if isinstance(self.airspeed, Unset):
            airspeed = UNSET
        elif isinstance(self.airspeed, SweepParamRangeIn):
            airspeed = self.airspeed.to_dict()
        else:
            airspeed = self.airspeed

        battery_charge: dict[str, Any] | None | Unset
        if isinstance(self.battery_charge, Unset):
            battery_charge = UNSET
        elif isinstance(self.battery_charge, SweepParamRangeIn):
            battery_charge = self.battery_charge.to_dict()
        else:
            battery_charge = self.battery_charge

        component_axes: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.component_axes, Unset):
            component_axes = []
            for component_axes_item_data in self.component_axes:
                component_axes_item = component_axes_item_data.to_dict()
                component_axes.append(component_axes_item)

        density: dict[str, Any] | None | Unset
        if isinstance(self.density, Unset):
            density = UNSET
        elif isinstance(self.density, SweepParamRangeIn):
            density = self.density.to_dict()
        else:
            density = self.density

        esc_pwm_frequency_khz: dict[str, Any] | None | Unset
        if isinstance(self.esc_pwm_frequency_khz, Unset):
            esc_pwm_frequency_khz = UNSET
        elif isinstance(self.esc_pwm_frequency_khz, SweepParamRangeIn):
            esc_pwm_frequency_khz = self.esc_pwm_frequency_khz.to_dict()
        else:
            esc_pwm_frequency_khz = self.esc_pwm_frequency_khz

        esc_timing_values: list[str] | None | Unset
        if isinstance(self.esc_timing_values, Unset):
            esc_timing_values = UNSET
        elif isinstance(self.esc_timing_values, list):
            esc_timing_values = []
            for esc_timing_values_type_0_item_data in self.esc_timing_values:
                esc_timing_values_type_0_item = esc_timing_values_type_0_item_data.value
                esc_timing_values.append(esc_timing_values_type_0_item)

        else:
            esc_timing_values = self.esc_timing_values

        throttle: dict[str, Any] | None | Unset
        if isinstance(self.throttle, Unset):
            throttle = UNSET
        elif isinstance(self.throttle, SweepParamRangeIn):
            throttle = self.throttle.to_dict()
        else:
            throttle = self.throttle

        tilt: dict[str, Any] | None | Unset
        if isinstance(self.tilt, Unset):
            tilt = UNSET
        elif isinstance(self.tilt, SweepParamRangeIn):
            tilt = self.tilt.to_dict()
        else:
            tilt = self.tilt

        tilt_sweep_mask: list[bool] | Unset = UNSET
        if not isinstance(self.tilt_sweep_mask, Unset):
            tilt_sweep_mask = self.tilt_sweep_mask

        vertical_speed: dict[str, Any] | None | Unset
        if isinstance(self.vertical_speed, Unset):
            vertical_speed = UNSET
        elif isinstance(self.vertical_speed, SweepParamRangeIn):
            vertical_speed = self.vertical_speed.to_dict()
        else:
            vertical_speed = self.vertical_speed

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "rotor_sweep_mask": rotor_sweep_mask,
            }
        )
        if airspeed is not UNSET:
            field_dict["airspeed"] = airspeed
        if battery_charge is not UNSET:
            field_dict["battery_charge"] = battery_charge
        if component_axes is not UNSET:
            field_dict["component_axes"] = component_axes
        if density is not UNSET:
            field_dict["density"] = density
        if esc_pwm_frequency_khz is not UNSET:
            field_dict["esc_pwm_frequency_khz"] = esc_pwm_frequency_khz
        if esc_timing_values is not UNSET:
            field_dict["esc_timing_values"] = esc_timing_values
        if throttle is not UNSET:
            field_dict["throttle"] = throttle
        if tilt is not UNSET:
            field_dict["tilt"] = tilt
        if tilt_sweep_mask is not UNSET:
            field_dict["tilt_sweep_mask"] = tilt_sweep_mask
        if vertical_speed is not UNSET:
            field_dict["vertical_speed"] = vertical_speed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.component_sweep_axis_in import ComponentSweepAxisIn
        from thrustlab._models.sweep_param_range_in import SweepParamRangeIn

        d = dict(src_dict)
        rotor_sweep_mask = cast(list[bool], d.pop("rotor_sweep_mask"))

        def _parse_airspeed(data: object) -> None | SweepParamRangeIn | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                airspeed_type_0 = SweepParamRangeIn.from_dict(data)

                return airspeed_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SweepParamRangeIn | Unset, data)

        airspeed = _parse_airspeed(d.pop("airspeed", UNSET))

        def _parse_battery_charge(data: object) -> None | SweepParamRangeIn | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                battery_charge_type_0 = SweepParamRangeIn.from_dict(data)

                return battery_charge_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SweepParamRangeIn | Unset, data)

        battery_charge = _parse_battery_charge(d.pop("battery_charge", UNSET))

        _component_axes = d.pop("component_axes", UNSET)
        component_axes: list[ComponentSweepAxisIn] | Unset = UNSET
        if _component_axes is not UNSET:
            component_axes = []
            for component_axes_item_data in _component_axes:
                component_axes_item = ComponentSweepAxisIn.from_dict(component_axes_item_data)

                component_axes.append(component_axes_item)

        def _parse_density(data: object) -> None | SweepParamRangeIn | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                density_type_0 = SweepParamRangeIn.from_dict(data)

                return density_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SweepParamRangeIn | Unset, data)

        density = _parse_density(d.pop("density", UNSET))

        def _parse_esc_pwm_frequency_khz(data: object) -> None | SweepParamRangeIn | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                esc_pwm_frequency_khz_type_0 = SweepParamRangeIn.from_dict(data)

                return esc_pwm_frequency_khz_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SweepParamRangeIn | Unset, data)

        esc_pwm_frequency_khz = _parse_esc_pwm_frequency_khz(d.pop("esc_pwm_frequency_khz", UNSET))

        def _parse_esc_timing_values(data: object) -> list[SweepConfigInEscTimingValuesType0Item] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                esc_timing_values_type_0 = []
                _esc_timing_values_type_0 = data
                for esc_timing_values_type_0_item_data in _esc_timing_values_type_0:
                    esc_timing_values_type_0_item = SweepConfigInEscTimingValuesType0Item(
                        esc_timing_values_type_0_item_data
                    )

                    esc_timing_values_type_0.append(esc_timing_values_type_0_item)

                return esc_timing_values_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[SweepConfigInEscTimingValuesType0Item] | None | Unset, data)

        esc_timing_values = _parse_esc_timing_values(d.pop("esc_timing_values", UNSET))

        def _parse_throttle(data: object) -> None | SweepParamRangeIn | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                throttle_type_0 = SweepParamRangeIn.from_dict(data)

                return throttle_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SweepParamRangeIn | Unset, data)

        throttle = _parse_throttle(d.pop("throttle", UNSET))

        def _parse_tilt(data: object) -> None | SweepParamRangeIn | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                tilt_type_0 = SweepParamRangeIn.from_dict(data)

                return tilt_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SweepParamRangeIn | Unset, data)

        tilt = _parse_tilt(d.pop("tilt", UNSET))

        tilt_sweep_mask = cast(list[bool], d.pop("tilt_sweep_mask", UNSET))

        def _parse_vertical_speed(data: object) -> None | SweepParamRangeIn | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                vertical_speed_type_0 = SweepParamRangeIn.from_dict(data)

                return vertical_speed_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SweepParamRangeIn | Unset, data)

        vertical_speed = _parse_vertical_speed(d.pop("vertical_speed", UNSET))

        sweep_config_in = cls(
            rotor_sweep_mask=rotor_sweep_mask,
            airspeed=airspeed,
            battery_charge=battery_charge,
            component_axes=component_axes,
            density=density,
            esc_pwm_frequency_khz=esc_pwm_frequency_khz,
            esc_timing_values=esc_timing_values,
            throttle=throttle,
            tilt=tilt,
            tilt_sweep_mask=tilt_sweep_mask,
            vertical_speed=vertical_speed,
        )

        return sweep_config_in
