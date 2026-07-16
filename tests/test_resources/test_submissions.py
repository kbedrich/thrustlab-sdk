from httpx import Response

from thrustlab import Client


def test_list_passes_params(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.get("/v1/submissions").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    client.submissions.list(limit=10).data  # trigger fetch
    qs = dict(route.calls[0].request.url.params)
    assert qs["limit"] == "10"


def test_create_calls_post(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.post("/v1/submissions").mock(
        return_value=Response(201, json={"id": "sub_1", "status": "pending_review"})
    )
    out = client.submissions.create(component_data={"type": "motor", "brand": "KDE"})
    assert out["id"] == "sub_1"
    assert route.calls[0].request.headers["Idempotency-Key"]


def test_retrieve_calls_get(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/submissions/sub_1").mock(
        return_value=Response(200, json={"id": "sub_1", "status": "approved"})
    )
    out = client.submissions.retrieve("sub_1")
    assert out["status"] == "approved"
