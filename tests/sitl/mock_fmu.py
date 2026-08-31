"""A stub FMI 3.0 slave that speaks the schema-3 variable names.

Deliberately NOT a mock of :class:`~thrustlab.sitl.model.RotorModel`: it
stubs the level BELOW it, so the tests drive the real
:class:`~thrustlab.sitl.fmu.FmuRotorModel` — name resolution, extent
checks, the Initialization Mode dance, set-then-step-then-get — over synthetic
values.  What that CANNOT prove is anything about the exported DLL's own
physics; see the README's "What only U5 can prove".

The stub physics are linear and hand-checkable on purpose:

    rpm_i      = RPM_PER_THROTTLE * throttle_i
    thrust_i   = THRUST_PER_THROTTLE * throttle_i
    torque_i   = -sense_i * TORQUE_PER_THROTTLE * throttle_i   # = -s_i Q_aero
    inplane_i  = INPLANE_PER_THROTTLE_EDGE * throttle_i * v_edge_i
    current    = CURRENT_PER_THROTTLE * Σ throttle_i
    voltage    = OPEN_CIRCUIT_V - PACK_RESISTANCE_OHM * current
    soc       -= current * dt / (3600 * PACK_CAPACITY_AH)
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np

RPM_PER_THROTTLE = 24000.0
THRUST_PER_THROTTLE = 6.0
TORQUE_PER_THROTTLE = 0.09
INPLANE_PER_THROTTLE_EDGE = 0.05
CURRENT_PER_THROTTLE = 22.0
OPEN_CIRCUIT_V = 25.2
PACK_RESISTANCE_OHM = 0.02
PACK_CAPACITY_AH = 1.5


@dataclass
class StubVariable:
    """Duck-types enough of fmpy's ``ScalarVariable`` for ``build_variable_map``."""

    name: str
    valueReference: int
    type: str
    shape: tuple[int, ...] = ()


@dataclass
class StubModelDescription:
    modelVariables: list[StubVariable]
    fmiVersion: str = "3.0"
    instantiationToken: str = "stub"


def build_model_description(n_rotors: int) -> StubModelDescription:
    """Appendix A's names at the extents a real N-rotor export would carry."""
    per_rotor = ("Float64", (n_rotors,))
    variables = [
        StubVariable("throttle", 1, *per_rotor),
        StubVariable("v_axial_m_s", 2, *per_rotor),
        StubVariable("air_density_kg_m3", 3, "Float64"),
        StubVariable("v_edge_m_s", 5, *per_rotor),
        StubVariable("ambient_temp_C", 6, "Float64"),
        StubVariable("thrust_N", 10, *per_rotor),
        StubVariable("torque_Nm", 11, *per_rotor),
        StubVariable("force_inplane_N", 12, *per_rotor),
        StubVariable("rpm", 13, *per_rotor),
        StubVariable("rotor_in_envelope", 14, "Boolean", (n_rotors,)),
        StubVariable("voltage_bus_V", 20, "Float64"),
        StubVariable("current_bus_A", 21, "Float64"),
        StubVariable("battery_soc", 22, "Float64"),
        StubVariable("all_in_envelope", 23, "Boolean"),
        StubVariable("use_vehicle_frame", 30, "Boolean"),
        StubVariable("initial_soc", 31, "Float64"),
    ]
    return StubModelDescription(modelVariables=variables)


class StubSlaveError(RuntimeError):
    """The stub was driven in a way a conforming FMU would refuse."""


