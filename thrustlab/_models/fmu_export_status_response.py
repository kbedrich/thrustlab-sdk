from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from thrustlab._models.types import UNSET, Unset

if TYPE_CHECKING:
    from thrustlab._models.fmu_export_job_error import FmuExportJobError


T = TypeVar("T", bound="FmuExportStatusResponse")


@_attrs_define
class FmuExportStatusResponse:
    """The job resource: poll it, or stream ``.../stream`` for live progress.

    Read ``units_done``/``units_total`` for progress: they are weighted by
    expected cost and rise monotonically across the whole job.
    ``chunks_done``/``chunks_total`` are the CURRENT sampling phase's own
    counters and restart when the job moves to the next phase.

        Attributes:
            id (str):
            status (str):
            artifact_available (bool | Unset):  Default: False.
            bytes_ (int | None | Unset):
            chunks_done (int | None | Unset):
            chunks_total (int | None | Unset):
            error (FmuExportJobError | None | Unset):
            eta_s (float | None | Unset):
            filename (None | str | Unset):
            object_ (str | Unset):  Default: 'fmu_export'.
            phase (None | str | Unset):
            phase_count (int | None | Unset):
            phase_index (int | None | Unset):
            progress (float | None | Unset):
            started_at (float | None | Unset):
            units_done (int | None | Unset):
            units_total (int | None | Unset):
            updated_at (float | None | Unset):
    """

    id: str
    status: str
    artifact_available: bool | Unset = False
    bytes_: int | None | Unset = UNSET
    chunks_done: int | None | Unset = UNSET
    chunks_total: int | None | Unset = UNSET
    error: FmuExportJobError | None | Unset = UNSET
    eta_s: float | None | Unset = UNSET
    filename: None | str | Unset = UNSET
    object_: str | Unset = "fmu_export"
    phase: None | str | Unset = UNSET
    phase_count: int | None | Unset = UNSET
    phase_index: int | None | Unset = UNSET
    progress: float | None | Unset = UNSET
    started_at: float | None | Unset = UNSET
    units_done: int | None | Unset = UNSET
    units_total: int | None | Unset = UNSET
    updated_at: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from thrustlab._models.fmu_export_job_error import FmuExportJobError

        id = self.id

        status = self.status

        artifact_available = self.artifact_available

        bytes_: int | None | Unset
        if isinstance(self.bytes_, Unset):
            bytes_ = UNSET
        else:
            bytes_ = self.bytes_

        chunks_done: int | None | Unset
        if isinstance(self.chunks_done, Unset):
            chunks_done = UNSET
        else:
            chunks_done = self.chunks_done

        chunks_total: int | None | Unset
        if isinstance(self.chunks_total, Unset):
            chunks_total = UNSET
        else:
            chunks_total = self.chunks_total

        error: dict[str, Any] | None | Unset
        if isinstance(self.error, Unset):
            error = UNSET
        elif isinstance(self.error, FmuExportJobError):
            error = self.error.to_dict()
        else:
            error = self.error

        eta_s: float | None | Unset
        if isinstance(self.eta_s, Unset):
            eta_s = UNSET
        else:
            eta_s = self.eta_s

        filename: None | str | Unset
        if isinstance(self.filename, Unset):
            filename = UNSET
        else:
            filename = self.filename

        object_ = self.object_

        phase: None | str | Unset
        if isinstance(self.phase, Unset):
            phase = UNSET
        else:
            phase = self.phase

        phase_count: int | None | Unset
        if isinstance(self.phase_count, Unset):
            phase_count = UNSET
        else:
            phase_count = self.phase_count

        phase_index: int | None | Unset
        if isinstance(self.phase_index, Unset):
            phase_index = UNSET
        else:
            phase_index = self.phase_index

        progress: float | None | Unset
        if isinstance(self.progress, Unset):
            progress = UNSET
        else:
            progress = self.progress

        started_at: float | None | Unset
        if isinstance(self.started_at, Unset):
            started_at = UNSET
        else:
            started_at = self.started_at

        units_done: int | None | Unset
        if isinstance(self.units_done, Unset):
            units_done = UNSET
        else:
            units_done = self.units_done

        units_total: int | None | Unset
        if isinstance(self.units_total, Unset):
            units_total = UNSET
        else:
            units_total = self.units_total

        updated_at: float | None | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "status": status,
            }
        )
        if artifact_available is not UNSET:
            field_dict["artifact_available"] = artifact_available
        if bytes_ is not UNSET:
            field_dict["bytes"] = bytes_
        if chunks_done is not UNSET:
            field_dict["chunks_done"] = chunks_done
        if chunks_total is not UNSET:
            field_dict["chunks_total"] = chunks_total
        if error is not UNSET:
            field_dict["error"] = error
        if eta_s is not UNSET:
            field_dict["eta_s"] = eta_s
        if filename is not UNSET:
            field_dict["filename"] = filename
        if object_ is not UNSET:
            field_dict["object"] = object_
        if phase is not UNSET:
            field_dict["phase"] = phase
        if phase_count is not UNSET:
            field_dict["phase_count"] = phase_count
        if phase_index is not UNSET:
            field_dict["phase_index"] = phase_index
        if progress is not UNSET:
            field_dict["progress"] = progress
        if started_at is not UNSET:
            field_dict["started_at"] = started_at
        if units_done is not UNSET:
            field_dict["units_done"] = units_done
        if units_total is not UNSET:
            field_dict["units_total"] = units_total
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from thrustlab._models.fmu_export_job_error import FmuExportJobError

        d = dict(src_dict)
        id = d.pop("id")

        status = d.pop("status")

        artifact_available = d.pop("artifact_available", UNSET)

        def _parse_bytes_(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        bytes_ = _parse_bytes_(d.pop("bytes", UNSET))

        def _parse_chunks_done(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        chunks_done = _parse_chunks_done(d.pop("chunks_done", UNSET))

        def _parse_chunks_total(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        chunks_total = _parse_chunks_total(d.pop("chunks_total", UNSET))

        def _parse_error(data: object) -> FmuExportJobError | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                error_type_0 = FmuExportJobError.from_dict(data)

                return error_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(FmuExportJobError | None | Unset, data)

        error = _parse_error(d.pop("error", UNSET))

        def _parse_eta_s(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        eta_s = _parse_eta_s(d.pop("eta_s", UNSET))

        def _parse_filename(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        filename = _parse_filename(d.pop("filename", UNSET))

        object_ = d.pop("object", UNSET)

        def _parse_phase(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        phase = _parse_phase(d.pop("phase", UNSET))

        def _parse_phase_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        phase_count = _parse_phase_count(d.pop("phase_count", UNSET))

        def _parse_phase_index(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        phase_index = _parse_phase_index(d.pop("phase_index", UNSET))

        def _parse_progress(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        progress = _parse_progress(d.pop("progress", UNSET))

        def _parse_started_at(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        started_at = _parse_started_at(d.pop("started_at", UNSET))

        def _parse_units_done(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        units_done = _parse_units_done(d.pop("units_done", UNSET))

        def _parse_units_total(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        units_total = _parse_units_total(d.pop("units_total", UNSET))

        def _parse_updated_at(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        fmu_export_status_response = cls(
            id=id,
            status=status,
            artifact_available=artifact_available,
            bytes_=bytes_,
            chunks_done=chunks_done,
            chunks_total=chunks_total,
            error=error,
            eta_s=eta_s,
            filename=filename,
            object_=object_,
            phase=phase,
            phase_count=phase_count,
            phase_index=phase_index,
            progress=progress,
            started_at=started_at,
            units_done=units_done,
            units_total=units_total,
            updated_at=updated_at,
        )

        fmu_export_status_response.additional_properties = d
        return fmu_export_status_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
