#!/usr/bin/env python3
"""Arm, climb, hold altitude, land — a Betaflight SITL flight on FMU physics.

The bridge (``python -m thrustlab.sitl --target betaflight``) owns the
physics and the FDM feed.  This script is the pilot and the ground station:

  * RC over UDP 9004 (``rc_packet``) — ``FEATURE_RX_UDP`` is the default
    receiver for a bare ``TARGET=SITL`` build, so this IS the transmitter;
  * MSP over TCP 5761 for arm/mode state and the accelerometer calibration;
  * the bridge's ground-truth JSON fan-out on UDP 9005 for the assertions,
    because the flight controller's own estimate is not evidence about the
    flight controller.

It writes ``mission_telemetry.csv`` (truth, 20 Hz) and ``mission_events.csv``
next to the bridge's ``mission_rpm_log.csv``, and asserts QUALITATIVE outcomes
only — armed, altitude held in a loose band, clean disarm, envelope clean.  The
upstream harness's numeric tolerances are tuned to its own scheduler and mean
nothing here.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import socket
import struct
import sys
import threading
import time
from pathlib import Path

# ─────────────────────────────────────────────────────────────── constants

RC_PORT = 9004
MSP_PORT = 5761
TRUTH_PORT = 9005

RC_LOW, RC_MID, RC_HIGH = 1000, 1500, 2000

# Channel indices into the 16-channel rc_packet (AETR by Betaflight default).
CH_ROLL, CH_PITCH, CH_THROTTLE, CH_YAW = 0, 1, 2, 3
CH_AUX1, CH_AUX2, CH_AUX3 = 4, 5, 6

MSP_STATUS = 101
MSP_BOXIDS = 119
MSP_ACC_CALIBRATION = 205

# Box permanent IDs (src/main/msp/msp_box.c).
BOX_ARM = 0
BOX_ANGLE = 1
BOX_ALTHOLD = 3
BOX_POSHOLD = 11
BOX_FAILSAFE = 27
BOX_AUTOPILOT = 56

# src/main/fc/runtime_config.c, armingDisableFlagNames — bit index is the flag.
ARMING_DISABLE_FLAG_NAMES = [
    "NOGYRO", "FAILSAFE", "RXLOSS", "NOT_DISARMED", "BOXFAILSAFE", "RUNAWAY",
    "CRASH", "THROTTLE", "ANGLE", "BOOTGRACE", "NOPREARM", "LOAD", "CALIB",
    "CLI", "CMS", "BST", "MSP", "PARALYZE", "GPS", "RESCUE_SW", "DSHOT_TELEM",
    "REBOOT_REQD", "DSHOT_BBANG", "NO_ACC_CAL", "MOTOR_PROTO", "FLIP_SWITCH",
    "ALT_HOLD_SW", "POS_HOLD_SW", "AUTOPILOT_SW", "ARM_SWITCH",
]


def arming_flag_names(flags: int) -> str:
    if not flags:
        return "none"
    return " ".join(
        name for bit, name in enumerate(ARMING_DISABLE_FLAG_NAMES) if flags & (1 << bit)
    )


BOX_NAMES = {
    BOX_ARM: "ARM",
    BOX_ANGLE: "ANGLE",
    BOX_ALTHOLD: "ALTHOLD",
    BOX_POSHOLD: "POSHOLD",
    BOX_FAILSAFE: "FAILSAFE",
    BOX_AUTOPILOT: "AUTOPILOT",
}


def log(message: str) -> None:
    print(f"[mission] {message}", flush=True)


# ────────────────────────────────────────────────────────────────── the RC


class RcTransmitter(threading.Thread):
    """100 Hz ``rc_packet`` stream.  Stop it and the failsafe trips.

    100 Hz, not the 50 Hz a real link runs at, because the flight controller's
    clock is scaled by ``simRate`` and a single scheduling hiccup on either side
    turns one missed 20 ms frame into a visible RX gap.  An RXLOSS blip while
    the arm switch is high latches ARM_SWITCH and NOT_DISARMED, and the run then
    looks armed over MSP for an instant and never flies.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = RC_PORT) -> None:
        super().__init__(daemon=True)
        self.address = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.channels = [RC_MID, RC_MID, RC_LOW, RC_MID] + [RC_LOW] * 12
        self.running = True
        self.t0 = time.monotonic()

    def set(self, index: int, value: int) -> None:
        self.channels[index] = int(value)

    def run(self) -> None:
        while self.running:
            packet = struct.pack(
                "<d16H", time.monotonic() - self.t0, *(int(v) for v in self.channels)
            )
            try:
                self.socket.sendto(packet, self.address)
            except OSError:
                pass
            time.sleep(0.01)

    def shutdown(self) -> None:
        self.running = False


