from httpx import Response

from thrustlab import Client

# ---------------------------------------------------------------------------
# compute-units SDK resource (renamed from credits).
#
# `client.compute_units` (renamed from `client.credits`) hits
# /v1/compute-units/{balance,transactions}: the `usage()` method became
# `transactions()` and the cursor param `starting_after` became `cursor`
# (matching the sims/sweeps pagination fix). The `credit_type` filter kwarg
# is retained — that is the real query param on the shipped
# /v1/compute-units/transactions endpoint.
# ---------------------------------------------------------------------------


def test_balance_calls_get(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/compute-units/balance").mock(
        return_value=Response(200, json={"simulation": 100, "sweep": 20, "ai": 5})
    )
    out = client.compute_units.balance()
    assert out["simulation"] == 100


def test_transactions_passes_filter(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.get("/v1/compute-units/transactions").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    client.compute_units.transactions(credit_type="simulation", limit=10).data  # trigger fetch
    qs = dict(route.calls[0].request.url.params)
    assert qs["credit_type"] == "simulation"
    assert qs["limit"] == "10"


def test_transactions_passes_cursor(mock_router, monkeypatch):
    """The pager param is `cursor`, not the legacy `starting_after` (Phase-60 fix)."""
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    route = mock_router.get("/v1/compute-units/transactions").mock(
        return_value=Response(200, json={"data": [], "has_more": False})
    )
    client.compute_units.transactions(cursor="txn_5", limit=5).data  # trigger fetch
    qs = dict(route.calls[0].request.url.params)
    assert qs["cursor"] == "txn_5"
    assert "starting_after" not in qs
