"""``client.submissions`` — community component submissions.

Endpoints:
    GET    /v1/submissions
    POST   /v1/submissions
    GET    /v1/submissions/{id}
    PATCH  /v1/submissions/{id}
    DELETE /v1/submissions/{id}
"""

from __future__ import annotations

from typing import Any, Optional

from thrustlab._pagination import CursorPager
from thrustlab.resources._base import Resource


class SubmissionsResource(Resource):
    def list(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 20,
        cursor: Optional[str] = None,
    ) -> CursorPager[dict[str, Any]]:
        """List submissions (cursor-paginated).

        Args:
            status: Optional filter — one of ``submitted`` / ``under_review``
                / ``approved`` / ``rejected``.
            cursor: Opaque pagination token from a prior response's
                ``next_cursor`` (the backend reads ``cursor``; the pre-0.3.2
                ``starting_after`` kwarg was silently ignored server-side).

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        """
        params: dict[str, Any] = {"limit": limit}
        if status:
            params["status"] = status
        if cursor:
            params["cursor"] = cursor
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

    def update(
        self,
        submission_id: str,
        *,
        idempotency_key: Optional[str] = None,
        **fields: Any,
    ) -> dict[str, Any]:
        """Edit a submission while it is still ``status="submitted"``.

        Editable fields: ``name``, ``manufacturer``, ``data_json``,
        ``source_url``, ``notes`` (``component_type`` is not editable).
        Raises ``ConflictError`` once a moderator has started review.
        """
        return self._transport.request(
            "PATCH", f"/v1/submissions/{submission_id}", json=fields,
            idempotency_key=idempotency_key,
        )

    def withdraw(
        self,
        submission_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> None:
        """Withdraw (hard-delete) a submission while ``status="submitted"``.

        Raises ``ConflictError`` once a moderator has started review.
        """
        self._transport.request(
            "DELETE", f"/v1/submissions/{submission_id}",
            idempotency_key=idempotency_key,
        )
