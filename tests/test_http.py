import time
from unittest.mock import patch

import pytest
import respx
from httpx import Response

from thrustlab._http import Transport, _parse_retry_after
from thrustlab.exceptions import (
    AuthenticationError, NetworkError, RateLimitError, ValidationError,
)


def test_get_succeeds(mock_router, transport):
    mock_router.get("/v1/projects/p_1").mock(return_value=Response(200, json={"id": "p_1", "name": "x"}))
    body = transport.request("GET", "/v1/projects/p_1")
    assert body == {"id": "p_1", "name": "x"}


def test_authorization_header_injected(mock_router, transport):
    route = mock_router.get("/v1/x").mock(return_value=Response(200, json={}))
    transport.request("GET", "/v1/x")
    assert route.calls[0].request.headers["Authorization"] == "Bearer key_test"


def test_idempotency_key_auto_injected_on_post(mock_router, transport):
    route = mock_router.post("/v1/x").mock(return_value=Response(201, json={}))
    transport.request("POST", "/v1/x", json={"name": "x"})
    assert "Idempotency-Key" in route.calls[0].request.headers


def test_idempotency_key_caller_supplied(mock_router, transport):
    route = mock_router.post("/v1/x").mock(return_value=Response(201, json={}))
    transport.request("POST", "/v1/x", json={"name": "x"}, idempotency_key="my-key")
    assert route.calls[0].request.headers["Idempotency-Key"] == "my-key"


def test_no_idempotency_key_on_get(mock_router, transport):
    route = mock_router.get("/v1/x").mock(return_value=Response(200, json={}))
    transport.request("GET", "/v1/x")
    assert "Idempotency-Key" not in route.calls[0].request.headers


def test_401_raises_authentication_error(mock_router, transport):
    mock_router.get("/v1/x").mock(return_value=Response(401, json={
        "error": {"type": "authentication_error", "code": "invalid_credential",
                  "message": "no good"}
    }, headers={"X-Request-ID": "req_1"}))
    with pytest.raises(AuthenticationError) as exc_info:
        transport.request("GET", "/v1/x")
    assert exc_info.value.code == "invalid_credential"
    assert exc_info.value.request_id == "req_1"


def test_400_raises_validation_error_with_param(mock_router, transport):
    mock_router.post("/v1/x").mock(return_value=Response(400, json={
        "error": {"type": "invalid_request_error", "code": "missing_field",
                  "message": "name required", "param": "name"}
    }))
    with pytest.raises(ValidationError) as exc_info:
        transport.request("POST", "/v1/x", json={})
    assert exc_info.value.param == "name"


def test_429_raises_rate_limit_with_retry_after(mock_router):
    transport = Transport(api_key="k", base_url="https://api.test.local", max_retries=0)
    mock_router.get("/v1/x").mock(return_value=Response(429, json={
        "error": {"type": "rate_limit_error", "code": "rate_limited", "message": "slow"}
    }, headers={"Retry-After": "2.5"}))
    with pytest.raises(RateLimitError) as exc_info:
        transport.request("GET", "/v1/x")
    assert exc_info.value.retry_after == 2.5


def test_retries_on_500(mock_router):
    transport = Transport(api_key="k", base_url="https://api.test.local", max_retries=2)
    route = mock_router.get("/v1/x").mock(side_effect=[
        Response(500, json={"error": {"message": "boom"}}),
        Response(500, json={"error": {"message": "boom"}}),
        Response(200, json={"ok": True}),
    ])
    body = transport.request("GET", "/v1/x")
    assert body == {"ok": True}
    assert route.call_count == 3


def test_does_not_retry_on_400(mock_router):
    transport = Transport(api_key="k", base_url="https://api.test.local", max_retries=3)
    route = mock_router.get("/v1/x").mock(return_value=Response(400, json={
        "error": {"type": "invalid_request_error", "code": "bad", "message": "no"}
    }))
    with pytest.raises(ValidationError):
        transport.request("GET", "/v1/x")
    assert route.call_count == 1


# ---------------------------------------------------------------------------
# _parse_retry_after unit tests
# ---------------------------------------------------------------------------

def test_parse_retry_after_integer_seconds():
    resp = Response(429, headers={"Retry-After": "30"})
    assert _parse_retry_after(resp) == 30.0


def test_parse_retry_after_float_seconds():
    resp = Response(429, headers={"Retry-After": "2.5"})
    assert _parse_retry_after(resp) == 2.5


def test_parse_retry_after_http_date():
    # Freeze time so the delta is deterministic.
    fixed_now = 1_000_000.0
    # HTTP-date 500 seconds in the future relative to fixed_now.
    import datetime
    future_dt = datetime.datetime.fromtimestamp(fixed_now + 500, tz=datetime.timezone.utc)
    http_date = future_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
    resp = Response(429, headers={"Retry-After": http_date})
    with patch("thrustlab._http.time") as mock_time:
        mock_time.time.return_value = fixed_now
        result = _parse_retry_after(resp)
    assert result is not None
    assert abs(result - 500.0) < 2.0  # within 2 s of expected delta


def test_parse_retry_after_missing_header():
    resp = Response(429)
    assert _parse_retry_after(resp) is None


def test_parse_retry_after_garbage_value():
    resp = Response(429, headers={"Retry-After": "not-a-date-or-number"})
    assert _parse_retry_after(resp) is None
