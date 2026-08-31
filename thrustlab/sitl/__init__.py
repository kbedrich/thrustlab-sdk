"""SITL external-physics backend driven by a ThrustLab schema-3 FMU.

The sign and wrench conventions live in exactly one place,
:mod:`thrustlab.sitl.kinematics`; the frames are documented in
:mod:`thrustlab.sitl.rigidbody`.

Two autopilots are supported.  ArduPilot's JSON backend is the original target
and keeps this package's name and its whole public surface; Betaflight SITL is
:mod:`thrustlab.sitl.targets.betaflight`.  Both drive the same physics
core through the seams in :mod:`thrustlab.sitl.targets`.
"""

from __future__ import annotations

from .bridge import Bridge, BridgeCounters, BridgeServer, FrameResult
from .fmu import FmuError, FmuRotorModel, VariableRef, build_variable_map
from .kinematics import DiscInflow, assemble_wrench, disc_inflow
from .model import RotorModel, RotorOutputs
from .protocol import (
    MAGIC_16,
    MAGIC_32,
    ProtocolError,
    ServoPacket,
    StateReply,
    decode_servo_packet,
    encode_servo_packet,
    encode_state_json,
)
from .rigidbody import BodyState, RigidBody
from .rpmlog import RotorLog
from .targets import PhysicsCore, StateSample, StepResult
from .targets.betaflight import (
    BetaflightBridge,
    BetaflightProtocolError,
    BetaflightServer,
    HomeOrigin,
    MotorPacket,
    decode_motor_packet,
    encode_motor_packet,
    encode_rc_packet,
)
from .vehicle import (
    RotorConfig,
    VehicleConfig,
    VehicleConfigError,
    load_vehicle_config,
    parse_vehicle_config,
)

__version__ = "0.1.0"

__all__ = [
    "MAGIC_16",
    "MAGIC_32",
    "BetaflightBridge",
    "BetaflightProtocolError",
    "BetaflightServer",
    "BodyState",
    "Bridge",
    "BridgeCounters",
    "BridgeServer",
    "DiscInflow",
    "FmuError",
    "FmuRotorModel",
    "FrameResult",
    "HomeOrigin",
    "MotorPacket",
    "PhysicsCore",
    "ProtocolError",
    "RigidBody",
    "RotorConfig",
    "RotorLog",
    "RotorModel",
    "RotorOutputs",
    "ServoPacket",
    "StateReply",
    "StateSample",
    "StepResult",
    "VariableRef",
    "VehicleConfig",
    "VehicleConfigError",
    "assemble_wrench",
    "build_variable_map",
    "decode_motor_packet",
    "decode_servo_packet",
    "disc_inflow",
    "encode_motor_packet",
    "encode_rc_packet",
    "encode_servo_packet",
    "encode_state_json",
    "load_vehicle_config",
    "parse_vehicle_config",
]
