"""Internal HTTP transport for the ThrustLab SDK.

Wraps httpx.Client with auth, idempotency-key generation, retries with
exponential backoff + jitter, and error-envelope → exception mapping.
"""

from __future__ import annotations

import logging
import platform
import random
import time
import uuid
from typing import Any, Optional

import httpx

from thrustlab._version import __version__
from thrustlab.exceptions import (
    APIError, NetworkError, RateLimitError, from_response_status,
)


logger = logging.getLogger("thrustlab")


def _user_agent() -> str:
    return (
        f"thrustlab-python/{__version__} "
        f"(Python/{platform.python_version()}; {platform.system()})"
    )


_RETRYABLE_STATUSES = {429, 500, 502, 503, 504}
_MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class Transport:
    """HTTP transport for the SDK Client.

    Responsibilities:
      - inject Authorization + User-Agent on every request
      - auto-generate Idempotency-Key on every mutating request unless caller passes one
      - retry on 429 + 5xx + connection errors with exponential backoff + jitter
      - map error responses to the right APIError subclass
      - parse JSON responses
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        client: Optional[httpx.Client] = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._max_retries = max_retries
        self._client = client or httpx.Client(timeout=timeout)

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json: Optional[Any] = None,
        idempotency_key: Optional[str] = None,
    ) -> Any:
        url = self._base_url + path
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "User-Agent": _user_agent(),
            "Accept": "application/json",
        }
        if json is not None:
            headers["Content-Type"] = "application/json"
        if method.upper() in _MUTATING_METHODS:
            headers["Idempotency-Key"] = idempotency_key or str(uuid.uuid4())

        last_exc: Optional[Exception] = None
        for attempt in range(self._max_retries + 1):
            try:
                resp = self._client.request(method, url, params=params, json=json, headers=headers)
            except httpx.HTTPError as exc:
                net_err = NetworkError(f"network error: {exc}")
                net_err.__cause__ = exc
                last_exc = net_err
                if attempt < self._max_retries:
                    self._sleep(attempt, retry_after=None)
                    continue
                raise last_exc
            else:
                if resp.status_code in _RETRYABLE_STATUSES and attempt < self._max_retries:
                    retry_after = _parse_retry_after(resp)
                    self._sleep(attempt, retry_after=retry_after)
                    continue
                return self._handle_response(resp)

        # Unreachable in practice (loop returns or raises), but pacifies type checker.
        if last_exc is not None:
            raise last_exc
        raise NetworkError("unreachable: exhausted retries with no exception")

    def _sleep(self, attempt: int, retry_after: Optional[float]) -> None:
        if retry_after is not None:
            delay = retry_after
        else:
            base = 0.5 * (2 ** attempt)
            jitter = random.uniform(0, 0.5)
            delay = base + jitter
        logger.debug("thrustlab: retrying after %.2fs (attempt %d)", delay, attempt + 1)
        time.sleep(delay)

    def _handle_response(self, resp: httpx.Response) -> Any:
        if 200 <= resp.status_code < 300:
            if resp.status_code == 204 or not resp.content:
                return None
            return resp.json()

        # Error path. Parse envelope: { "error": { "type": ..., "code": ..., "message": ..., "param": ..., "request_id": ... } }.
        body: dict[str, Any] = {}
        try:
            body = resp.json()
        except ValueError:
            pass
        env = body.get("error", {}) if isinstance(body, dict) else {}
        # The envelope's request_id is authoritative; the header is a fallback.
        request_id = env.get("request_id") or resp.headers.get("X-Request-ID")

        kwargs = dict(
            code=env.get("code"),
            type=env.get("type"),
            request_id=request_id,
            http_status=resp.status_code,
            param=env.get("param"),
        )
        message = env.get("message") or f"HTTP {resp.status_code}"

        cls = from_response_status(resp.status_code)
        if cls is RateLimitError:
            return self._raise_rate_limit(message, kwargs, resp)
        raise cls(message, **kwargs)

    def _raise_rate_limit(self, message: str, kwargs: dict[str, Any], resp: httpx.Response) -> None:
        retry_after = _parse_retry_after(resp)
        raise RateLimitError(message, retry_after=retry_after, **kwargs)


def _parse_retry_after(resp: httpx.Response) -> Optional[float]:
    raw = resp.headers.get("Retry-After")
    if not raw:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        pass
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(raw)
        if dt is not None:
            delta = dt.timestamp() - time.time()
            return max(0.0, delta)
    except (TypeError, ValueError):
        pass
    return None
