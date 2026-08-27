from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.dynamic_rotor_in_esc_timing import DynamicRotorInEscTiming
from thrustlab._models.dynamic_rotor_in_esc_type import DynamicRotorInEscType
from thrustlab._models.dynamic_rotor_in_motor_cooling_source import DynamicRotorInMotorCoolingSource
from thrustlab._models.dynamic_rotor_in_rotation_sense import DynamicRotorInRotationSense
from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="DynamicRotorIn")


@_attrs_define
class DynamicRotorIn:
    """ONE rotor for a dynamic run.

    Mirrors ``DynamicRotorGroupIn``: no static throttle, no pinned motor
    temperatures, no oblique flight-condition fields — the schedule supplies all
    of those over time. It DOES take the coaxial trio, because a stack's
    geometry is a property of the machine, not of the operating point.

        Attributes:
            label (str):
            propeller_component_id (str):
            coax_position_m (float | Unset): Position along the coaxial stack axis in metres, increasing downstream (in the
                direction the slipstream travels). The spacing between two rotors is the difference of their positions. Ignored
                when coax_stack_id is 0. Default: 0.0.
            coax_stack_id (int | Unset): Coaxial stack this rotor belongs to. 0 (default) means the rotor is not stacked and
                is simulated in isolation. Rotors sharing a non-zero value form one contra-rotating or co-rotating stack.
                Default: 0.
            esc_motor_wire_resistance_mohm (float | Unset):  Default: 0.0.
            esc_pwm_frequency_khz (float | Unset): ESC switching frequency (kHz) Default: 24.0.
            esc_resistance_mohm (float | Unset):  Default: 0.0.
            esc_sync_rectification (bool | Unset): Synchronous rectification (comp_pwm); default ON Default: True.
            esc_timing (DynamicRotorInEscTiming | Unset): Six-step commutation advance preset (low 7.5°/medium 15°/high
                22.5°/auto duty-scheduled); FOC ignores it Default: DynamicRotorInEscTiming.MEDIUM.
            esc_type (DynamicRotorInEscType | Unset): ESC commutation type. Selects K_volt, copper_mult, iron_mult, the six-
                step commutation-advance physics and the throttle->duty map — not a cosmetic flag. Single-sourced (ESC-7):
                app/constants_esc.py. Default: DynamicRotorInEscType.SIX_STEP.
            motor_component_id (None | str | Unset):
            motor_cooling_source (DynamicRotorInMotorCoolingSource | Unset): Per-rotor-group motor cooling mode. cowling =
                still air; prop_exit_velocity = forced convection from the prop slipstream (default); custom = fixed velocity or
                direct thermal resistance. Default: DynamicRotorInMotorCoolingSource.PROP_EXIT_VELOCITY.
            motor_cooling_velocity_m_s (float | None | Unset): Custom motor cooling convection velocity (m/s); only used
                when motor_cooling_source=custom.
            motor_r_th (float | None | Unset): Custom direct motor thermal resistance override (K/W); only used when
                motor_cooling_source=custom.
            rotation_sense (DynamicRotorInRotationSense | Unset): Direction of rotation about the downstream axis: 1 or -1.
                Opposite values in one stack give a contra-rotating pair, which recovers swirl energy and is the usual choice.
                Only read by coaxial pairing — a single rotor's value does not affect its own performance. Default:
                DynamicRotorInRotationSense.VALUE_1.
    """

    label: str
    propeller_component_id: str
    coax_position_m: float | Unset = 0.0
    coax_stack_id: int | Unset = 0
    esc_motor_wire_resistance_mohm: float | Unset = 0.0
    esc_pwm_frequency_khz: float | Unset = 24.0
    esc_resistance_mohm: float | Unset = 0.0
    esc_sync_rectification: bool | Unset = True
    esc_timing: DynamicRotorInEscTiming | Unset = DynamicRotorInEscTiming.MEDIUM
    esc_type: DynamicRotorInEscType | Unset = DynamicRotorInEscType.SIX_STEP
    motor_component_id: None | str | Unset = UNSET
    motor_cooling_source: DynamicRotorInMotorCoolingSource | Unset = DynamicRotorInMotorCoolingSource.PROP_EXIT_VELOCITY
    motor_cooling_velocity_m_s: float | None | Unset = UNSET
    motor_r_th: float | None | Unset = UNSET
    rotation_sense: DynamicRotorInRotationSense | Unset = DynamicRotorInRotationSense.VALUE_1

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        propeller_component_id = self.propeller_component_id

        coax_position_m = self.coax_position_m

        coax_stack_id = self.coax_stack_id

        esc_motor_wire_resistance_mohm = self.esc_motor_wire_resistance_mohm

        esc_pwm_frequency_khz = self.esc_pwm_frequency_khz

        esc_resistance_mohm = self.esc_resistance_mohm

        esc_sync_rectification = self.esc_sync_rectification

        esc_timing: str | Unset = UNSET
        if not isinstance(self.esc_timing, Unset):
            esc_timing = self.esc_timing.value

        esc_type: str | Unset = UNSET
        if not isinstance(self.esc_type, Unset):
            esc_type = self.esc_type.value

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

        rotation_sense: int | Unset = UNSET
        if not isinstance(self.rotation_sense, Unset):
            rotation_sense = self.rotation_sense.value

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "label": label,
                "propeller_component_id": propeller_component_id,
            }
        )
        if coax_position_m is not UNSET:
            field_dict["coax_position_m"] = coax_position_m
        if coax_stack_id is not UNSET:
            field_dict["coax_stack_id"] = coax_stack_id
        if esc_motor_wire_resistance_mohm is not UNSET:
            field_dict["esc_motor_wire_resistance_mohm"] = esc_motor_wire_resistance_mohm
        if esc_pwm_frequency_khz is not UNSET:
            field_dict["esc_pwm_frequency_khz"] = esc_pwm_frequency_khz
        if esc_resistance_mohm is not UNSET:
            field_dict["esc_resistance_mohm"] = esc_resistance_mohm
        if esc_sync_rectification is not UNSET:
            field_dict["esc_sync_rectification"] = esc_sync_rectification
        if esc_timing is not UNSET:
            field_dict["esc_timing"] = esc_timing
        if esc_type is not UNSET:
            field_dict["esc_type"] = esc_type
        if motor_component_id is not UNSET:
            field_dict["motor_component_id"] = motor_component_id
        if motor_cooling_source is not UNSET:
            field_dict["motor_cooling_source"] = motor_cooling_source
        if motor_cooling_velocity_m_s is not UNSET:
            field_dict["motor_cooling_velocity_m_s"] = motor_cooling_velocity_m_s
        if motor_r_th is not UNSET:
            field_dict["motor_r_th"] = motor_r_th
        if rotation_sense is not UNSET:
            field_dict["rotation_sense"] = rotation_sense

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label = d.pop("label")

        propeller_component_id = d.pop("propeller_component_id")

        coax_position_m = d.pop("coax_position_m", UNSET)

        coax_stack_id = d.pop("coax_stack_id", UNSET)

        esc_motor_wire_resistance_mohm = d.pop("esc_motor_wire_resistance_mohm", UNSET)

        esc_pwm_frequency_khz = d.pop("esc_pwm_frequency_khz", UNSET)

        esc_resistance_mohm = d.pop("esc_resistance_mohm", UNSET)

        esc_sync_rectification = d.pop("esc_sync_rectification", UNSET)

        _esc_timing = d.pop("esc_timing", UNSET)
        esc_timing: DynamicRotorInEscTiming | Unset
        if isinstance(_esc_timing, Unset):
            esc_timing = UNSET
        else:
            esc_timing = DynamicRotorInEscTiming(_esc_timing)

        _esc_type = d.pop("esc_type", UNSET)
        esc_type: DynamicRotorInEscType | Unset
        if isinstance(_esc_type, Unset):
            esc_type = UNSET
        else:
            esc_type = DynamicRotorInEscType(_esc_type)

        def _parse_motor_component_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        motor_component_id = _parse_motor_component_id(d.pop("motor_component_id", UNSET))

        _motor_cooling_source = d.pop("motor_cooling_source", UNSET)
        motor_cooling_source: DynamicRotorInMotorCoolingSource | Unset
        if isinstance(_motor_cooling_source, Unset):
            motor_cooling_source = UNSET
        else:
            motor_cooling_source = DynamicRotorInMotorCoolingSource(_motor_cooling_source)

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

        _rotation_sense = d.pop("rotation_sense", UNSET)
        rotation_sense: DynamicRotorInRotationSense | Unset
        if isinstance(_rotation_sense, Unset):
            rotation_sense = UNSET
        else:
            rotation_sense = DynamicRotorInRotationSense(_rotation_sense)

        dynamic_rotor_in = cls(
            label=label,
            propeller_component_id=propeller_component_id,
            coax_position_m=coax_position_m,
            coax_stack_id=coax_stack_id,
            esc_motor_wire_resistance_mohm=esc_motor_wire_resistance_mohm,
            esc_pwm_frequency_khz=esc_pwm_frequency_khz,
            esc_resistance_mohm=esc_resistance_mohm,
            esc_sync_rectification=esc_sync_rectification,
            esc_timing=esc_timing,
            esc_type=esc_type,
            motor_component_id=motor_component_id,
            motor_cooling_source=motor_cooling_source,
            motor_cooling_velocity_m_s=motor_cooling_velocity_m_s,
            motor_r_th=motor_r_th,
            rotation_sense=rotation_sense,
        )

        return dynamic_rotor_in