@dataclass
class StubSlave:
    """Records the FMI call sequence and answers with the linear stub physics."""

    n_rotors: int
    senses: Sequence[float]
    initial_soc: float = 1.0

    values: dict[int, list[Any]] = field(default_factory=dict)
    calls: list[str] = field(default_factory=list)
    mode: str = "instantiated"
    reset_count: int = 0
    step_count: int = 0
    get_float64_calls: int = 0
    get_boolean_calls: int = 0
    #: Stand-in for the DLL's lazy bus solve, which the core bench measures at
    #: ~23.5 us per fmi3GetFloat64 REQUEST regardless of how many variables the
    #: request names. Counting requests is therefore counting solves.
    bus_solves: int = 0
    last_step: tuple[float, float] | None = None
    terminated: bool = False
    freed: bool = False

    def __post_init__(self) -> None:
        self._seed()

    def _seed(self) -> None:
        zeros = [0.0] * self.n_rotors
        self.values = {
            1: list(zeros),
            2: list(zeros),
            3: [1.225],
            5: list(zeros),
            6: [25.0],
            10: list(zeros),
            11: list(zeros),
            12: list(zeros),
            13: list(zeros),
            14: [True] * self.n_rotors,
            20: [OPEN_CIRCUIT_V],
            21: [0.0],
            22: [self.initial_soc],
            23: [True],
            30: [False],
            31: [self.initial_soc],
        }

    # ------------------------------------------------------------- lifecycle

    def enterInitializationMode(self, tolerance=None, startTime=0.0, stopTime=None) -> None:
        if self.mode not in ("instantiated",):
            raise StubSlaveError(f"enterInitializationMode from mode {self.mode}")
        self.mode = "initialization"
        self.calls.append("enterInitializationMode")

    def exitInitializationMode(self) -> None:
        if self.mode != "initialization":
            raise StubSlaveError(f"exitInitializationMode from mode {self.mode}")
        self.mode = "step"
        self.calls.append("exitInitializationMode")

    def reset(self) -> None:
        self.mode = "instantiated"
        self.reset_count += 1
        self.calls.append("reset")
        self._seed()

    def terminate(self) -> None:
        self.terminated = True
        self.calls.append("terminate")

    def freeInstance(self) -> None:
        self.freed = True
        self.calls.append("freeInstance")

    # -------------------------------------------------------------- get/set

    def setFloat64(self, vr: Sequence[int], values: Sequence[float]) -> None:
        if self.mode not in ("initialization", "step"):
            raise StubSlaveError(f"setFloat64 in mode {self.mode}")
        self._store(vr, [float(v) for v in values])

    def setBoolean(self, vr: Sequence[int], values: Sequence[bool]) -> None:
        if len(vr) == 1 and vr[0] == 30 and self.mode != "initialization":
            raise StubSlaveError(
                "use_vehicle_frame has variability=fixed and is settable in "
                "Initialization Mode only"
            )
        self._store(vr, [bool(v) for v in values])

    def _store(self, vr: Sequence[int], values: list[Any]) -> None:
        if len(vr) != 1:
            raise StubSlaveError("the bridge sets one value reference at a time")
        slot = self.values.get(vr[0])
        if slot is None:
            raise StubSlaveError(f"unknown value reference {vr[0]}")
        if len(values) != len(slot):
            raise StubSlaveError(
                f"value reference {vr[0]} has extent {len(slot)}, got {len(values)} values"
            )
        self.values[vr[0]] = values

    def getFloat64(self, vr: Sequence[int], nValues: int | None = None) -> list[float]:
        self.get_float64_calls += 1
        self.bus_solves += 1  # the real DLL pays one lazy bus solve per REQUEST
        return self._load(vr, nValues)

    def getBoolean(self, vr: Sequence[int], nValues: int | None = None) -> list[bool]:
        self.get_boolean_calls += 1
        return self._load(vr, nValues)

    def _load(self, vr: Sequence[int], n_values: int | None) -> list[Any]:
        """FMI 3 concatenates the values of every requested VR, in order.

        The bridge batches its whole output block into one call per data type,
        so the stub honours multi-VR requests and enforces the standard's exact
        total-``nValues`` rule against the concatenated length.
        """
        if not vr:
            raise StubSlaveError("a get call must name at least one value reference")
        values: list[Any] = []
        for reference in vr:
            slot = self.values.get(reference)
            if slot is None:
                raise StubSlaveError(f"unknown value reference {reference}")
            values.extend(slot)
        if n_values is not None and n_values != len(values):
            raise StubSlaveError(
                f"value references {list(vr)} total {len(values)} elements, asked for {n_values}"
            )
        return values

    # ------------------------------------------------------------------ step

    def doStep(
        self,
        currentCommunicationPoint: float,
        communicationStepSize: float,
        noSetFMUStatePriorToCurrentPoint: bool = True,
    ) -> tuple[bool, bool, bool, float]:
        if self.mode != "step":
            raise StubSlaveError(f"doStep in mode {self.mode}")
        self.step_count += 1
        self.last_step = (currentCommunicationPoint, communicationStepSize)
        self.calls.append("doStep")

        throttle = np.asarray(self.values[1], dtype=float)
        v_edge = np.asarray(self.values[5], dtype=float)
        senses = np.asarray(self.senses, dtype=float)

        self.values[13] = list(RPM_PER_THROTTLE * throttle)
        self.values[10] = list(THRUST_PER_THROTTLE * throttle)
        # Decision 5 rev 2.1: torque_Nm is the SIGNED REACTION, -s_i Q_i^aero.
        self.values[11] = list(-senses * TORQUE_PER_THROTTLE * throttle)
        self.values[12] = list(INPLANE_PER_THROTTLE_EDGE * throttle * v_edge)

        current = float(CURRENT_PER_THROTTLE * throttle.sum())
        self.values[21] = [current]
        self.values[20] = [OPEN_CIRCUIT_V - PACK_RESISTANCE_OHM * current]
        soc = self.values[22][0] - current * communicationStepSize / (3600.0 * PACK_CAPACITY_AH)
        self.values[22] = [max(0.0, soc)]

        in_envelope = [bool(t <= 1.0 + 1e-12) for t in throttle]
        self.values[14] = in_envelope
        self.values[23] = [all(in_envelope)]
        return (False, False, False, currentCommunicationPoint + communicationStepSize)
