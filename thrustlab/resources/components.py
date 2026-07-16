"""``client.components`` — browse the component catalog and create your own.

Endpoints:
    GET    /v1/components
    POST   /v1/components
    GET    /v1/components/{id}
    GET    /v1/components/brands
"""

from __future__ import annotations

from typing import Any, List, Optional

from thrustlab._pagination import CursorPager
from thrustlab.resources._base import Resource


class ComponentsResource(Resource):
    def list(
        self,
        *,
        type: Optional[str] = None,
        brand_in: Optional[List[str]] = None,
        kv_gte: Optional[float] = None,
        kv_lte: Optional[float] = None,
        limit: int = 20,
        cursor: Optional[str] = None,
        **extra_filters: Any,
    ) -> CursorPager[dict[str, Any]]:
        """List components with optional filters (cursor-paginated).

        Args:
            brand_in: List of brand names — serialised as ``brand[in]=KDE,Sunnysky``.
                      Pass ``None`` to omit the filter (returns all brands including
                      null-brand custom components).
            cursor: Opaque pagination token from a prior response's ``next_cursor``.
                    (The ``/v1/components`` endpoint reads ``cursor``.)

        Returns a :class:`CursorPager` that lazily fetches subsequent pages.
        """
        params: dict[str, Any] = {"limit": limit}
        if type is not None:
            params["type"] = type
        if brand_in is not None:
            params["brand[in]"] = ",".join(brand_in)
        if kv_gte is not None:
            params["kv[gte]"] = kv_gte
        if kv_lte is not None:
            params["kv[lte]"] = kv_lte
        if cursor:
            params["cursor"] = cursor
        params.update(extra_filters)
        return CursorPager(
            fetch_page=lambda p: self._transport.request("GET", "/v1/components", params=p),
            initial_params=params,
        )

    def find(self, **filters: Any) -> dict[str, Any]:
        """Look up the single component matching ``filters`` (one-hit-or-raise).

        Convenience over :meth:`list` for the common "I know there's exactly one"
        case — e.g. ``client.components.find(name="T-Motor F80")``::

            motor = client.components.find(name="T-Motor F80")
            sim = client.simulations.create(..., motor_component_id=motor["id"])

        Delegates to ``self.list(**filters).one()``. Bounded — only the first
        page is inspected (the first two items decide ambiguity).

        ``name=`` is a convenience alias for the ``search=`` query param
        (``/v1/components`` has no ``name`` filter — it matches names via
        ``search``/``q``), so ``find(name="T-Motor F80")`` does a name search.

        Raises:
            AmbiguousComponentError: more than one component matched. The
                exception's ``candidates`` lists the matches so you can pick one
                by ``id``.
            NotFoundError: no component matched.
        """
        if "name" in filters and "search" not in filters:
            filters["search"] = filters.pop("name")
        return self.list(**filters).one()

    def create(
        self,
        *,
        type: str,
        name: str,
        spec_json: dict[str, Any],
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Create a private custom component.

        Args:
            type: ``motor`` | ``battery`` | ``propeller``.
            name: Display name (1–255 chars).
            spec_json: Type-specific spec map — see the "Creating your own
                components" guide for the per-type required fields and units.

        The component is scoped to your account (``source="user"``,
        ``visibility="private"``); pass the returned ``id`` (``comp_...``) to a
        simulation. Persisting a propeller requires the hobbyist tier or
        higher — a free account gets a ``402``.
        """
        return self._transport.request(
            "POST", "/v1/components",
            json={"type": type, "name": name, "spec_json": spec_json},
            idempotency_key=idempotency_key,
        )

    def retrieve(self, component_id: str) -> dict[str, Any]:
        return self._transport.request("GET", f"/v1/components/{component_id}")

    def brands(self) -> dict[str, Any]:
        """Return the list of distinct component brands."""
        return self._transport.request("GET", "/v1/components/brands")
