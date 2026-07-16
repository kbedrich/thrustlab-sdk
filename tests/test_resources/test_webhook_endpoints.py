from httpx import Response

from thrustlab import Client


def _client(monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    return Client()


def test_list_passes_params(mock_router, monkeypatch):
    client = _client(monkeypatch)
    route = mock_router.get("/v1/webhook_endpoints").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    client.webhook_endpoints.list(limit=5).data  # trigger fetch
    qs = dict(route.calls[0].request.url.params)
    assert qs["limit"] == "5"


def test_create_calls_post(mock_router, monkeypatch):
    client = _client(monkeypatch)
    route = mock_router.post("/v1/webhook_endpoints").mock(
        return_value=Response(201, json={"id": "we_1", "url": "https://example.com/hook"})
    )
    out = client.webhook_endpoints.create(url="https://example.com/hook", events=["simulation.complete"])
    assert out["id"] == "we_1"
    assert route.calls[0].request.headers["Idempotency-Key"]


def test_retrieve_calls_get(mock_router, monkeypatch):
    client = _client(monkeypatch)
    mock_router.get("/v1/webhook_endpoints/we_1").mock(
        return_value=Response(200, json={"id": "we_1"})
    )
    out = client.webhook_endpoints.retrieve("we_1")
    assert out["id"] == "we_1"


def test_update_calls_patch(mock_router, monkeypatch):
    client = _client(monkeypatch)
    route = mock_router.patch("/v1/webhook_endpoints/we_1").mock(
        return_value=Response(200, json={"id": "we_1", "enabled": False})
    )
    out = client.webhook_endpoints.update("we_1", enabled=False)
    assert out["enabled"] is False
    assert route.calls[0].request.headers["Idempotency-Key"]


def test_delete_calls_delete(mock_router, monkeypatch):
    client = _client(monkeypatch)
    route = mock_router.delete("/v1/webhook_endpoints/we_1").mock(return_value=Response(204))
    client.webhook_endpoints.delete("we_1")
    assert route.call_count == 1


def test_rotate_secret_calls_post(mock_router, monkeypatch):
    client = _client(monkeypatch)
    route = mock_router.post("/v1/webhook_endpoints/we_1/rotate_secret").mock(
        return_value=Response(200, json={"secret": "whsec_new"})
    )
    out = client.webhook_endpoints.rotate_secret("we_1")
    assert "secret" in out
    assert route.call_count == 1


def test_test_calls_post(mock_router, monkeypatch):
    client = _client(monkeypatch)
    route = mock_router.post("/v1/webhook_endpoints/we_1/test").mock(
        return_value=Response(200, json={"delivered": True})
    )
    out = client.webhook_endpoints.test("we_1")
    assert out["delivered"] is True


def test_list_events_calls_get(mock_router, monkeypatch):
    client = _client(monkeypatch)
    route = mock_router.get("/v1/events").mock(
        return_value=Response(200, json={"data": [{"type": "simulation.complete"}], "has_more": False})
    )
    items = client.webhook_endpoints.list_events().data  # trigger fetch
    assert items[0]["type"] == "simulation.complete"


def test_list_deliveries_passes_filter(mock_router, monkeypatch):
    client = _client(monkeypatch)
    route = mock_router.get("/v1/webhook_endpoints/we_1/deliveries").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    client.webhook_endpoints.list_deliveries("we_1", status="failed").data  # trigger fetch
    qs = dict(route.calls[0].request.url.params)
    assert qs["status"] == "failed"


def test_retry_delivery_calls_post(mock_router, monkeypatch):
    client = _client(monkeypatch)
    route = mock_router.post("/v1/webhook_endpoints/we_1/deliveries/del_1/retry").mock(
        return_value=Response(200, json={"id": "del_2", "status": "pending"})
    )
    out = client.webhook_endpoints.retry_delivery("we_1", "del_1")
    assert out["id"] == "del_2"
    assert route.call_count == 1