# ───────────────────────────────────────────────────────────────── the MSP


class Msp:
    """Minimal MSP v1 client over the SITL TCP port."""

    def __init__(self, sock: socket.socket) -> None:
        self.socket = sock
        self.buffer = b""
        self.lock = threading.Lock()

    def request(self, command: int, payload: bytes = b"", timeout: float = 2.0) -> bytes:
        with self.lock:
            frame = struct.pack("<BB", len(payload), command) + payload
            checksum = 0
            for byte in frame:
                checksum ^= byte
            self.socket.sendall(b"$M<" + frame + bytes([checksum]))
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                reply = self._read_frame(command, deadline)
                if reply is not None:
                    return reply
            raise TimeoutError(f"no MSP reply for command {command}")

    def _read_frame(self, want: int, deadline: float) -> bytes | None:
        while time.monotonic() < deadline:
            start = self.buffer.find(b"$M>")
            if start < 0:
                if self.buffer.find(b"$M!") >= 0:
                    raise RuntimeError(f"MSP error frame for command {want}")
                self._fill(deadline)
                continue
            if len(self.buffer) < start + 5:
                self._fill(deadline)
                continue
            size = self.buffer[start + 3]
            command = self.buffer[start + 4]
            end = start + 5 + size + 1
            if len(self.buffer) < end:
                self._fill(deadline)
                continue
            payload = self.buffer[start + 5 : start + 5 + size]
            self.buffer = self.buffer[end:]
            if command == want:
                return payload
        return None

    def _fill(self, deadline: float) -> None:
        self.socket.settimeout(max(0.05, deadline - time.monotonic()))
        try:
            data = self.socket.recv(4096)
            if data:
                self.buffer += data
        except socket.timeout:
            pass


class FlightController:
    """MSP view of the running SITL: modes and arming-disable flags."""

    def __init__(self, host: str = "127.0.0.1", port: int = MSP_PORT, timeout: float = 30.0):
        deadline = time.monotonic() + timeout
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                self.socket = socket.create_connection((host, port), timeout=2.0)
                self.msp = Msp(self.socket)
                self.boxids = list(self.msp.request(MSP_BOXIDS))
                log(f"MSP connected, {len(self.boxids)} boxes")
                return
            except (OSError, TimeoutError, RuntimeError) as exc:
                last_error = exc
                time.sleep(0.5)
        raise RuntimeError(f"could not reach MSP on {host}:{port} — {last_error}")

    def status(self) -> dict:
        payload = self.msp.request(MSP_STATUS)
        mode_flags = struct.unpack_from("<I", payload, 6)[0]
        extra_count = payload[15]
        offset = 16 + extra_count
        arming_flags = struct.unpack_from("<I", payload, offset + 1)[0]
        active = {
            self.boxids[i]
            for i in range(min(32, len(self.boxids)))
            if mode_flags & (1 << i)
        }
        return {"modes": active, "arming_flags": arming_flags}

    def modes(self) -> set[int]:
        return self.status()["modes"]

    def mode_names(self) -> list[str]:
        return sorted(BOX_NAMES.get(b, f"BOX{b}") for b in self.modes())

    def armed(self) -> bool:
        return BOX_ARM in self.modes()

    def calibrate_accelerometer(self) -> None:
        self.msp.request(MSP_ACC_CALIBRATION)

    def close(self) -> None:
        try:
            self.socket.close()
        except OSError:
            pass


# ──────────────────────────────────────────────────────────────── the truth


