"""``client.projects`` — manage simulation projects.

Endpoints:
    GET    /v1/projects
    POST   /v1/projects
    GET    /v1/projects/{id}
    PATCH  /v1/projects/{id}
    DELETE /v1/projects/{id}
"""

from __future__ import annotations

from typing import Any, Optional

from thrustlab._pagination import CursorPager
from thrustlab.resources._base import Resource


class ProjectsResource(Resource):
    def list(self, *, limit: int = 20, cursor: Optional[str] = None) -> CursorPager[dict[str, Any]]:
        """List projects (cursor-paginated).

        Args:
            cursor: Opaque pagination token from a prior response's
                ``next_cursor`` (the backend reads ``cursor``; the pre-0.3.2
                ``starting_after`` kwarg was silently ignored server-side).

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        Iterate to consume all pages, or access ``.data`` / ``.has_more`` for
        manual cursor control.
        """
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return CursorPager(
            fetch_page=lambda p: self._transport.request("GET", "/v1/projects", params=p),
            initial_params=params,
        )

    def create(self, *, name: str, idempotency_key: Optional[str] = None) -> dict[str, Any]:
        return self._transport.request(
            "POST", "/v1/projects", json={"name": name},
            idempotency_key=idempotency_key,
        )

    def retrieve(self, project_id: str) -> dict[str, Any]:
        return self._transport.request("GET", f"/v1/projects/{project_id}")

    def update(self, project_id: str, *, idempotency_key: Optional[str] = None, **fields: Any) -> dict[str, Any]:
        return self._transport.request(
            "PATCH", f"/v1/projects/{project_id}", json=fields,
            idempotency_key=idempotency_key,
        )

    def delete(self, project_id: str, *, idempotency_key: Optional[str] = None) -> None:
        self._transport.request(
            "DELETE", f"/v1/projects/{project_id}",
            idempotency_key=idempotency_key,
        )
