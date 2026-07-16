"""``client.components.create()`` + ``client.compute_units.summary()`` wire contracts.

Pre-0.3.0-publish gap: the docs taught the private ``client._transport.request``
for ``POST /v1/components`` and ``GET /v1/compute-units/summary`` because the
SDK had no public method for either documented endpoint. These tests lock the
public methods' wire behavior (method, path, body, Idempotency-Key
passthrough) using the respx ``mock_router`` fixture from tests/conftest.py.
"""
from __future__ import annotations

import json

from httpx import Response

from thrustlab import Client


def _client(monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    return Client()


def test_components_create_posts_body(mock_router, monkeypatch):
    """create() POSTs {type, name, spec_json} and returns the new resource."""
    client = _client(monkeypatch)
    route = mock_router.post("/v1/components").mock(
        return_value=Response(
            201, json={"id": "comp_1", "type": "motor", "name": "M"}
        ),
    )
    out = client.components.create(type="motor", name="M", spec_json={"kv": 800.0})
    assert out["id"] == "comp_1"
    sent = json.loads(route.calls.last.request.content)
    assert sent == {"type": "motor", "name": "M", "spec_json": {"kv": 800.0}}


def test_components_create_passes_idempotency_key(mock_router, monkeypatch):
    """An explicit idempotency_key wins over the transport's auto-generated one."""
    client = _client(monkeypatch)
    route = mock_router.post("/v1/components").mock(
        return_value=Response(201, json={"id": "comp_1"}),
    )
    client.components.create(
        type="battery",
        name="B",
        spec_json={"chemistry": "lipo"},
        idempotency_key="idem-123",
    )
    assert route.calls.last.request.headers["Idempotency-Key"] == "idem-123"


def test_compute_units_summary_hits_summary(mock_router, monkeypatch):
    """summary() GETs /v1/compute-units/summary and returns the meter read."""
    client = _client(monkeypatch)
    mock_router.get("/v1/compute-units/summary").mock(
        return_value=Response(
            200,
            json={
                "object": "credit_usage_summary",
                "window": "day",
                "used": 12,
                "cap": 30,
                "remaining": 18,
            },
        ),
    )
    out = client.compute_units.summary()
    assert out["cap"] == 30
    assert out["remaining"] == 18
