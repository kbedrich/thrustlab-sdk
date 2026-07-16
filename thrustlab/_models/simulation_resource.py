from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.simulation_resource_status import SimulationResourceStatus
from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.rotor_group_resource import RotorGroupResource
    from thrustlab._models.simulation_inputs import SimulationInputs
    from thrustlab._models.simulation_resource_display_labels_type_0 import SimulationResourceDisplayLabelsType0
    from thrustlab._models.simulation_resource_error_type_0 import SimulationResourceErrorType0
    from thrustlab._models.simulation_resource_input_snapshot_type_0 import SimulationResourceInputSnapshotType0
    from thrustlab._models.simulation_resource_plot_config_json_type_0_item import SimulationResourcePlotConfigJsonType0Item
    from thrustlab._models.simulation_resource_result_type_0 import SimulationResourceResultType0


T = TypeVar("T", bound="SimulationResource")


@_attrs_define
class SimulationResource:
    """
    Attributes:
        analysis_type (str):
        battery_component_id (str):
        completed_at (None | str):
        created_at (None | str):
        credits_cost (int):
        error (None | SimulationResourceErrorType0):
        id (str):
        inputs (SimulationInputs):
        is_starred (bool):
        name (None | str):
        object_ (Literal['simulation']):
        plot_config_json (list[SimulationResourcePlotConfigJsonType0Item] | None):
        progress (float | None):
        project_id (str):
        result (None | SimulationResourceResultType0):
        rotor_groups (list[RotorGroupResource]):
        status (SimulationResourceStatus):
        dispatched_at (None | str | Unset):
        display_labels (None | SimulationResourceDisplayLabelsType0 | Unset):
        input_snapshot (None | SimulationResourceInputSnapshotType0 | Unset):
        project_name (None | str | Unset):
        snapshot_version (int | Unset):  Default: 1.
    """

    analysis_type: str
    battery_component_id: str
    completed_at: None | str
    created_at: None | str
    credits_cost: int
    error: None | SimulationResourceErrorType0
    id: str
    inputs: SimulationInputs
    is_starred: bool
    name: None | str
    object_: Literal["simulation"]
    plot_config_json: list[SimulationResourcePlotConfigJsonType0Item] | None
    progress: float | None
    project_id: str
    result: None | SimulationResourceResultType0
    rotor_groups: list[RotorGroupResource]
    status: SimulationResourceStatus
    dispatched_at: None | str | Unset = UNSET
    display_labels: None | SimulationResourceDisplayLabelsType0 | Unset = UNSET
    input_snapshot: None | SimulationResourceInputSnapshotType0 | Unset = UNSET
    project_name: None | str | Unset = UNSET
    snapshot_version: int | Unset = 1

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.simulation_resource_display_labels_type_0 import SimulationResourceDisplayLabelsType0
        from thrustlab._models.simulation_resource_error_type_0 import SimulationResourceErrorType0
        from thrustlab._models.simulation_resource_input_snapshot_type_0 import SimulationResourceInputSnapshotType0
        from thrustlab._models.simulation_resource_result_type_0 import SimulationResourceResultType0

        analysis_type = self.analysis_type

        battery_component_id = self.battery_component_id

        completed_at: None | str
        completed_at = self.completed_at

        created_at: None | str
        created_at = self.created_at

        credits_cost = self.credits_cost

        error: dict[str, Any] | None
        if isinstance(self.error, SimulationResourceErrorType0):
            error = self.error.to_dict()
        else:
            error = self.error

        id = self.id

        inputs = self.inputs.to_dict()

        is_starred = self.is_starred

        name: None | str
        name = self.name

        object_ = self.object_

        plot_config_json: list[dict[str, Any]] | None
        if isinstance(self.plot_config_json, list):
            plot_config_json = []
            for plot_config_json_type_0_item_data in self.plot_config_json:
                plot_config_json_type_0_item = plot_config_json_type_0_item_data.to_dict()
                plot_config_json.append(plot_config_json_type_0_item)

        else:
            plot_config_json = self.plot_config_json

        progress: float | None
        progress = self.progress

        project_id = self.project_id

        result: dict[str, Any] | None
        if isinstance(self.result, SimulationResourceResultType0):
            result = self.result.to_dict()
        else:
            result = self.result

        rotor_groups = []
        for rotor_groups_item_data in self.rotor_groups:
            rotor_groups_item = rotor_groups_item_data.to_dict()
            rotor_groups.append(rotor_groups_item)

        status = self.status.value

        dispatched_at: None | str | Unset
        if isinstance(self.dispatched_at, Unset):
            dispatched_at = UNSET
        else:
            dispatched_at = self.dispatched_at

        display_labels: dict[str, Any] | None | Unset
        if isinstance(self.display_labels, Unset):
            display_labels = UNSET
        elif isinstance(self.display_labels, SimulationResourceDisplayLabelsType0):
            display_labels = self.display_labels.to_dict()
        else:
            display_labels = self.display_labels

        input_snapshot: dict[str, Any] | None | Unset
        if isinstance(self.input_snapshot, Unset):
            input_snapshot = UNSET
        elif isinstance(self.input_snapshot, SimulationResourceInputSnapshotType0):
            input_snapshot = self.input_snapshot.to_dict()
        else:
            input_snapshot = self.input_snapshot

        project_name: None | str | Unset
        if isinstance(self.project_name, Unset):
            project_name = UNSET
        else:
            project_name = self.project_name

        snapshot_version = self.snapshot_version

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "analysis_type": analysis_type,
                "battery_component_id": battery_component_id,
                "completed_at": completed_at,
                "created_at": created_at,
                "credits_cost": credits_cost,
                "error": error,
                "id": id,
                "inputs": inputs,
                "is_starred": is_starred,
                "name": name,
                "object": object_,
                "plot_config_json": plot_config_json,
                "progress": progress,
                "project_id": project_id,
                "result": result,
                "rotor_groups": rotor_groups,
                "status": status,
            }
        )
        if dispatched_at is not UNSET:
            field_dict["dispatched_at"] = dispatched_at
        if display_labels is not UNSET:
            field_dict["display_labels"] = display_labels
        if input_snapshot is not UNSET:
            field_dict["input_snapshot"] = input_snapshot
        if project_name is not UNSET:
            field_dict["project_name"] = project_name
        if snapshot_version is not UNSET:
            field_dict["snapshot_version"] = snapshot_version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.rotor_group_resource import RotorGroupResource
        from thrustlab._models.simulation_inputs import SimulationInputs
        from thrustlab._models.simulation_resource_display_labels_type_0 import SimulationResourceDisplayLabelsType0
        from thrustlab._models.simulation_resource_error_type_0 import SimulationResourceErrorType0
        from thrustlab._models.simulation_resource_input_snapshot_type_0 import SimulationResourceInputSnapshotType0
        from thrustlab._models.simulation_resource_plot_config_json_type_0_item import SimulationResourcePlotConfigJsonType0Item
        from thrustlab._models.simulation_resource_result_type_0 import SimulationResourceResultType0

        d = dict(src_dict)
        analysis_type = d.pop("analysis_type")

        battery_component_id = d.pop("battery_component_id")

        def _parse_completed_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        completed_at = _parse_completed_at(d.pop("completed_at"))

        def _parse_created_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        created_at = _parse_created_at(d.pop("created_at"))

        credits_cost = d.pop("credits_cost")

        def _parse_error(data: object) -> None | SimulationResourceErrorType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                error_type_0 = SimulationResourceErrorType0.from_dict(data)

                return error_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SimulationResourceErrorType0, data)

        error = _parse_error(d.pop("error"))

        id = d.pop("id")

        inputs = SimulationInputs.from_dict(d.pop("inputs"))

        is_starred = d.pop("is_starred")

        def _parse_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        name = _parse_name(d.pop("name"))

        object_ = cast(Literal["simulation"], d.pop("object"))
        if object_ != "simulation":
            raise ValueError(f"object must match const 'simulation', got '{object_}'")

        def _parse_plot_config_json(data: object) -> list[SimulationResourcePlotConfigJsonType0Item] | None:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                plot_config_json_type_0 = []
                _plot_config_json_type_0 = data
                for plot_config_json_type_0_item_data in _plot_config_json_type_0:
                    plot_config_json_type_0_item = SimulationResourcePlotConfigJsonType0Item.from_dict(
                        plot_config_json_type_0_item_data
                    )

                    plot_config_json_type_0.append(plot_config_json_type_0_item)

                return plot_config_json_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[SimulationResourcePlotConfigJsonType0Item] | None, data)

        plot_config_json = _parse_plot_config_json(d.pop("plot_config_json"))

        def _parse_progress(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        progress = _parse_progress(d.pop("progress"))

        project_id = d.pop("project_id")

        def _parse_result(data: object) -> None | SimulationResourceResultType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                result_type_0 = SimulationResourceResultType0.from_dict(data)

                return result_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SimulationResourceResultType0, data)

        result = _parse_result(d.pop("result"))

        rotor_groups = []
        _rotor_groups = d.pop("rotor_groups")
        for rotor_groups_item_data in _rotor_groups:
            rotor_groups_item = RotorGroupResource.from_dict(rotor_groups_item_data)

            rotor_groups.append(rotor_groups_item)

        status = SimulationResourceStatus(d.pop("status"))

        def _parse_dispatched_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        dispatched_at = _parse_dispatched_at(d.pop("dispatched_at", UNSET))

        def _parse_display_labels(data: object) -> None | SimulationResourceDisplayLabelsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                display_labels_type_0 = SimulationResourceDisplayLabelsType0.from_dict(data)

                return display_labels_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SimulationResourceDisplayLabelsType0 | Unset, data)

        display_labels = _parse_display_labels(d.pop("display_labels", UNSET))

        def _parse_input_snapshot(data: object) -> None | SimulationResourceInputSnapshotType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                input_snapshot_type_0 = SimulationResourceInputSnapshotType0.from_dict(data)

                return input_snapshot_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SimulationResourceInputSnapshotType0 | Unset, data)

        input_snapshot = _parse_input_snapshot(d.pop("input_snapshot", UNSET))

        def _parse_project_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        project_name = _parse_project_name(d.pop("project_name", UNSET))

        snapshot_version = d.pop("snapshot_version", UNSET)

        simulation_resource = cls(
            analysis_type=analysis_type,
            battery_component_id=battery_component_id,
            completed_at=completed_at,
            created_at=created_at,
            credits_cost=credits_cost,
            error=error,
            id=id,
            inputs=inputs,
            is_starred=is_starred,
            name=name,
            object_=object_,
            plot_config_json=plot_config_json,
            progress=progress,
            project_id=project_id,
            result=result,
            rotor_groups=rotor_groups,
            status=status,
            dispatched_at=dispatched_at,
            display_labels=display_labels,
            input_snapshot=input_snapshot,
            project_name=project_name,
            snapshot_version=snapshot_version,
        )

        return simulation_resource
