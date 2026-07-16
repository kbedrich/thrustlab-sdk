"""Base class shared by all SDK resource modules."""

from __future__ import annotations

from thrustlab._http import Transport


class Resource:
    """Holds a Transport reference. Subclasses expose resource-specific methods."""

    def __init__(self, transport: Transport) -> None:
        self._transport = transport
