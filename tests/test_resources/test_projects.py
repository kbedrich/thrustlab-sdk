from httpx import Response

from thrustlab import Client


def test_list_passes_params(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.get("/v1/projects").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    client.projects.list(limit=10, cursor="proj_5").data  # trigger fetch
    qs = dict(route.calls[0].request.url.params)
    assert qs["limit"] == "10"
    # The endpoint reads `cursor` — the pre-0.3.2 `starting_after` was ignored.
    assert qs["cursor"] == "proj_5"
    assert "starting_after" not in qs


def test_create_calls_post(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.post("/v1/projects").mock(
        return_value=Response(201, json={"id": "proj_1", "name": "Test"})
    )
    out = client.projects.create(name="Test")
    assert out["id"] == "proj_1"
    assert route.calls[0].request.headers["Idempotency-Key"]


def test_retrieve_calls_get(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/projects/proj_1").mock(return_value=Response(200, json={"id": "proj_1"}))
    out = client.projects.retrieve("proj_1")
    assert out["id"] == "proj_1"


def test_update_calls_patch(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.patch("/v1/projects/proj_1").mock(
        return_value=Response(200, json={"id": "proj_1", "name": "Updated"})
    )
    out = client.projects.update("proj_1", name="Updated")
    assert out["name"] == "Updated"
    assert route.calls[0].request.headers["Idempotency-Key"]


def test_delete_calls_delete(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.delete("/v1/projects/proj_1").mock(return_value=Response(204))
    client.projects.delete("proj_1")
    assert route.call_count == 1
