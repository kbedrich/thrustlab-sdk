"""Render a recorded FMU mission into an animated flight-report video.

The same recordings :mod:`plot_mission` reads — the bridge's per-rotor CSV and
fly_mission.py's telemetry/events — become a time-compressed replay: the
mission track draws itself colored by electrical power while live panels show
per-rotor speed, bus voltage and current, power and state of charge, with the
autopilot's mission phases called out as they happen.

Usage: python render_mission_video.py <data_dir> <out_dir> [--speed 4]
                                      [--fps 30] [--weight-n 11.77]

Frames go to <out_dir>/frames/frame_%05d.png. If ffmpeg is on PATH the video
is encoded to <out_dir>/fmu_mission_replay.mp4 automatically; otherwise the
exact ffmpeg command is printed so you can run it wherever ffmpeg lives.
"""
import argparse
import csv
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon

# Gruvbox Soft (dark) — frontend/src/app/gruvbox-soft.css
BG = "#111111"
SURFACE = "#1b1b1b"
TEXT = "#f5efe2"
MUTED = "#bdb0a0"
AXIS = "#d4be98"
GRID = (1.0, 1.0, 1.0, 0.10)
ORANGE = "#e78a4e"
BLUE = "#7daea3"
GREEN = "#a9b665"
PURPLE = "#d3869b"
AQUA = "#89b482"
YELLOW = "#d8a657"
RED = "#ea6962"
ROTORS = [ORANGE, BLUE, GREEN, PURPLE, AQUA, YELLOW, RED]

M_PER_DEG_LAT = 111320.0
COMET_SECONDS = 9.0  # length of the glowing trail behind the vehicle
DRAW_HZ = 20.0  # time-series draw rate after decimation
INTRO_S = 2.0
OUTRO_S = 2.5


def style():
    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": BG,
            "savefig.facecolor": BG,
            "text.color": TEXT,
            "axes.edgecolor": AXIS,
            "axes.labelcolor": MUTED,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "font.family": "DejaVu Sans",
            "axes.titlesize": 11,
            "axes.titlecolor": TEXT,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "legend.frameon": False,
            "legend.labelcolor": MUTED,
        }
    )


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def col(rows, name, default=np.nan):
    out = np.empty(len(rows))
    for i, r in enumerate(rows):
        v = r.get(name, "")
        out[i] = float(v) if v not in ("", None) else default
    return out


def smooth(x, w):
    # Normalise by the actual kernel overlap so the edges are averaged over
    # the samples that exist instead of being dragged toward zero.
    kernel = np.ones(w)
    return np.convolve(x, kernel, mode="same") / np.convolve(
        np.ones_like(x), kernel, mode="same"
    )


