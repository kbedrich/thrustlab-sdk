import pytest
import respx

from thrustlab._http import Transport


@pytest.fixture
def mock_router():
    """A respx router that intercepts httpx requests for unit tests."""
    with respx.mock(base_url="https://api.test.local") as router:
        yield router


@pytest.fixture
def transport(mock_router):
    return Transport(api_key="key_test", base_url="https://api.test.local", max_retries=0)
