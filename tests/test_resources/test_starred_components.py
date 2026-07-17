from httpx import Response

from thrustlab import Client


def test_list_calls_get(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.get("/v1/starred_components").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    client.starred_components.list(project_id="proj_1").data  # trigger fetch
    assert route.call_count == 1
    qs = dict(route.calls[0].request.url.params)
    # The endpoint's filter param is `project` (the SDK kwarg stays project_id).
    assert qs["project"] == "proj_1"


def test_list_passes_component_type_and_cursor(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.get("/v1/starred_components").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    client.starred_components.list(
        component_type="motor", cursor="star_abc"
    ).data
    qs = dict(route.calls[0].request.url.params)
    assert qs["component_type"] == "motor"
    assert qs["cursor"] == "star_abc"


def test_add_calls_post(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.post("/v1/starred_components").mock(
        return_value=Response(
            201,
            json={
                "id": "star_1",
                "project_id": "proj_1",
                "component_id": "cmp_1",
                "component_type": "motor",
            },
        )
    )
    out = client.starred_components.add(
        project_id="proj_1", component_id="cmp_1", component_type="motor"
    )
    assert out["id"] == "star_1"
    assert route.calls[0].request.headers["Idempotency-Key"]
    import json

    body = json.loads(route.calls[0].request.content)
    assert body == {
        "project_id": "proj_1",
        "component_id": "cmp_1",
        "component_type": "motor",
    }


def test_remove_calls_delete(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.delete("/v1/starred_components/star_1").mock(
        return_value=Response(204)
    )
    # Removal keys on the star's own id, not the component id.
    client.starred_components.remove("star_1")
    assert route.call_count == 1
