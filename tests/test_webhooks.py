"""Tests for Webhook.verify + SignatureVerificationError.

Signing scheme matches the ThrustLab webhook service exactly:
  signed_blob = f"{ts}.{body_utf8}".encode("utf-8")
  sig_hex     = hmac.new(secret.encode(), signed_blob, hashlib.sha256).hexdigest()
  header      = f"t={ts},v1={sig_hex}"
"""

import hashlib
import hmac
import json
import time

import pytest

from thrustlab import Event, Webhook
from thrustlab.exceptions import SignatureVerificationError


# ---------------------------------------------------------------------------
# Helper: mirrors server-side build_signature_header + sign_body
# ---------------------------------------------------------------------------

def _sign(payload: str | bytes, secret: str, ts: int) -> str:
    """Return a Thrustlab-Signature header value for the given payload."""
    if isinstance(payload, str):
        body_bytes = payload.encode("utf-8")
    else:
        body_bytes = payload
    signed = f"{ts}.{body_bytes.decode('utf-8')}".encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), signed, hashlib.sha256).hexdigest()
    return f"t={ts},v1={sig}"


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_verify_happy_path():
    secret = "whsec_test"
    payload = json.dumps({
        "id": "evt_1",
        "type": "simulation.succeeded",
        "created": 1,
        "data": {"sim_id": "sim_1"},
    })
    ts = int(time.time())
    header = _sign(payload, secret, ts)

    event = Webhook.verify(payload, header, secret)

    assert isinstance(event, Event)
    assert event.id == "evt_1"
    assert event.type == "simulation.succeeded"
    assert event.data["sim_id"] == "sim_1"
    assert event.raw["created"] == 1


def test_verify_accepts_bytes_payload():
    secret = "whsec_test"
    payload = json.dumps({"id": "evt_2", "type": "sweep.succeeded", "created": 0, "data": {}})
    ts = int(time.time())
    header = _sign(payload, secret, ts)

    event = Webhook.verify(payload.encode("utf-8"), header, secret)
    assert event.id == "evt_2"


# ---------------------------------------------------------------------------
# Bad signature
# ---------------------------------------------------------------------------

def test_verify_rejects_tampered_payload():
    secret = "whsec_test"
    payload = json.dumps({"id": "evt_1", "type": "x", "created": 0, "data": {}})
    ts = int(time.time())
    header = _sign(payload, secret, ts)

    with pytest.raises(SignatureVerificationError):
        Webhook.verify(payload + " ", header, secret)


def test_verify_rejects_bad_secret():
    payload = json.dumps({"id": "evt_1", "type": "x", "created": 0, "data": {}})
    ts = int(time.time())
    header = _sign(payload, "right_secret", ts)

    with pytest.raises(SignatureVerificationError):
        Webhook.verify(payload, header, "wrong_secret")


# ---------------------------------------------------------------------------
# Expired timestamp
# ---------------------------------------------------------------------------

def test_verify_rejects_old_timestamp():
    secret = "whsec_test"
    payload = json.dumps({"id": "evt_1", "type": "x", "created": 0, "data": {}})
    ts = int(time.time()) - 1000  # way past default 300 s tolerance

    header = _sign(payload, secret, ts)

    with pytest.raises(SignatureVerificationError, match="tolerance"):
        Webhook.verify(payload, header, secret)


def test_verify_accepts_timestamp_at_edge_of_tolerance():
    """Timestamp exactly at tolerance boundary should succeed."""
    secret = "whsec_test"
    payload = json.dumps({"id": "evt_1", "type": "x", "created": 0, "data": {}})
    # Just inside window (1 second to spare).
    ts = int(time.time()) - 299

    header = _sign(payload, secret, ts)
    event = Webhook.verify(payload, header, secret, tolerance=300)
    assert event.id == "evt_1"


# ---------------------------------------------------------------------------
# Malformed / missing header
# ---------------------------------------------------------------------------

def test_verify_rejects_missing_header():
    with pytest.raises(SignatureVerificationError):
        Webhook.verify(b"{}", "", "whsec")


def test_verify_rejects_header_without_t():
    """Header missing t= part."""
    secret = "whsec_test"
    payload = json.dumps({"id": "x", "type": "y", "created": 0, "data": {}})
    ts = int(time.time())
    sig = hmac.new(
        secret.encode(),
        f"{ts}.{payload}".encode(),
        hashlib.sha256,
    ).hexdigest()
    # Only v1=, no t=
    bad_header = f"v1={sig}"

    with pytest.raises(SignatureVerificationError):
        Webhook.verify(payload, bad_header, secret)


def test_verify_rejects_header_without_v1():
    """Header missing v1= part."""
    ts = int(time.time())
    bad_header = f"t={ts}"

    with pytest.raises(SignatureVerificationError):
        Webhook.verify(b"{}", bad_header, "whsec")


def test_verify_rejects_completely_malformed_header():
    """Header with no '=' at all."""
    with pytest.raises(SignatureVerificationError):
        Webhook.verify(b"{}", "garbage-no-equals-signs", "whsec")


def test_verify_rejects_non_integer_timestamp():
    """t= value that isn't an int."""
    with pytest.raises(SignatureVerificationError):
        Webhook.verify(b"{}", "t=notanint,v1=aabbcc", "whsec")


# ---------------------------------------------------------------------------
# Custom tolerance
# ---------------------------------------------------------------------------

def test_verify_custom_tolerance():
    """Zero tolerance rejects any non-current timestamp."""
    secret = "whsec_test"
    payload = json.dumps({"id": "evt_1", "type": "x", "created": 0, "data": {}})
    ts = int(time.time()) - 5  # 5 seconds old

    header = _sign(payload, secret, ts)

    with pytest.raises(SignatureVerificationError, match="tolerance"):
        Webhook.verify(payload, header, secret, tolerance=0)
