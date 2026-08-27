from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.sweep_rotor_in_esc_timing import SweepRotorInEscTiming
from thrustlab._models.sweep_rotor_in_esc_type import SweepRotorInEscType
from thrustlab._models.sweep_rotor_in_motor_cooling_source import SweepRotorInMotorCoolingSource
from thrustlab._models.sweep_rotor_in_rotation_sense import SweepRotorInRotationSense
from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.v1_custom_component_override import V1CustomComponentOverride


T = TypeVar("T", bound="SweepRotorIn")


@_attrs_define
class SweepRotorIn:
    """A sweep rotor carries the SAME field set as the single-point ``RotorIn``.

    Same reason as ``SweepRotorGroupIn``: the axes live on the body. Declared as
    its own name so the OpenAPI schema (and therefore the SDK) keeps the sweep
    and single-point request shapes separately addressable, matching the
    existing group-side convention.

        Attributes:
            label (str):
            propeller_component_id (str):
            throttle_pct (float):
            coax_position_m (float | Unset): Position along the coaxial stack axis in metres, increasing downstream (in the
                direction the slipstream travels). The spacing between two rotors is the difference of their positions. Ignored
                when coax_stack_id is 0. Default: 0.0.
            coax_stack_id (int | Unset): Coaxial stack this rotor belongs to. 0 (default) means the rotor is not stacked and
                is simulated in isolation. Rotors sharing a non-zero value form one contra-rotating or co-rotating stack.
                Default: 0.
            custom_motor (None | Unset | V1CustomComponentOverride):
            custom_propeller (None | Unset | V1CustomComponentOverride):
            esc_motor_wire_resistance_mohm (float | Unset):  Default: 0.0.
            esc_pwm_frequency_khz (float | Unset): ESC switching frequency (kHz) Default: 24.0.
            esc_resistance_mohm (float | Unset):  Default: 0.0.
            esc_sync_rectification (bool | Unset): Synchronous rectification (comp_pwm); default ON Default: True.
            esc_timing (SweepRotorInEscTiming | Unset): Six-step commutation advance preset (low 7.5°/medium 15°/high
                22.5°/auto duty-scheduled); FOC ignores it Default: SweepRotorInEscTiming.MEDIUM.
            esc_type (SweepRotorInEscType | Unset): ESC commutation type. Selects K_volt, copper_mult, iron_mult, the six-
                step commutation-advance physics and the throttle->duty map — not a cosmetic flag. Single-sourced (ESC-7):
                app/constants_esc.py. Default: SweepRotorInEscType.SIX_STEP.
            motor_component_id (None | str | Unset):
            motor_cooling_source (SweepRotorInMotorCoolingSource | Unset): Per-rotor-group motor cooling mode. cowling =
                still air; prop_exit_velocity = forced convection from the prop slipstream (default); custom = fixed velocity or
                direct thermal resistance. Default: SweepRotorInMotorCoolingSource.PROP_EXIT_VELOCITY.
            motor_cooling_velocity_m_s (float | None | Unset): Custom motor cooling convection velocity (m/s); only used
                when motor_cooling_source=custom.
            motor_r_th (float | None | Unset): Custom direct motor thermal resistance override (K/W); only used when
                motor_cooling_source=custom.
            motor_t_mag (float | None | Unset): Optional fixed magnet temperature (°C, -60…250); omit to let the model
                compute it.
            motor_t_w (float | None | Unset): Optional fixed winding temperature (°C, -60…250); omit to let the model
                compute it.
            rotation_sense (SweepRotorInRotationSense | Unset): Direction of rotation about the downstream axis: 1 or -1.
                Opposite values in one stack give a contra-rotating pair, which recovers swirl energy and is the usual choice.
                Only read by coaxial pairing — a single rotor's value does not affect its own performance. Default:
                SweepRotorInRotationSense.VALUE_1.
            tilt_deg (float | Unset): Ground-mode rotor-axis tilt measured from the horizontal-forward (flight) direction
                (0° = forward/cruise — the axis lies along the flight path and all airspeed becomes axial inflow; 90° =
                lift/hover — the axis points up and forward airspeed becomes pure edgewise inflow). Decomposed host-side to
                V_axial = V_h·cosθ + V_v·sinθ, V_edge = |V_v·cosθ − V_h·sinθ|. Default: 0.0.
            v_axial_m_s (float | None | Unset): Components-mode signed axial inflow (m/s); only with
                inflow_mode='components'.
            v_edge_m_s (float | None | Unset): Components-mode edgewise inflow magnitude (m/s, ≥0); only with
                inflow_mode='components'.
    """

    label: str
    propeller_component_id: str
    throttle_pct: float
    coax_position_m: float | Unset = 0.0
    coax_stack_id: int | Unset = 0
    custom_motor: None | Unset | V1CustomComponentOverride = UNSET
    custom_propeller: None | Unset | V1CustomComponentOverride = UNSET
    esc_motor_wire_resistance_mohm: float | Unset = 0.0
    esc_pwm_frequency_khz: float | Unset = 24.0
    esc_resistance_mohm: float | Unset = 0.0
    esc_sync_rectification: bool | Unset = True
    esc_timing: SweepRotorInEscTiming | Unset = SweepRotorInEscTiming.MEDIUM
    esc_type: SweepRotorInEscType | Unset = SweepRotorInEscType.SIX_STEP
    motor_component_id: None | str | Unset = UNSET
    motor_cooling_source: SweepRotorInMotorCoolingSource | Unset = SweepRotorInMotorCoolingSource.PROP_EXIT_VELOCITY
    motor_cooling_velocity_m_s: float | None | Unset = UNSET
    motor_r_th: float | None | Unset = UNSET
    motor_t_mag: float | None | Unset = UNSET
    motor_t_w: float | None | Unset = UNSET
    rotation_sense: SweepRotorInRotationSense | Unset = SweepRotorInRotationSense.VALUE_1
    tilt_deg: float | Unset = 0.0
    v_axial_m_s: float | None | Unset = UNSET
    v_edge_m_s: float | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.v1_custom_component_override import V1CustomComponentOverride

        label = self.label

        propeller_component_id = self.propeller_component_id

        throttle_pct = self.throttle_pct

        coax_position_m = self.coax_position_m

        coax_stack_id = self.coax_stack_id

        custom_motor: dict[str, Any] | None | Unset
        if isinstance(self.custom_motor, Unset):
            custom_motor = UNSET
        elif isinstance(self.custom_motor, V1CustomComponentOverride):
            custom_motor = self.custom_motor.to_dict()
        else:
            custom_motor = self.custom_motor

        custom_propeller: dict[str, Any] | None | Unset
        if isinstance(self.custom_propeller, Unset):
            custom_propeller = UNSET
        elif isinstance(self.custom_propeller, V1CustomComponentOverride):
            custom_propeller = self.custom_propeller.to_dict()
        else:
            custom_propeller = self.custom_propeller

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

        motor_t_mag: float | None | Unset
        if isinstance(self.motor_t_mag, Unset):
            motor_t_mag = UNSET
        else:
            motor_t_mag = self.motor_t_mag

        motor_t_w: float | None | Unset
        if isinstance(self.motor_t_w, Unset):
            motor_t_w = UNSET
        else:
            motor_t_w = self.motor_t_w

        rotation_sense: int | Unset = UNSET
        if not isinstance(self.rotation_sense, Unset):
            rotation_sense = self.rotation_sense.value

        tilt_deg = self.tilt_deg

        v_axial_m_s: float | None | Unset
        if isinstance(self.v_axial_m_s, Unset):
            v_axial_m_s = UNSET
        else:
            v_axial_m_s = self.v_axial_m_s

        v_edge_m_s: float | None | Unset
        if isinstance(self.v_edge_m_s, Unset):
            v_edge_m_s = UNSET
        else:
            v_edge_m_s = self.v_edge_m_s

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "label": label,
                "propeller_component_id": propeller_component_id,
                "throttle_pct": throttle_pct,
            }
        )
        if coax_position_m is not UNSET:
            field_dict["coax_position_m"] = coax_position_m
        if coax_stack_id is not UNSET:
            field_dict["coax_stack_id"] = coax_stack_id
        if custom_motor is not UNSET:
            field_dict["custom_motor"] = custom_motor
        if custom_propeller is not UNSET:
            field_dict["custom_propeller"] = custom_propeller
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
        if motor_t_mag is not UNSET:
            field_dict["motor_t_mag"] = motor_t_mag
        if motor_t_w is not UNSET:
            field_dict["motor_t_w"] = motor_t_w
        if rotation_sense is not UNSET:
            field_dict["rotation_sense"] = rotation_sense
        if tilt_deg is not UNSET:
            field_dict["tilt_deg"] = tilt_deg
        if v_axial_m_s is not UNSET:
            field_dict["v_axial_m_s"] = v_axial_m_s
        if v_edge_m_s is not UNSET:
            field_dict["v_edge_m_s"] = v_edge_m_s

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.v1_custom_component_override import V1CustomComponentOverride

        d = dict(src_dict)
        label = d.pop("label")

        propeller_component_id = d.pop("propeller_component_id")

        throttle_pct = d.pop("throttle_pct")

        coax_position_m = d.pop("coax_position_m", UNSET)

        coax_stack_id = d.pop("coax_stack_id", UNSET)

        def _parse_custom_motor(data: object) -> None | Unset | V1CustomComponentOverride:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                custom_motor_type_0 = V1CustomComponentOverride.from_dict(data)

                return custom_motor_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | V1CustomComponentOverride, data)

        custom_motor = _parse_custom_motor(d.pop("custom_motor", UNSET))

        def _parse_custom_propeller(data: object) -> None | Unset | V1CustomComponentOverride:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                custom_propeller_type_0 = V1CustomComponentOverride.from_dict(data)

                return custom_propeller_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | V1CustomComponentOverride, data)

        custom_propeller = _parse_custom_propeller(d.pop("custom_propeller", UNSET))

        esc_motor_wire_resistance_mohm = d.pop("esc_motor_wire_resistance_mohm", UNSET)

        esc_pwm_frequency_khz = d.pop("esc_pwm_frequency_khz", UNSET)

        esc_resistance_mohm = d.pop("esc_resistance_mohm", UNSET)

        esc_sync_rectification = d.pop("esc_sync_rectification", UNSET)

        _esc_timing = d.pop("esc_timing", UNSET)
        esc_timing: SweepRotorInEscTiming | Unset
        if isinstance(_esc_timing, Unset):
            esc_timing = UNSET
        else:
            esc_timing = SweepRotorInEscTiming(_esc_timing)

        _esc_type = d.pop("esc_type", UNSET)
        esc_type: SweepRotorInEscType | Unset
        if isinstance(_esc_type, Unset):
            esc_type = UNSET
        else:
            esc_type = SweepRotorInEscType(_esc_type)

        def _parse_motor_component_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        motor_component_id = _parse_motor_component_id(d.pop("motor_component_id", UNSET))

        _motor_cooling_source = d.pop("motor_cooling_source", UNSET)
        motor_cooling_source: SweepRotorInMotorCoolingSource | Unset
        if isinstance(_motor_cooling_source, Unset):
            motor_cooling_source = UNSET
        else:
            motor_cooling_source = SweepRotorInMotorCoolingSource(_motor_cooling_source)

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

        def _parse_motor_t_mag(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        motor_t_mag = _parse_motor_t_mag(d.pop("motor_t_mag", UNSET))

        def _parse_motor_t_w(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        motor_t_w = _parse_motor_t_w(d.pop("motor_t_w", UNSET))

        _rotation_sense = d.pop("rotation_sense", UNSET)
        rotation_sense: SweepRotorInRotationSense | Unset
        if isinstance(_rotation_sense, Unset):
            rotation_sense = UNSET
        else:
            rotation_sense = SweepRotorInRotationSense(_rotation_sense)

        tilt_deg = d.pop("tilt_deg", UNSET)

        def _parse_v_axial_m_s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        v_axial_m_s = _parse_v_axial_m_s(d.pop("v_axial_m_s", UNSET))

        def _parse_v_edge_m_s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        v_edge_m_s = _parse_v_edge_m_s(d.pop("v_edge_m_s", UNSET))

        sweep_rotor_in = cls(
            label=label,
            propeller_component_id=propeller_component_id,
            throttle_pct=throttle_pct,
            coax_position_m=coax_position_m,
            coax_stack_id=coax_stack_id,
            custom_motor=custom_motor,
            custom_propeller=custom_propeller,
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
            motor_t_mag=motor_t_mag,
            motor_t_w=motor_t_w,
            rotation_sense=rotation_sense,
            tilt_deg=tilt_deg,
            v_axial_m_s=v_axial_m_s,
            v_edge_m_s=v_edge_m_s,
        )

        return sweep_rotor_in
