"""Render a recorded FMU mission into flight-report PNGs.

Reads the bridge's per-rotor CSV (FMU truth: rpm, thrust, bus V/I, SOC) and
the mission telemetry/events CSVs written by fly_mission.py, aligns the two
clocks on the takeoff event, and renders three figures:

  fmu_mission_track.png       top-down track colored by electrical power + altitude band
  fmu_mission_timeseries.png  the powertrain story over time (rpm, V/I, power, SOC)
  fmu_mission_loiter.png      loiter close-up: per-rotor rpm split vs roll

Usage: python plot_mission.py <data_dir> <out_dir>
<data_dir> holds mission_rpm_log.csv (from the bridge's --rpm-log),
mission_telemetry.csv and mission_events.csv (from fly_mission.py).
"""
import csv
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

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
ROTORS = [ORANGE, BLUE, GREEN, PURPLE]

# Your vehicle's weight in newtons (mass_kg * 9.81) — used only to detect
# takeoff in the bridge log for clock alignment between the two recordings.
WEIGHT_N = 11.77
M_PER_DEG_LAT = 111320.0


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
        rows = list(csv.DictReader(f))
    return rows


def col(rows, name, default=np.nan):
    out = np.empty(len(rows))
    for i, r in enumerate(rows):
        v = r.get(name, "")
        out[i] = float(v) if v not in ("", None) else default
    return out


