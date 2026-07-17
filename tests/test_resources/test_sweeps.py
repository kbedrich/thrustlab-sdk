import pytest
from httpx import Response

from thrustlab import Client


def test_list_passes_project_filter(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.get("/v1/sweeps").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    client.sweeps.list(project_id="proj_1").data  # trigger fetch
    qs = dict(route.calls[0].request.url.params)
    # The endpoint's filter param is `project` — the pre-0.3.2 `project_id`
    # key was silently ignored server-side (filter did nothing).
    assert qs["project"] == "proj_1"
    assert "project_id" not in qs


def test_create_returns_pending(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.post("/v1/sweeps").mock(
        return_value=Response(202, json={"id": "swp_1", "status": "pending"})
    )
    out = client.sweeps.create(project_id="proj_1", throttle_range=[25, 100])
    assert out["id"] == "swp_1"
    assert route.calls[0].request.headers["Idempotency-Key"]


def test_retrieve_calls_get(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/sweeps/swp_1").mock(
        return_value=Response(200, json={"id": "swp_1", "status": "complete"})
    )
    out = client.sweeps.retrieve("swp_1")
    assert out["status"] == "complete"


def test_cancel_calls_post(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.post("/v1/sweeps/swp_1/cancel").mock(
        return_value=Response(200, json={"id": "swp_1", "status": "cancelled"})
    )
    client.sweeps.cancel("swp_1")
    assert route.call_count == 1


def test_list_points_calls_get(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.get("/v1/sweeps/swp_1/points").mock(
        return_value=Response(200, json={"data": [{"id": "sp_1"}], "has_more": False})
    )
    items = client.sweeps.list_points("swp_1").data  # trigger fetch
    assert items[0]["id"] == "sp_1"
    assert route.call_count == 1


def test_wait_implemented(mock_router, monkeypatch):
    """wait() is now implemented and polls until terminal state."""
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/sweeps/swp_1").mock(
        return_value=Response(200, json={"id": "swp_1", "status": "completed"})
    )
    out = client.sweeps.wait("swp_1", poll_interval=0.01)
    assert out["status"] == "completed"
