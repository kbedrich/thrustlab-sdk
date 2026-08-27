from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.sweep_point_component_selection import SweepPointComponentSelection


T = TypeVar("T", bound="SweepPointInputs")


@_attrs_define
class SweepPointInputs:
    """ESC-13 item 4 — the operating condition this grid point was solved at.

    Previously typed ``dict[str, Any]``, which is the wire equivalent of saying
    nothing: an SDK user got an untyped bag and had to learn the key set by
    running a sweep and reading one. ESC-13 already made the RUNTIME blob
    self-describing (it is built from the point rather than from a hardcoded
    five-key literal, so a new axis appears the day it lands); this makes the
    CONTRACT say so too.

    ``extra="allow"`` is load-bearing, not laziness. Two families of key are
    generated per-sweep and cannot be enumerated in a static model:

      * ``tilt_<group_index>`` — group-targeted tilt is one grid dimension per
        MASKED rotor group, so the key set depends on the mask.
      * ``component_<axis>_<slots>`` — a component axis contributes its selected
        index under a name encoding the slots it spans (``component_motor_0``,
        or ``component_motor_0-2`` when synced).

    Declaring those away would be worse than leaving the model untyped, because
    a strict model would DROP them at serialization — the same failure mode as
    the 2026-06-02 aggregate-drop that ``rotors`` is deliberately non-coercing to
    avoid. Every declared field is optional and permissively typed for the same
    reason: this model documents the shape, it does not police it.

        Attributes:
            airspeed (float | None | Unset): Forward airspeed at this point, m/s.
            battery_charge_pct (float | None | Unset): Pack state of charge at this point, %.
            component (list[SweepPointComponentSelection] | Unset): Components selected at this point, one entry per swept
                slot. Empty when no component axis is active.
            density (float | None | Unset): Air density at this point, kg/m^3.
            esc_pwm_frequency_khz (float | None | Unset): ESC switching frequency at this point, kHz. Present only when an
                ESC PWM axis is swept.
            esc_timing (None | str | Unset): Six-step commutation timing preset at this point ("low", "medium", "high",
                "auto"). Present only when an ESC timing axis is swept — absent means each rotor group used its own persisted
                setting.
            grid_index (list[int] | None | Unset): Multi-dimensional coordinate of this point in the sweep grid, one entry
                per axis in the order the axes were declared. The flat `index` on the point itself is the pagination counter,
                not this.
            throttle (float | None | Unset): Commanded throttle % at this point. Always present. NOTE: this is the value of
                the throttle AXIS when one is swept; with no throttle axis it echoes rotor group 0's persisted throttle and
                applies to no other group (DM-6) — read the per-rotor results for what each group actually ran at.
            vertical_speed (float | None | Unset): Signed vertical speed at this point, m/s (positive = climb).
    """

    airspeed: float | None | Unset = UNSET
    battery_charge_pct: float | None | Unset = UNSET
    component: list[SweepPointComponentSelection] | Unset = UNSET
    density: float | None | Unset = UNSET
    esc_pwm_frequency_khz: float | None | Unset = UNSET
    esc_timing: None | str | Unset = UNSET
    grid_index: list[int] | None | Unset = UNSET
    throttle: float | None | Unset = UNSET
    vertical_speed: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        airspeed: float | None | Unset
        if isinstance(self.airspeed, Unset):
            airspeed = UNSET
        else:
            airspeed = self.airspeed

        battery_charge_pct: float | None | Unset
        if isinstance(self.battery_charge_pct, Unset):
            battery_charge_pct = UNSET
        else:
            battery_charge_pct = self.battery_charge_pct

        component: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.component, Unset):
            component = []
            for component_item_data in self.component:
                component_item = component_item_data.to_dict()
                component.append(component_item)

        density: float | None | Unset
        if isinstance(self.density, Unset):
            density = UNSET
        else:
            density = self.density

        esc_pwm_frequency_khz: float | None | Unset
        if isinstance(self.esc_pwm_frequency_khz, Unset):
            esc_pwm_frequency_khz = UNSET
        else:
            esc_pwm_frequency_khz = self.esc_pwm_frequency_khz

        esc_timing: None | str | Unset
        if isinstance(self.esc_timing, Unset):
            esc_timing = UNSET
        else:
            esc_timing = self.esc_timing

        grid_index: list[int] | None | Unset
        if isinstance(self.grid_index, Unset):
            grid_index = UNSET
        elif isinstance(self.grid_index, list):
            grid_index = self.grid_index

        else:
            grid_index = self.grid_index

        throttle: float | None | Unset
        if isinstance(self.throttle, Unset):
            throttle = UNSET
        else:
            throttle = self.throttle

        vertical_speed: float | None | Unset
        if isinstance(self.vertical_speed, Unset):
            vertical_speed = UNSET
        else:
            vertical_speed = self.vertical_speed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if airspeed is not UNSET:
            field_dict["airspeed"] = airspeed
        if battery_charge_pct is not UNSET:
            field_dict["battery_charge_pct"] = battery_charge_pct
        if component is not UNSET:
            field_dict["component"] = component
        if density is not UNSET:
            field_dict["density"] = density
        if esc_pwm_frequency_khz is not UNSET:
            field_dict["esc_pwm_frequency_khz"] = esc_pwm_frequency_khz
        if esc_timing is not UNSET:
            field_dict["esc_timing"] = esc_timing
        if grid_index is not UNSET:
            field_dict["grid_index"] = grid_index
        if throttle is not UNSET:
            field_dict["throttle"] = throttle
        if vertical_speed is not UNSET:
            field_dict["vertical_speed"] = vertical_speed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.sweep_point_component_selection import SweepPointComponentSelection

        d = dict(src_dict)

        def _parse_airspeed(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        airspeed = _parse_airspeed(d.pop("airspeed", UNSET))

        def _parse_battery_charge_pct(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        battery_charge_pct = _parse_battery_charge_pct(d.pop("battery_charge_pct", UNSET))

        _component = d.pop("component", UNSET)
        component: list[SweepPointComponentSelection] | Unset = UNSET
        if _component is not UNSET:
            component = []
            for component_item_data in _component:
                component_item = SweepPointComponentSelection.from_dict(component_item_data)

                component.append(component_item)

        def _parse_density(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        density = _parse_density(d.pop("density", UNSET))

        def _parse_esc_pwm_frequency_khz(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        esc_pwm_frequency_khz = _parse_esc_pwm_frequency_khz(d.pop("esc_pwm_frequency_khz", UNSET))

        def _parse_esc_timing(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        esc_timing = _parse_esc_timing(d.pop("esc_timing", UNSET))

        def _parse_grid_index(data: object) -> list[int] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                grid_index_type_0 = cast(list[int], data)

                return grid_index_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[int] | None | Unset, data)

        grid_index = _parse_grid_index(d.pop("grid_index", UNSET))

        def _parse_throttle(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        throttle = _parse_throttle(d.pop("throttle", UNSET))

        def _parse_vertical_speed(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        vertical_speed = _parse_vertical_speed(d.pop("vertical_speed", UNSET))

        sweep_point_inputs = cls(
            airspeed=airspeed,
            battery_charge_pct=battery_charge_pct,
            component=component,
            density=density,
            esc_pwm_frequency_khz=esc_pwm_frequency_khz,
            esc_timing=esc_timing,
            grid_index=grid_index,
            throttle=throttle,
            vertical_speed=vertical_speed,
        )

        sweep_point_inputs.additional_properties = d
        return sweep_point_inputs

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
