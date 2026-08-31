"""Per-rotor RPM (and the rest of the per-rotor lane) to a plain CSV.

The ArduPilot JSON protocol has NO RPM lane — ``keytable[36]`` in ``SIM_JSON.h``
carries battery, airspeed, rangefinders, RC and wind, and nothing else — so
per-rotor rotational state cannot reach the flight log through the wire at all.
It is written here instead, one row per physics frame, so a SITL run can still
be reconciled against the FMU's ``rpm[]`` afterwards.

One wide row per frame keeps it directly plottable; the per-rotor columns are
suffixed with the rotor index.
"""

from __future__ import annotations

import csv
from pathlib import Path
from types import TracebackType

import numpy as np


class RotorLog:
    """Append-only CSV of per-frame, per-rotor propulsion state."""

    def __init__(self, path: str | Path, n_rotors: int) -> None:
        self.path = Path(path)
        self.n_rotors = int(n_rotors)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = self.path.open("w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._handle)
        self._writer.writerow(self._header())
        self.rows_written = 0

    def _header(self) -> list[str]:
        columns = [
            "timestamp_s",
            "frame_count",
            "dt_s",
            "voltage_bus_V",
            "current_bus_A",
            "battery_soc",
            "all_in_envelope",
        ]
        for prefix in (
            "throttle",
            "rpm",
            "thrust_N",
            "torque_Nm",
            "force_inplane_N",
            "v_axial_m_s",
            "v_edge_m_s",
            "in_envelope",
        ):
            columns.extend(f"{prefix}_{i}" for i in range(self.n_rotors))
        return columns

    def write(
        self,
        *,
        timestamp_s: float,
        frame_count: int,
        dt_s: float,
        voltage_bus_V: float,
        current_bus_A: float,
        battery_soc: float,
        all_in_envelope: bool,
        throttle: np.ndarray,
        rpm: np.ndarray,
        thrust_N: np.ndarray,
        torque_Nm: np.ndarray,
        force_inplane_N: np.ndarray,
        v_axial_m_s: np.ndarray,
        v_edge_m_s: np.ndarray,
        rotor_in_envelope: np.ndarray,
    ) -> None:
        row: list[object] = [
            f"{timestamp_s:.6f}",
            frame_count,
            f"{dt_s:.6f}",
            f"{voltage_bus_V:.6g}",
            f"{current_bus_A:.6g}",
            f"{battery_soc:.6g}",
            int(all_in_envelope),
        ]
        for values in (
            throttle,
            rpm,
            thrust_N,
            torque_Nm,
            force_inplane_N,
            v_axial_m_s,
            v_edge_m_s,
        ):
            row.extend(f"{float(v):.6g}" for v in np.asarray(values).reshape(-1))
        row.extend(int(bool(v)) for v in np.asarray(rotor_in_envelope).reshape(-1))
        self._writer.writerow(row)
        self.rows_written += 1

    def flush(self) -> None:
        self._handle.flush()

    def close(self) -> None:
        if not self._handle.closed:
            self._handle.close()

    def __enter__(self) -> RotorLog:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()
