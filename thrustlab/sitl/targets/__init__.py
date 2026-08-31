"""Per-autopilot protocol targets around one shared physics core.

Everything an autopilot-specific target has to supply is one of three seams,
declared in :mod:`thrustlab.sitl.targets.base`:

``ChannelSource``
    PWM microseconds for a 1-based output channel — exactly what
    :meth:`~thrustlab.sitl.vehicle.VehicleConfig.throttles` consumes.
``FrameClock``
    inbound packet -> ``dt`` plus the advance / duplicate / restart decision.
``StateEncoder``
    a :class:`~thrustlab.sitl.targets.base.StateSample` (NED world, FRD
    body, ``(w, x, y, z)`` body->NED quaternion) -> the outbound bytes.

:mod:`~thrustlab.sitl.targets.ardupilot` holds ArduPilot's JSON backend;
:mod:`~thrustlab.sitl.targets.betaflight` holds Betaflight SITL's binary
UDP triple.  The 6DOF and the FMU step path are shared and identical for both.
"""

from __future__ import annotations

from .base import (
    BridgeCounters,
    ChannelSource,
    FrameClock,
    FrameTick,
    PhysicsCore,
    StateEncoder,
    StateSample,
    StepResult,
)

__all__ = [
    "BridgeCounters",
    "ChannelSource",
    "FrameClock",
    "FrameTick",
    "PhysicsCore",
    "StateEncoder",
    "StateSample",
    "StepResult",
]
