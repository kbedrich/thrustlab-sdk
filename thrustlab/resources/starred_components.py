"""``client.starred_components`` — per-project component starring.

Endpoints:
    GET    /v1/projects/{pid}/starred-components
    POST   /v1/projects/{pid}/starred-components
    DELETE /v1/projects/{pid}/starred-components/{cid}
"""

from __future__ import annotations

from typing import Any, Optional

from thrustlab._pagination import CursorPager
from thrustlab.resources._base import Resource


class StarredComponentsResource(Resource):
    def list(self, project_id: str) -> CursorPager[dict[str, Any]]:
        """List starred components for a project (cursor-paginated).

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        """
        return CursorPager(
            fetch_page=lambda p: self._transport.request(
                "GET", f"/v1/projects/{project_id}/starred-components", params=p
            ),
            initial_params={},
        )

    def add(
        self,
        project_id: str,
        component_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Star a component in the given project."""
        return self._transport.request(
            "POST",
            f"/v1/projects/{project_id}/starred-components",
            json={"component_id": component_id},
            idempotency_key=idempotency_key,
        )

    def remove(
        self,
        project_id: str,
        component_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> None:
        """Unstar a component from the given project."""
        self._transport.request(
            "DELETE",
            f"/v1/projects/{project_id}/starred-components/{component_id}",
            idempotency_key=idempotency_key,
        )
