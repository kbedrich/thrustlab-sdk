from httpx import Response

from thrustlab import Client


def test_list_calls_get(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.get("/v1/projects/proj_1/starred-components").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    client.starred_components.list("proj_1").data  # trigger fetch
    assert route.call_count == 1


def test_add_calls_post(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.post("/v1/projects/proj_1/starred-components").mock(
        return_value=Response(201, json={"project_id": "proj_1", "component_id": "cmp_1"})
    )
    out = client.starred_components.add("proj_1", "cmp_1")
    assert out["component_id"] == "cmp_1"
    assert route.calls[0].request.headers["Idempotency-Key"]


def test_remove_calls_delete(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.delete("/v1/projects/proj_1/starred-components/cmp_1").mock(
        return_value=Response(204)
    )
    client.starred_components.remove("proj_1", "cmp_1")
    assert route.call_count == 1
