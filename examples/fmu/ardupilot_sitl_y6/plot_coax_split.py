"""The coax figure: what the lower rotor does inside the upper's wake.

Reads the bridge's per-rotor CSV from a Y6 mission (three contra-rotating
stacks) and renders one two-panel figure:

  fmu_y6_coax_split.png   top: per-stack rotor speed, upper solid / lower
                          dashed; bottom: lower/upper thrust share per stack.

The generic flight report (track, powertrain time series) comes from
../ardupilot_sitl/plot_mission.py — this script only adds what a coax stack
uniquely shows: the lower rotor spinning harder for less thrust, because it
flies in the upper rotor's induced flow. Both numbers come straight from the
FMU's per-rotor outputs; the autopilot never sees them.

Usage: python plot_coax_split.py <data_dir> <out_dir> [--weight-n 15.2]
"""
import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Gruvbox Soft (dark) — frontend/src/app/gruvbox-soft.css
BG = "#111111"
TEXT = "#f5efe2"
MUTED = "#bdb0a0"
AXIS = "#d4be98"
GRID = (1.0, 1.0, 1.0, 0.10)
STACKS = ["#e78a4e", "#7daea3", "#a9b665"]  # right-front, rear, left-front
STACK_NAMES = ["right-front", "rear", "left-front"]


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def col(rows, name):
    return np.array([float(r[name]) for r in rows])


def smooth(x, w=25):
    kernel = np.ones(w)
    return np.convolve(x, kernel, mode="same") / np.convolve(
        np.ones_like(x), kernel, mode="same"
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("data_dir", type=Path)
    ap.add_argument("out_dir", type=Path)
    ap.add_argument("--weight-n", type=float, default=15.2,
                    help="vehicle weight (N), for takeoff detection")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
        "text.color": TEXT, "axes.edgecolor": AXIS, "axes.labelcolor": MUTED,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
        "grid.color": GRID, "font.family": "DejaVu Sans",
        "axes.titlesize": 11, "axes.titlecolor": TEXT,
        "axes.spines.top": False, "axes.spines.right": False,
        "legend.frameon": False, "legend.labelcolor": MUTED,
    })

    b = read_csv(args.data_dir / "mission_rpm_log.csv")
    n_rotors = sum(1 for k in b[0] if k.startswith("rpm_"))
    if n_rotors % 2:
        raise SystemExit(f"{n_rotors} rotors is not a stack-of-pairs vehicle")
    n_stacks = n_rotors // 2
    t = col(b, "timestamp_s")
    vbus = col(b, "voltage_bus_V")
    rpm = [smooth(col(b, f"rpm_{i}")) for i in range(n_rotors)]
    thrust = [smooth(col(b, f"thrust_N_{i}")) for i in range(n_rotors)]

    total = np.sum(thrust, axis=0)
    t_take = t[np.argmax(total > 1.05 * args.weight_n)]
    mask = (t >= t_take - 4.0) & (vbus > 20.0)
    tr = (t - t_take)[mask]
    dec = slice(None, None, 20)

    fig, axes = plt.subplots(2, 1, figsize=(9.6, 6.4), sharex=True)
    fig.subplots_adjust(hspace=0.16)

    a = axes[0]
    for s in range(n_stacks):
        color = STACKS[s % len(STACKS)]
        a.plot(tr[dec], rpm[2 * s][mask][dec], color=color, lw=1.2,
               label=f"{STACK_NAMES[s % len(STACK_NAMES)]} upper")
        a.plot(tr[dec], rpm[2 * s + 1][mask][dec], color=color, lw=1.2,
               ls=(0, (4, 2)), alpha=0.85,
               label=f"{STACK_NAMES[s % len(STACK_NAMES)]} lower")
    a.set_ylabel("rotor speed (rpm)")
    a.legend(ncol=n_stacks, fontsize=7.5, loc="lower right")
    a.set_title("Per-stack rotor speed — upper solid, lower dashed")

    a = axes[1]
    for s in range(n_stacks):
        upper, lower = thrust[2 * s][mask], thrust[2 * s + 1][mask]
        pair = upper + lower
        ok = pair > 0.5  # the share is meaningless while the stack is unloaded
        share = np.full(len(pair), np.nan)
        share[ok] = lower[ok] / pair[ok]
        a.plot(tr[dec], share[dec] * 100.0, color=STACKS[s % len(STACKS)],
               lw=1.3)
    a.axhline(50.0, color=MUTED, lw=0.8, ls=(0, (4, 3)), alpha=0.6)
    a.set_ylabel("lower rotor share of stack thrust (%)")
    a.set_xlabel("time since takeoff (s)")
    a.set_title(
        "The lower rotor's thrust share — below 50% because it flies in the "
        "upper's induced flow"
    )

    fig.suptitle(
        "ThrustLab FMU · Y6 coax stacks — per-rotor truth the autopilot "
        "never sees",
        color=TEXT, fontsize=12.5, y=0.97,
    )
    out = args.out_dir / "fmu_y6_coax_split.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
