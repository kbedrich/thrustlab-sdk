"""ArduPilot's JSON SITL backend: the frame clock, the state encoder, the server.

This is the ORIGINAL bridge behaviour, moved behind the seams in
:mod:`thrustlab.sitl.targets.base` and not otherwise changed.  The wire
format itself still lives in :mod:`thrustlab.sitl.protocol`, and
:class:`thrustlab.sitl.bridge.Bridge` still assembles the two into the
public class the CLI runs.

Spec decision 12, clause by clause:

  * exactly one physics advance per NEW ``frame_count``;
  * a duplicate packet is answered with an IDEMPOTENT resend of the last reply,
    byte for byte, and advances nothing;
  * a ``frame_count`` REGRESSION is a full restart — ``fmi3Reset`` plus
    re-initialisation and a 6DOF re-seed — because ArduPilot resets its counter
    when SITL restarts (``examples/JSON/readme.md``);
  * ``frame_rate`` is honoured per packet;
  * a FORWARD gap advances ONE step of ``dt = gap / frame_rate`` capped at
    100 ms;
  * reply timestamps are end-of-step.

DT, ONE RESOLUTION THE SPEC LEAVES OPEN.  Decision 12 says the DoStep is
``1/frame_rate`` and also that a gap advances ``gap/frame_rate``; those differ
whenever a frame is lost.  The bridge uses the SAME ``dt`` for the FMU step and
the 6DOF advance — ``min(gap / frame_rate, MAX_STEP_S)`` — so FMU time, 6DOF
time and the reply timestamp never diverge.  With no lost frames (``gap == 1``)
this is exactly ``1/frame_rate``.

THE CAP IS STRICTLY BELOW ARDUPILOT'S CEILING, NOT EQUAL TO IT.  Decision 12
says "capped at 100 ms", but ArduPilot's consumer predicate is EXCLUSIVE —
``SIM_JSON.cpp::recv_fdm`` runs ``if (is_positive(deltat) && deltat < 0.1)``
before calling ``time_advance()``.  A reply carrying a timestamp delta of
exactly 0.1 s therefore advances ``time_now_us`` but never reaches
``time_advance()``: the catch-up frame the cap exists to deliver is silently
dropped by the very consumer it was sized for.  ``MAX_STEP_S`` is set just
inside that bound so a capped frame is actually consumed.
"""

from __future__ import annotations

import logging
import socket
from dataclasses import dataclass, field

import numpy as np

from ..protocol import ServoPacket, StateReply, encode_state_json
from .base import BridgeCounters, FrameTick, StateSample

logger = logging.getLogger(__name__)

#: ArduPilot's own ceiling on a usable timestamp delta.  ``recv_fdm`` gates
#: ``time_advance()`` on ``deltat < 0.1`` — EXCLUSIVE, so 0.1 itself is rejected.
ARDUPILOT_MAX_DELTAT_S = 0.1

#: Spec decision 12's catch-up cap, placed strictly inside ArduPilot's bound so
#: that a capped frame is actually consumed rather than dropped by the predicate
#: above.  The 0.5 ms of headroom is far larger than any accumulated float error
#: in the timestamp the autopilot differences.
MAX_STEP_S = 0.0995

#: Used when a packet carries ``frame_rate == 0`` (SITL has been seen to emit a
#: zero rate before its scheduler settles).
DEFAULT_FRAME_RATE_HZ = 400


