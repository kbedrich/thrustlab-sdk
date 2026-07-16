"""``client.simulations`` — run and manage single-point simulations.

Endpoints:
    GET    /v1/simulations
    POST   /v1/simulations
    GET    /v1/simulations/{id}
    POST   /v1/simulations/{id}/cancel
"""

from __future__ import annotations

from typing import Any, Optional

from thrustlab._async_polling import poll_until_terminal
from thrustlab._pagination import CursorPager
from thrustlab.resources._base import Resource


class SimulationsResource(Resource):
    def list(
        self,
        *,
        project_id: Optional[str] = None,
        limit: int = 20,
        cursor: Optional[str] = None,
    ) -> CursorPager[dict[str, Any]]:
        """List simulations (cursor-paginated).

        Args:
            cursor: Opaque pagination token from a prior response's
                ``next_cursor`` (the ``/v1/simulations`` endpoint reads
                ``cursor``). Omit to start from the first page.

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        """
        params: dict[str, Any] = {"limit": limit}
        if project_id:
            params["project_id"] = project_id
        if cursor:
            params["cursor"] = cursor
        return CursorPager(
            fetch_page=lambda p: self._transport.request("GET", "/v1/simulations", params=p),
            initial_params=params,
        )

    def create(
        self,
        *,
        project_id: str,
        idempotency_key: Optional[str] = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Submit a simulation. Returns the resource in pending/running state."""
        body = {"project_id": project_id, **params}
        return self._transport.request(
            "POST", "/v1/simulations", json=body,
            idempotency_key=idempotency_key,
        )

    def retrieve(self, simulation_id: str) -> dict[str, Any]:
        return self._transport.request("GET", f"/v1/simulations/{simulation_id}")

    def cancel(self, simulation_id: str, *, idempotency_key: Optional[str] = None) -> dict[str, Any]:
        return self._transport.request(
            "POST", f"/v1/simulations/{simulation_id}/cancel",
            idempotency_key=idempotency_key,
        )

    def wait(self, simulation_id: str, *, poll_interval: float = 2.0, timeout: float = 600.0) -> dict[str, Any]:
        """Poll until the simulation reaches a terminal state.

        Returns the final resource dict. If ``timeout`` is exceeded, the dict
        has ``status="timed_out"`` (SDK-side sentinel, not a server state).
        """
        return poll_until_terminal(
            fetch=lambda: self.retrieve(simulation_id),
            timeout=timeout,
            poll_interval=poll_interval,
        )
