"""FMI 3.0 Co-Simulation client: resolve variables BY NAME, step, read back.

Value references are never hardcoded.  The FMU's ``modelDescription.xml`` is
generated per export and the ``instantiationToken`` is a contract hash over N
and the variable layout, so a VR baked into this bridge would be wrong the
first time N changes.  :func:`build_variable_map` reads the names from the
model description and everything downstream goes through it.

The bridge always runs the FMU in DISC mode: ``use_vehicle_frame`` is set false
during Initialization Mode, and the bridge itself owns the per-rotor kinematics
and the wrench assembly so that the vehicle YAML — not the FMU's geometry
parameters — is the single source of airframe truth.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .model import RotorOutputs

logger = logging.getLogger(__name__)

# Appendix A names.  Required = the bridge cannot run without them.
INPUT_THROTTLE = "throttle"
INPUT_V_AXIAL = "v_axial_m_s"
INPUT_V_EDGE = "v_edge_m_s"
INPUT_AIR_DENSITY = "air_density_kg_m3"
INPUT_AMBIENT_TEMP = "ambient_temp_C"

OUTPUT_THRUST = "thrust_N"
OUTPUT_TORQUE = "torque_Nm"
OUTPUT_FORCE_INPLANE = "force_inplane_N"
OUTPUT_RPM = "rpm"
OUTPUT_VOLTAGE = "voltage_bus_V"
OUTPUT_CURRENT = "current_bus_A"
OUTPUT_SOC = "battery_soc"
OUTPUT_ROTOR_ENVELOPE = "rotor_in_envelope"
OUTPUT_ALL_ENVELOPE = "all_in_envelope"

PARAM_USE_VEHICLE_FRAME = "use_vehicle_frame"

#: Every Appendix-A variable the bridge touches.  ALL of them are required.
#:
#: Decision 9 makes the variable table normative, so a missing name means the
#: FMU is not a conforming schema-3 export and the bridge refuses to load it,
#: naming what is absent.  Substituting a default would be worse than useless:
#: a fabricated zero ``force_inplane_N`` silently deletes the H-force from every
#: wrench, and a fabricated all-true ``rotor_in_envelope`` reports a clamped,
#: out-of-envelope solve as trustworthy.  Both would fly, and both would lie.
#:
#: This is the bridge's own contract surface, a SUBSET of Appendix A — the
#: vehicle-mode variables (``v_body_m_s``, ``rotor_position_m``, …) are absent
#: from this list because the bridge runs the FMU in disc mode and never touches
#: them.  Validating the whole table against the export is the cross-language
#: contract test's job (decision 10), not this bridge's.
REQUIRED_VARIABLES = (
    INPUT_THROTTLE,
    INPUT_V_AXIAL,
    INPUT_V_EDGE,
    INPUT_AIR_DENSITY,
    INPUT_AMBIENT_TEMP,
    PARAM_USE_VEHICLE_FRAME,
    OUTPUT_THRUST,
    OUTPUT_TORQUE,
    OUTPUT_FORCE_INPLANE,
    OUTPUT_RPM,
    OUTPUT_VOLTAGE,
    OUTPUT_CURRENT,
    OUTPUT_SOC,
    OUTPUT_ROTOR_ENVELOPE,
    OUTPUT_ALL_ENVELOPE,
)

#: Variables Appendix A itself marks optional.  Currently EMPTY — the table
#: contracts every name above.  A future genuinely-optional variable goes here
#: and gets a documented fallback in :meth:`FmuRotorModel.get_outputs`; nothing
#: else may be treated as absent.
OPTIONAL_VARIABLES: tuple[str, ...] = ()

_FLOAT_TYPES = frozenset({"Float64", "Float32", "Real"})
_BOOL_TYPES = frozenset({"Boolean"})

#: Every Float64 output the bridge reads, in the order they are requested in the
#: single batched ``fmi3GetFloat64`` call per frame.
FLOAT_OUTPUTS = (
    OUTPUT_THRUST,
    OUTPUT_TORQUE,
    OUTPUT_FORCE_INPLANE,
    OUTPUT_RPM,
    OUTPUT_VOLTAGE,
    OUTPUT_CURRENT,
    OUTPUT_SOC,
)

#: Likewise for the Boolean envelope flags.
BOOL_OUTPUTS = (OUTPUT_ROTOR_ENVELOPE, OUTPUT_ALL_ENVELOPE)


class FmuError(RuntimeError):
    """The FMU is missing a contracted variable, or an FMI call failed."""


@dataclass(frozen=True)
class VariableRef:
    """One resolved model variable."""

    name: str
    value_reference: int
    type_name: str
    extent: int

    @property
    def is_array(self) -> bool:
        return self.extent != 1


@dataclass(frozen=True)
class _ReadPlan:
    """A frozen layout for one batched FMI get call.

    ``value_references`` goes on the wire as-is; ``offsets`` maps each variable
    name to its ``(start, extent)`` slice of the flat result, which FMI 3
    concatenates in value-reference order.
    """

    value_references: list[int]
    total_values: int
    offsets: dict[str, tuple[int, int]]


def _extent(variable: Any) -> int:
    """Total element count of a model variable.

    fmpy exposes FMI 3 array shapes as ``ScalarVariable.shape``; a scalar has an
    empty shape.  Fall back to ``dimensions`` for description objects that only
    carry the raw dimension list.
    """
    shape = getattr(variable, "shape", None)
    if shape:
        total = 1
        for extent in shape:
            total *= int(extent)
        return total
    dimensions = getattr(variable, "dimensions", None)
    if dimensions:
        total = 1
        for dimension in dimensions:
            start = getattr(dimension, "start", None)
            if start is None:
                raise FmuError(
                    f"variable '{getattr(variable, 'name', '?')}' has a dimension resolved by "
                    "value reference; the bridge only supports fixed-extent arrays"
                )
            total *= int(start)
        return total
    return 1


def build_variable_map(model_description: Any) -> dict[str, VariableRef]:
    """Index a model description's variables by NAME.

    Duplicate names are a hard error: spec decision 9 makes name uniqueness part
    of the generated-XML contract, and a silent last-one-wins here would resolve
    the wrong array.
    """
    variables: dict[str, VariableRef] = {}
    for variable in model_description.modelVariables:
        name = variable.name
        if name in variables:
            raise FmuError(
                f"modelDescription.xml declares '{name}' more than once; the schema-3 "
                "contract requires unique variable names (spec decision 9)"
            )
        variables[name] = VariableRef(
            name=name,
            value_reference=int(variable.valueReference),
            type_name=str(variable.type),
            extent=_extent(variable),
        )
    return variables


#: Appendix-A names carrying one value per rotor.
PER_ROTOR_VARIABLES = (
    INPUT_THROTTLE,
    INPUT_V_AXIAL,
    INPUT_V_EDGE,
    OUTPUT_THRUST,
    OUTPUT_TORQUE,
    OUTPUT_FORCE_INPLANE,
    OUTPUT_RPM,
    OUTPUT_ROTOR_ENVELOPE,
)

#: Appendix-A names carrying exactly one value for the whole system.
SCALAR_VARIABLES = (
    INPUT_AIR_DENSITY,
    INPUT_AMBIENT_TEMP,
    PARAM_USE_VEHICLE_FRAME,
    OUTPUT_VOLTAGE,
    OUTPUT_CURRENT,
    OUTPUT_SOC,
    OUTPUT_ALL_ENVELOPE,
)


def _check_contract(variables: Mapping[str, VariableRef], n_rotors: int) -> None:
    """Refuse anything that is not a conforming schema-3 export, loudly.

    Decision 9 makes Appendix A normative; every name the bridge touches must be
    declared, at the right extent.  Nothing is substituted — see
    :data:`REQUIRED_VARIABLES` for why a fallback is the wrong answer here.
    """
    missing = [name for name in REQUIRED_VARIABLES if name not in variables]
    if missing:
        available = ", ".join(sorted(variables)) or "(none)"
        raise FmuError(
            "FMU does not declare the schema-3 variable(s) "
            f"{', '.join(missing)}. Appendix A of the schema-3 spec contracts every one of "
            f"{', '.join(REQUIRED_VARIABLES)}, and the bridge substitutes nothing for a missing "
            f"name. The FMU declares: {available}"
        )

    for name in PER_ROTOR_VARIABLES:
        ref = variables[name]
        if ref.extent != n_rotors:
            raise FmuError(
                f"FMU variable '{name}' has extent {ref.extent} but the vehicle YAML declares "
                f"{n_rotors} rotors; the vehicle and the FMU describe different aircraft"
            )

    for name in SCALAR_VARIABLES:
        ref = variables[name]
        if ref.extent != 1:
            raise FmuError(
                f"FMU variable '{name}' has extent {ref.extent}; Appendix A declares it a scalar, "
                "and reading element 0 of an unexpected array would silently hide the mismatch"
            )


class FmuRotorModel:
    """Drive one schema-3 propulsion FMU through its Co-Simulation interface."""

    def __init__(
        self,
        slave: Any,
        variables: Mapping[str, VariableRef],
        n_rotors: int,
        *,
        air_density_kg_m3: float = 1.225,
        ambient_temp_C: float = 25.0,
        tolerance: float | None = None,
        owns_slave: bool = True,
    ) -> None:
        _check_contract(variables, n_rotors)
        self._slave = slave
        self._variables = dict(variables)
        self.n_rotors = int(n_rotors)
        self._tolerance = tolerance
        self._owns_slave = owns_slave
        self._initial_air_density = float(air_density_kg_m3)
        self._initial_ambient_temp = float(ambient_temp_C)
        # Frozen once: the per-frame read then costs one FMI call per data type.
        self._float_output_plan = self._build_plan(FLOAT_OUTPUTS, _FLOAT_TYPES)
        self._bool_output_plan = self._build_plan(BOOL_OUTPUTS, _BOOL_TYPES)
        self._initialise()

    # ------------------------------------------------------------------ setup

    @classmethod
    def from_file(
        cls,
        fmu_path: str | Path,
        n_rotors: int,
        *,
        air_density_kg_m3: float = 1.225,
        ambient_temp_C: float = 25.0,
        tolerance: float | None = None,
    ) -> FmuRotorModel:
        """Extract, instantiate and initialise the FMU at ``fmu_path``.

        fmpy is imported here rather than at module scope so the pure-Python
        parts of the bridge (and its test suite) stay importable without it.
        """
        try:
            import fmpy
        except ImportError as exc:  # pragma: no cover - dependency is declared
            raise FmuError("fmpy is required to load an FMU: pip install 'fmpy>=0.3.31'") from exc

        path = Path(fmu_path)
        if not path.is_file():
            raise FmuError(f"FMU not found: {path}")

        model_description = fmpy.read_model_description(str(path))
        if not str(model_description.fmiVersion).startswith("3"):
            raise FmuError(
                f"{path} declares FMI {model_description.fmiVersion}; the schema-3 bridge "
                "requires an FMI 3.0 Co-Simulation FMU"
            )
        if model_description.coSimulation is None:
            raise FmuError(f"{path} does not provide a Co-Simulation interface")

        unzip_dir = fmpy.extract(str(path))
        slave = fmpy.instantiate_fmu(
            unzip_dir, model_description, fmi_type="CoSimulation", visible=False
        )
        variables = build_variable_map(model_description)
        logger.info(
            "loaded %s (FMI %s, instantiationToken %s) with %d declared variables",
            path.name,
            model_description.fmiVersion,
            model_description.instantiationToken,
            len(variables),
        )
        return cls(
            slave,
            variables,
            n_rotors,
            air_density_kg_m3=air_density_kg_m3,
            ambient_temp_C=ambient_temp_C,
            tolerance=tolerance,
        )

    def _initialise(self) -> None:
        """Initialization Mode: pin the fixed parameters, then enter Step Mode."""
        self._slave.enterInitializationMode(tolerance=self._tolerance, startTime=0.0)
        # Disc mode. use_vehicle_frame has variability=fixed, so this is the ONLY
        # place it can be written (spec decision 4).
        self._set_bool(PARAM_USE_VEHICLE_FRAME, False)
        self._set_float(INPUT_AIR_DENSITY, [self._initial_air_density])
        self._set_float(INPUT_AMBIENT_TEMP, [self._initial_ambient_temp])
        zeros = [0.0] * self.n_rotors
        self._set_float(INPUT_THROTTLE, zeros)
        self._set_float(INPUT_V_AXIAL, zeros)
        self._set_float(INPUT_V_EDGE, zeros)
        self._slave.exitInitializationMode()

    # ------------------------------------------------------------ raw get/set

    def _ref(self, name: str, *, optional: bool) -> VariableRef | None:
        ref = self._variables.get(name)
        if ref is None and not optional:
            raise FmuError(f"FMU variable '{name}' is not declared")
        return ref

    def _set_float(self, name: str, values: list[float], *, optional: bool = False) -> None:
        ref = self._ref(name, optional=optional)
        if ref is None:
            return
        if ref.type_name not in _FLOAT_TYPES:
            raise FmuError(f"FMU variable '{name}' is {ref.type_name}, expected a float type")
        if len(values) != ref.extent:
            raise FmuError(
                f"FMU variable '{name}' has extent {ref.extent}; refusing to set {len(values)} "
                "values (FMI 3 requires the total nValues to match exactly)"
            )
        self._slave.setFloat64([ref.value_reference], values)

    def _set_bool(self, name: str, value: bool, *, optional: bool = False) -> None:
        ref = self._ref(name, optional=optional)
        if ref is None:
            return
        if ref.type_name not in _BOOL_TYPES:
            raise FmuError(f"FMU variable '{name}' is {ref.type_name}, expected Boolean")
        self._slave.setBoolean([ref.value_reference], [value])

    def _build_plan(self, names: tuple[str, ...], type_names: frozenset[str]) -> _ReadPlan:
        """Freeze the VR list and the slice offsets for one batched read.

        Built once at construction: the layout only depends on the model
        description, so the per-frame path does no bookkeeping at all.
        """
        refs: list[VariableRef] = []
        offsets: dict[str, tuple[int, int]] = {}
        cursor = 0
        for name in names:
            ref = self._variables.get(name)
            if ref is None:
                if name in OPTIONAL_VARIABLES:
                    continue  # Appendix A marks it optional; get_outputs defaults it
                raise FmuError(f"FMU variable '{name}' is not declared")
            if ref.type_name not in type_names:
                raise FmuError(
                    f"FMU variable '{name}' is {ref.type_name}, expected one of "
                    f"{sorted(type_names)}"
                )
            refs.append(ref)
            offsets[name] = (cursor, ref.extent)
            cursor += ref.extent
        return _ReadPlan(
            value_references=[ref.value_reference for ref in refs],
            total_values=cursor,
            offsets=offsets,
        )

    def _read(self, plan: _ReadPlan, getter, dtype) -> dict[str, np.ndarray]:
        """One FMI get call, then slice the flat result by the frozen offsets.

        FMI 3 concatenates the values of every requested value reference in the
        order the references are given (spec decision 7), so a single call can
        carry the whole output block.
        """
        if not plan.value_references:
            return {}
        values = getter(plan.value_references, nValues=plan.total_values)
        array = np.asarray(values, dtype=dtype).reshape(-1)
        if array.size != plan.total_values:
            raise FmuError(
                f"FMU returned {array.size} values for a batched read of "
                f"{len(plan.value_references)} variable(s) totalling {plan.total_values} elements"
            )
        return {
            name: array[start : start + extent]
            for name, (start, extent) in plan.offsets.items()
        }

    # ------------------------------------------------------------- step cycle

    def set_inputs(
        self,
        *,
        throttle: np.ndarray,
        v_axial_m_s: np.ndarray,
        v_edge_m_s: np.ndarray,
        air_density_kg_m3: float,
        ambient_temp_C: float,
    ) -> None:
        self._set_float(INPUT_THROTTLE, [float(v) for v in throttle])
        self._set_float(INPUT_V_AXIAL, [float(v) for v in v_axial_m_s])
        self._set_float(INPUT_V_EDGE, [float(v) for v in v_edge_m_s])
        self._set_float(INPUT_AIR_DENSITY, [float(air_density_kg_m3)])
        self._set_float(INPUT_AMBIENT_TEMP, [float(ambient_temp_C)])

    def do_step(self, current_time_s: float, step_size_s: float) -> None:
        result = self._slave.doStep(
            currentCommunicationPoint=float(current_time_s),
            communicationStepSize=float(step_size_s),
        )
        # fmpy's FMU3Slave.doStep returns
        # (eventEncountered, terminateSimulation, earlyReturn, lastSuccessfulTime).
        if isinstance(result, tuple) and len(result) >= 2 and bool(result[1]):
            raise FmuError(
                f"FMU requested termination during doStep at t={current_time_s:.6f} s"
            )

    def get_outputs(self) -> RotorOutputs:
        """Read the whole output block in TWO FMI calls, one per data type.

        The DLL computes outputs lazily and every ``fmi3GetFloat64`` REQUEST
        pays one bus solve — ~23.5 µs on the core implementation's bench — while
        the cost does not depend on how many variables the request names.
        Reading variable by variable therefore multiplied the per-frame solve
        cost by the number of Float64 output lanes; at 400 Hz that is ~9 ms/s
        batched against ~66 ms/s for the seven-lane schema-3 block.  So: one
        request for every Float64 output, one for the Boolean envelope flags.

        Every name below is contracted by Appendix A and was checked present at
        load, so these are direct lookups: nothing is defaulted, and no absent
        lane can be mistaken for a real zero.
        """
        floats = self._read(self._float_output_plan, self._slave.getFloat64, float)
        booleans = self._read(self._bool_output_plan, self._slave.getBoolean, bool)

        return RotorOutputs(
            thrust_N=floats[OUTPUT_THRUST],
            torque_Nm=floats[OUTPUT_TORQUE],
            force_inplane_N=floats[OUTPUT_FORCE_INPLANE],
            rpm=floats[OUTPUT_RPM],
            voltage_bus_V=float(floats[OUTPUT_VOLTAGE][0]),
            current_bus_A=float(floats[OUTPUT_CURRENT][0]),
            battery_soc=float(floats[OUTPUT_SOC][0]),
            rotor_in_envelope=booleans[OUTPUT_ROTOR_ENVELOPE],
            all_in_envelope=bool(booleans[OUTPUT_ALL_ENVELOPE][0]),
        )

    def reset(self) -> None:
        """Full restart: ``fmi3Reset`` then re-initialise (spec decision 8)."""
        self._slave.reset()
        self._initialise()

    def terminate(self) -> None:
        try:
            self._slave.terminate()
        finally:
            if self._owns_slave:
                free = getattr(self._slave, "freeInstance", None)
                if free is not None:
                    free()
