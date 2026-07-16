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
    def list(self, *, limit: int = 20, starting_after: Optional[str] = None) -> CursorPager[dict[str, Any]]:
        """List webhook endpoints (cursor-paginated).

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        """
        params: dict[str, Any] = {"limit": limit}
        if starting_after:
            params["starting_after"] = starting_after
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

    def list_events(self, *, limit: int = 20, starting_after: Optional[str] = None) -> CursorPager[dict[str, Any]]:
        """List all event types (cursor-paginated).

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        """
        params: dict[str, Any] = {"limit": limit}
        if starting_after:
            params["starting_after"] = starting_after
        return CursorPager(
            fetch_page=lambda p: self._transport.request("GET", "/v1/events", params=p),
            initial_params=params,
        )

    def list_deliveries(
        self,
        endpoint_id: str,
        *,
        status: Optional[str] = None,
        limit: int = 20,
        starting_after: Optional[str] = None,
    ) -> CursorPager[dict[str, Any]]:
        """List delivery attempts for an endpoint (cursor-paginated).

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        """
        params: dict[str, Any] = {"limit": limit}
        if status:
            params["status"] = status
        if starting_after:
            params["starting_after"] = starting_after
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
