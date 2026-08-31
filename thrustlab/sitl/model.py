"""The propulsion-model seam the bridge steps.

The bridge never talks to fmpy directly: it talks to :class:`RotorModel`.  The
real implementation is :class:`thrustlab.sitl.fmu.FmuRotorModel`; the
tests drive the identical step path through a stub slave, which is what makes
the wrench mapping and battery feedback provable without an exported FMU.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np


@dataclass(frozen=True)
class RotorOutputs:
    """One communication point's worth of FMU outputs (spec decision 11).

    Per-rotor arrays are indexed by ``rotor_index`` (flat ``0..N-1``).
    ``torque_Nm`` is the raw FMU output; how it becomes the reaction moment is
    :func:`thrustlab.sitl.kinematics.assemble_wrench`'s job, governed by
    the vehicle YAML's ``fmu.torque_convention``.
    """

    thrust_N: np.ndarray
    torque_Nm: np.ndarray
    force_inplane_N: np.ndarray
    rpm: np.ndarray
    voltage_bus_V: float
    current_bus_A: float
    battery_soc: float
    rotor_in_envelope: np.ndarray
    all_in_envelope: bool


@runtime_checkable
class RotorModel(Protocol):
    """Set inputs, take one step, read outputs.  Nothing else."""

    n_rotors: int

    def set_inputs(
        self,
        *,
        throttle: np.ndarray,
        v_axial_m_s: np.ndarray,
        v_edge_m_s: np.ndarray,
        air_density_kg_m3: float,
        ambient_temp_C: float,
    ) -> None: ...

    def do_step(self, current_time_s: float, step_size_s: float) -> None: ...

    def get_outputs(self) -> RotorOutputs: ...

    def reset(self) -> None:
        """Return to Instantiated, re-enter Initialization Mode, exit to Step Mode.

        Spec decision 8: ``fmi3Reset`` REQUIRES re-initialisation before the
        next step, so an implementation must do both halves here.
        """
        ...

    def terminate(self) -> None: ...
