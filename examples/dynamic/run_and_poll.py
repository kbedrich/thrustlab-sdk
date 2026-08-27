"""Dynamic (time-domain) simulation: auth -> submit -> wait() -> read the result.

Run it:
    export THRUSTLAB_API_KEY=key_...        # never hard-code the key
    python examples/dynamic/run_and_poll.py

A dynamic run integrates the powertrain through a throttle/airspeed *schedule*
until a *termination* condition (here: a 2 s spin-up ramp, then a 20 s hover
at 70% — a fixed-duration mission). It returns per-step `samples` (each a full
steady-shaped result),
time `series`, a `scorecard`, and `events`. Swap in your own component IDs, or
resolve them by name with client.components.find(...).
"""

from thrustlab import Client

client = Client()  # reads $THRUSTLAB_API_KEY from the environment

project = client.projects.create(name="sdk dynamic example")

# Resolve by name, or paste explicit IDs: motor_id = "comp_motor_xxx"
motor = client.components.find(name="BadAss 2826-820Kv")
prop = client.components.find(name="10.5x4.5")
battery = client.components.find(
    name="Liperior 5000mAh 4S 35C 14.8V Lipo Battery With XT90 Plug"
)

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
    # Ramp to 70% over 2 s, then hold for 20 s. The soft-start matters:
    # stepping 70% onto a stationary rotor draws an in-rush that can sag the
    # pack below the low-voltage cutoff and end the run immediately — exactly
    # as it would on real hardware. Endurance ("until depleted") missions work
    # the same way but integrate minutes of pack time; keep examples short.
    schedule={
        "mode": "segments",
        "segments": [
            {
                "duration_s": 2.0,
                "airspeed_target": 0.0,
                "per_group": {"main": {"throttle_target": 70, "throttle_ramp": "linear"}},
            },
            {
                "duration_s": 20.0,
                "airspeed_target": 0.0,
                "per_group": {"main": {"throttle_target": 70}},
            },
        ],
    },
    # Fixed-duration mission: run the schedule to its end.
    termination={"mode": "fixed"},
)
print(f"created {dyn['id']}, status={dyn['status']}")

result = client.dynamic_simulations.wait(dyn["id"], timeout=600)
print(f"final status: {result['status']}")

if result["status"] == "completed":
    blob = result["result"]

    # scorecard: whole-run headline metrics (canonical snake_case).
    sc = blob["scorecard"]
    print(f"peak winding temp: {sc['peak_winding_temp_c']:.1f} C")
    print(f"avg efficiency:    {sc['avg_efficiency']:.3f}")
    print(f"peak current:      {sc['peak_current_a']:.1f} A")
    print(f"min cell voltage:  {sc['min_cell_voltage_v']:.2f} V")

    # samples[]: each entry is a full steady-shaped snapshot at one time step —
    # read the same canonical per-rotor / aggregate keys as a single-point run.
    samples = blob["samples"]
    first, last = samples[0], samples[-1]
    print(f"steps: {len(samples)}")
    print(f"  t0 total thrust: {first['All']['total_thrust_n']:.2f} N")
    print(f"  tN total thrust: {last['All']['total_thrust_n']:.2f} N")
