"""Pins the FMU-export SDK resource surface.

``client.fmu`` is a real ``FmuResource`` wired in ``client.py``
(export / status / wait / cancel / download). Fixtures use
``api_key="dummy"``/``"key_test"`` + respx mocks only — no real key, no
network egress (mirrors ``tests/test_resources/test_sweeps.py``).
"""

from __future__ import annotations

from httpx import Response

from thrustlab import Client


def test_fmu_resource_surface():
    """client.fmu exposes the export-job method set."""
    client = Client(api_key="dummy")
    resource = client.fmu
    assert resource is not None
    for method in ("export", "status", "wait", "cancel", "download"):
        assert callable(getattr(resource, method)), f"missing method: {method}"


def test_export_returns_queued_job(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.post("/v1/simulations/sim_1/export/fmu").mock(
        return_value=Response(
            202, json={"id": "fmu_1", "object": "fmu_export", "status": "queued"}
        )
    )
    out = client.fmu.export("sim_1")
    assert out["id"] == "fmu_1"
    assert out["status"] == "queued"
    assert route.calls[0].request.headers["Idempotency-Key"]


def test_status_calls_get(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/simulations/export/fmu/fmu_1").mock(
        return_value=Response(200, json={"id": "fmu_1", "status": "solving", "chunks_done": 1, "chunks_total": 4})
    )
    out = client.fmu.status("fmu_1")
    assert out["status"] == "solving"
    assert out["chunks_done"] == 1


def test_cancel_calls_post(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.post("/v1/simulations/export/fmu/fmu_1/cancel").mock(
        return_value=Response(200, json={"id": "fmu_1", "status": "solving"})
    )
    client.fmu.cancel("fmu_1")
    assert route.call_count == 1


def test_wait_reaches_completed(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/simulations/export/fmu/fmu_1").mock(
        return_value=Response(
            200,
            json={
                "id": "fmu_1",
                "status": "completed",
                "filename": "powertrain.fmu",
                "artifact_available": True,
            },
        )
    )
    out = client.fmu.wait("fmu_1", poll_interval=0.01)
    assert out["status"] == "completed"
    assert out["artifact_available"] is True


def test_wait_does_not_raise_on_failed(mock_router, monkeypatch):
    """wait() mirrors every other SDK wait() — a failed job is returned, not
    raised. Callers branch on result["status"], same as simulations/sweeps/
    dynamic_simulations."""
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/simulations/export/fmu/fmu_1").mock(
        return_value=Response(
            200,
            json={
                "id": "fmu_1",
                "status": "failed",
                "error": {"error_code": "export_cancelled", "message": "cancelled"},
            },
        )
    )
    out = client.fmu.wait("fmu_1", poll_interval=0.01)
    assert out["status"] == "failed"
    assert out["error"]["error_code"] == "export_cancelled"


def test_wait_calls_on_progress_for_every_poll(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.get("/v1/simulations/export/fmu/fmu_1")
    route.side_effect = [
        Response(200, json={"id": "fmu_1", "status": "solving", "progress": 0.4}),
        Response(200, json={"id": "fmu_1", "status": "completed", "progress": 1.0}),
    ]
    seen = []
    out = client.fmu.wait("fmu_1", on_progress=seen.append, poll_interval=0.01)
    assert out["status"] == "completed"
    assert [o["status"] for o in seen] == ["solving", "completed"]
    # Tolerant of additive fields (progress/eta_s/phase) — never asserted as required.
    assert seen[0]["progress"] == 0.4


def test_wait_times_out(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/simulations/export/fmu/fmu_1").mock(
        return_value=Response(200, json={"id": "fmu_1", "status": "solving"})
    )
    out = client.fmu.wait("fmu_1", poll_interval=0.01, timeout=0.02)
    assert out["status"] == "timed_out"


def test_download_writes_bytes(mock_router, monkeypatch, tmp_path):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    fake_fmu_bytes = b"PK\x03\x04fake-fmu-zip-bytes"
    mock_router.get("/v1/simulations/export/fmu/fmu_1/download").mock(
        return_value=Response(
            200,
            content=fake_fmu_bytes,
            headers={"Content-Type": "application/octet-stream"},
        )
    )
    dest = tmp_path / "powertrain.fmu"
    out_path = client.fmu.download("fmu_1", dest)
    assert out_path == str(dest)
    assert dest.read_bytes() == fake_fmu_bytes
