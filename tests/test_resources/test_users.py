from httpx import Response

from thrustlab import Client


def test_me_calls_get(mock_router, monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_test")
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://api.test.local")
    client = Client()
    mock_router.get("/v1/users/me").mock(return_value=Response(200, json={"id": "user_1", "tier": "pro"}))
    out = client.users.me()
    assert out["id"] == "user_1"
    assert out["tier"] == "pro"
