"""Tests for CursorPager and list() resource methods."""

from httpx import Response

from thrustlab import Client


def test_pager_walks_three_pages(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()

    page1 = {"data": [{"id": "p_1"}, {"id": "p_2"}], "has_more": True}
    page2 = {"data": [{"id": "p_3"}, {"id": "p_4"}], "has_more": True}
    page3 = {"data": [{"id": "p_5"}], "has_more": False}

    route = mock_router.get("/v1/projects").mock(side_effect=[
        Response(200, json=page1),
        Response(200, json=page2),
        Response(200, json=page3),
    ])

    items = list(client.projects.list())
    ids = [item["id"] for item in items]
    assert ids == ["p_1", "p_2", "p_3", "p_4", "p_5"]
    assert route.call_count == 3


def test_pager_stops_on_empty_page(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/projects").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    assert list(client.projects.list()) == []


def test_pager_cursor_advance(mock_router, monkeypatch):
    """Subsequent page request advances via the `cursor` param.

    Falls back to the last item's id when the envelope omits next_cursor."""
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()

    page1 = {"data": [{"id": "p_1"}, {"id": "p_2"}], "has_more": True}
    page2 = {"data": [{"id": "p_3"}], "has_more": False}

    route = mock_router.get("/v1/projects").mock(side_effect=[
        Response(200, json=page1),
        Response(200, json=page2),
    ])

    list(client.projects.list())

    # Second request must use `cursor` (the param every /v1/ list endpoint
    # reads), NOT the legacy `starting_after`. No next_cursor in page1 → fall
    # back to the last item's id (p_2).
    second_qs = dict(route.calls[1].request.url.params)
    assert second_qs["cursor"] == "p_2"
    assert "starting_after" not in second_qs


def test_pager_advances_via_next_cursor_token(mock_router, monkeypatch):
    """When the envelope carries an opaque next_cursor token, the pager advances
    via that token (not the raw last-item id) — required for the sort-aware
    composite cursors used by components/projects/simulations."""
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()

    page1 = {
        "data": [{"id": "p_1"}, {"id": "p_2"}],
        "has_more": True,
        "next_cursor": "opaque_token_abc",
    }
    page2 = {"data": [{"id": "p_3"}], "has_more": False}

    route = mock_router.get("/v1/projects").mock(side_effect=[
        Response(200, json=page1),
        Response(200, json=page2),
    ])

    list(client.projects.list())

    second_qs = dict(route.calls[1].request.url.params)
    assert second_qs["cursor"] == "opaque_token_abc"


def test_pager_data_property_returns_first_page(mock_router, monkeypatch):
    """Accessing .data triggers first-page fetch and returns items without full iteration."""
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()

    route = mock_router.get("/v1/projects").mock(
        return_value=Response(200, json={"data": [{"id": "p_1"}], "has_more": True})
    )

    pager = client.projects.list(limit=1)
    assert pager.data == [{"id": "p_1"}]
    assert pager.has_more is True
    # Only one HTTP call should have been made
    assert route.call_count == 1


def test_pager_single_page(mock_router, monkeypatch):
    """Single-page response returns all items in one iteration."""
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()

    mock_router.get("/v1/projects").mock(
        return_value=Response(
            200, json={"data": [{"id": "p_1"}, {"id": "p_2"}], "has_more": False}
        )
    )
    items = list(client.projects.list())
    assert [i["id"] for i in items] == ["p_1", "p_2"]


def test_pager_data_stable_after_iteration(mock_router, monkeypatch):
    """.data returns first-page items even after iteration advances to later pages."""
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()

    page1 = {"data": [{"id": "p_1"}, {"id": "p_2"}], "has_more": True}
    page2 = {"data": [{"id": "p_3"}, {"id": "p_4"}], "has_more": False}

    mock_router.get("/v1/projects").mock(side_effect=[
        Response(200, json=page1),
        Response(200, json=page2),
    ])

    pager = client.projects.list()
    # Consume all pages via iteration.
    all_items = list(pager)
    assert [i["id"] for i in all_items] == ["p_1", "p_2", "p_3", "p_4"]
    # .data must still reflect the first page, not the last position of _current.
    assert [i["id"] for i in pager.data] == ["p_1", "p_2"]
