"""Exception hierarchy for the ThrustLab SDK.

All errors derive from :class:`ThrustlabError`. HTTP-derived errors carry the
full Stripe-style envelope (code, type, request_id, http_status, message,
optional param). See https://thrustlab.com/docs/guides/errors for the full
error code reference.
"""

from __future__ import annotations

from typing import Optional


class ThrustlabError(Exception):
    """Base for all thrustlab errors."""


class APIError(ThrustlabError):
    """An HTTP error response from the ThrustLab API.

    Attributes:
        code: Stripe-style code, e.g. ``invalid_request_parameter``.
        type: Stripe-style type, e.g. ``invalid_request_error``.
        request_id: Server-assigned request id from the ``X-Request-ID`` header.
        http_status: HTTP status code.
        message: Human-readable description.
        param: For validation errors, the offending parameter name.
    """

    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        type: Optional[str] = None,
        request_id: Optional[str] = None,
        http_status: Optional[int] = None,
        param: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.type = type
        self.request_id = request_id
        self.http_status = http_status
        self.param = param

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(message={self.message!r}, code={self.code!r}, "
            f"http_status={self.http_status}, request_id={self.request_id!r})"
        )


class AuthenticationError(APIError):
    """401 — bearer token is missing, malformed, or invalid."""


class ForbiddenError(APIError):
    """403 — authenticated but not authorized for this resource."""


class NotFoundError(APIError):
    """404 — resource does not exist or is not accessible to this caller."""


class ValidationError(APIError):
    """400 / 422 — request body or query did not validate."""


class ConflictError(APIError):
    """409 — conflict (e.g. idempotency-key replay collision)."""


class RateLimitError(APIError):
    """429 — rate limit exceeded.

    Attributes:
        retry_after: Seconds to wait before retrying, from the ``Retry-After`` header.
    """

    def __init__(self, *args, retry_after: Optional[float] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.retry_after = retry_after


class APIServerError(APIError):
    """5xx — server-side failure."""


class NetworkError(ThrustlabError):
    """Connection or timeout failure (no HTTP response received)."""


class SignatureVerificationError(ThrustlabError):
    """Webhook payload signature did not verify."""


class ConfigurationError(ThrustlabError):
    """SDK configuration error (missing key, bad base_url, etc.)."""


class AmbiguousComponentError(ThrustlabError):
    """A one-hit lookup (``find()`` / ``.one()``) matched more than one component.

    Raised by :meth:`thrustlab.resources.components.ComponentsResource.find` and
    :meth:`thrustlab._pagination.CursorPager.one` when the filters narrow to more
    than a single result. The matching rows are surfaced on ``candidates`` so the
    caller can disambiguate (e.g. pick a specific ``id``) rather than guessing.

    Attributes:
        candidates: The list of matching component dicts (each carries at least
            ``id`` and ``name``). Also aliased as ``matches``.
    """

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        candidates: Optional[list] = None,
    ) -> None:
        self.candidates = candidates or []
        # ``matches`` alias kept for callers that prefer the other spelling.
        self.matches = self.candidates
        if message is None:
            ids = ", ".join(
                str(c.get("id") if isinstance(c, dict) else c)
                for c in self.candidates
            )
            message = (
                f"Lookup matched {len(self.candidates)} components ({ids}); "
                "narrow the filters or call .first()/.list() and pick one by id."
            )
        super().__init__(message)
        self.message = message


# Mapping from HTTP status → exception class. Used by the transport layer.
HTTP_STATUS_EXCEPTIONS = {
    400: ValidationError,
    401: AuthenticationError,
    403: ForbiddenError,
    404: NotFoundError,
    409: ConflictError,
    422: ValidationError,
    429: RateLimitError,
}


def from_response_status(status: int) -> type[APIError]:
    """Pick the right APIError subclass for a given HTTP status."""
    if status in HTTP_STATUS_EXCEPTIONS:
        return HTTP_STATUS_EXCEPTIONS[status]
    if 500 <= status < 600:
        return APIServerError
    return APIError
