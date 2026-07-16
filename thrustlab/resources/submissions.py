"""``client.submissions`` — community component submissions.

Endpoints:
    GET    /v1/submissions
    POST   /v1/submissions
    GET    /v1/submissions/{id}
"""

from __future__ import annotations

from typing import Any, Optional

from thrustlab._pagination import CursorPager
from thrustlab.resources._base import Resource


class SubmissionsResource(Resource):
    def list(self, *, limit: int = 20, starting_after: Optional[str] = None) -> CursorPager[dict[str, Any]]:
        """List submissions (cursor-paginated).

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        """
        params: dict[str, Any] = {"limit": limit}
        if starting_after:
            params["starting_after"] = starting_after
        return CursorPager(
            fetch_page=lambda p: self._transport.request("GET", "/v1/submissions", params=p),
            initial_params=params,
        )

    def create(
        self,
        *,
        component_data: dict[str, Any],
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Submit a new component for review."""
        return self._transport.request(
            "POST", "/v1/submissions", json=component_data,
            idempotency_key=idempotency_key,
        )

    def retrieve(self, submission_id: str) -> dict[str, Any]:
        return self._transport.request("GET", f"/v1/submissions/{submission_id}")