def main():
    data = Path(sys.argv[1])
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    style()

    b = read_csv(data / "mission_rpm_log.csv")
    t_rows = read_csv(data / "mission_telemetry.csv")
    events = read_csv(data / "mission_events.csv")

    n_rotors = sum(1 for k in b[0] if k.startswith("rpm_"))
    bt = col(b, "timestamp_s")
    thrust = sum(col(b, f"thrust_N_{i}") for i in range(n_rotors))
    rpm = [col(b, f"rpm_{i}") for i in range(n_rotors)]
    vbus = col(b, "voltage_bus_V")
    ibus = col(b, "current_bus_A")
    soc = col(b, "battery_soc")
    power = vbus * ibus

    tt = col(t_rows, "t_s")
    alt = col(t_rows, "alt_rel_m")
    gs = col(t_rows, "groundspeed_m_s")
    lat = col(t_rows, "lat")
    lon = col(t_rows, "lon")
    roll = col(t_rows, "roll_deg")

    # ---- clock alignment: takeoff (bridge thrust > weight) vs (alt > 1 m) ----
    b_take = bt[np.argmax(thrust > 1.05 * WEIGHT_N)]
    t_take = tt[np.argmax(alt > 1.0)]
    bt = bt + (t_take - b_take)
    print(f"clock offset applied: {t_take - b_take:+.2f} s")

    # Smooth the 400 Hz bridge channels ONCE, globally, before any windowing —
    # smoothing inside a window leaves edge artifacts at its boundaries.
    def smooth(x, w=9):
        return np.convolve(x, np.ones(w) / w, mode="same")

    rpm_s = [smooth(r) for r in rpm]
    vbus_s = smooth(vbus)
    ibus_s = smooth(ibus)
    power_s = smooth(power)
    soc_s = smooth(soc)

    # Flight window: a little pre-takeoff ramp, ending at the telemetry end;
    # spool-up and post-kill frames (bus collapsed / negative current) are cut.
    t0, t1 = t_take - 4.0, tt[-1]
    bm = (bt >= t0) & (bt <= t1) & (vbus > 20.0)
    tm = (tt >= t0) & (tt <= t1)

    def dec(x, k=20):
        return x[bm][::k]

    bt_d = bt[bm][::20]
    modes = [(float(e["t_s"]), e["detail"]) for e in events if e["kind"] == "mode"]
    wps = [(float(e["t_s"]), int(e["detail"])) for e in events if e["kind"] == "wp"]

    def mode_lines(ax, label_y=None):
        for ts, name in modes:
            if ts < t0 or ts > t1 or name in ("GUIDED",):
                continue
            ax.axvline(ts, color=MUTED, lw=0.7, alpha=0.5, ls=(0, (4, 3)))
            if label_y is not None:
                ax.annotate(
                    name, (ts, label_y), color=MUTED, fontsize=7.5,
                    xytext=(3, 0), textcoords="offset points",
                )

    # ================= Figure 1: track + altitude =================
    east = (lon - lon[0]) * M_PER_DEG_LAT * math.cos(math.radians(lat[0]))
    north = (lat - lat[0]) * M_PER_DEG_LAT
    p_at_t = np.interp(tt, bt[bm], power_s[bm])

    fig = plt.figure(figsize=(8.0, 9.0))
    gs_ = fig.add_gridspec(2, 1, height_ratios=[2.4, 1.0], hspace=0.28)
    ax = fig.add_subplot(gs_[0])
    sc = ax.scatter(east[tm], north[tm], c=np.clip(p_at_t[tm], 0, None), s=7, cmap="plasma", lw=0)
    ax.plot(0, 0, marker="^", ms=9, color=TEXT)
    ax.annotate("launch", (0, 0), xytext=(8, -4), textcoords="offset points",
                color=MUTED, fontsize=8)
    ax.set_aspect("equal", adjustable="datalim")
    ax.set_xlabel("east (m)")
    ax.set_ylabel("north (m)")
    ax.set_title("Mission track — colored by electrical power")
    cb = fig.colorbar(sc, ax=ax, pad=0.02, fraction=0.04)
    cb.set_label("power (W)", color=MUTED)
    cb.ax.yaxis.set_tick_params(color=MUTED)
    plt.setp(cb.ax.get_yticklabels(), color=MUTED)
    cb.outline.set_edgecolor(AXIS)

    ax2 = fig.add_subplot(gs_[1])
    ax2.fill_between(tt[tm], 0, alt[tm], color=BLUE, alpha=0.25, lw=0)
    ax2.plot(tt[tm], alt[tm], color=BLUE, lw=1.6)
    mode_lines(ax2, label_y=max(alt[tm]) * 0.86)
    ax2.set_xlabel("mission time (s)")
    ax2.set_ylabel("altitude (m)")
    fig.suptitle(
        "ThrustLab FMU · ArduPilot SITL — the exported powertrain flying a real mission",
        color=TEXT, fontsize=12.5, y=0.985,
    )
    fig.savefig(out / "fmu_mission_track.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # ================= Figure 2: powertrain time series =================
    fig, axes = plt.subplots(4, 1, figsize=(9.6, 9.4), sharex=True)
    fig.subplots_adjust(hspace=0.16)

    a = axes[0]
    a.plot(tt[tm], alt[tm], color=BLUE, lw=1.5, label="altitude (m)")
    a.set_ylabel("altitude (m)")
    ag = a.twinx()
    ag.plot(tt[tm], gs[tm], color=MUTED, lw=1.1, alpha=0.8, label="groundspeed (m/s)")
    ag.set_ylabel("groundspeed (m/s)", color=MUTED)
    ag.grid(False)
    ag.spines["right"].set_visible(True)
    mode_lines(a, label_y=max(alt[tm]) * 0.9)
    a.set_title("Flight profile")

    a = axes[1]
    for i in range(n_rotors):
        a.plot(bt_d, dec(rpm_s[i]), color=ROTORS[i % len(ROTORS)], lw=1.1, label=f"rotor {i}")
    a.set_ylabel("rotor speed (rpm)")
    a.legend(ncol=4, fontsize=8, loc="lower right")
    a.set_title("Per-rotor speed — FMU state, integrated from torque imbalance")

    a = axes[2]
    a.plot(bt_d, dec(vbus_s), color=YELLOW, lw=1.4, label="bus voltage (V)")
    a.set_ylabel("bus voltage (V)", color=YELLOW)
    ai = a.twinx()
    ai.plot(bt_d, dec(ibus_s), color=RED, lw=1.1, alpha=0.9, label="bus current (A)")
    ai.set_ylabel("bus current (A)", color=RED)
    ai.grid(False)
    ai.spines["right"].set_visible(True)
    a.set_title("Battery under load — sag and recovery from the pack surface")

    a = axes[3]
    a.plot(bt_d, dec(power_s), color=ORANGE, lw=1.3, label="electrical power (W)")
    a.set_ylabel("power (W)", color=ORANGE)
    asoc = a.twinx()
    asoc.plot(bt_d, dec(soc_s) * 100.0, color=AQUA, lw=1.4)
    asoc.set_ylabel("state of charge (%)", color=AQUA)
    asoc.grid(False)
    asoc.spines["right"].set_visible(True)
    a.set_xlabel("mission time (s)")
    a.set_title("Energy — power draw and state of charge")

    fig.suptitle(
        "ThrustLab FMU outputs over one mission — every line is the exported model",
        color=TEXT, fontsize=12.5, y=0.945,
    )
    fig.savefig(out / "fmu_mission_timeseries.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    # ================= Figure 3: loiter close-up =================
    lo_wp = [ts for ts, seq in wps if seq == 5]
    lo_end = [ts for ts, seq in wps if seq == 7]
    w1 = (lo_end[0] + 12.0) if lo_end else t0 + (t1 - t0) * 0.75
    w0 = max(lo_wp[0] - 2.0, w1 - 75.0) if lo_wp else w1 - 75.0
    bw = (bt >= w0) & (bt <= w1) & (vbus > 20.0)
    tw = (tt >= w0) & (tt <= w1)

    fig, axes = plt.subplots(2, 1, figsize=(9.6, 5.6), sharex=True)
    fig.subplots_adjust(hspace=0.14)
    a = axes[0]
    for i in range(n_rotors):
        a.plot(bt[bw][::8], rpm_s[i][bw][::8],
               color=ROTORS[i % len(ROTORS)], lw=1.2, label=f"rotor {i}")
    a.set_ylabel("rotor speed (rpm)")
    a.legend(ncol=4, fontsize=8, loc="upper right")
    a.set_title("Loiter and exit — the mixer splits the rotors, the FMU answers per rotor")
    a2 = axes[1]
    a2.plot(tt[tw], roll[tw], color=PURPLE, lw=1.3)
    a2.set_ylabel("roll (deg)")
    a2.set_xlabel("mission time (s)")
    fig.savefig(out / "fmu_mission_loiter.png", dpi=180, bbox_inches="tight")
    plt.close(fig)

    print(f"wrote 3 figures to {out}")


if __name__ == "__main__":
    main()
