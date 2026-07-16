"""``client.compute_units`` — compute-unit balance, usage summary, and history.

Endpoints:
    GET    /v1/compute-units/balance
    GET    /v1/compute-units/summary
    GET    /v1/compute-units/transactions
"""

from __future__ import annotations

from typing import Any, Optional

from thrustlab._pagination import CursorPager
from thrustlab.resources._base import Resource


class ComputeUnitsResource(Resource):
    def balance(self) -> dict[str, Any]:
        """Return current compute-unit balances (simulation, sweep, ai)."""
        return self._transport.request("GET", "/v1/compute-units/balance")

    def summary(self) -> dict[str, Any]:
        """Return the usage-meter summary for the current metering window."""
        return self._transport.request("GET", "/v1/compute-units/summary")

    def transactions(
        self,
        *,
        credit_type: Optional[str] = None,
        limit: int = 20,
        cursor: Optional[str] = None,
    ) -> CursorPager[dict[str, Any]]:
        """Return compute-unit transaction history (cursor-paginated).

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        """
        params: dict[str, Any] = {"limit": limit}
        if credit_type:
            params["credit_type"] = credit_type
        if cursor:
            params["cursor"] = cursor
        return CursorPager(
            fetch_page=lambda p: self._transport.request("GET", "/v1/compute-units/transactions", params=p),
            initial_params=params,
        )
