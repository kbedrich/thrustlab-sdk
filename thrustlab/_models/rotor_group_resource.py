from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

T = TypeVar("T", bound="RotorGroupResource")


@_attrs_define
class RotorGroupResource:
    """Reused by SimulationResource and SweepResource.

    Attributes:
        count (int):
        esc_motor_wire_resistance_mohm (float):
        esc_resistance_mohm (float):
        esc_type (str):
        label (str):
        motor_component_id (None | str):
        propeller_component_id (str):
        throttle_pct (float):
        coax_position_m (float | Unset):  Default: 0.0.
        coax_stack_id (int | Unset):  Default: 0.
        esc_pwm_frequency_khz (float | Unset):  Default: 24.0.
        esc_sync_rectification (bool | Unset):  Default: True.
        esc_timing (str | Unset):  Default: 'medium'.
        rotation_sense (int | Unset):  Default: 1.
    """

    count: int
    esc_motor_wire_resistance_mohm: float
    esc_resistance_mohm: float
    esc_type: str
    label: str
    motor_component_id: None | str
    propeller_component_id: str
    throttle_pct: float
    coax_position_m: float | Unset = 0.0
    coax_stack_id: int | Unset = 0
    esc_pwm_frequency_khz: float | Unset = 24.0
    esc_sync_rectification: bool | Unset = True
    esc_timing: str | Unset = "medium"
    rotation_sense: int | Unset = 1

    def to_dict(self) -> dict[str, Any]:
        count = self.count

        esc_motor_wire_resistance_mohm = self.esc_motor_wire_resistance_mohm

        esc_resistance_mohm = self.esc_resistance_mohm

        esc_type = self.esc_type

        label = self.label

        motor_component_id: None | str
        motor_component_id = self.motor_component_id

        propeller_component_id = self.propeller_component_id

        throttle_pct = self.throttle_pct

        coax_position_m = self.coax_position_m

        coax_stack_id = self.coax_stack_id

        esc_pwm_frequency_khz = self.esc_pwm_frequency_khz

        esc_sync_rectification = self.esc_sync_rectification

        esc_timing = self.esc_timing

        rotation_sense = self.rotation_sense

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "count": count,
                "esc_motor_wire_resistance_mohm": esc_motor_wire_resistance_mohm,
                "esc_resistance_mohm": esc_resistance_mohm,
                "esc_type": esc_type,
                "label": label,
                "motor_component_id": motor_component_id,
                "propeller_component_id": propeller_component_id,
                "throttle_pct": throttle_pct,
            }
        )
        if coax_position_m is not UNSET:
            field_dict["coax_position_m"] = coax_position_m
        if coax_stack_id is not UNSET:
            field_dict["coax_stack_id"] = coax_stack_id
        if esc_pwm_frequency_khz is not UNSET:
            field_dict["esc_pwm_frequency_khz"] = esc_pwm_frequency_khz
        if esc_sync_rectification is not UNSET:
            field_dict["esc_sync_rectification"] = esc_sync_rectification
        if esc_timing is not UNSET:
            field_dict["esc_timing"] = esc_timing
        if rotation_sense is not UNSET:
            field_dict["rotation_sense"] = rotation_sense

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        count = d.pop("count")

        esc_motor_wire_resistance_mohm = d.pop("esc_motor_wire_resistance_mohm")

        esc_resistance_mohm = d.pop("esc_resistance_mohm")

        esc_type = d.pop("esc_type")

        label = d.pop("label")

        def _parse_motor_component_id(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        motor_component_id = _parse_motor_component_id(d.pop("motor_component_id"))

        propeller_component_id = d.pop("propeller_component_id")

        throttle_pct = d.pop("throttle_pct")

        coax_position_m = d.pop("coax_position_m", UNSET)

        coax_stack_id = d.pop("coax_stack_id", UNSET)

        esc_pwm_frequency_khz = d.pop("esc_pwm_frequency_khz", UNSET)

        esc_sync_rectification = d.pop("esc_sync_rectification", UNSET)

        esc_timing = d.pop("esc_timing", UNSET)

        rotation_sense = d.pop("rotation_sense", UNSET)

        rotor_group_resource = cls(
            count=count,
            esc_motor_wire_resistance_mohm=esc_motor_wire_resistance_mohm,
            esc_resistance_mohm=esc_resistance_mohm,
            esc_type=esc_type,
            label=label,
            motor_component_id=motor_component_id,
            propeller_component_id=propeller_component_id,
            throttle_pct=throttle_pct,
            coax_position_m=coax_position_m,
            coax_stack_id=coax_stack_id,
            esc_pwm_frequency_khz=esc_pwm_frequency_khz,
            esc_sync_rectification=esc_sync_rectification,
            esc_timing=esc_timing,
            rotation_sense=rotation_sense,
        )

        return rotor_group_resource
