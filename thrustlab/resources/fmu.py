"""``client.fmu`` — export a simulation as an FMI 3.0 Co-Simulation FMU.

An FMU export packages a completed single-point simulation's powertrain (aero,
motor and pack surfaces, sampled through the same engine that produced the
on-screen result) as a Modelica-standard ``.fmu`` — a generic map interpolator
plus operating-point tables, no solver and no component specs. Export is
async-as-a-resource, same pattern as :mod:`thrustlab.resources.sweeps`: queue
it, poll (or ``wait()``) for a terminal status, then download the artifact
(available 24 h after completion).

Endpoints:
    POST   /v1/simulations/{id}/export/fmu           (202, queues the job)
    GET    /v1/simulations/export/fmu/{job_id}
    POST   /v1/simulations/export/fmu/{job_id}/cancel
    GET    /v1/simulations/export/fmu/{job_id}/download   (raw bytes — not JSON)

``GET /v1/simulations/export/fmu/{job_id}/stream`` (SSE) is not wrapped, same
posture as the dynamic-simulations stream endpoint — no polling/wait use case
for it in the SDK; the web app's progress tab consumes it directly.
"""

from __future__ import annotations

import os
import time
from typing import Any, Callable, Optional, Union

from thrustlab._async_polling import TERMINAL_STATES
from thrustlab.resources._base import Resource


class FmuResource(Resource):
    def export(
        self,
        simulation_id: str,
        *,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Queue an FMU export for a completed simulation. Returns the 202 body
        (``{"id": "fmu_...", "object": "fmu_export", "status": "queued"}``).

        The source simulation must be a completed ``single_point`` run with at
        least one rotor group, no multi-pack battery topology and no coaxial
        stack (heterogeneous rotor groups ARE supported). One export job runs
        per account at a time — a second call while one is in flight raises
        :class:`~thrustlab.exceptions.ConflictError` (``export_in_progress``).
        """
        return self._transport.request(
            "POST", f"/v1/simulations/{simulation_id}/export/fmu",
            idempotency_key=idempotency_key,
        )

    def status(self, job_id: str) -> dict[str, Any]:
        """Read an FMU export job's current status.

        ``status`` walks ``queued`` -> ``solving`` (with ``chunks_done`` /
        ``chunks_total``) -> ``completed`` | ``failed``. A completed job
        carries ``filename`` and ``artifact_available``; a failed job carries
        an ``error`` object (``error_code``, ``message``). The response may
        carry additional fields beyond these (e.g. ``progress``, ``eta_s``,
        ``phase``) — treat any key not documented here as optional.
        """
        return self._transport.request("GET", f"/v1/simulations/export/fmu/{job_id}")

    def cancel(self, job_id: str, *, idempotency_key: Optional[str] = None) -> dict[str, Any]:
        """Request cancellation of a running export (cooperative — the worker
        stops at the next chunk boundary). Returns the current status; poll
        or ``wait()`` to observe it settle to ``failed`` with
        ``error.error_code == "export_cancelled"``. A no-op on an
        already-terminal job.
        """
        return self._transport.request(
            "POST", f"/v1/simulations/export/fmu/{job_id}/cancel",
            idempotency_key=idempotency_key,
        )

    def wait(
        self,
        job_id: str,
        *,
        on_progress: Optional[Callable[[dict[str, Any]], None]] = None,
        poll_interval: float = 2.0,
        timeout: Optional[float] = None,
    ) -> dict[str, Any]:
        """Poll ``status()`` until the export job reaches a terminal state.

        Unlike the other ``wait()`` methods in this SDK, ``timeout`` defaults
        to ``None`` (wait indefinitely) — an export's lane-table / aero-table
        build cost is not bounded the way a single steady-state point is. Pass
        an explicit ``timeout`` to cap it; on expiry the returned dict has
        ``status="timed_out"`` (an SDK-side sentinel — the job keeps running
        server-side and you can call ``wait()`` or ``status()`` again).

        ``on_progress``, if given, is called with EVERY status response as it
        arrives (including non-terminal ones) — useful for driving a progress
        bar. The response may carry additive fields (``progress``, ``eta_s``,
        ``phase``) beyond the ones ``status()`` documents; don't assume any
        given key is present.

        Terminal states are ``completed`` / ``failed`` (an export job never
        actually reaches ``canceled`` on the wire — ``cancel()`` resolves a
        running job to ``failed`` with ``error.error_code ==
        "export_cancelled"``). This does NOT raise on a failed job, mirroring
        every other ``wait()`` in the SDK — check ``result["status"]``; a
        failed job's ``result["error"]`` carries ``error_code`` / ``message``.
        """
        # A zero interval is a tight request loop and a negative one raises
        # from time.sleep(); the exponent is capped so an indefinite wait
        # stays indefinite (2**attempt overflows float conversion past ~1e308).
        poll_interval = max(float(poll_interval), 0.001)
        deadline = None if timeout is None else time.monotonic() + timeout
        attempt = 0
        while True:
            obj = self.status(job_id)
            if on_progress is not None:
                on_progress(obj)
            if obj.get("status") in TERMINAL_STATES:
                return obj
            if deadline is not None and time.monotonic() >= deadline:
                obj = dict(obj)
                obj["status"] = "timed_out"
                return obj
            sleep_for = min(poll_interval * (2.0 ** min(attempt, 16)), 30.0)
            if deadline is not None:
                # Never sleep past the deadline: wait(timeout=...) should
                # return promptly at expiry, not up to 30 s late.
                sleep_for = min(sleep_for, max(deadline - time.monotonic(), 0.0))
            time.sleep(sleep_for)
            attempt += 1

    def download(self, job_id: str, path: Union[str, "os.PathLike[str]"]) -> str:
        """Download a completed export's ``.fmu`` artifact to ``path``.

        Available for 24 hours after the job completes
        (``status()["artifact_available"]``); afterwards this raises
        :class:`~thrustlab.exceptions.NotFoundError` (``export_expired``) and
        the export must be run again. Streams no further than one buffered
        response body — FMU artifacts here are small map/table packages, not
        solver state. Returns ``path`` (as ``str``) for chaining.
        """
        content = self._transport.request(
            "GET", f"/v1/simulations/export/fmu/{job_id}/download",
            parse_json=False,
        )
        with open(path, "wb") as f:
            f.write(content)
        return str(path)