def phase_labels(events, t0, t1):
    """(t, label) mission-phase callouts from fly_mission's event log.

    ArduPilot announces each mission item as ``Mission: <n> <Name>``; those
    names plus flight-mode changes are the replay's phase captions.
    """
    pretty = {
        "Takeoff": "TAKEOFF",
        "ChangeSpeed": None,  # speed changes precede the leg they shape — skip
        "WP": "WAYPOINT LEG",
        "LoitTurns": "LOITER TURNS",
        "RTL": "RETURN TO LAUNCH",
        "Land": "LANDING",
        "VTOLTakeoff": "VTOL TAKEOFF",
        "VTOLLand": "VTOL LANDING",
    }
    # QuadPlane narrates its transitions as statustexts, not mission items or
    # mode changes — without these the caption reads AUTO for the whole
    # circuit and the hand-over to the wing is invisible.
    transitions = [
        (re.compile(r"^Transition started"), "TRANSITIONING"),
        (re.compile(r"^Transition (FW )?done"), "WING-BORNE FLIGHT"),
        (re.compile(r"^VTOL approach"), "VTOL APPROACH"),
        (re.compile(r"^Land complete"), "LANDED"),
    ]
    out = []
    for e in events:
        ts = float(e["t_s"])
        if ts < t0 - 1.0 or ts > t1:
            continue
        if e["kind"] == "mode" and e["detail"] not in ("GUIDED",):
            out.append((ts, e["detail"]))
        elif e["kind"] == "text":
            m = re.match(r"Mission: \d+ (\w+)", e["detail"])
            if m:
                label = pretty.get(m.group(1), m.group(1).upper())
                if label:
                    out.append((ts, label))
                continue
            for pattern, label in transitions:
                if pattern.match(e["detail"]):
                    out.append((ts, label))
                    break
    # Collapse consecutive duplicates so a caption only changes when the
    # phase does.
    collapsed = []
    for ts, label in sorted(out):
        if not collapsed or collapsed[-1][1] != label:
            collapsed.append((ts, label))
    return collapsed


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("data_dir", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--speed", type=float, default=4.0, help="time compression")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument(
        "--weight-n", type=float, default=11.77,
        help="vehicle weight (N) — only for takeoff-based clock alignment",
    )
    args = ap.parse_args()
    frames_dir = args.out_dir / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    style()

    b = read_csv(args.data_dir / "mission_rpm_log.csv")
    t_rows = read_csv(args.data_dir / "mission_telemetry.csv")
    events = read_csv(args.data_dir / "mission_events.csv")

    n_rotors = sum(1 for k in b[0] if k.startswith("rpm_"))
    bt = col(b, "timestamp_s")
    thrust = sum(col(b, f"thrust_N_{i}") for i in range(n_rotors))
    rpm = [col(b, f"rpm_{i}") for i in range(n_rotors)]
    vbus = col(b, "voltage_bus_V")
    ibus = col(b, "current_bus_A")
    soc = col(b, "battery_soc")
    in_env = [col(b, f"in_envelope_{i}", default=1.0) for i in range(n_rotors)]
    power = vbus * ibus

    tt = col(t_rows, "t_s")
    alt = col(t_rows, "alt_rel_m")
    gs = col(t_rows, "groundspeed_m_s")
    lat = col(t_rows, "lat")
    lon = col(t_rows, "lon")
    yaw = np.radians(col(t_rows, "yaw_deg"))

    # Clock alignment on the takeoff event, exactly as plot_mission.py does.
    b_take = bt[np.argmax(thrust > 1.05 * args.weight_n)]
    t_take = tt[np.argmax(alt > 1.0)]
    bt = bt + (t_take - b_take)

    # Smooth the 400 Hz bridge channels once, globally, then decimate to the
    # draw rate. Post-kill frames (bus collapsed) are cut by the vbus mask.
    w = 25
    bm = vbus > 20.0
    rpm_s = [smooth(r, w)[bm] for r in rpm]
    vbus_s = smooth(vbus, w)[bm]
    ibus_s = smooth(ibus, w)[bm]
    power_s = smooth(power, w)[bm]
    soc_s = smooth(soc, w)[bm]
    # A rotor the autopilot has STOPPED (a lift motor in wing-borne flight)
    # produces no meaningful forces, so its envelope flag is vacuous — the
    # chip judges only rotors that are actually spinning, and says so.
    env_arr = np.array([e[bm] for e in in_env]) > 0.5
    spin_arr = np.array([r[bm] for r in rpm_s]) > 300.0
    env_ok = np.all(env_arr | ~spin_arr, axis=0)
    n_stopped = np.sum(~spin_arr, axis=0)
    btm = bt[bm]

    # Stop 1.5 s before the log ends so the motor-kill transient at disarm
    # never becomes the video's closing readout.
    t0, t1 = t_take - 4.0, tt[-1] - 1.5
    step = max(1, int(round(1.0 / (DRAW_HZ * np.median(np.diff(btm))))))
    bd = slice(None, None, step)
    btd, rpmd = btm[bd], [r[bd] for r in rpm_s]
    vbusd, ibusd, powerd, socd = vbus_s[bd], ibus_s[bd], power_s[bd], soc_s[bd]

    east = (lon - lon[0]) * M_PER_DEG_LAT * math.cos(math.radians(lat[0]))
    north = (lat - lat[0]) * M_PER_DEG_LAT
    p_at_t = np.interp(tt, btm, power_s)
    phases = phase_labels(events, t0, t1)

    # Every displayed clock and axis is takeoff-relative; the raw log times
    # stay untouched for lookups.
    btd_r, tt_r = btd - t_take, tt - t_take
    x0, x1 = t0 - t_take, t1 - t_take
    win_b = (btd >= t0) & (btd <= t1)
    win_t = (tt >= t0) & (tt <= t1)

    def lims(x, pad=0.06, floor=None):
        # nan-aware: telemetry rows recorded before every stream is up carry
        # empty fields, which col() reads as NaN.
        lo, hi = float(np.nanmin(x)), float(np.nanmax(x))
        span = (hi - lo) or 1.0
        lo, hi = lo - pad * span, hi + pad * span
        return (max(lo, floor) if floor is not None else lo, hi)

    # ------------------------------------------------------------- the figure
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.text(0.035, 0.955, "ThrustLab FMU  ·  ArduPilot SITL",
             fontsize=21, color=TEXT, weight="bold")
    fig.text(0.035, 0.925,
             "the exported powertrain flying a real mission — "
             "per-rotor thrust, battery sag and state of charge from the .fmu",
             fontsize=12, color=MUTED)
    fig.text(0.975, 0.955, f"{args.speed:g}× speed", fontsize=12,
             color=BG, ha="right",
             bbox=dict(boxstyle="round,pad=0.35", fc=AXIS, ec="none"))

    ax = fig.add_axes([0.035, 0.06, 0.46, 0.80])
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel("east (m)")
    ax.set_ylabel("north (m)")
    ax.set_xlim(*lims(east[win_t], pad=0.10))
    ax.set_ylim(*lims(north[win_t], pad=0.10))
    ax.plot(east[win_t], north[win_t], color=MUTED, lw=1.0, alpha=0.22)
    ax.plot(0, 0, marker="^", ms=10, color=TEXT)
    ax.annotate("launch", (0, 0), xytext=(9, -4), textcoords="offset points",
                color=MUTED, fontsize=9)

    comet = LineCollection([], linewidths=3.5, capstyle="round", zorder=4)
    comet.set_cmap("plasma")
    comet.set_norm(plt.Normalize(0.0, float(np.percentile(powerd[win_b], 99))))
    ax.add_collection(comet)
    head = ax.plot([], [], marker="o", ms=5, color=TEXT, zorder=6)[0]
    vehicle = Polygon(np.zeros((3, 2)), closed=True, fc=TEXT, ec=BG, lw=0.6,
                      zorder=5)
    ax.add_patch(vehicle)

    clock = ax.text(0.02, 0.975, "", transform=ax.transAxes, fontsize=13,
                    color=TEXT, family="DejaVu Sans Mono", va="top")
    phase = ax.text(0.02, 0.925, "", transform=ax.transAxes, fontsize=15,
                    color=YELLOW, weight="bold", va="top")
    env_chip = ax.text(0.02, 0.02, "", transform=ax.transAxes, fontsize=10,
                       color=BG, va="bottom",
                       bbox=dict(boxstyle="round,pad=0.3", fc=GREEN, ec="none"))
    sm = plt.cm.ScalarMappable(norm=comet.norm, cmap=comet.cmap)
    cb = fig.colorbar(sm, ax=ax, orientation="horizontal", pad=0.075,
                      fraction=0.035, aspect=45)
    cb.set_label("electrical power (W)", color=MUTED, fontsize=9)
    cb.ax.tick_params(color=MUTED, labelcolor=MUTED, labelsize=8)
    cb.outline.set_edgecolor(AXIS)

    # Headline readouts above the right-hand column.
    readouts = {}
    for x, key, label, color in (
        (0.585, "power", "power", ORANGE),
        (0.72, "vbus", "bus voltage", YELLOW),
        (0.845, "soc", "state of charge", AQUA),
    ):
        readouts[key] = fig.text(x, 0.885, "", fontsize=25, color=color,
                                 family="DejaVu Sans Mono", weight="bold")
        fig.text(x, 0.862, label, fontsize=10, color=MUTED)

    panels = []
    specs = [
        ("altitude (m) / groundspeed (m/s)", 0.645),
        ("rotor speed (rpm)", 0.455),
        ("bus voltage (V) / current (A)", 0.265),
        ("electrical power (W) / state of charge (%)", 0.075),
    ]
    for title, y in specs:
        a = fig.add_axes([0.585, y, 0.36, 0.155])
        a.set_xlim(x0, x1)
        a.set_title(title, loc="left", fontsize=10, color=MUTED, pad=3)
        a.tick_params(labelsize=8)
        if y != specs[-1][1]:
            a.set_xticklabels([])
        panels.append(a)
    panels[-1].set_xlabel("time since takeoff (s)", fontsize=9)

    def twin(a):
        t = a.twinx()
        t.grid(False)
        t.tick_params(labelsize=8, colors=MUTED)
        t.set_xlim(x0, x1)
        return t

    aline = panels[0].plot([], [], color=BLUE, lw=1.5)[0]
    gtwin = twin(panels[0])
    gline = gtwin.plot([], [], color=MUTED, lw=1.0, alpha=0.85)[0]
    panels[0].set_ylim(*lims(alt[win_t], floor=0.0))
    gtwin.set_ylim(*lims(gs[win_t], floor=0.0))
    rpm_lines = [
        panels[1].plot([], [], color=ROTORS[i % len(ROTORS)], lw=1.2,
                       label=f"rotor {i}")[0]
        for i in range(n_rotors)
    ]
    panels[1].legend(ncol=min(n_rotors, 4), fontsize=7, loc="lower right")
    panels[1].set_ylim(0, float(np.max([r[win_b] for r in rpmd])) * 1.12)
    vline = panels[2].plot([], [], color=YELLOW, lw=1.4)[0]
    itwin = twin(panels[2])
    iline = itwin.plot([], [], color=RED, lw=1.1, alpha=0.9)[0]
    panels[2].set_ylim(*lims(vbusd[win_b]))
    itwin.set_ylim(*lims(ibusd[win_b], floor=0.0))
    pline = panels[3].plot([], [], color=ORANGE, lw=1.3)[0]
    stwin = twin(panels[3])
    sline = stwin.plot([], [], color=AQUA, lw=1.6)[0]
    panels[3].set_ylim(*lims(powerd[win_b], floor=0.0))
    stwin.set_ylim(*lims(socd[win_b] * 100.0))
    cursors = [a.axvline(x0, color=MUTED, lw=0.8, alpha=0.6) for a in panels]

    overlay = fig.text(0.5, 0.5, "", fontsize=30, color=TEXT, ha="center",
                       va="center", weight="bold",
                       bbox=dict(boxstyle="round,pad=0.8", fc=SURFACE,
                                 ec=AXIS, alpha=0.92))

    # -------------------------------------------------------------- rendering
    n_mission = int(round((t1 - t0) / args.speed * args.fps))
    n_intro, n_outro = int(INTRO_S * args.fps), int(OUTRO_S * args.fps)
    tri = np.array([[7.0, 0.0], [-4.5, 4.0], [-4.5, -4.0]])  # display points

    def draw(now):
        k = int(np.searchsorted(btd, now))
        j = int(np.searchsorted(tt, now))
        for i, line in enumerate(rpm_lines):
            line.set_data(btd_r[:k], rpmd[i][:k])
        vline.set_data(btd_r[:k], vbusd[:k])
        iline.set_data(btd_r[:k], ibusd[:k])
        pline.set_data(btd_r[:k], powerd[:k])
        sline.set_data(btd_r[:k], socd[:k] * 100.0)
        aline.set_data(tt_r[:j], alt[:j])
        gline.set_data(tt_r[:j], gs[:j])
        for c in cursors:
            c.set_xdata([now - t_take, now - t_take])

        j0 = int(np.searchsorted(tt, now - COMET_SECONDS))
        if j - j0 >= 2:
            pts = np.column_stack([east[j0:j], north[j0:j]])
            comet.set_segments(np.stack([pts[:-1], pts[1:]], axis=1))
            comet.set_array(p_at_t[j0 + 1: j])
        if j >= 1:
            jj = j - 1
            head.set_data([east[jj]], [north[jj]])
            heading = yaw[jj]
            # Yaw is a compass bearing (0 = north, CW); the track plot is
            # east-x / north-y, so bearing b maps to plot angle pi/2 - b.
            a = math.pi / 2 - heading
            rot = np.array([[math.cos(a), -math.sin(a)],
                            [math.sin(a), math.cos(a)]])
            span = max(np.ptp(east[win_t]), np.ptp(north[win_t]), 1.0)
            verts = tri @ rot.T * (span / 260.0)
            vehicle.set_xy(verts + np.array([east[jj], north[jj]]))

        kb = min(max(k, 1), len(btd)) - 1
        readouts["power"].set_text(f"{powerd[kb]:5.0f} W")
        readouts["vbus"].set_text(f"{vbusd[kb]:5.2f} V")
        readouts["soc"].set_text(f"{socd[kb] * 100:4.1f} %")
        if now >= t_take:
            kf = min(max(int(np.searchsorted(btm, now)), 1), len(env_ok)) - 1
            ok = bool(env_ok[kf])
            stopped = int(n_stopped[kf])
            env_chip.set_visible(True)
            if ok and stopped:
                env_chip.set_text(f"envelope OK · {stopped} rotor stopped")
            elif ok:
                env_chip.set_text("envelope OK")
            else:
                env_chip.set_text("OUT OF ENVELOPE")
            env_chip.get_bbox_patch().set_facecolor(GREEN if ok else RED)
        else:
            env_chip.set_visible(False)

        clock.set_text(f"t = {max(now - t_take, 0.0):6.1f} s")
        current = ""
        for ts, label in phases:
            if ts <= now:
                current = label
        phase.set_text(current)

    frame = 0

    def save():
        nonlocal frame
        fig.savefig(frames_dir / f"frame_{frame:05d}.png")
        frame += 1

    draw(t0)
    overlay.set_text("Your powertrain.\nA real autopilot.")
    for _ in range(n_intro):
        save()
    overlay.set_text("")
    for i in range(n_mission + 1):
        draw(t0 + (t1 - t0) * i / n_mission)
        if i % (10 * args.fps) == 0:
            print(f"  frame {frame}/{n_intro + n_mission + n_outro}", flush=True)
        save()
    overlay.set_text("ThrustLab · FMI 3.0 powertrain export")
    for _ in range(n_outro):
        save()
    plt.close(fig)
    print(f"wrote {frame} frames to {frames_dir}")

    out_mp4 = args.out_dir / "fmu_mission_replay.mp4"
    encode = [
        "ffmpeg", "-y", "-framerate", str(args.fps),
        "-i", str(frames_dir / "frame_%05d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        "-movflags", "+faststart", str(out_mp4),
    ]
    if shutil.which("ffmpeg"):
        subprocess.run(encode, check=True)
        print(f"encoded {out_mp4}")
    else:
        print("ffmpeg not on PATH; encode with:")
        print("  " + " ".join(encode))


if __name__ == "__main__":
    main()
