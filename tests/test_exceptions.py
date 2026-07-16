from thrustlab.exceptions import (
    APIError, APIServerError, AuthenticationError, ConfigurationError,
    ConflictError, ForbiddenError, NetworkError, NotFoundError, RateLimitError,
    SignatureVerificationError, ThrustlabError, ValidationError,
    from_response_status,
)


def test_inheritance():
    assert issubclass(APIError, ThrustlabError)
    assert issubclass(AuthenticationError, APIError)
    assert issubclass(NetworkError, ThrustlabError)
    assert issubclass(SignatureVerificationError, ThrustlabError)
    assert issubclass(ConfigurationError, ThrustlabError)


def test_api_error_carries_envelope():
    e = APIError("nope", code="invalid_request", type="invalid_request_error",
                 request_id="req_123", http_status=400, param="name")
    assert e.message == "nope"
    assert e.code == "invalid_request"
    assert e.request_id == "req_123"
    assert e.http_status == 400
    assert e.param == "name"


def test_rate_limit_carries_retry_after():
    e = RateLimitError("slow down", retry_after=2.5, http_status=429)
    assert e.retry_after == 2.5
    assert e.http_status == 429


def test_status_to_exception_mapping():
    assert from_response_status(400) is ValidationError
    assert from_response_status(401) is AuthenticationError
    assert from_response_status(403) is ForbiddenError
    assert from_response_status(404) is NotFoundError
    assert from_response_status(409) is ConflictError
    assert from_response_status(422) is ValidationError
    assert from_response_status(429) is RateLimitError
    assert from_response_status(500) is APIServerError
    assert from_response_status(503) is APIServerError
    assert from_response_status(418) is APIError  # falls through to base
