"""Hover endurance vs payload, straight from the exported FMU — no simulator.

fmpy drives the FMU's disc mode directly: a proportional governor trims total
thrust to vehicle weight while the battery model sags and drains underneath
it, so throttle creeps up over the flight exactly the way a real hover does.
Endurance is the integrated time from full charge to the SOC cutoff, once per
payload step.

Usage: python hover_endurance.py my-powertrain.fmu --mass-kg 1.20
                                 [--payloads-g 0,100,200,300,400,500]
                                 [--soc-cutoff 0.20] [--out hover_endurance.png]

The FMU is the whole model here: thrust response, rotor spin-up, bus voltage
under load and state of charge all come from the export. This script adds
nothing but weight and a throttle trim.
"""
import argparse
from pathlib import Path

import fmpy
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
ORANGE = "#e78a4e"
AQUA = "#89b482"
RED = "#ea6962"

G = 9.80665
DT_S = 0.1
GOVERNOR_GAIN = 0.4  # throttle per unit of (weight - thrust)/weight, per step
SETTLE_S = 8.0  # spin-up + trim capture before the endurance clock starts
WALL_CAP_S = 5400.0  # give up on a single hover after 90 simulated minutes

INPUTS = ("throttle", "v_axial_m_s", "v_edge_m_s")
OUTPUTS = ("thrust_N", "voltage_bus_V", "current_bus_A", "battery_soc")


class Hover:
    """One FMU instance, reset between payload steps."""

    def __init__(self, fmu_path: Path):
        self.description = fmpy.read_model_description(str(fmu_path))
        unzip = fmpy.extract(str(fmu_path))
        self.slave = fmpy.instantiate_fmu(
            unzip, self.description, fmi_type="CoSimulation"
        )
        by_name = {v.name: v for v in self.description.modelVariables}
        self.vr = {name: by_name[name].valueReference for name in (
            *INPUTS, *OUTPUTS, "air_density_kg_m3", "ambient_temp_C",
            "use_vehicle_frame",
        )}
        shape = getattr(by_name["throttle"], "shape", None)
        self.n_rotors = int(shape[0]) if shape else 1
        self._out_vrs = [self.vr[n] for n in OUTPUTS]
        self._out_n = self.n_rotors + 3  # thrust is per-rotor, the rest scalar
        self._initialise()

    def _initialise(self):
        self.slave.enterInitializationMode(startTime=0.0)
        self.slave.setBoolean([self.vr["use_vehicle_frame"]], [False])
        self.slave.setFloat64([self.vr["air_density_kg_m3"]], [1.225])
        self.slave.setFloat64([self.vr["ambient_temp_C"]], [25.0])
        zeros = [0.0] * self.n_rotors
        for name in INPUTS:
            self.slave.setFloat64([self.vr[name]], zeros)
        self.slave.exitInitializationMode()

    def reset(self):
        self.slave.reset()
        self._initialise()

    def step(self, t_s: float, throttle: float):
        """One communication point at a uniform throttle; returns the outputs."""
        self.slave.setFloat64(
            [self.vr["throttle"]], [throttle] * self.n_rotors
        )
        self.slave.doStep(
            currentCommunicationPoint=t_s, communicationStepSize=DT_S
        )
        flat = self.slave.getFloat64(self._out_vrs, nValues=self._out_n)
        thrust = float(np.sum(flat[: self.n_rotors]))
        voltage, current, soc = (float(v) for v in flat[self.n_rotors:])
        return thrust, voltage, current, soc


