"""Contract tests for the SDK lookup ergonomics (find / one / first).

These lock the contract for ``client.components.find(...)`` and the pager
``.one()`` / ``.first()`` helpers, plus the ``AmbiguousComponentError``
exception (a ``ThrustlabError`` subclass carrying the candidate matches).

Idiom mirrors tests/test_resources/test_components.py (the respx ``mock_router``
fixture from tests/conftest.py). The transport is mocked with canned pages.
"""
from __future__ import annotations

from httpx import Response

from thrustlab import Client

from thrustlab.exceptions import AmbiguousComponentError, NotFoundError


def _client(monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    return Client()


def _comp(cid: str, name: str) -> dict:
    return {"id": cid, "type": "motor", "name": name}


# ---------------------------------------------------------------------------
# find() — single hit
# ---------------------------------------------------------------------------

def test_find_single_hit(mock_router, monkeypatch):
    """client.components.find(name=...) returns the one matching component."""
    client = _client(monkeypatch)
    mock_router.get("/v1/components").mock(
        return_value=Response(200, json={
            "data": [_comp("comp_1", "T-Motor F80")],
            "has_more": False,
        })
    )
    out = client.components.find(name="T-Motor F80")
    assert out["id"] == "comp_1"


def test_find_name_is_sent_as_search(mock_router, monkeypatch):
    """find(name=...) maps to the ``search=`` query param.

    ``/v1/components`` has no ``name`` filter — it matches names via
    ``search``/``q``. Without this alias, ``find(name=...)`` would send an
    ignored ``?name=`` and the API would return every component (a spurious
    AmbiguousComponentError), so ``find()`` aliases ``name`` -> ``search``.
    """
    client = _client(monkeypatch)
    route = mock_router.get("/v1/components").mock(
        return_value=Response(200, json={
            "data": [_comp("comp_1", "T-Motor F80")],
            "has_more": False,
        })
    )
    client.components.find(name="T-Motor F80")
    sent = route.calls.last.request
    assert sent.url.params.get("search") == "T-Motor F80"
    assert "name" not in sent.url.params, "name must not leak as an ignored query param"


# ---------------------------------------------------------------------------
# find() — ambiguous (>1 hit) raises with candidates
# ---------------------------------------------------------------------------

def test_find_ambiguous_raises(mock_router, monkeypatch):
    """>1 hit raises AmbiguousComponentError carrying candidate ids/names."""
    client = _client(monkeypatch)
    mock_router.get("/v1/components").mock(
        return_value=Response(200, json={
            "data": [_comp("comp_1", "F80"), _comp("comp_2", "F80")],
            "has_more": False,
        })
    )
    try:
        client.components.find(name="F80")
    except AmbiguousComponentError as exc:
        # Candidate ids surfaced on the exception so the caller can disambiguate.
        candidates = getattr(exc, "candidates", None) or getattr(exc, "matches", None)
        assert candidates is not None, "AmbiguousComponentError must carry candidates"
        ids = [c["id"] if isinstance(c, dict) else c for c in candidates]
        assert "comp_1" in ids and "comp_2" in ids
    else:
        raise AssertionError("expected AmbiguousComponentError on >1 hit")


# ---------------------------------------------------------------------------
# find() — zero hits raises NotFoundError
# ---------------------------------------------------------------------------

def test_find_zero_raises(mock_router, monkeypatch):
    """0 hits raises NotFoundError."""
    client = _client(monkeypatch)
    mock_router.get("/v1/components").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    try:
        client.components.find(name="does-not-exist")
    except NotFoundError:
        pass
    else:
        raise AssertionError("expected NotFoundError on 0 hits")


# ---------------------------------------------------------------------------
# pager .one() / .first()
# ---------------------------------------------------------------------------

def test_list_one_and_first(mock_router, monkeypatch):
    """list(...).one() raises AmbiguousComponentError on >1; .first() returns
    first-or-None."""
    client = _client(monkeypatch)

    # >1 result → .one() must raise; .first() returns the first item.
    mock_router.get("/v1/components").mock(
        return_value=Response(200, json={
            "data": [_comp("comp_1", "A"), _comp("comp_2", "B")],
            "has_more": False,
        })
    )
    try:
        client.components.list(type="motor").one()
    except AmbiguousComponentError:
        pass
    else:
        raise AssertionError("expected AmbiguousComponentError from .one() on >1")

    first = client.components.list(type="motor").first()
    assert first["id"] == "comp_1"


def test_list_first_returns_none_on_empty(mock_router, monkeypatch):
    """.first() returns None on an empty page (first-or-None semantics)."""
    client = _client(monkeypatch)
    mock_router.get("/v1/components").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    assert client.components.list(type="motor").first() is None
