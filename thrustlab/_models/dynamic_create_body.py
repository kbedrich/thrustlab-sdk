from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.dynamic_rotor_group_in import DynamicRotorGroupIn
    from thrustlab._models.schedule_in import ScheduleIn
    from thrustlab._models.termination_in import TerminationIn


T = TypeVar("T", bound="DynamicCreateBody")


@_attrs_define
class DynamicCreateBody:
    """Create body for ``POST /v1/dynamic-simulations``.

    Attributes:
        battery_component_id (str):
        density_kg_m3 (float):
        project_id (str):
        rotor_groups (list[DynamicRotorGroupIn]):
        schedule (ScheduleIn): The control schedule — a ``segments`` list OR a per-rotor ``csv_text``.

            ``mode`` is the discriminator. ``segments`` is required for ``mode=segments``;
            ``csv_text`` (+ optional ``interpolation``) for ``mode=csv``. The cross-field
            requirement is enforced server-side by the schedule compiler (``validate_schedule``) so a malformed schedule
            4xx's BEFORE any reservation.
        termination (TerminationIn): Run-termination policy: the SOC / cell-voltage depletion cutoffs and the
            fixed-duration vs until-depleted run mode.
        ambient_temp_c (float | Unset):  Default: 25.0.
        battery_charge_pct (float | Unset):  Default: 100.0.
        battery_initial_temp_c (float | None | Unset):
        motor_initial_temp_c (float | None | Unset):
        name (None | str | Unset):
    """

    battery_component_id: str
    density_kg_m3: float
    project_id: str
    rotor_groups: list[DynamicRotorGroupIn]
    schedule: ScheduleIn
    termination: TerminationIn
    ambient_temp_c: float | Unset = 25.0
    battery_charge_pct: float | Unset = 100.0
    battery_initial_temp_c: float | None | Unset = UNSET
    motor_initial_temp_c: float | None | Unset = UNSET
    name: None | str | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        battery_component_id = self.battery_component_id

        density_kg_m3 = self.density_kg_m3

        project_id = self.project_id

        rotor_groups = []
        for rotor_groups_item_data in self.rotor_groups:
            rotor_groups_item = rotor_groups_item_data.to_dict()
            rotor_groups.append(rotor_groups_item)

        schedule = self.schedule.to_dict()

        termination = self.termination.to_dict()

        ambient_temp_c = self.ambient_temp_c

        battery_charge_pct = self.battery_charge_pct

        battery_initial_temp_c: float | None | Unset
        if isinstance(self.battery_initial_temp_c, Unset):
            battery_initial_temp_c = UNSET
        else:
            battery_initial_temp_c = self.battery_initial_temp_c

        motor_initial_temp_c: float | None | Unset
        if isinstance(self.motor_initial_temp_c, Unset):
            motor_initial_temp_c = UNSET
        else:
            motor_initial_temp_c = self.motor_initial_temp_c

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "battery_component_id": battery_component_id,
                "density_kg_m3": density_kg_m3,
                "project_id": project_id,
                "rotor_groups": rotor_groups,
                "schedule": schedule,
                "termination": termination,
            }
        )
        if ambient_temp_c is not UNSET:
            field_dict["ambient_temp_c"] = ambient_temp_c
        if battery_charge_pct is not UNSET:
            field_dict["battery_charge_pct"] = battery_charge_pct
        if battery_initial_temp_c is not UNSET:
            field_dict["battery_initial_temp_c"] = battery_initial_temp_c
        if motor_initial_temp_c is not UNSET:
            field_dict["motor_initial_temp_c"] = motor_initial_temp_c
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.dynamic_rotor_group_in import DynamicRotorGroupIn
        from thrustlab._models.schedule_in import ScheduleIn
        from thrustlab._models.termination_in import TerminationIn

        d = dict(src_dict)
        battery_component_id = d.pop("battery_component_id")

        density_kg_m3 = d.pop("density_kg_m3")

        project_id = d.pop("project_id")

        rotor_groups = []
        _rotor_groups = d.pop("rotor_groups")
        for rotor_groups_item_data in _rotor_groups:
            rotor_groups_item = DynamicRotorGroupIn.from_dict(rotor_groups_item_data)

            rotor_groups.append(rotor_groups_item)

        schedule = ScheduleIn.from_dict(d.pop("schedule"))

        termination = TerminationIn.from_dict(d.pop("termination"))

        ambient_temp_c = d.pop("ambient_temp_c", UNSET)

        battery_charge_pct = d.pop("battery_charge_pct", UNSET)

        def _parse_battery_initial_temp_c(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        battery_initial_temp_c = _parse_battery_initial_temp_c(d.pop("battery_initial_temp_c", UNSET))

        def _parse_motor_initial_temp_c(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        motor_initial_temp_c = _parse_motor_initial_temp_c(d.pop("motor_initial_temp_c", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        dynamic_create_body = cls(
            battery_component_id=battery_component_id,
            density_kg_m3=density_kg_m3,
            project_id=project_id,
            rotor_groups=rotor_groups,
            schedule=schedule,
            termination=termination,
            ambient_temp_c=ambient_temp_c,
            battery_charge_pct=battery_charge_pct,
            battery_initial_temp_c=battery_initial_temp_c,
            motor_initial_temp_c=motor_initial_temp_c,
            name=name,
        )

        return dynamic_create_body
