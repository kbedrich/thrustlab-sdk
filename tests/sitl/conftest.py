"""Shared fixtures.  No network, no FMU, no ArduPilot binary."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import pytest
import yaml

from thrustlab.sitl.fmu import FmuRotorModel, build_variable_map
from thrustlab.sitl.vehicle import VehicleConfig, parse_vehicle_config

from .mock_fmu import StubSlave, build_model_description

EXAMPLES = Path(__file__).resolve().parents[2] / "examples" / "fmu"
QUAD_YAML = EXAMPLES / "quad_5inch_x.yaml"


@pytest.fixture
def quad_document() -> dict[str, Any]:
    """The shipped example YAML, parsed but not validated — mutate freely."""
    return copy.deepcopy(yaml.safe_load(QUAD_YAML.read_text(encoding="utf-8")))


@pytest.fixture
def quad(quad_document: dict[str, Any]) -> VehicleConfig:
    return parse_vehicle_config(quad_document)


@pytest.fixture
def stub_slave(quad: VehicleConfig) -> StubSlave:
    return StubSlave(n_rotors=quad.rotor_count, senses=list(quad.senses))


@pytest.fixture
def stub_model(quad: VehicleConfig, stub_slave: StubSlave) -> FmuRotorModel:
    """A real FmuRotorModel over the stub slave — name resolution included."""
    variables = build_variable_map(build_model_description(quad.rotor_count))
    return FmuRotorModel(
        stub_slave,
        variables,
        quad.rotor_count,
        air_density_kg_m3=quad.air_density_kg_m3,
        ambient_temp_C=quad.ambient_temp_C,
    )
