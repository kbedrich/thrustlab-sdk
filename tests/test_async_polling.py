"""Tests for poll_until_terminal and simulations/sweeps.wait()."""

import time
from unittest.mock import call, patch

import pytest
from httpx import Response

from thrustlab import Client
from thrustlab._async_polling import TERMINAL_STATES, poll_until_terminal


# ---------------------------------------------------------------------------
# Unit tests for poll_until_terminal directly
# ---------------------------------------------------------------------------

def test_terminal_states_constant():
    # These are the EXACT wire values the v1 API emits (see
    # backend/app/v1/_async_serialize.py ``_DB_TO_V1``). A prior version of the
    # SDK used {"succeeded","failed","cancelled"}, which never matched the server
    # → wait() looped to its full timeout and returned a bogus "timed_out" on
    # every successful run. Guard against that regression from both sides.
    assert TERMINAL_STATES == {"completed", "failed", "canceled"}
    assert "succeeded" not in TERMINAL_STATES  # server never emits this
    assert "cancelled" not in TERMINAL_STATES  # server uses "canceled" (one 'l')


def test_poll_returns_immediately_when_terminal():
    calls = [0]

    def fetch():
        calls[0] += 1
        return {"id": "x", "status": "completed"}

    result = poll_until_terminal(fetch, timeout=10.0, poll_interval=0.01)
    assert result["status"] == "completed"
    assert calls[0] == 1


def test_poll_waits_for_terminal():
    responses = [
        {"id": "x", "status": "running"},
        {"id": "x", "status": "running"},
        {"id": "x", "status": "failed"},
    ]
    idx = [0]

    def fetch():
        r = responses[min(idx[0], len(responses) - 1)]
        idx[0] += 1
        return r

    result = poll_until_terminal(fetch, timeout=10.0, poll_interval=0.01)
    assert result["status"] == "failed"


def test_poll_times_out():
    def fetch():
        return {"id": "x", "status": "running"}

    result = poll_until_terminal(fetch, timeout=0.05, poll_interval=0.01)
    assert result["status"] == "timed_out"


def test_poll_cancelled_is_terminal():
    def fetch():
        return {"id": "x", "status": "canceled"}

    result = poll_until_terminal(fetch, timeout=5.0, poll_interval=0.01)
    assert result["status"] == "canceled"


# ---------------------------------------------------------------------------
# Integration via client.simulations.wait
# ---------------------------------------------------------------------------

def test_wait_returns_on_terminal(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/simulations/sim_1").mock(side_effect=[
        Response(200, json={"id": "sim_1", "status": "running"}),
        Response(200, json={"id": "sim_1", "status": "running"}),
        Response(200, json={"id": "sim_1", "status": "completed"}),
    ])
    out = client.simulations.wait("sim_1", timeout=10.0, poll_interval=0.01)
    assert out["status"] == "completed"


def test_wait_returns_timed_out(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/simulations/sim_2").mock(
        return_value=Response(200, json={"id": "sim_2", "status": "running"})
    )
    out = client.simulations.wait("sim_2", timeout=0.05, poll_interval=0.01)
    assert out["status"] == "timed_out"


def test_sweep_wait_returns_on_terminal(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/sweeps/sw_1").mock(side_effect=[
        Response(200, json={"id": "sw_1", "status": "running"}),
        Response(200, json={"id": "sw_1", "status": "completed"}),
    ])
    out = client.sweeps.wait("sw_1", timeout=10.0, poll_interval=0.01)
    assert out["status"] == "completed"


def test_poll_backoff_doubles_each_attempt():
    """sleep duration doubles on each non-terminal poll, capped at 30 s."""
    responses = [
        {"id": "x", "status": "running"},
        {"id": "x", "status": "running"},
        {"id": "x", "status": "running"},
        {"id": "x", "status": "completed"},
    ]
    idx = [0]

    def fetch():
        r = responses[idx[0]]
        idx[0] += 1
        return r

    with patch("thrustlab._async_polling.time") as mock_time:
        mock_time.monotonic.return_value = 0.0  # never expire
        mock_time.sleep = patch("thrustlab._async_polling.time.sleep").start()
        poll_until_terminal(fetch, timeout=600.0, poll_interval=1.0)
        sleep_calls = [c.args[0] for c in mock_time.sleep.call_args_list]

    # 3 non-terminal responses → 3 sleeps: 1.0, 2.0, 4.0
    assert sleep_calls == [1.0, 2.0, 4.0]


def test_poll_backoff_capped_at_30s():
    """sleep is capped at 30 s regardless of attempt count."""
    # 7 running responses then terminal; poll_interval=1 → doubles would be
    # 1, 2, 4, 8, 16, 32, 64 but should cap at 30.
    running = [{"id": "x", "status": "running"}] * 7
    responses = running + [{"id": "x", "status": "completed"}]
    idx = [0]

    def fetch():
        r = responses[idx[0]]
        idx[0] += 1
        return r

    with patch("thrustlab._async_polling.time") as mock_time:
        mock_time.monotonic.return_value = 0.0
        mock_time.sleep = patch("thrustlab._async_polling.time.sleep").start()
        poll_until_terminal(fetch, timeout=600.0, poll_interval=1.0)
        sleep_calls = [c.args[0] for c in mock_time.sleep.call_args_list]

    assert sleep_calls == [1.0, 2.0, 4.0, 8.0, 16.0, 30.0, 30.0]


def test_sweep_wait_timed_out(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/sweeps/sw_2").mock(
        return_value=Response(200, json={"id": "sw_2", "status": "pending"})
    )
    out = client.sweeps.wait("sw_2", timeout=0.05, poll_interval=0.01)
    assert out["status"] == "timed_out"
