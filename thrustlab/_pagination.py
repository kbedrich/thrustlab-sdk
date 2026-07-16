"""Cursor-paginated iterator for /v1/ list endpoints."""

from __future__ import annotations

from typing import Any, Callable, Generic, Iterator, TypeVar

T = TypeVar("T")


class CursorPager(Generic[T]):
    """Lazy iterator that walks through cursor-paginated /v1/ list responses.

    Construct via the resource's ``list()`` method; iterate to consume all pages.

    Manual cursor control::

        page = client.projects.list(limit=20)
        items = page.data          # first page items
        if page.has_more:
            page2 = client.projects.list(limit=20, cursor=items[-1]["id"])

    Auto-iterate all pages::

        for project in client.projects.list():
            print(project["id"])
    """

    def __init__(
        self,
        fetch_page: Callable[[dict[str, Any]], dict[str, Any]],
        initial_params: dict[str, Any],
    ) -> None:
        self._fetch = fetch_page
        self._params = dict(initial_params)
        self._current: list[T] = []
        self._index = 0
        self._has_more = True
        self._loaded_first = False
        # Stable snapshot of first-page items for .data property.
        self._first_page_data: list[T] = []

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def __iter__(self) -> Iterator[T]:
        return self

    def __next__(self) -> T:
        # Load first page on demand.
        if not self._loaded_first:
            self._load_next_page()
            self._loaded_first = True

        # Within current page?
        if self._index < len(self._current):
            item = self._current[self._index]
            self._index += 1
            return item  # type: ignore[return-value]

        # Need next page?
        if self._has_more:
            self._load_next_page()
            if self._current:
                item = self._current[0]
                self._index = 1
                return item  # type: ignore[return-value]

        raise StopIteration

    def _load_next_page(self) -> None:
        page = self._fetch(self._params)
        data = page.get("data", [])
        if not self._loaded_first:
            self._first_page_data = list(data)
        self._current = data
        self._index = 0
        self._has_more = bool(page.get("has_more", False))
        if self._has_more:
            # Advance via the server-issued opaque pagination token. Every /v1/
            # list endpoint reads `cursor` and echoes the next page token as
            # `next_cursor` (a sort-aware composite keyset for components/projects
            # /simulations — NOT the raw last-item id). Fall back to the last
            # item's id only if the envelope omits next_cursor.
            next_cursor = page.get("next_cursor")
            if next_cursor is None and data:
                last = data[-1]
                next_cursor = (
                    last["id"] if isinstance(last, dict) else getattr(last, "id", None)
                )
            self._params["cursor"] = next_cursor

    # ------------------------------------------------------------------
    # Manual-cursor helpers (access first-page data without iteration)
    # ------------------------------------------------------------------

    def _ensure_first_page(self) -> None:
        if not self._loaded_first:
            self._load_next_page()
            self._loaded_first = True

    @property
    def data(self) -> list[T]:
        """Items from the first page (for manual cursor control)."""
        self._ensure_first_page()
        return self._first_page_data

    @property
    def has_more(self) -> bool:
        """Whether the server signalled more pages after the first page."""
        self._ensure_first_page()
        return self._has_more

    # ------------------------------------------------------------------
    # One-hit-or-raise / first-or-None helpers (A9)
    # ------------------------------------------------------------------

    def one(self) -> T:
        """Return the single matching item, or raise.

        Bounded: this only inspects the first page (the first two items are
        enough to decide ambiguity) — it does NOT exhaust the pager.

        Raises:
            AmbiguousComponentError: if more than one item matched. The
                exception carries ``candidates`` so the caller can disambiguate.
            NotFoundError: if zero items matched.
        """
        # Local import keeps the module import-cycle-free.
        from thrustlab.exceptions import AmbiguousComponentError, NotFoundError

        items = self.data
        if len(items) == 0:
            raise NotFoundError(
                "No matching component found.",
                code="not_found",
                http_status=404,
            )
        # >1 on the first page OR exactly-one-but-more-pages-exist is ambiguous.
        if len(items) > 1 or self._has_more:
            raise AmbiguousComponentError(candidates=list(items))
        return items[0]  # type: ignore[return-value]

    def first(self) -> "T | None":
        """Return the first matching item, or ``None`` if there are none.

        Bounded: inspects only the first page; does NOT exhaust the pager.
        """
        items = self.data
        return items[0] if items else None  # type: ignore[return-value]