class TruthListener(threading.Thread):
    """The bridge's ground-truth fan-out: what actually happened."""

    def __init__(self, port: int = TRUTH_PORT) -> None:
        super().__init__(daemon=True)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("127.0.0.1", port))
        self.socket.settimeout(0.5)
        self.running = True
        self.latest: dict | None = None
        self.history: list[dict] = []
        self._lock = threading.Lock()

    def run(self) -> None:
        while self.running:
            try:
                data, _ = self.socket.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                return
            try:
                sample = json.loads(data.decode("ascii"))
            except (UnicodeDecodeError, ValueError):
                continue
            with self._lock:
                self.latest = sample
                self.history.append(sample)

    def snapshot(self) -> list[dict]:
        with self._lock:
            return list(self.history)

    def altitude(self) -> float:
        sample = self.latest
        return float(sample["altitude_m"]) if sample else 0.0

    def heading(self) -> float:
        sample = self.latest
        return float(sample["heading_deg"]) if sample else 0.0

    def east(self) -> float:
        sample = self.latest
        return float(sample["position_ned_m"][1]) if sample else 0.0

    def shutdown(self) -> None:
        self.running = False


def wait_for(description: str, predicate, timeout: float = 25.0, interval: float = 0.2):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            log(f"ok: {description}")
            return value
        time.sleep(interval)
    raise AssertionError(f"timeout waiting for: {description}")


# ────────────────────────────────────────────────────────────── the mission


def fly(args: argparse.Namespace) -> int:
    """Run the flight.  Always writes the logs, pass or fail."""
    events: list[tuple[float, str]] = []
    started = time.monotonic()
    truth = TruthListener(args.truth_port)

    def record(name: str) -> None:
        events.append((time.monotonic() - started, name))
        log(f"event: {name}")

    try:
        return _fly(args, truth, record)
    finally:
        # A failed flight is exactly when the telemetry matters most.
        _write_telemetry(Path(args.telemetry), truth.snapshot())
        _write_events(Path(args.events), events)
        truth.shutdown()


