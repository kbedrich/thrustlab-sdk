"""Polling helpers for async resources (simulations, sweeps).

The terminal states are: 'completed' | 'failed' | 'canceled' — these are the
exact wire values the v1 API emits (see backend/app/v1/_async_serialize.py
``_DB_TO_V1``; DB ``cancelled`` maps to wire ``canceled`` with one 'l').
'timed_out' is an SDK-side sentinel set when wait() exceeds its timeout budget
— it is never returned by the server.
"""

from __future__ import annotations

import time
from typing import Any, Callable

TERMINAL_STATES = {"completed", "failed", "canceled"}


def poll_until_terminal(
    fetch: Callable[[], dict[str, Any]],
    *,
    timeout: float = 600.0,
    poll_interval: float = 2.0,
) -> dict[str, Any]:
    """Poll ``fetch`` until the returned object reaches a terminal state.

    Args:
        fetch: Zero-argument callable that returns the latest resource dict.
        timeout: Maximum seconds to wait. If exceeded, returns the last dict
                 with ``status`` set to ``"timed_out"``.
        poll_interval: Seconds between polls (``time.sleep``).

    Returns:
        The resource dict when status is in ``TERMINAL_STATES``, or a copy
        with ``status="timed_out"`` if the deadline was exceeded.
    """
    deadline = time.monotonic() + timeout
    attempt = 0
    while True:
        obj = fetch()
        status = obj.get("status")
        if status in TERMINAL_STATES:
            return obj
        if time.monotonic() >= deadline:
            obj = dict(obj)
            obj["status"] = "timed_out"
            return obj
        sleep_for = min(poll_interval * (2 ** attempt), 30.0)
        time.sleep(sleep_for)
        attempt += 1
