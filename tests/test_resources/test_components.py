from httpx import Response

from thrustlab import Client


def test_list_no_filters(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.get("/v1/components").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    client.components.list().data  # trigger fetch
    qs = dict(route.calls[0].request.url.params)
    assert qs["limit"] == "20"
    assert "brand[in]" not in qs


def test_list_with_type_filter(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.get("/v1/components").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    client.components.list(type="motor").data  # trigger fetch
    qs = dict(route.calls[0].request.url.params)
    assert qs["type"] == "motor"


def test_list_brand_in_roundtrips(mock_router, monkeypatch):
    """brand[in] filter serialises as comma-joined string."""
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.get("/v1/components").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    client.components.list(brand_in=["KDE", "Sunnysky"]).data  # trigger fetch
    qs = dict(route.calls[0].request.url.params)
    assert qs["brand[in]"] == "KDE,Sunnysky"


def test_retrieve_calls_get(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/components/cmp_1").mock(return_value=Response(200, json={"id": "cmp_1"}))
    out = client.components.retrieve("cmp_1")
    assert out["id"] == "cmp_1"


def test_brands_calls_get(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/components/brands").mock(
        return_value=Response(200, json={"data": ["KDE", "Sunnysky"]})
    )
    out = client.components.brands()
    assert "KDE" in out["data"]
