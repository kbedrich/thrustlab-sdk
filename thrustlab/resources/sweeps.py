"""``client.sweeps`` — run and manage parameter sweeps.

Endpoints:
    GET    /v1/sweeps
    POST   /v1/sweeps
    GET    /v1/sweeps/{id}
    POST   /v1/sweeps/{id}/cancel
    GET    /v1/sweeps/{id}/points
"""

from __future__ import annotations

from typing import Any, Optional

from thrustlab._async_polling import poll_until_terminal
from thrustlab._pagination import CursorPager
from thrustlab.resources._base import Resource


class SweepsResource(Resource):
    def list(
        self,
        *,
        project_id: Optional[str] = None,
        limit: int = 20,
        cursor: Optional[str] = None,
    ) -> CursorPager[dict[str, Any]]:
        """List sweeps (cursor-paginated).

        Args:
            cursor: Opaque pagination token from a prior response's
                ``next_cursor`` (the ``/v1/sweeps`` endpoint reads ``cursor``).
                Omit to start from the first page.

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
            fetch_page=lambda p: self._transport.request("GET", "/v1/sweeps", params=p),
            initial_params=params,
        )

    def create(
        self,
        *,
        project_id: str,
        idempotency_key: Optional[str] = None,
        **params: Any,
    ) -> dict[str, Any]:
        """Submit a sweep. Returns the resource in pending/running state."""
        body = {"project_id": project_id, **params}
        return self._transport.request(
            "POST", "/v1/sweeps", json=body,
            idempotency_key=idempotency_key,
        )

    def retrieve(self, sweep_id: str) -> dict[str, Any]:
        return self._transport.request("GET", f"/v1/sweeps/{sweep_id}")

    def cancel(self, sweep_id: str, *, idempotency_key: Optional[str] = None) -> dict[str, Any]:
        return self._transport.request(
            "POST", f"/v1/sweeps/{sweep_id}/cancel",
            idempotency_key=idempotency_key,
        )

    def list_points(
        self,
        sweep_id: str,
        *,
        limit: int = 100,
        cursor: Optional[str] = None,
    ) -> CursorPager[dict[str, Any]]:
        """List computed sweep points (cursor-paginated).

        Args:
            cursor: Opaque pagination token from a prior response's
                ``next_cursor`` (the points endpoint reads ``cursor``). Omit to
                start from the first page.

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        """
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return CursorPager(
            fetch_page=lambda p: self._transport.request(
                "GET", f"/v1/sweeps/{sweep_id}/points", params=p
            ),
            initial_params=params,
        )

    def wait(self, sweep_id: str, *, poll_interval: float = 2.0, timeout: float = 600.0) -> dict[str, Any]:
        """Poll until the sweep reaches a terminal state.

        Returns the final resource dict. If ``timeout`` is exceeded, the dict
        has ``status="timed_out"`` (SDK-side sentinel, not a server state).
        """
        return poll_until_terminal(
            fetch=lambda: self.retrieve(sweep_id),
            timeout=timeout,
            poll_interval=poll_interval,
        )
