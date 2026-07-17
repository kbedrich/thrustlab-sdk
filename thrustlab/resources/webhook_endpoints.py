"""``client.webhook_endpoints`` — manage webhook endpoints, events, and deliveries.

Endpoints:
    GET    /v1/webhook_endpoints
    POST   /v1/webhook_endpoints
    GET    /v1/webhook_endpoints/{id}
    PATCH  /v1/webhook_endpoints/{id}
    DELETE /v1/webhook_endpoints/{id}
    POST   /v1/webhook_endpoints/{id}/rotate_secret
    POST   /v1/webhook_endpoints/{id}/test
    GET    /v1/events
    GET    /v1/webhook_endpoints/{id}/deliveries
    POST   /v1/webhook_endpoints/{id}/deliveries/{did}/retry
"""

from __future__ import annotations

from typing import Any, List, Optional

from thrustlab._pagination import CursorPager
from thrustlab.resources._base import Resource


class WebhookEndpointsResource(Resource):
    def list(self, *, limit: int = 20, cursor: Optional[str] = None) -> CursorPager[dict[str, Any]]:
        """List webhook endpoints (cursor-paginated).

        Args:
            cursor: Opaque pagination token from a prior response's
                ``next_cursor`` (the backend reads ``cursor``; the pre-0.3.2
                ``starting_after`` kwarg was silently ignored server-side).

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        """
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return CursorPager(
            fetch_page=lambda p: self._transport.request("GET", "/v1/webhook_endpoints", params=p),
            initial_params=params,
        )

    def create(
        self,
        *,
        url: str,
        events: List[str],
        description: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"url": url, "events": events}
        if description is not None:
            body["description"] = description
        return self._transport.request(
            "POST", "/v1/webhook_endpoints", json=body,
            idempotency_key=idempotency_key,
        )

    def retrieve(self, endpoint_id: str) -> dict[str, Any]:
        return self._transport.request("GET", f"/v1/webhook_endpoints/{endpoint_id}")

    def update(
        self,
        endpoint_id: str,
        *,
        idempotency_key: Optional[str] = None,
        **fields: Any,
    ) -> dict[str, Any]:
        return self._transport.request(
            "PATCH", f"/v1/webhook_endpoints/{endpoint_id}", json=fields,
            idempotency_key=idempotency_key,
        )

    def delete(self, endpoint_id: str, *, idempotency_key: Optional[str] = None) -> None:
        self._transport.request(
            "DELETE", f"/v1/webhook_endpoints/{endpoint_id}",
            idempotency_key=idempotency_key,
        )

    def rotate_secret(self, endpoint_id: str, *, idempotency_key: Optional[str] = None) -> dict[str, Any]:
        """Rotate the signing secret for this endpoint."""
        return self._transport.request(
            "POST", f"/v1/webhook_endpoints/{endpoint_id}/rotate_secret",
            idempotency_key=idempotency_key,
        )

    def test(self, endpoint_id: str, *, idempotency_key: Optional[str] = None) -> dict[str, Any]:
        """Send a test event to the endpoint."""
        return self._transport.request(
            "POST", f"/v1/webhook_endpoints/{endpoint_id}/test",
            idempotency_key=idempotency_key,
        )

    def list_events(self, *, limit: int = 20, cursor: Optional[str] = None) -> CursorPager[dict[str, Any]]:
        """List the account's event OCCURRENCE log (cursor-paginated).

        Each item is an emitted event instance — ``{id, object, type,
        created_at, api_version, data}`` — not a catalog of available event
        type names (that list lives in the docs).

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        """
        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return CursorPager(
            fetch_page=lambda p: self._transport.request("GET", "/v1/events", params=p),
            initial_params=params,
        )

    def list_deliveries(
        self,
        endpoint_id: str,
        *,
        status: Optional[str] = None,
        event_type: Optional[str] = None,
        created_at_gte: Optional[str] = None,
        limit: int = 20,
        cursor: Optional[str] = None,
    ) -> CursorPager[dict[str, Any]]:
        """List delivery attempts for an endpoint (cursor-paginated).

        Args:
            status: Optional filter — ``pending`` / ``succeeded`` /
                ``failed`` / ``permanently_failed``.
            event_type: Optional filter on the delivered event's type
                (e.g. ``simulation.completed``).
            created_at_gte: Optional ISO-8601 lower bound on delivery
                creation time (sent as ``created_at[gte]``).
            cursor: Opaque pagination token from a prior response's
                ``next_cursor``.

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        """
        params: dict[str, Any] = {"limit": limit}
        if status:
            params["status"] = status
        if event_type:
            params["event_type"] = event_type
        if created_at_gte:
            params["created_at[gte]"] = created_at_gte
        if cursor:
            params["cursor"] = cursor
        return CursorPager(
            fetch_page=lambda p: self._transport.request(
                "GET", f"/v1/webhook_endpoints/{endpoint_id}/deliveries", params=p
            ),
            initial_params=params,
        )

    def retry_delivery(
        self,
        endpoint_id: str,
        delivery_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Retry a failed delivery."""
        return self._transport.request(
            "POST",
            f"/v1/webhook_endpoints/{endpoint_id}/deliveries/{delivery_id}/retry",
            idempotency_key=idempotency_key,
        )
