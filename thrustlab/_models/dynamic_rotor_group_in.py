from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.dynamic_rotor_group_in_motor_cooling_source import DynamicRotorGroupInMotorCoolingSource
from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="DynamicRotorGroupIn")


@_attrs_define
class DynamicRotorGroupIn:
    """A rotor group for a dynamic run. The dynamic run takes exactly the shared
    ``RotorGroupBase`` fields — label / count (bounded 1..16) / motor+propeller ids
    / the per-group motor-cooling trio + cooling validator — and nothing more: the
    schedule supplies throttle over time, so there is no static ``throttle_pct``,
    ESC block, pinned motor temperatures, or oblique flight-condition fields on the
    dynamic group.

        Attributes:
            label (str):
            propeller_component_id (str):
            count (int | Unset):  Default: 1.
            motor_component_id (None | str | Unset):
            motor_cooling_source (DynamicRotorGroupInMotorCoolingSource | Unset): Per-rotor-group motor cooling mode.
                cowling = still air; prop_exit_velocity = forced convection from the prop slipstream (default); custom = fixed
                velocity or direct thermal resistance. Default: DynamicRotorGroupInMotorCoolingSource.PROP_EXIT_VELOCITY.
            motor_cooling_velocity_m_s (float | None | Unset): Custom motor cooling convection velocity (m/s); only used
                when motor_cooling_source=custom.
            motor_r_th (float | None | Unset): Custom direct motor thermal resistance override (K/W); only used when
                motor_cooling_source=custom.
    """

    label: str
    propeller_component_id: str
    count: int | Unset = 1
    motor_component_id: None | str | Unset = UNSET
    motor_cooling_source: DynamicRotorGroupInMotorCoolingSource | Unset = (
        DynamicRotorGroupInMotorCoolingSource.PROP_EXIT_VELOCITY
    )
    motor_cooling_velocity_m_s: float | None | Unset = UNSET
    motor_r_th: float | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        propeller_component_id = self.propeller_component_id

        count = self.count

        motor_component_id: None | str | Unset
        if isinstance(self.motor_component_id, Unset):
            motor_component_id = UNSET
        else:
            motor_component_id = self.motor_component_id

        motor_cooling_source: str | Unset = UNSET
        if not isinstance(self.motor_cooling_source, Unset):
            motor_cooling_source = self.motor_cooling_source.value

        motor_cooling_velocity_m_s: float | None | Unset
        if isinstance(self.motor_cooling_velocity_m_s, Unset):
            motor_cooling_velocity_m_s = UNSET
        else:
            motor_cooling_velocity_m_s = self.motor_cooling_velocity_m_s

        motor_r_th: float | None | Unset
        if isinstance(self.motor_r_th, Unset):
            motor_r_th = UNSET
        else:
            motor_r_th = self.motor_r_th

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "label": label,
                "propeller_component_id": propeller_component_id,
            }
        )
        if count is not UNSET:
            field_dict["count"] = count
        if motor_component_id is not UNSET:
            field_dict["motor_component_id"] = motor_component_id
        if motor_cooling_source is not UNSET:
            field_dict["motor_cooling_source"] = motor_cooling_source
        if motor_cooling_velocity_m_s is not UNSET:
            field_dict["motor_cooling_velocity_m_s"] = motor_cooling_velocity_m_s
        if motor_r_th is not UNSET:
            field_dict["motor_r_th"] = motor_r_th

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label = d.pop("label")

        propeller_component_id = d.pop("propeller_component_id")

        count = d.pop("count", UNSET)

        def _parse_motor_component_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        motor_component_id = _parse_motor_component_id(d.pop("motor_component_id", UNSET))

        _motor_cooling_source = d.pop("motor_cooling_source", UNSET)
        motor_cooling_source: DynamicRotorGroupInMotorCoolingSource | Unset
        if isinstance(_motor_cooling_source, Unset):
            motor_cooling_source = UNSET
        else:
            motor_cooling_source = DynamicRotorGroupInMotorCoolingSource(_motor_cooling_source)

        def _parse_motor_cooling_velocity_m_s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        motor_cooling_velocity_m_s = _parse_motor_cooling_velocity_m_s(d.pop("motor_cooling_velocity_m_s", UNSET))

        def _parse_motor_r_th(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        motor_r_th = _parse_motor_r_th(d.pop("motor_r_th", UNSET))

        dynamic_rotor_group_in = cls(
            label=label,
            propeller_component_id=propeller_component_id,
            count=count,
            motor_component_id=motor_component_id,
            motor_cooling_source=motor_cooling_source,
            motor_cooling_velocity_m_s=motor_cooling_velocity_m_s,
            motor_r_th=motor_r_th,
        )

        return dynamic_rotor_group_in
