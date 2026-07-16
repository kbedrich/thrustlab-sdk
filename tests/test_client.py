import pytest

from thrustlab import Client
from thrustlab.exceptions import ConfigurationError


def test_client_requires_api_key(monkeypatch):
    monkeypatch.delenv("THRUSTLAB_API_KEY", raising=False)
    with pytest.raises(ConfigurationError):
        Client()


def test_client_reads_env_key(monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_env")
    client = Client()
    assert client._transport._api_key == "key_env"


def test_client_explicit_key_wins(monkeypatch):
    monkeypatch.setenv("THRUSTLAB_API_KEY", "key_env")
    client = Client(api_key="key_explicit")
    assert client._transport._api_key == "key_explicit"


def test_client_default_base_url():
    c = Client(api_key="k")
    assert c._transport._base_url == "https://thrustlab.com"


def test_client_env_base_url(monkeypatch):
    monkeypatch.setenv("THRUSTLAB_BASE_URL", "https://staging.thrustlab.com")
    c = Client(api_key="k")
    assert c._transport._base_url == "https://staging.thrustlab.com"


# ---------------------------------------------------------------------------
# SDK 0.3.0 accessor surface.
#
# These lock the 0.3.0 accessor set: `credits` → `compute_units`, and
# `subscriptions` / `api_keys` removed (no longer part of the public SDK).
# ---------------------------------------------------------------------------


def test_compute_units_accessor_present():
    client = Client(api_key="k")
    assert hasattr(client, "compute_units")
    # It must be a live resource with a balance() method, not a bare attribute.
    assert callable(getattr(client.compute_units, "balance", None))


def test_subscriptions_accessor_removed():
    client = Client(api_key="k")
    with pytest.raises(AttributeError):
        _ = client.subscriptions


def test_api_keys_accessor_removed():
    client = Client(api_key="k")
    with pytest.raises(AttributeError):
        _ = client.api_keys


def test_credits_accessor_removed():
    client = Client(api_key="k")
    with pytest.raises(AttributeError):
        _ = client.credits