def _fly(args: argparse.Namespace, truth: TruthListener, record) -> int:
    truth.start()
    wait_for(
        "the bridge's ground-truth feed is live",
        lambda: truth.latest is not None,
        timeout=30,
    )

    controller = FlightController(port=args.msp_port)
    rc = RcTransmitter(port=args.rc_port)
    rc.start()
    record("rc_stream_up")

    # The flight controller needs a GPS fix and a settled RX before it will
    # clear its arming-disable flags.
    wait_for(
        "arming flags clear (GPS fix + RX)",
        lambda: controller.status()["arming_flags"] == 0,
        timeout=60,
    )
    record("arming_flags_clear")

    # Recalibrate the accelerometer NOW the FDM feed is live. The boot-time
    # calibration captures a dead feed, and the resulting bias integrates into a
    # phantom vertical velocity that alt-hold then chases into the ground.
    controller.calibrate_accelerometer()
    time.sleep(2.0)
    wait_for(
        "accelerometer recalibration complete",
        lambda: controller.status()["arming_flags"] == 0,
        timeout=25,
    )
    record("acc_calibrated")

    rc.set(CH_AUX3, RC_HIGH)  # ANGLE: self-levelling for the manual segment
    for attempt in range(4):
        rc.set(CH_AUX1, RC_HIGH)  # arm switch, throttle low
        try:
            wait_for("armed", controller.armed, timeout=10)
            # Arming must STICK. An RXLOSS blip disarms and immediately latches
            # ARM_SWITCH + NOT_DISARMED, and a poll that catches the brief armed
            # window sends the rest of the flight chasing a craft that is on the
            # ground with its motors at mincommand.
            time.sleep(2.0)
            if controller.armed():
                break
            log("arming did not stick — the flight controller disarmed itself")
        except AssertionError:
            pass
        status = controller.status()
        log(f"arming disable flags: {arming_flag_names(status['arming_flags'])}")
        if attempt == 3:
            raise AssertionError(
                f"could not arm — arming disable flags "
                f"{arming_flag_names(status['arming_flags'])}"
            )
        # A transient arming-disable at the instant the switch goes high latches
        # ARM_SWITCH until the switch is cycled.
        log("cycling the arm switch")
        rc.set(CH_AUX1, RC_LOW)
        time.sleep(2.0)
    record("armed")

    rc.set(CH_THROTTLE, args.climb_throttle)

    def climbed():
        if not controller.armed():
            raise AssertionError(
                f"disarmed during the climb at {truth.altitude():.2f} m — "
                f"flags {arming_flag_names(controller.status()['arming_flags'])}"
            )
        return truth.altitude() > args.target_altitude_m

    wait_for(f"climbed above {args.target_altitude_m:.1f} m", climbed, timeout=45)
    record("climbed")

    rc.set(CH_AUX2, RC_HIGH)  # ALTHOLD
    wait_for("ALTHOLD engaged", lambda: BOX_ALTHOLD in controller.modes(), timeout=20)
    log(f"modes: {controller.mode_names()}")
    # Centre the throttle into the alt-hold deadband so the hold, not the stick,
    # decides the altitude.
    rc.set(CH_THROTTLE, RC_MID)
    record("althold")

    hold_start = time.monotonic()
    hold_altitudes: list[float] = []
    next_report = 0.0
    # THE PROBES ARE THE POINT OF THE HOLD.
    #
    # A quad hovering undisturbed in a deterministic, perfectly symmetric
    # simulation proves almost nothing about the sign conventions: with no
    # disturbance to amplify, even an INVERTED axis sits at exactly zero. Both
    # probes inject a disturbance the loop has to answer.
    #
    # The roll probe covers the accelerometer and quaternion chain (roll right
    # in ANGLE mode must move the airframe EAST). The yaw probe covers the gyro
    # yaw sign and the vehicle YAML's prop senses — the two things this bridge
    # got wrong on the first try, in opposite directions.
    roll_probe_start = args.hold_seconds / 5.0
    roll_probe_end = roll_probe_start + args.probe_seconds
    yaw_probe_start = args.hold_seconds / 2.0
    yaw_probe_end = yaw_probe_start + args.probe_seconds

    roll_before: float | None = None
    roll_after: float | None = None
    roll_commanded = False
    # The yaw probe is scored on the BODY YAW RATE over its window, not on a
    # heading difference: at the default rate profile a two-second full-stick
    # command turns the airframe well past 180 degrees, and a heading delta
    # wrapped into +/-180 then reports a 220-degree RIGHT turn as 139 degrees
    # LEFT. The rate has no wrap and states the sign directly.
    yaw_window: list[float] = []
    yaw_commanded = False
    yaw_released = False

    while True:
        elapsed = time.monotonic() - hold_start
        if elapsed >= args.hold_seconds:
            break
        hold_altitudes.append(truth.altitude())
        if elapsed >= next_report:
            next_report = elapsed + 5.0
            log(
                f"hold t={elapsed:5.1f} s  altitude {truth.altitude():6.2f} m  "
                f"heading {truth.heading():6.1f} deg"
            )
        if not controller.armed():
            raise AssertionError(
                f"disarmed mid-hold at t={elapsed:.1f} s "
                f"(altitude {truth.altitude():.2f} m)"
            )
        if not roll_commanded and elapsed >= roll_probe_start:
            roll_commanded = True
            roll_before = truth.east()
            rc.set(CH_ROLL, args.probe_stick)  # stick RIGHT = roll right = east
            log(f"roll probe: commanding right from east {roll_before:+.2f} m")
        elif roll_after is None and roll_commanded and elapsed >= roll_probe_end:
            rc.set(CH_ROLL, RC_MID)
            time.sleep(1.5)  # let the attitude loop level off before reading back
            roll_after = truth.east()
            log(f"roll probe: east now {roll_after:+.2f} m")
        elif not yaw_commanded and elapsed >= yaw_probe_start:
            yaw_commanded = True
            rc.set(CH_YAW, args.probe_stick)  # stick RIGHT = nose right = CW
            log(f"yaw probe: commanding right from {truth.heading():.1f} deg")
        elif not yaw_released and yaw_commanded and elapsed >= yaw_probe_end:
            yaw_released = True
            rc.set(CH_YAW, RC_MID)
            log(f"yaw probe: released at {truth.heading():.1f} deg")
        if yaw_commanded and not yaw_released:
            sample = truth.latest
            if sample:
                yaw_window.append(float(sample["omega_body_rad_s"][2]))
        time.sleep(0.25)
    record("hold_complete")

    # Land: drop the throttle, wait for the ground, then disarm on the switch.
    rc.set(CH_AUX2, RC_LOW)  # leave ALTHOLD
    rc.set(CH_THROTTLE, args.descend_throttle)
    wait_for(
        "landed (truth altitude back under 0.5 m)",
        lambda: truth.altitude() < 0.5,
        timeout=90,
    )
    record("landed")

    rc.set(CH_THROTTLE, RC_LOW)
    time.sleep(1.0)
    rc.set(CH_AUX1, RC_LOW)
    wait_for("disarmed", lambda: not controller.armed(), timeout=15)
    record("disarmed")

    rc.shutdown()
    controller.close()

    # ───────────────────────────────────────────────────────── assertions

    samples = truth.snapshot()
    hold_mean = sum(hold_altitudes) / len(hold_altitudes)
    hold_min, hold_max = min(hold_altitudes), max(hold_altitudes)
    peak = max(s["altitude_m"] for s in samples)

    log(f"hold altitude: mean {hold_mean:.2f} m, band {hold_min:.2f}-{hold_max:.2f} m")
    log(f"peak altitude: {peak:.2f} m over {len(samples)} truth samples")

    failures = []
    if hold_mean < 1.0:
        failures.append(f"alt-hold mean {hold_mean:.2f} m is on the ground")
    band = hold_max - hold_min
    if band > args.hold_band_m:
        failures.append(
            f"alt-hold band {band:.2f} m exceeds the {args.hold_band_m:.1f} m limit"
        )

    if roll_before is None or roll_after is None:
        failures.append("the roll probe never ran — raise --hold-seconds")
    else:
        moved = roll_after - roll_before
        log(
            f"roll probe: commanded RIGHT, east {roll_before:+.2f} -> "
            f"{roll_after:+.2f} m ({moved:+.2f} m)"
        )
        if moved < args.probe_min_east_m:
            failures.append(
                f"a commanded right roll moved the airframe {moved:+.2f} m east "
                f"— a negative number inverts the roll axis (check the "
                f"accelerometer y sign and the quaternion conversion); a "
                f"near-zero one means the roll command reached no rotor"
            )

    if not yaw_window:
        failures.append("the yaw probe never ran — raise --hold-seconds")
    else:
        mean_rate = math.degrees(sum(yaw_window) / len(yaw_window))
        log(
            f"yaw probe: commanded RIGHT, mean body yaw rate "
            f"{mean_rate:+.1f} deg/s over {len(yaw_window)} samples"
        )
        if mean_rate < args.probe_min_yaw_rate_deg:
            failures.append(
                f"a commanded right yaw produced {mean_rate:+.1f} deg/s of body "
                f"yaw — the gyro yaw sign or the vehicle YAML's rotor_index "
                f"mapping disagrees with Betaflight's mixer (negative inverts "
                f"the whole chain; near-zero means the rotors' reaction torques "
                f"cancel)"
            )

    # A yaw loop closed with the wrong sign does not merely turn the wrong way:
    # it saturates the mixer and the rate grows without bound. Measured
    # 2026-08-30 on the inverted version: 45 rad/s and still climbing.
    peak_yaw_rate = max(abs(s["omega_body_rad_s"][2]) for s in samples)
    log(f"peak body yaw rate over the flight: {peak_yaw_rate:.2f} rad/s")
    if peak_yaw_rate > args.probe_max_yaw_rate:
        failures.append(
            f"peak yaw rate {peak_yaw_rate:.1f} rad/s — the yaw loop is POSITIVE "
            f"feedback, so the gyro yaw sign is inverted"
        )

    # The propulsion lane: what the FMU is actually being asked for, and whether
    # it was asked for it inside the operating envelope the export declares.
    flying = [s for s in samples if max(s["pwm_us"], default=0) > 1100]
    if flying:
        soc = [s["battery_soc"] for s in samples if s["battery_soc"] is not None]
        volts = [s["voltage_bus_V"] for s in flying if s["voltage_bus_V"] is not None]
        amps = [s["current_bus_A"] for s in flying if s["current_bus_A"] is not None]
        in_envelope = sum(1 for s in flying if s["all_in_envelope"])
        fraction = in_envelope / len(flying)
        if soc:
            log(f"battery: SOC {soc[0]:.4f} -> {soc[-1]:.4f}")
        if volts and amps:
            log(
                f"bus: {min(volts):.2f}-{max(volts):.2f} V, "
                f"{min(amps):.1f}-{max(amps):.1f} A"
            )
        log(f"in FMU envelope while flying: {100 * fraction:.1f}%")
        if fraction < args.min_envelope_fraction:
            failures.append(
                f"only {100 * fraction:.1f}% of the flying frames were inside the "
                f"FMU's envelope — the airframe is being flown outside what the "
                f"export covers, so the propulsion numbers are extrapolation"
            )

    if failures:
        for failure in failures:
            log(f"FAIL: {failure}")
        return 1
    log("PASS: armed, climbed, held altitude, landed and disarmed")
    return 0


