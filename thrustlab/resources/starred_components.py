"""``client.starred_components`` — per-project component starring.

Stars are first-class resources with their own ``star_<ksuid>`` id: adding a
star returns the star object, and removal keys on the STAR id (not the
component id). Duplicate stars are rejected with a 409 ``already_starred``.

Endpoints:
    GET    /v1/starred_components
    POST   /v1/starred_components
    DELETE /v1/starred_components/{star_id}
"""

from __future__ import annotations

from typing import Any, Optional

from thrustlab._pagination import CursorPager
from thrustlab.resources._base import Resource


class StarredComponentsResource(Resource):
    def list(
        self,
        *,
        project_id: Optional[str] = None,
        component_type: Optional[str] = None,
        limit: int = 25,
        cursor: Optional[str] = None,
    ) -> CursorPager[dict[str, Any]]:
        """List the caller's stars, newest first (cursor-paginated).

        Args:
            project_id: Optional filter — only stars in this project.
            component_type: Optional filter — ``motor`` / ``battery`` /
                ``propeller``.
            cursor: Opaque pagination token from a prior response's
                ``next_cursor``.

        Each row carries its own ``star_<ksuid>`` ``id`` plus ``project_id``,
        ``component_id``, ``component_type``, and ``created_at``.
        """
        params: dict[str, Any] = {"limit": limit}
        if project_id:
            params["project"] = project_id
        if component_type:
            params["component_type"] = component_type
        if cursor:
            params["cursor"] = cursor
        return CursorPager(
            fetch_page=lambda p: self._transport.request(
                "GET", "/v1/starred_components", params=p
            ),
            initial_params=params,
        )

    def add(
        self,
        *,
        project_id: str,
        component_id: str,
        component_type: str,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Star a component in the given project.

        ``component_type`` is required (``motor`` / ``battery`` /
        ``propeller``). Raises ``ConflictError`` (409 ``already_starred``)
        if the (project, component) pair is already starred — starring is
        NOT idempotent.
        """
        return self._transport.request(
            "POST",
            "/v1/starred_components",
            json={
                "project_id": project_id,
                "component_id": component_id,
                "component_type": component_type,
            },
            idempotency_key=idempotency_key,
        )

    def remove(
        self,
        star_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> None:
        """Remove a star by its own ``star_<ksuid>`` id (from ``list()`` or
        the ``add()`` response). Unknown ids raise ``NotFoundError`` — removal
        is NOT idempotent."""
        self._transport.request(
            "DELETE",
            f"/v1/starred_components/{star_id}",
            idempotency_key=idempotency_key,
        )
