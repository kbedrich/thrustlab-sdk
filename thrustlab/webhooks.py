"""Webhook signature verification + Event parsing.

Mirrors the live ThrustLab webhook service's HMAC scheme.

Signing scheme (as of 2026-04-25):
  Header name:  ``Thrustlab-Signature``
  Header value: ``t=<unix_ts>,v1=<hex>``
  Signed blob:  ``f"{unix_ts}.{body_utf8}".encode("utf-8")``
  Algorithm:    ``hmac.new(secret.encode("utf-8"), blob, hashlib.sha256).hexdigest()``
  Tolerance:    300 seconds (5 minutes) by default

Example::

    from thrustlab import Webhook
    from thrustlab.exceptions import SignatureVerificationError

    try:
        event = Webhook.verify(request.body, request.headers["Thrustlab-Signature"], secret)
    except SignatureVerificationError as e:
        return 400, str(e)
    process(event)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any

from thrustlab.exceptions import SignatureVerificationError


DEFAULT_TOLERANCE_SECONDS = 5 * 60  # 300 s


@dataclass
class Event:
    """A parsed, verified webhook event."""

    id: str
    type: str
    created: int
    data: dict[str, Any]
    raw: dict[str, Any]


class Webhook:
    @staticmethod
    def verify(
        payload: bytes | str,
        signature_header: str,
        secret: str,
        *,
        tolerance: int = DEFAULT_TOLERANCE_SECONDS,
    ) -> Event:
        """Verify the webhook signature and return the parsed Event.

        Args:
            payload: Raw request body (bytes or str).
            signature_header: Value of the ``Thrustlab-Signature`` header.
            secret: Signing secret starting with ``whsec_``.
            tolerance: Maximum age of the timestamp in seconds (default 300).

        Returns:
            Parsed :class:`Event` if verification succeeds.

        Raises:
            :class:`~thrustlab.exceptions.SignatureVerificationError` on:
              - Missing or malformed header (no ``t=`` or ``v1=`` parts)
              - HMAC mismatch (wrong secret, tampered payload)
              - Timestamp outside the tolerance window (replay protection)
        """
        if isinstance(payload, str):
            payload_bytes = payload.encode("utf-8")
        else:
            payload_bytes = payload

        timestamp, sig = _parse_signature_header(signature_header)

        # Construct the signed blob exactly as the server does:
        #   f"{unix_ts}.{body_utf8}".encode("utf-8")
        signed = f"{timestamp}.{payload_bytes.decode('utf-8')}".encode("utf-8")
        expected = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected, sig):
            raise SignatureVerificationError("HMAC signature does not match")

        # Check timestamp *after* HMAC so we don't leak timing info on bad sigs.
        if abs(time.time() - timestamp) > tolerance:
            raise SignatureVerificationError(
                f"timestamp outside tolerance ({tolerance}s)"
            )

        body = json.loads(payload_bytes)
        return Event(
            id=body.get("id", ""),
            type=body.get("type", ""),
            created=body.get("created", 0),
            data=body.get("data", {}),
            raw=body,
        )


def _parse_signature_header(header: str) -> tuple[int, str]:
    """Parse ``t=<unix>,v1=<hex>`` header into ``(timestamp, sig_hex)``."""
    parts: dict[str, str] = {}
    for chunk in header.split(","):
        if "=" not in chunk:
            raise SignatureVerificationError("malformed signature header")
        k, v = chunk.split("=", 1)
        parts[k.strip()] = v.strip()
    if "t" not in parts or "v1" not in parts:
        raise SignatureVerificationError("missing required signature parts (t or v1)")
    try:
        return int(parts["t"]), parts["v1"]
    except ValueError as exc:
        raise SignatureVerificationError("malformed timestamp") from exc