def _write_telemetry(path: Path, samples: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "t_s", "north_m", "east_m", "down_m", "altitude_m",
                "vn_m_s", "ve_m_s", "vd_m_s", "heading_deg",
                "p_rad_s", "q_rad_s", "r_rad_s",
                "pwm_1", "pwm_2", "pwm_3", "pwm_4",
                "voltage_bus_V", "current_bus_A", "battery_soc", "all_in_envelope",
            ]
        )
        for sample in samples:
            pwm = list(sample.get("pwm_us", []))[:4]
            pwm += [""] * (4 - len(pwm))
            writer.writerow(
                [f"{sample['t']:.4f}"]
                + [f"{v:.5f}" for v in sample["position_ned_m"]]
                + [f"{sample['altitude_m']:.5f}"]
                + [f"{v:.5f}" for v in sample["velocity_ned_m_s"]]
                + [f"{sample['heading_deg']:.3f}"]
                + [f"{v:.6f}" for v in sample["omega_body_rad_s"]]
                + pwm
                + [
                    "" if sample.get(key) is None else sample[key]
                    for key in ("voltage_bus_V", "current_bus_A", "battery_soc")
                ]
                + ["" if sample.get("all_in_envelope") is None
                   else int(sample["all_in_envelope"])]
            )
    log(f"wrote {len(samples)} telemetry rows to {path}")


