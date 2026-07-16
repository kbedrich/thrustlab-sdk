"""Pins the dynamic-simulations SDK resource surface.

``client.dynamic_simulations`` is a real ``DynamicSimulationsResource`` wired in
``client.py`` (create / retrieve / wait / list / cancel / estimate / update).

Fixtures use ``api_key="dummy"`` + respx mocks only — no real key, no network
egress (mirrors ``tests/test_resources/test_sweeps.py``).
"""

from __future__ import annotations

from httpx import Response

from thrustlab import Client


def test_dynamic_simulations_resource_surface():
    """client.dynamic_simulations exposes the standard sim-resource method set."""
    client = Client(api_key="dummy")
    resource = client.dynamic_simulations
    assert resource is not None
    for method in ("create", "retrieve", "wait", "list", "cancel", "estimate"):
        assert callable(getattr(resource, method)), f"missing method: {method}"


def test_dynamic_simulations_create_and_wait(mock_router, monkeypatch):
    """create() POSTs /v1/dynamic-simulations; wait() polls GET until terminal.

    Mirrors the respx idiom in test_sweeps.py — no real network, no real key.
    """
    monkeypatch.setenv("THRUSTLAB_API_KEY", "dummy")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()

    create_route = mock_router.post("/v1/dynamic-simulations").mock(
        return_value=Response(202, json={"id": "dyn_1", "status": "queued"})
    )
    mock_router.get("/v1/dynamic-simulations/dyn_1").mock(
        return_value=Response(200, json={"id": "dyn_1", "status": "completed"})
    )

    created = client.dynamic_simulations.create(
        project_id="proj_1",
        rotor_groups=[{"propeller_component_id": "cmp_prop", "throttle_pct": 70}],
        battery_component_id="cmp_bat",
    )
    assert created["id"] == "dyn_1"
    assert create_route.call_count == 1

    final = client.dynamic_simulations.wait("dyn_1", poll_interval=0.01)
    assert final["status"] == "completed"
