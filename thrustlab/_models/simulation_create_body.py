from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.simulation_create_body_cooling_source_type_0 import SimulationCreateBodyCoolingSourceType0
from thrustlab._models.simulation_create_body_flight_regime import SimulationCreateBodyFlightRegime
from thrustlab._models.simulation_create_body_inflow_mode import SimulationCreateBodyInflowMode
from thrustlab._models.simulation_create_body_launch_intent import SimulationCreateBodyLaunchIntent
from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.rotor_group_in import RotorGroupIn
    from thrustlab._models.v1_custom_component_override import V1CustomComponentOverride


T = TypeVar("T", bound="SimulationCreateBody")


@_attrs_define
class SimulationCreateBody:
    """
    Attributes:
        airspeed_m_s (float):
        density_kg_m3 (float):
        project_id (str):
        ambient_temp_c (float | Unset):  Default: 25.0.
        battery_charge_pct (float | Unset):  Default: 100.0.
        battery_component_id (None | str | Unset):
        battery_esc_wire_resistance_mohm (float | Unset):  Default: 0.0.
        cooling_source (None | SimulationCreateBodyCoolingSourceType0 | Unset):
        custom_battery (None | Unset | V1CustomComponentOverride):
        flight_duration (float | None | Unset): Flight time (seconds) for the time-bounded steady-state thermal solve. 0
            ≤ x ≤ 86400 (24 h). null disables time-bounding (infinite-hover baseline).. Default: 60.0.
        flight_regime (SimulationCreateBodyFlightRegime | Unset): Convective cooling regime — maps to h_conv (W/m²·K) at
            the battery thermal boundary.. Default: SimulationCreateBodyFlightRegime.STATIC_BENCH.
        forced_air_velocity_m_s (float | None | Unset):
        inflow_mode (SimulationCreateBodyInflowMode | Unset):  Default: SimulationCreateBodyInflowMode.GROUND.
        launch_intent (SimulationCreateBodyLaunchIntent | Unset): Launch intent. 'run' dispatches now; 'queue' reserves
            a credit slot but defers dispatch; 'draft' persists with no credit reservation and no dispatch.. Default:
            SimulationCreateBodyLaunchIntent.RUN.
        name (None | str | Unset):
        rotor_groups (list[RotorGroupIn] | Unset):
        vertical_speed_m_s (float | Unset):  Default: 0.0.
    """

    airspeed_m_s: float
    density_kg_m3: float
    project_id: str
    ambient_temp_c: float | Unset = 25.0
    battery_charge_pct: float | Unset = 100.0
    battery_component_id: None | str | Unset = UNSET
    battery_esc_wire_resistance_mohm: float | Unset = 0.0
    cooling_source: None | SimulationCreateBodyCoolingSourceType0 | Unset = UNSET
    custom_battery: None | Unset | V1CustomComponentOverride = UNSET
    flight_duration: float | None | Unset = 60.0
    flight_regime: SimulationCreateBodyFlightRegime | Unset = SimulationCreateBodyFlightRegime.STATIC_BENCH
    forced_air_velocity_m_s: float | None | Unset = UNSET
    inflow_mode: SimulationCreateBodyInflowMode | Unset = SimulationCreateBodyInflowMode.GROUND
    launch_intent: SimulationCreateBodyLaunchIntent | Unset = SimulationCreateBodyLaunchIntent.RUN
    name: None | str | Unset = UNSET
    rotor_groups: list[RotorGroupIn] | Unset = UNSET
    vertical_speed_m_s: float | Unset = 0.0

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.v1_custom_component_override import V1CustomComponentOverride

        airspeed_m_s = self.airspeed_m_s

        density_kg_m3 = self.density_kg_m3

        project_id = self.project_id

        ambient_temp_c = self.ambient_temp_c

        battery_charge_pct = self.battery_charge_pct

        battery_component_id: None | str | Unset
        if isinstance(self.battery_component_id, Unset):
            battery_component_id = UNSET
        else:
            battery_component_id = self.battery_component_id

        battery_esc_wire_resistance_mohm = self.battery_esc_wire_resistance_mohm

        cooling_source: None | str | Unset
        if isinstance(self.cooling_source, Unset):
            cooling_source = UNSET
        elif isinstance(self.cooling_source, SimulationCreateBodyCoolingSourceType0):
            cooling_source = self.cooling_source.value
        else:
            cooling_source = self.cooling_source

        custom_battery: dict[str, Any] | None | Unset
        if isinstance(self.custom_battery, Unset):
            custom_battery = UNSET
        elif isinstance(self.custom_battery, V1CustomComponentOverride):
            custom_battery = self.custom_battery.to_dict()
        else:
            custom_battery = self.custom_battery

        flight_duration: float | None | Unset
        if isinstance(self.flight_duration, Unset):
            flight_duration = UNSET
        else:
            flight_duration = self.flight_duration

        flight_regime: str | Unset = UNSET
        if not isinstance(self.flight_regime, Unset):
            flight_regime = self.flight_regime.value

        forced_air_velocity_m_s: float | None | Unset
        if isinstance(self.forced_air_velocity_m_s, Unset):
            forced_air_velocity_m_s = UNSET
        else:
            forced_air_velocity_m_s = self.forced_air_velocity_m_s

        inflow_mode: str | Unset = UNSET
        if not isinstance(self.inflow_mode, Unset):
            inflow_mode = self.inflow_mode.value

        launch_intent: str | Unset = UNSET
        if not isinstance(self.launch_intent, Unset):
            launch_intent = self.launch_intent.value

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

        vertical_speed_m_s = self.vertical_speed_m_s

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "airspeed_m_s": airspeed_m_s,
                "density_kg_m3": density_kg_m3,
                "project_id": project_id,
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
        if cooling_source is not UNSET:
            field_dict["cooling_source"] = cooling_source
        if custom_battery is not UNSET:
            field_dict["custom_battery"] = custom_battery
        if flight_duration is not UNSET:
            field_dict["flight_duration"] = flight_duration
        if flight_regime is not UNSET:
            field_dict["flight_regime"] = flight_regime
        if forced_air_velocity_m_s is not UNSET:
            field_dict["forced_air_velocity_m_s"] = forced_air_velocity_m_s
        if inflow_mode is not UNSET:
            field_dict["inflow_mode"] = inflow_mode
        if launch_intent is not UNSET:
            field_dict["launch_intent"] = launch_intent
        if name is not UNSET:
            field_dict["name"] = name
        if rotor_groups is not UNSET:
            field_dict["rotor_groups"] = rotor_groups
        if vertical_speed_m_s is not UNSET:
            field_dict["vertical_speed_m_s"] = vertical_speed_m_s

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.rotor_group_in import RotorGroupIn
        from thrustlab._models.v1_custom_component_override import V1CustomComponentOverride

        d = dict(src_dict)
        airspeed_m_s = d.pop("airspeed_m_s")

        density_kg_m3 = d.pop("density_kg_m3")

        project_id = d.pop("project_id")

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

        def _parse_cooling_source(data: object) -> None | SimulationCreateBodyCoolingSourceType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                cooling_source_type_0 = SimulationCreateBodyCoolingSourceType0(data)

                return cooling_source_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SimulationCreateBodyCoolingSourceType0 | Unset, data)

        cooling_source = _parse_cooling_source(d.pop("cooling_source", UNSET))

        def _parse_custom_battery(data: object) -> None | Unset | V1CustomComponentOverride:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                custom_battery_type_0 = V1CustomComponentOverride.from_dict(data)

                return custom_battery_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | V1CustomComponentOverride, data)

        custom_battery = _parse_custom_battery(d.pop("custom_battery", UNSET))

        def _parse_flight_duration(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        flight_duration = _parse_flight_duration(d.pop("flight_duration", UNSET))

        _flight_regime = d.pop("flight_regime", UNSET)
        flight_regime: SimulationCreateBodyFlightRegime | Unset
        if isinstance(_flight_regime, Unset):
            flight_regime = UNSET
        else:
            flight_regime = SimulationCreateBodyFlightRegime(_flight_regime)

        def _parse_forced_air_velocity_m_s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        forced_air_velocity_m_s = _parse_forced_air_velocity_m_s(d.pop("forced_air_velocity_m_s", UNSET))

        _inflow_mode = d.pop("inflow_mode", UNSET)
        inflow_mode: SimulationCreateBodyInflowMode | Unset
        if isinstance(_inflow_mode, Unset):
            inflow_mode = UNSET
        else:
            inflow_mode = SimulationCreateBodyInflowMode(_inflow_mode)

        _launch_intent = d.pop("launch_intent", UNSET)
        launch_intent: SimulationCreateBodyLaunchIntent | Unset
        if isinstance(_launch_intent, Unset):
            launch_intent = UNSET
        else:
            launch_intent = SimulationCreateBodyLaunchIntent(_launch_intent)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        _rotor_groups = d.pop("rotor_groups", UNSET)
        rotor_groups: list[RotorGroupIn] | Unset = UNSET
        if _rotor_groups is not UNSET:
            rotor_groups = []
            for rotor_groups_item_data in _rotor_groups:
                rotor_groups_item = RotorGroupIn.from_dict(rotor_groups_item_data)

                rotor_groups.append(rotor_groups_item)

        vertical_speed_m_s = d.pop("vertical_speed_m_s", UNSET)

        simulation_create_body = cls(
            airspeed_m_s=airspeed_m_s,
            density_kg_m3=density_kg_m3,
            project_id=project_id,
            ambient_temp_c=ambient_temp_c,
            battery_charge_pct=battery_charge_pct,
            battery_component_id=battery_component_id,
            battery_esc_wire_resistance_mohm=battery_esc_wire_resistance_mohm,
            cooling_source=cooling_source,
            custom_battery=custom_battery,
            flight_duration=flight_duration,
            flight_regime=flight_regime,
            forced_air_velocity_m_s=forced_air_velocity_m_s,
            inflow_mode=inflow_mode,
            launch_intent=launch_intent,
            name=name,
            rotor_groups=rotor_groups,
            vertical_speed_m_s=vertical_speed_m_s,
        )

        return simulation_create_body