def _write_events(path: Path, events: list[tuple[float, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["wall_s", "event"])
        for when, name in events:
            writer.writerow([f"{when:.3f}", name])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--rc-port", type=int, default=RC_PORT)
    parser.add_argument("--msp-port", type=int, default=MSP_PORT)
    parser.add_argument("--truth-port", type=int, default=TRUTH_PORT)
    parser.add_argument("--target-altitude-m", type=float, default=3.0)
    parser.add_argument("--hold-seconds", type=float, default=60.0)
    parser.add_argument(
        "--hold-band-m",
        type=float,
        default=6.0,
        help="widest peak-to-peak altitude excursion the hold may show",
    )
    parser.add_argument(
        "--probe-seconds",
        type=float,
        default=2.0,
        help="how long each mid-hold right-stick probe is held",
    )
    parser.add_argument("--probe-stick", type=int, default=1700)
    parser.add_argument(
        "--probe-min-east-m",
        type=float,
        default=0.5,
        help="least the airframe must move EAST during the roll probe",
    )
    parser.add_argument(
        "--probe-min-yaw-rate-deg",
        type=float,
        default=20.0,
        help="least mean body yaw rate (deg/s, nose right) during the yaw probe",
    )
    parser.add_argument(
        "--probe-max-yaw-rate",
        type=float,
        default=8.0,
        help="peak yaw rate (rad/s) above which the yaw loop is diverging",
    )
    parser.add_argument(
        "--min-envelope-fraction",
        type=float,
        default=0.90,
        help="least fraction of flying frames that must be inside the FMU envelope",
    )
    parser.add_argument("--climb-throttle", type=int, default=1650)
    parser.add_argument("--descend-throttle", type=int, default=1250)
    parser.add_argument("--telemetry", default="mission_telemetry.csv")
    parser.add_argument("--events", default="mission_events.csv")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return fly(args)
    except AssertionError as exc:
        log(f"FAIL: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
