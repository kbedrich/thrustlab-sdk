import pytest
from httpx import Response

from thrustlab import Client


def test_list_passes_project_filter(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.get("/v1/simulations").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    client.simulations.list(project_id="proj_1", limit=5).data  # trigger fetch
    qs = dict(route.calls[0].request.url.params)
    assert qs["project_id"] == "proj_1"
    assert qs["limit"] == "5"


def test_create_returns_pending(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.post("/v1/simulations").mock(
        return_value=Response(202, json={"id": "sim_1", "status": "pending"})
    )
    out = client.simulations.create(project_id="proj_1", throttle=50)
    assert out["status"] == "pending"
    assert route.calls[0].request.headers["Idempotency-Key"]


def test_retrieve_calls_get(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/simulations/sim_1").mock(
        return_value=Response(200, json={"id": "sim_1", "status": "complete"})
    )
    out = client.simulations.retrieve("sim_1")
    assert out["status"] == "complete"


def test_cancel_calls_post(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.post("/v1/simulations/sim_1/cancel").mock(
        return_value=Response(200, json={"id": "sim_1", "status": "cancelled"})
    )
    out = client.simulations.cancel("sim_1")
    assert out["status"] == "cancelled"
    assert route.call_count == 1


def test_wait_implemented(mock_router, monkeypatch):
    """wait() is now implemented and polls until terminal state."""
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/simulations/sim_1").mock(
        return_value=Response(200, json={"id": "sim_1", "status": "completed"})
    )
    out = client.simulations.wait("sim_1", poll_interval=0.01)
    assert out["status"] == "completed"