class ArduPilotFrameClock:
    """``frame_count`` -> ``dt`` plus advance / duplicate / restart.

    The whole of spec decision 12's state machine, and nothing else.  It counts
    into the caller's :class:`~thrustlab.sitl.targets.base.BridgeCounters`
    so the bridge's totals stay in one place.
    """

    def __init__(self, counters: BridgeCounters) -> None:
        self.counters = counters
        self.last_frame_count = -1
        self._pending_frame_count = -1

    def reset(self) -> None:
        self.last_frame_count = -1
        self._pending_frame_count = -1

    def commit(self) -> None:
        """Adopt the ticked frame as the last one, once its step has SUCCEEDED.

        A packet whose step raises — an out-of-range servo channel is the one
        that happens in practice — must not become the duplicate baseline, or
        the autopilot's retry of that same frame is answered with an empty
        idempotent reply instead of the error the caller needs to see.
        """
        self.last_frame_count = self._pending_frame_count

    def tick(self, packet: ServoPacket) -> FrameTick:
        if packet.frame_count == self.last_frame_count:
            # Duplicate: ArduPilot re-sends the same frame when it has heard
            # nothing for ~1 s (SIM_JSON.cpp, wait_ms > 1000).  Answer with the
            # identical bytes and advance NOTHING.
            self.counters.duplicates_resent += 1
            logger.debug("duplicate frame_count %d — resending last reply", packet.frame_count)
            return FrameTick(dt_s=0.0, advance=False, duplicate=True)

        restart = False
        if self.last_frame_count >= 0 and packet.frame_count < self.last_frame_count:
            logger.info(
                "frame_count regressed %d -> %d: SITL restarted, resetting physics",
                self.last_frame_count,
                packet.frame_count,
            )
            restart = True
            self.reset()

        gap = 1 if self.last_frame_count < 0 else packet.frame_count - self.last_frame_count
        if gap > 1:
            self.counters.frames_skipped += gap - 1
            logger.debug("frame_count gap of %d — advancing one catch-up step", gap)

        frame_rate = packet.frame_rate
        if frame_rate <= 0:
            logger.warning(
                "packet carries frame_rate %d; falling back to %d Hz",
                frame_rate,
                DEFAULT_FRAME_RATE_HZ,
            )
            frame_rate = DEFAULT_FRAME_RATE_HZ

        dt = gap / float(frame_rate)
        if dt > MAX_STEP_S:
            self.counters.steps_capped += 1
            dt = MAX_STEP_S

        self._pending_frame_count = packet.frame_count
        return FrameTick(dt_s=dt, advance=True, restart=restart)


class ArduPilotStateEncoder:
    """:class:`StateSample` -> the JSON datagram ``recv_fdm`` parses.

    Nothing is converted: ArduPilot's frames ARE the bridge's frames (world NED,
    body FRD, ``(w, x, y, z)`` body->NED quaternion, accelerometer as specific
    force).  Battery values are omitted from the payload entirely when the FMU
    does not produce them, rather than sent as zero — ``SIM_JSON.cpp`` falls
    back to ``sitl->batt_voltage`` for an absent ``battery/voltage``, which is a
    far better default than a fabricated 0 V.
    """

    def __init__(self, counters: BridgeCounters) -> None:
        self.counters = counters

    def state_reply(self, sample: StateSample) -> StateReply:
        return StateReply(
            timestamp_s=sample.timestamp_s,
            gyro_rad_s=sample.state.omega_body_rad_s,
            accel_body_m_s2=sample.accel_body_m_s2,
            position_ned_m=sample.state.position_ned_m,
            velocity_ned_m_s=sample.state.velocity_ned_m_s,
            quaternion=sample.state.quaternion,
            airspeed_m_s=sample.airspeed_m_s,
            battery_voltage_V=(
                sample.voltage_bus_V if np.isfinite(sample.voltage_bus_V) else None
            ),
            battery_current_A=(
                sample.current_bus_A if np.isfinite(sample.current_bus_A) else None
            ),
        )

    def encode(self, sample: StateSample) -> bytes:
        reply, substitutions = encode_state_json(self.state_reply(sample))
        if substitutions:
            self.counters.non_finite_substitutions += substitutions
            logger.error(
                "%d non-finite value(s) in the state reply at t=%.4f s were sent as 0.0; "
                "the 6DOF or the FMU has diverged",
                substitutions,
                sample.timestamp_s,
            )
        return reply


@dataclass
class BridgeServer:
    """UDP transport around :class:`thrustlab.sitl.bridge.Bridge`.

    ArduPilot's readme is explicit that the backend replies to whatever address
    the servo packet came from, so nothing here needs a configured peer.
    """

    bridge: object
    host: str = "0.0.0.0"
    port: int = 9002
    recv_buffer_bytes: int = 4096
    _socket: socket.socket | None = field(default=None, init=False, repr=False)

    def open(self) -> None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        self._socket = sock
        logger.info("listening for ArduPilot servo packets on %s:%d", self.host, self.port)

    def close(self) -> None:
        if self._socket is not None:
            self._socket.close()
            self._socket = None

    def serve_forever(self) -> None:
        if self._socket is None:
            self.open()
        assert self._socket is not None
        while True:
            data, address = self._socket.recvfrom(self.recv_buffer_bytes)
            reply = self.bridge.handle_datagram(data)
            if reply:
                self._socket.sendto(reply, address)

    def __enter__(self) -> BridgeServer:
        self.open()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()