def hover_out(hover: Hover, weight_n: float, soc_cutoff: float):
    """Trim to weight, then hold hover until the SOC cutoff.

    Returns (endurance_s, mean_power_W, throttle_start, throttle_end) or None
    when the powertrain cannot lift the weight at full throttle.
    """
    hover.reset()
    throttle, t = 0.5, 0.0
    saturated_since = None
    power_acc, power_n = 0.0, 0
    t_clock_start = None
    while t < WALL_CAP_S:
        thrust, voltage, current, soc = hover.step(t, throttle)
        t += DT_S
        error = (weight_n - thrust) / weight_n
        throttle = float(np.clip(throttle + GOVERNOR_GAIN * error * DT_S * 10, 0.0, 1.0))

        if t_clock_start is None:
            if t >= SETTLE_S:
                if abs(error) > 0.02:
                    # Still not carrying the weight after the settle window —
                    # check for saturation rather than looping forever.
                    if throttle >= 0.995:
                        saturated_since = saturated_since or t
                        if t - saturated_since > 5.0:
                            return None
                    else:
                        saturated_since = None
                    continue
                t_clock_start = t
                throttle_start = throttle
            continue

        power_acc += voltage * current
        power_n += 1
        if throttle >= 0.995 and error > 0.05:
            return None  # the sagging pack can no longer hold the hover
        if soc <= soc_cutoff:
            return (
                t - t_clock_start,
                power_acc / max(power_n, 1),
                throttle_start,
                throttle,
            )
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("fmu", type=Path)
    ap.add_argument("--mass-kg", type=float, required=True,
                    help="all-up mass WITHOUT payload (airframe + battery)")
    ap.add_argument("--payloads-g", default="0,100,200,300,400,500")
    ap.add_argument("--soc-cutoff", type=float, default=0.20)
    ap.add_argument("--out", type=Path, default=Path("hover_endurance.png"))
    args = ap.parse_args()

    payloads = [float(p) for p in args.payloads_g.split(",")]
    hover = Hover(args.fmu)
    print(f"{args.fmu.name}: {hover.n_rotors} rotors, "
          f"base mass {args.mass_kg:.2f} kg, SOC cutoff {args.soc_cutoff:.0%}")

    rows = []
    for payload_g in payloads:
        weight = (args.mass_kg + payload_g / 1000.0) * G
        result = hover_out(hover, weight, args.soc_cutoff)
        if result is None:
            print(f"  payload {payload_g:5.0f} g: cannot sustain hover")
            rows.append((payload_g, None, None, None, None))
            continue
        endurance, power, thr0, thr1 = result
        print(f"  payload {payload_g:5.0f} g: {endurance / 60:6.1f} min at "
              f"{power:6.1f} W (throttle {thr0:.2f} -> {thr1:.2f})")
        rows.append((payload_g, endurance, power, thr0, thr1))

    flyable = [r for r in rows if r[1] is not None]
    if not flyable:
        print("nothing flyable in this payload range; no plot written")
        return

    plt.rcParams.update({
        "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
        "text.color": TEXT, "axes.edgecolor": AXIS, "axes.labelcolor": MUTED,
        "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
        "grid.color": GRID, "font.family": "DejaVu Sans",
        "axes.titlecolor": TEXT, "axes.spines.top": False,
        "axes.spines.right": False, "legend.frameon": False,
        "legend.labelcolor": MUTED,
    })
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    xs = [r[0] for r in flyable]
    ax.plot(xs, [r[1] / 60 for r in flyable], color=AQUA, lw=2.0, marker="o",
            ms=5, label="hover endurance")
    ax.set_xlabel("payload (g)")
    ax.set_ylabel("endurance to cutoff (min)", color=AQUA)
    ax.set_ylim(bottom=0)
    at = ax.twinx()
    at.grid(False)
    at.spines["right"].set_visible(True)
    at.plot(xs, [r[2] for r in flyable], color=ORANGE, lw=1.6, marker="s",
            ms=4, alpha=0.9, label="mean electrical power")
    at.set_ylabel("mean electrical power (W)", color=ORANGE)
    dead = [r[0] for r in rows if r[1] is None]
    if dead:
        ax.axvspan(min(dead), max(max(dead), ax.get_xlim()[1]), color=RED,
                   alpha=0.12, lw=0)
        ax.annotate("cannot hover", (min(dead), ax.get_ylim()[1] * 0.92),
                    color=RED, fontsize=9, xytext=(6, 0),
                    textcoords="offset points")
    ax.set_title(
        f"Hover endurance vs payload — {hover.n_rotors}-rotor export, "
        f"SOC {1.0:.0%} → {args.soc_cutoff:.0%}",
        fontsize=12, loc="left",
    )
    fig.tight_layout()
    fig.savefig(args.out, dpi=180)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
