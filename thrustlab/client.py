"""Top-level SDK Client. Owns the Transport and exposes resource accessors."""

from __future__ import annotations

import os
from typing import Optional

import httpx

from thrustlab._http import Transport
from thrustlab.exceptions import ConfigurationError


DEFAULT_BASE_URL = "https://thrustlab.com"


class Client:
    """Synchronous client for the ThrustLab API.

    Args:
        api_key: bearer token (``key_...``). Falls back to ``$THRUSTLAB_API_KEY``.
        base_url: API base URL. Falls back to ``$THRUSTLAB_BASE_URL`` then
            ``https://thrustlab.com``.
        timeout: per-request timeout in seconds (default 30).
        max_retries: max retries on 429/5xx/connection errors (default 3).
        http_client: optional pre-built ``httpx.Client`` for advanced configuration.

    Example:
        >>> from thrustlab import Client
        >>> client = Client(api_key="key_...")
        >>> project = client.projects.create(name="my project")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        key = api_key or os.environ.get("THRUSTLAB_API_KEY")
        if not key:
            raise ConfigurationError(
                "no API key provided; pass api_key= or set $THRUSTLAB_API_KEY"
            )
        url = base_url or os.environ.get("THRUSTLAB_BASE_URL") or DEFAULT_BASE_URL

        self._transport = Transport(
            api_key=key,
            base_url=url,
            timeout=timeout,
            max_retries=max_retries,
            client=http_client,
        )

        # Resource accessors are populated as resources land in T35–T46.
        # Lazy import each one in its property so partial commits don't break Client.
        self._resources_initialized = False

    def _init_resources(self) -> None:
        """Lazy-init resource accessors. Avoids import cycles during partial builds."""
        if self._resources_initialized:
            return
        from thrustlab.resources.users import UsersResource
        from thrustlab.resources.projects import ProjectsResource
        from thrustlab.resources.simulations import SimulationsResource
        from thrustlab.resources.sweeps import SweepsResource
        from thrustlab.resources.dynamic_simulations import DynamicSimulationsResource
        from thrustlab.resources.components import ComponentsResource
        from thrustlab.resources.submissions import SubmissionsResource
        from thrustlab.resources.starred_components import StarredComponentsResource
        from thrustlab.resources.compute_units import ComputeUnitsResource
        from thrustlab.resources.webhook_endpoints import WebhookEndpointsResource
        from thrustlab.resources.fmu import FmuResource

        self.users = UsersResource(self._transport)
        self.projects = ProjectsResource(self._transport)
        self.simulations = SimulationsResource(self._transport)
        self.sweeps = SweepsResource(self._transport)
        self.dynamic_simulations = DynamicSimulationsResource(self._transport)
        self.components = ComponentsResource(self._transport)
        self.submissions = SubmissionsResource(self._transport)
        self.starred_components = StarredComponentsResource(self._transport)
        self.compute_units = ComputeUnitsResource(self._transport)
        self.webhook_endpoints = WebhookEndpointsResource(self._transport)
        self.fmu = FmuResource(self._transport)
        self._resources_initialized = True

    def __getattr__(self, name: str):
        # Trigger lazy init on first access of any resource accessor.
        if name in {
            "users", "projects", "simulations", "sweeps",
            "dynamic_simulations", "components", "submissions", "starred_components",
            "compute_units", "webhook_endpoints", "fmu",
        }:
            self._init_resources()
            return getattr(self, name)
        raise AttributeError(name)
