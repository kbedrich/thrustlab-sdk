"""``client.users`` — authenticated user profile."""

from __future__ import annotations

from typing import Any

from thrustlab.resources._base import Resource


class UsersResource(Resource):
    def me(self) -> dict[str, Any]:
        """Return the authenticated user's profile."""
        return self._transport.request("GET", "/v1/users/me")
