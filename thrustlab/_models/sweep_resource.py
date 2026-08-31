from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.sweep_resource_status import SweepResourceStatus
from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.rotor_group_resource import RotorGroupResource
    from thrustlab._models.sweep_inputs import SweepInputs
    from thrustlab._models.sweep_resource_error_type_0 import SweepResourceErrorType0
    from thrustlab._models.sweep_resource_input_snapshot_type_0 import SweepResourceInputSnapshotType0
    from thrustlab._models.sweep_resource_plot_config_json_type_0_item import SweepResourcePlotConfigJsonType0Item
    from thrustlab._models.sweep_resource_summary_type_0 import SweepResourceSummaryType0
    from thrustlab._models.sweep_resource_sweep_config_type_0 import SweepResourceSweepConfigType0


T = TypeVar("T", bound="SweepResource")


@_attrs_define
class SweepResource:
    """
    Attributes:
        analysis_type (str):
        battery_component_id (str):
        completed_at (None | str):
        completed_points (int):
        created_at (None | str):
        credits_cost (int):
        error (None | SweepResourceErrorType0):
        id (str):
        inputs (SweepInputs):
        is_starred (bool):
        name (None | str):
        object_ (Literal['sweep']):
        plot_config_json (list[SweepResourcePlotConfigJsonType0Item] | None):
        progress (float | None):
        project_id (str):
        rotor_groups (list[RotorGroupResource]):
        status (SweepResourceStatus):
        summary (None | SweepResourceSummaryType0):
        sweep_config (None | SweepResourceSweepConfigType0):
        total_points (int):
        dispatched_at (None | str | Unset):
        input_snapshot (None | SweepResourceInputSnapshotType0 | Unset):
        snapshot_version (int | Unset):  Default: 1.
        solver_engine (str | Unset):  Default: 'prom-rs/0.2.6'.
    """

    analysis_type: str
    battery_component_id: str
    completed_at: None | str
    completed_points: int
    created_at: None | str
    credits_cost: int
    error: None | SweepResourceErrorType0
    id: str
    inputs: SweepInputs
    is_starred: bool
    name: None | str
    object_: Literal["sweep"]
    plot_config_json: list[SweepResourcePlotConfigJsonType0Item] | None
    progress: float | None
    project_id: str
    rotor_groups: list[RotorGroupResource]
    status: SweepResourceStatus
    summary: None | SweepResourceSummaryType0
    sweep_config: None | SweepResourceSweepConfigType0
    total_points: int
    dispatched_at: None | str | Unset = UNSET
    input_snapshot: None | SweepResourceInputSnapshotType0 | Unset = UNSET
    snapshot_version: int | Unset = 1
    solver_engine: str | Unset = "prom-rs/0.2.6"

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.sweep_resource_error_type_0 import SweepResourceErrorType0
        from thrustlab._models.sweep_resource_input_snapshot_type_0 import SweepResourceInputSnapshotType0
        from thrustlab._models.sweep_resource_summary_type_0 import SweepResourceSummaryType0
        from thrustlab._models.sweep_resource_sweep_config_type_0 import SweepResourceSweepConfigType0

        analysis_type = self.analysis_type

        battery_component_id = self.battery_component_id

        completed_at: None | str
        completed_at = self.completed_at

        completed_points = self.completed_points

        created_at: None | str
        created_at = self.created_at

        credits_cost = self.credits_cost

        error: dict[str, Any] | None
        if isinstance(self.error, SweepResourceErrorType0):
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

        rotor_groups = []
        for rotor_groups_item_data in self.rotor_groups:
            rotor_groups_item = rotor_groups_item_data.to_dict()
            rotor_groups.append(rotor_groups_item)

        status = self.status.value

        summary: dict[str, Any] | None
        if isinstance(self.summary, SweepResourceSummaryType0):
            summary = self.summary.to_dict()
        else:
            summary = self.summary

        sweep_config: dict[str, Any] | None
        if isinstance(self.sweep_config, SweepResourceSweepConfigType0):
            sweep_config = self.sweep_config.to_dict()
        else:
            sweep_config = self.sweep_config

        total_points = self.total_points

        dispatched_at: None | str | Unset
        if isinstance(self.dispatched_at, Unset):
            dispatched_at = UNSET
        else:
            dispatched_at = self.dispatched_at

        input_snapshot: dict[str, Any] | None | Unset
        if isinstance(self.input_snapshot, Unset):
            input_snapshot = UNSET
        elif isinstance(self.input_snapshot, SweepResourceInputSnapshotType0):
            input_snapshot = self.input_snapshot.to_dict()
        else:
            input_snapshot = self.input_snapshot

        snapshot_version = self.snapshot_version

        solver_engine = self.solver_engine

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "analysis_type": analysis_type,
                "battery_component_id": battery_component_id,
                "completed_at": completed_at,
                "completed_points": completed_points,
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
                "rotor_groups": rotor_groups,
                "status": status,
                "summary": summary,
                "sweep_config": sweep_config,
                "total_points": total_points,
            }
        )
        if dispatched_at is not UNSET:
            field_dict["dispatched_at"] = dispatched_at
        if input_snapshot is not UNSET:
            field_dict["input_snapshot"] = input_snapshot
        if snapshot_version is not UNSET:
            field_dict["snapshot_version"] = snapshot_version
        if solver_engine is not UNSET:
            field_dict["solver_engine"] = solver_engine

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.rotor_group_resource import RotorGroupResource
        from thrustlab._models.sweep_inputs import SweepInputs
        from thrustlab._models.sweep_resource_error_type_0 import SweepResourceErrorType0
        from thrustlab._models.sweep_resource_input_snapshot_type_0 import SweepResourceInputSnapshotType0
        from thrustlab._models.sweep_resource_plot_config_json_type_0_item import SweepResourcePlotConfigJsonType0Item
        from thrustlab._models.sweep_resource_summary_type_0 import SweepResourceSummaryType0
        from thrustlab._models.sweep_resource_sweep_config_type_0 import SweepResourceSweepConfigType0

        d = dict(src_dict)
        analysis_type = d.pop("analysis_type")

        battery_component_id = d.pop("battery_component_id")

        def _parse_completed_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        completed_at = _parse_completed_at(d.pop("completed_at"))

        completed_points = d.pop("completed_points")

        def _parse_created_at(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        created_at = _parse_created_at(d.pop("created_at"))

        credits_cost = d.pop("credits_cost")

        def _parse_error(data: object) -> None | SweepResourceErrorType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                error_type_0 = SweepResourceErrorType0.from_dict(data)

                return error_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SweepResourceErrorType0, data)

        error = _parse_error(d.pop("error"))

        id = d.pop("id")

        inputs = SweepInputs.from_dict(d.pop("inputs"))

        is_starred = d.pop("is_starred")

        def _parse_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        name = _parse_name(d.pop("name"))

        object_ = cast(Literal["sweep"], d.pop("object"))
        if object_ != "sweep":
            raise ValueError(f"object must match const 'sweep', got '{object_}'")

        def _parse_plot_config_json(data: object) -> list[SweepResourcePlotConfigJsonType0Item] | None:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                plot_config_json_type_0 = []
                _plot_config_json_type_0 = data
                for plot_config_json_type_0_item_data in _plot_config_json_type_0:
                    plot_config_json_type_0_item = SweepResourcePlotConfigJsonType0Item.from_dict(
                        plot_config_json_type_0_item_data
                    )

                    plot_config_json_type_0.append(plot_config_json_type_0_item)

                return plot_config_json_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[SweepResourcePlotConfigJsonType0Item] | None, data)

        plot_config_json = _parse_plot_config_json(d.pop("plot_config_json"))

        def _parse_progress(data: object) -> float | None:
            if data is None:
                return data
            return cast(float | None, data)

        progress = _parse_progress(d.pop("progress"))

        project_id = d.pop("project_id")

        rotor_groups = []
        _rotor_groups = d.pop("rotor_groups")
        for rotor_groups_item_data in _rotor_groups:
            rotor_groups_item = RotorGroupResource.from_dict(rotor_groups_item_data)

            rotor_groups.append(rotor_groups_item)

        status = SweepResourceStatus(d.pop("status"))

        def _parse_summary(data: object) -> None | SweepResourceSummaryType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                summary_type_0 = SweepResourceSummaryType0.from_dict(data)

                return summary_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SweepResourceSummaryType0, data)

        summary = _parse_summary(d.pop("summary"))

        def _parse_sweep_config(data: object) -> None | SweepResourceSweepConfigType0:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                sweep_config_type_0 = SweepResourceSweepConfigType0.from_dict(data)

                return sweep_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SweepResourceSweepConfigType0, data)

        sweep_config = _parse_sweep_config(d.pop("sweep_config"))

        total_points = d.pop("total_points")

        def _parse_dispatched_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        dispatched_at = _parse_dispatched_at(d.pop("dispatched_at", UNSET))

        def _parse_input_snapshot(data: object) -> None | SweepResourceInputSnapshotType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                input_snapshot_type_0 = SweepResourceInputSnapshotType0.from_dict(data)

                return input_snapshot_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SweepResourceInputSnapshotType0 | Unset, data)

        input_snapshot = _parse_input_snapshot(d.pop("input_snapshot", UNSET))

        snapshot_version = d.pop("snapshot_version", UNSET)

        solver_engine = d.pop("solver_engine", UNSET)

        sweep_resource = cls(
            analysis_type=analysis_type,
            battery_component_id=battery_component_id,
            completed_at=completed_at,
            completed_points=completed_points,
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
            rotor_groups=rotor_groups,
            status=status,
            summary=summary,
            sweep_config=sweep_config,
            total_points=total_points,
            dispatched_at=dispatched_at,
            input_snapshot=input_snapshot,
            snapshot_version=snapshot_version,
            solver_engine=solver_engine,
        )

        return sweep_resource
