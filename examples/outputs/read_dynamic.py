"""Read a dynamic (time-domain) result: samples, time-series, and the scorecard.

Run it:
    export THRUSTLAB_API_KEY=key_...        # never hard-code the key
    python examples/outputs/read_dynamic.py

A completed dynamic run integrates the powertrain through a throttle/airspeed
schedule until a termination condition. Its `result` blob carries:
  * scorecard   — whole-run headline metrics (flight_time_s, peak_current_a,
                  min_cell_voltage_v, peak_winding_temp_c, avg_efficiency, ...).
  * samples[]    — one full steady-shaped snapshot per saved step; each entry has
                  the SAME canonical per-rotor / "All" / "Battery" keys as a
                  single-point result, so display_labels applies to it too.
  * series       — {channel_name: list[float]} aligned to series["time_s"], the
                  down-sampled plotting source (total_thrust_n, total_current_a,
                  rotor1_rpm, ...).
  * events / run_meta — timestamped run events + step/depletion bookkeeping.

Swap in your own component IDs, or resolve them by name with
client.components.find(...).
"""

from thrustlab import Client

client = Client()  # reads $THRUSTLAB_API_KEY from the environment

project = client.projects.create(name="sdk read-dynamic example")

# Resolve by name, or paste explicit IDs: motor_id = "comp_motor_xxx"
motor = client.components.find(name="Spektrum Avian 4260 800Kv")
prop = client.components.find(name="10.5x4.5")
battery = client.components.find(name="Liperior 5000mAh 4S 35C")

dyn = client.dynamic_simulations.create(
    project_id=project["id"],
    battery_component_id=battery["id"],
    density_kg_m3=1.225,
    battery_charge_pct=100,
    ambient_temp_c=25,
    rotor_groups=[
        {
            "label": "main",
            "count": 4,
            "motor_component_id": motor["id"],
            "propeller_component_id": prop["id"],
        }
    ],
    # Hold 70% throttle, static, until the pack depletes.
    schedule={
        "mode": "segments",
        "segments": [
            {
                "until_depleted": True,
                "airspeed_target": 0.0,
                "per_group": {"main": {"throttle_target": 70}},
            }
        ],
    },
    termination={"mode": "until_depleted", "soc_cutoff_pct": 20.0},
)
result = client.dynamic_simulations.wait(dyn["id"], timeout=600)
print(f"dynamic status: {result['status']}")

if result["status"] == "completed":
    blob = result["result"]
    labels = result["display_labels"]  # applies to each samples[] entry

    # scorecard: whole-run headline metrics (canonical snake_case).
    print("\n[scorecard]")
    for key, value in blob["scorecard"].items():
        print(f"  {key:<24} {value}")

    # samples[]: each entry is a full steady-shaped snapshot — read the same
    # per-rotor / "All" keys (and display_labels) as a single-point result.
    samples = blob["samples"]
    first, last = samples[0], samples[-1]
    print(f"\nsteps: {len(samples)}")
    print(f"  t0 total_thrust_n: {first['All']['total_thrust_n']:.2f} "
          f"({labels['total_thrust_n']})")
    print(f"  tN total_thrust_n: {last['All']['total_thrust_n']:.2f}")

    # series: down-sampled channels aligned to series["time_s"]. Print a couple.
    series = blob["series"]
    print("\n[series channels]")
    print(f"  available: {sorted(series.keys())}")
    time_s = series["time_s"]
    thrust = series.get("total_thrust_n", [])
    current = series.get("total_current_a", [])
    print("\n  t (s) | total_thrust_n | total_current_a")
    for i in range(0, len(time_s), max(1, len(time_s) // 5)):
        t = time_s[i]
        th = thrust[i] if i < len(thrust) else float("nan")
        cu = current[i] if i < len(current) else float("nan")
        print(f"  {t:6.1f} | {th:>14.2f} | {cu:>15.2f}")

    # events: timestamped run events (depletion, in_rush_peak, thermal_threshold).
    print("\n[events]")
    for ev in blob["events"]:
        print(f"  t={ev['t']:.1f}s  {ev['type']:<18} {ev['severity']:<8} {ev['detail']}")
