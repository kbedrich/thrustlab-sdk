from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal, TypeVar, cast

from attrs import define as _attrs_define

from thrustlab._models.dynamic_resource_status import DynamicResourceStatus
from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.dynamic_resource_battery_topology_type_0 import DynamicResourceBatteryTopologyType0
    from thrustlab._models.dynamic_resource_display_labels_type_0 import DynamicResourceDisplayLabelsType0
    from thrustlab._models.dynamic_resource_error_type_0 import DynamicResourceErrorType0
    from thrustlab._models.dynamic_resource_input_snapshot_type_0 import DynamicResourceInputSnapshotType0
    from thrustlab._models.dynamic_resource_result_type_0 import DynamicResourceResultType0


T = TypeVar("T", bound="DynamicResource")


@_attrs_define
class DynamicResource:
    """The dynamic-simulation resource. ``result`` is populated only once the run
    is ``completed`` (the worker writes it); it stays ``None`` for
    queued/running/failed/canceled (the SweepResource optional-result idiom).

        Attributes:
            credits_cost (int):
            id (str):
            project_id (str):
            status (DynamicResourceStatus):
            battery_topology (DynamicResourceBatteryTopologyType0 | None | Unset):
            created_at (None | str | Unset):
            dispatched_at (None | str | Unset):
            display_labels (DynamicResourceDisplayLabelsType0 | None | Unset):
            error (DynamicResourceErrorType0 | None | Unset):
            input_snapshot (DynamicResourceInputSnapshotType0 | None | Unset):
            is_starred (bool | Unset):  Default: False.
            name (None | str | Unset):
            object_ (Literal['dynamic_simulation'] | Unset):  Default: 'dynamic_simulation'.
            result (DynamicResourceResultType0 | None | Unset):
            snapshot_version (int | Unset):  Default: 2.
            solver_engine (str | Unset):  Default: 'prom-rs/0.2.5'.
    """

    credits_cost: int
    id: str
    project_id: str
    status: DynamicResourceStatus
    battery_topology: DynamicResourceBatteryTopologyType0 | None | Unset = UNSET
    created_at: None | str | Unset = UNSET
    dispatched_at: None | str | Unset = UNSET
    display_labels: DynamicResourceDisplayLabelsType0 | None | Unset = UNSET
    error: DynamicResourceErrorType0 | None | Unset = UNSET
    input_snapshot: DynamicResourceInputSnapshotType0 | None | Unset = UNSET
    is_starred: bool | Unset = False
    name: None | str | Unset = UNSET
    object_: Literal["dynamic_simulation"] | Unset = "dynamic_simulation"
    result: DynamicResourceResultType0 | None | Unset = UNSET
    snapshot_version: int | Unset = 2
    solver_engine: str | Unset = "prom-rs/0.2.5"

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.dynamic_resource_battery_topology_type_0 import DynamicResourceBatteryTopologyType0
        from thrustlab._models.dynamic_resource_display_labels_type_0 import DynamicResourceDisplayLabelsType0
        from thrustlab._models.dynamic_resource_error_type_0 import DynamicResourceErrorType0
        from thrustlab._models.dynamic_resource_input_snapshot_type_0 import DynamicResourceInputSnapshotType0
        from thrustlab._models.dynamic_resource_result_type_0 import DynamicResourceResultType0

        credits_cost = self.credits_cost

        id = self.id

        project_id = self.project_id

        status = self.status.value

        battery_topology: dict[str, Any] | None | Unset
        if isinstance(self.battery_topology, Unset):
            battery_topology = UNSET
        elif isinstance(self.battery_topology, DynamicResourceBatteryTopologyType0):
            battery_topology = self.battery_topology.to_dict()
        else:
            battery_topology = self.battery_topology

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        dispatched_at: None | str | Unset
        if isinstance(self.dispatched_at, Unset):
            dispatched_at = UNSET
        else:
            dispatched_at = self.dispatched_at

        display_labels: dict[str, Any] | None | Unset
        if isinstance(self.display_labels, Unset):
            display_labels = UNSET
        elif isinstance(self.display_labels, DynamicResourceDisplayLabelsType0):
            display_labels = self.display_labels.to_dict()
        else:
            display_labels = self.display_labels

        error: dict[str, Any] | None | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        elif isinstance(self.error, DynamicResourceErrorType0):
            error = self.error.to_dict()
        else:
            error = self.error

        input_snapshot: dict[str, Any] | None | Unset
        if isinstance(self.input_snapshot, Unset):
            input_snapshot = UNSET
        elif isinstance(self.input_snapshot, DynamicResourceInputSnapshotType0):
            input_snapshot = self.input_snapshot.to_dict()
        else:
            input_snapshot = self.input_snapshot

        is_starred = self.is_starred

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        object_ = self.object_

        result: dict[str, Any] | None | Unset
        if isinstance(self.result, Unset):
            result = UNSET
        elif isinstance(self.result, DynamicResourceResultType0):
            result = self.result.to_dict()
        else:
            result = self.result

        snapshot_version = self.snapshot_version

        solver_engine = self.solver_engine

        field_dict: dict[str, Any] = {}

        field_dict.update(
            {
                "credits_cost": credits_cost,
                "id": id,
                "project_id": project_id,
                "status": status,
            }
        )
        if battery_topology is not UNSET:
            field_dict["battery_topology"] = battery_topology
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if dispatched_at is not UNSET:
            field_dict["dispatched_at"] = dispatched_at
        if display_labels is not UNSET:
            field_dict["display_labels"] = display_labels
        if error is not UNSET:
            field_dict["error"] = error
        if input_snapshot is not UNSET:
            field_dict["input_snapshot"] = input_snapshot
        if is_starred is not UNSET:
            field_dict["is_starred"] = is_starred
        if name is not UNSET:
            field_dict["name"] = name
        if object_ is not UNSET:
            field_dict["object"] = object_
        if result is not UNSET:
            field_dict["result"] = result
        if snapshot_version is not UNSET:
            field_dict["snapshot_version"] = snapshot_version
        if solver_engine is not UNSET:
            field_dict["solver_engine"] = solver_engine

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.dynamic_resource_battery_topology_type_0 import DynamicResourceBatteryTopologyType0
        from thrustlab._models.dynamic_resource_display_labels_type_0 import DynamicResourceDisplayLabelsType0
        from thrustlab._models.dynamic_resource_error_type_0 import DynamicResourceErrorType0
        from thrustlab._models.dynamic_resource_input_snapshot_type_0 import DynamicResourceInputSnapshotType0
        from thrustlab._models.dynamic_resource_result_type_0 import DynamicResourceResultType0

        d = dict(src_dict)
        credits_cost = d.pop("credits_cost")

        id = d.pop("id")

        project_id = d.pop("project_id")

        status = DynamicResourceStatus(d.pop("status"))

        def _parse_battery_topology(data: object) -> DynamicResourceBatteryTopologyType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                battery_topology_type_0 = DynamicResourceBatteryTopologyType0.from_dict(data)

                return battery_topology_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DynamicResourceBatteryTopologyType0 | None | Unset, data)

        battery_topology = _parse_battery_topology(d.pop("battery_topology", UNSET))

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        def _parse_dispatched_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        dispatched_at = _parse_dispatched_at(d.pop("dispatched_at", UNSET))

        def _parse_display_labels(data: object) -> DynamicResourceDisplayLabelsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                display_labels_type_0 = DynamicResourceDisplayLabelsType0.from_dict(data)

                return display_labels_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DynamicResourceDisplayLabelsType0 | None | Unset, data)

        display_labels = _parse_display_labels(d.pop("display_labels", UNSET))

        def _parse_error(data: object) -> DynamicResourceErrorType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                error_type_0 = DynamicResourceErrorType0.from_dict(data)

                return error_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DynamicResourceErrorType0 | None | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        def _parse_input_snapshot(data: object) -> DynamicResourceInputSnapshotType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                input_snapshot_type_0 = DynamicResourceInputSnapshotType0.from_dict(data)

                return input_snapshot_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DynamicResourceInputSnapshotType0 | None | Unset, data)

        input_snapshot = _parse_input_snapshot(d.pop("input_snapshot", UNSET))

        is_starred = d.pop("is_starred", UNSET)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        object_ = cast(Literal["dynamic_simulation"] | Unset, d.pop("object", UNSET))
        if object_ != "dynamic_simulation" and not isinstance(object_, Unset):
            raise ValueError(f"object must match const 'dynamic_simulation', got '{object_}'")

        def _parse_result(data: object) -> DynamicResourceResultType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                result_type_0 = DynamicResourceResultType0.from_dict(data)

                return result_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DynamicResourceResultType0 | None | Unset, data)

        result = _parse_result(d.pop("result", UNSET))

        snapshot_version = d.pop("snapshot_version", UNSET)

        solver_engine = d.pop("solver_engine", UNSET)

        dynamic_resource = cls(
            credits_cost=credits_cost,
            id=id,
            project_id=project_id,
            status=status,
            battery_topology=battery_topology,
            created_at=created_at,
            dispatched_at=dispatched_at,
            display_labels=display_labels,
            error=error,
            input_snapshot=input_snapshot,
            is_starred=is_starred,
            name=name,
            object_=object_,
            result=result,
            snapshot_version=snapshot_version,
            solver_engine=solver_engine,
        )

        return dynamic_resource
