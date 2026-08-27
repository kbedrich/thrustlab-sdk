from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.dynamic_rotor_group_in import DynamicRotorGroupIn
    from thrustlab._models.dynamic_rotor_in import DynamicRotorIn
    from thrustlab._models.pack_topology_in import PackTopologyIn
    from thrustlab._models.schedule_in import ScheduleIn
    from thrustlab._models.termination_in import TerminationIn


T = TypeVar("T", bound="DynamicCreateBody")


@_attrs_define
class DynamicCreateBody:
    """Create body for ``POST /v1/dynamic-simulations``.

    Attributes:
        density_kg_m3 (float):
        project_id (str):
        schedule (ScheduleIn): The control schedule — a ``segments`` list OR a per-rotor ``csv_text``.

            ``mode`` is the discriminator. ``segments`` is required for ``mode=segments``;
            ``csv_text`` (+ optional ``interpolation``) for ``mode=csv``. The cross-field
            requirement is enforced server-side by the schedule compiler (``validate_schedule``) so a malformed schedule
            4xx's BEFORE any reservation.
        termination (TerminationIn): Run-termination policy: the SOC / cell-voltage depletion cutoffs and the
            fixed-duration vs until-depleted run mode.
        ambient_temp_c (float | Unset):  Default: 25.0.
        battery_charge_pct (float | Unset):  Default: 100.0.
        battery_component_id (None | str | Unset):
        battery_esc_wire_resistance_mohm (float | Unset):  Default: 0.0.
        battery_initial_temp_c (float | None | Unset):
        battery_topology (None | PackTopologyIn | Unset):
        motor_initial_temp_c (float | None | Unset):
        name (None | str | Unset):
        rotor_groups (list[DynamicRotorGroupIn] | Unset):
        rotors (list[DynamicRotorIn] | None | Unset): One entry per rotor. Preferred over rotor_groups, and required for
            coaxial stacks: set coax_stack_id to the same non-zero value on the rotors that share an axis, give each a
            distinct coax_position_m, and set opposite rotation_sense values for a contra-rotating stack. Supply either
            rotors or rotor_groups, not both.
    """

    density_kg_m3: float
    project_id: str
    schedule: ScheduleIn
    termination: TerminationIn
    ambient_temp_c: float | Unset = 25.0
    battery_charge_pct: float | Unset = 100.0
    battery_component_id: None | str | Unset = UNSET
    battery_esc_wire_resistance_mohm: float | Unset = 0.0
    battery_initial_temp_c: float | None | Unset = UNSET
    battery_topology: None | PackTopologyIn | Unset = UNSET
    motor_initial_temp_c: float | None | Unset = UNSET
    name: None | str | Unset = UNSET
    rotor_groups: list[DynamicRotorGroupIn] | Unset = UNSET
    rotors: list[DynamicRotorIn] | None | Unset = UNSET

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.pack_topology_in import PackTopologyIn

        density_kg_m3 = self.density_kg_m3

        project_id = self.project_id

        schedule = self.schedule.to_dict()

        termination = self.termination.to_dict()

        ambient_temp_c = self.ambient_temp_c

        battery_charge_pct = self.battery_charge_pct

        battery_component_id: None | str | Unset
        if isinstance(self.battery_component_id, Unset):
            battery_component_id = UNSET
        else:
            battery_component_id = self.battery_component_id

        battery_esc_wire_resistance_mohm = self.battery_esc_wire_resistance_mohm

        battery_initial_temp_c: float | None | Unset
        if isinstance(self.battery_initial_temp_c, Unset):
            battery_initial_temp_c = UNSET
        else:
            battery_initial_temp_c = self.battery_initial_temp_c

        battery_topology: dict[str, Any] | None | Unset
        if isinstance(self.battery_topology, Unset):
            battery_topology = UNSET
        elif isinstance(self.battery_topology, PackTopologyIn):
            battery_topology = self.battery_topology.to_dict()
        else:
            battery_topology = self.battery_topology

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

        rotor_groups: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.rotor_groups, Unset):
            rotor_groups = []
            for rotor_groups_item_data in self.rotor_groups:
                rotor_groups_item = rotor_groups_item_data.to_dict()
                rotor_groups.append(rotor_groups_item)

        rotors: list[dict[str, Any]] | None | Unset
        if isinstance(self.rotors, Unset):
            rotors = UNSET
        elif isinstance(self.rotors, list):
            rotors = []
            for rotors_type_0_item_data in self.rotors:
                rotors_type_0_item = rotors_type_0_item_data.to_dict()
                rotors.append(rotors_type_0_item)

        else:
            rotors = self.rotors

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "density_kg_m3": density_kg_m3,
                "project_id": project_id,
                "schedule": schedule,
                "termination": termination,
            }
        )
        if ambient_temp_c is not UNSET:
            field_dict["ambient_temp_c"] = ambient_temp_c
        if battery_charge_pct is not UNSET:
            field_dict["battery_charge_pct"] = battery_charge_pct
        if battery_component_id is not UNSET:
            field_dict["battery_component_id"] = battery_component_id
        if battery_esc_wire_resistance_mohm is not UNSET:
            field_dict["battery_esc_wire_resistance_mohm"] = battery_esc_wire_resistance_mohm
        if battery_initial_temp_c is not UNSET:
            field_dict["battery_initial_temp_c"] = battery_initial_temp_c
        if battery_topology is not UNSET:
            field_dict["battery_topology"] = battery_topology
        if motor_initial_temp_c is not UNSET:
            field_dict["motor_initial_temp_c"] = motor_initial_temp_c
        if name is not UNSET:
            field_dict["name"] = name
        if rotor_groups is not UNSET:
            field_dict["rotor_groups"] = rotor_groups
        if rotors is not UNSET:
            field_dict["rotors"] = rotors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.dynamic_rotor_group_in import DynamicRotorGroupIn
        from thrustlab._models.dynamic_rotor_in import DynamicRotorIn
        from thrustlab._models.pack_topology_in import PackTopologyIn
        from thrustlab._models.schedule_in import ScheduleIn
        from thrustlab._models.termination_in import TerminationIn

        d = dict(src_dict)
        density_kg_m3 = d.pop("density_kg_m3")

        project_id = d.pop("project_id")

        schedule = ScheduleIn.from_dict(d.pop("schedule"))

        termination = TerminationIn.from_dict(d.pop("termination"))

        ambient_temp_c = d.pop("ambient_temp_c", UNSET)

        battery_charge_pct = d.pop("battery_charge_pct", UNSET)

        def _parse_battery_component_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        battery_component_id = _parse_battery_component_id(d.pop("battery_component_id", UNSET))

        battery_esc_wire_resistance_mohm = d.pop("battery_esc_wire_resistance_mohm", UNSET)

        def _parse_battery_initial_temp_c(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        battery_initial_temp_c = _parse_battery_initial_temp_c(d.pop("battery_initial_temp_c", UNSET))

        def _parse_battery_topology(data: object) -> None | PackTopologyIn | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                battery_topology_type_0 = PackTopologyIn.from_dict(data)

                return battery_topology_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PackTopologyIn | Unset, data)

        battery_topology = _parse_battery_topology(d.pop("battery_topology", UNSET))

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

        _rotor_groups = d.pop("rotor_groups", UNSET)
        rotor_groups: list[DynamicRotorGroupIn] | Unset = UNSET
        if _rotor_groups is not UNSET:
            rotor_groups = []
            for rotor_groups_item_data in _rotor_groups:
                rotor_groups_item = DynamicRotorGroupIn.from_dict(rotor_groups_item_data)

                rotor_groups.append(rotor_groups_item)

        def _parse_rotors(data: object) -> list[DynamicRotorIn] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                rotors_type_0 = []
                _rotors_type_0 = data
                for rotors_type_0_item_data in _rotors_type_0:
                    rotors_type_0_item = DynamicRotorIn.from_dict(rotors_type_0_item_data)

                    rotors_type_0.append(rotors_type_0_item)

                return rotors_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[DynamicRotorIn] | None | Unset, data)

        rotors = _parse_rotors(d.pop("rotors", UNSET))

        dynamic_create_body = cls(
            density_kg_m3=density_kg_m3,
            project_id=project_id,
            schedule=schedule,
            termination=termination,
            ambient_temp_c=ambient_temp_c,
            battery_charge_pct=battery_charge_pct,
            battery_component_id=battery_component_id,
            battery_esc_wire_resistance_mohm=battery_esc_wire_resistance_mohm,
            battery_initial_temp_c=battery_initial_temp_c,
            battery_topology=battery_topology,
            motor_initial_temp_c=motor_initial_temp_c,
            name=name,
            rotor_groups=rotor_groups,
            rotors=rotors,
        )

        return dynamic_create_body
