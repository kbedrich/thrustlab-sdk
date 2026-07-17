"""``client.dynamic_simulations`` — run and manage transient (time-domain) simulations.

A dynamic simulation integrates a powertrain through a throttle/airspeed
*schedule* until a *termination* condition (SOC/voltage cutoff or a fixed
duration), returning per-step samples, time series, a scorecard, and events.
It mirrors the ``client.sweeps`` surface (submit → ``wait()`` → read result).

Endpoints:
    GET    /v1/dynamic-simulations
    POST   /v1/dynamic-simulations
    POST   /v1/dynamic-simulations/estimate
    GET    /v1/dynamic-simulations/{id}
    PATCH  /v1/dynamic-simulations/{id}
    POST   /v1/dynamic-simulations/{id}/cancel
    GET    /v1/dynamic-simulations/{id}/export.csv   (raw CSV — not wrapped; fetch the URL directly)
    GET    /v1/dynamic-simulations/{id}/stream       (SSE — not wrapped; no polling use case)
"""

from __future__ import annotations

from typing import Any, Optional

from thrustlab._async_polling import poll_until_terminal
from thrustlab._pagination import CursorPager
from thrustlab.resources._base import Resource


class DynamicSimulationsResource(Resource):
    def list(
        self,
        *,
        project_id: Optional[str] = None,
        limit: int = 20,
        cursor: Optional[str] = None,
    ) -> CursorPager[dict[str, Any]]:
        """List dynamic simulations (cursor-paginated, newest first).

        Args:
            cursor: Opaque pagination token from a prior response's
                ``next_cursor`` (the backend reads ``cursor``). Omit to start
                from the first page.

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        """
        params: dict[str, Any] = {"limit": limit}
        if project_id:
            # The endpoint's filter param is ``project`` (pre-0.3.2 the SDK
            # sent an ignored ``project_id`` key — the filter did nothing).
            params["project"] = project_id
        if cursor:
            params["cursor"] = cursor
        return CursorPager(
            fetch_page=lambda p: self._transport.request(
                "GET", "/v1/dynamic-simulations", params=p
            ),
            initial_params=params,
        )

    def create(
        self,
        *,
        project_id: str,
        idempotency_key: Optional[str] = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Submit a dynamic simulation. Returns the resource in a queued/running state.

        Body fields (beyond ``project_id``): ``rotor_groups``,
        ``battery_component_id``, ``density_kg_m3``, ``schedule``,
        ``termination`` (all required), plus optional environment/initial-temp
        overrides. See ``examples/dynamic/run_and_poll.py``.
        """
        body = {"project_id": project_id, **params}
        return self._transport.request(
            "POST", "/v1/dynamic-simulations", json=body,
            idempotency_key=idempotency_key,
        )

    def estimate(
        self,
        *,
        idempotency_key: Optional[str] = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Estimate a dynamic run's coulombic duration without invoking the solver.

        Accepts the same body as :meth:`create` (the estimate path consumes only
        the battery + termination + schedule) and returns the projected duration.
        """
        return self._transport.request(
            "POST", "/v1/dynamic-simulations/estimate", json=dict(params),
            idempotency_key=idempotency_key,
        )

    def retrieve(self, dynamic_id: str) -> dict[str, Any]:
        return self._transport.request("GET", f"/v1/dynamic-simulations/{dynamic_id}")

    def update(
        self,
        dynamic_id: str,
        *,
        idempotency_key: Optional[str] = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Patch mutable fields (e.g. ``name``, ``is_starred``) on a dynamic run."""
        return self._transport.request(
            "PATCH", f"/v1/dynamic-simulations/{dynamic_id}", json=dict(params),
            idempotency_key=idempotency_key,
        )

    def cancel(self, dynamic_id: str, *, idempotency_key: Optional[str] = None) -> dict[str, Any]:
        return self._transport.request(
            "POST", f"/v1/dynamic-simulations/{dynamic_id}/cancel",
            idempotency_key=idempotency_key,
        )

    def wait(
        self,
        dynamic_id: str,
        *,
        poll_interval: float = 2.0,
        timeout: float = 600.0,
    ) -> dict[str, Any]:
        """Poll until the dynamic simulation reaches a terminal state.

        Returns the final resource dict. Terminal states are ``completed`` /
        ``failed`` / ``canceled`` (the exact wire spelling — one 'l'). If
        ``timeout`` is exceeded, the dict has ``status="timed_out"`` (an
        SDK-side sentinel, not a server state).
        """
        return poll_until_terminal(
            fetch=lambda: self.retrieve(dynamic_id),
            timeout=timeout,
            poll_interval=poll_interval,
        )
