"""Throttle sweep: auth -> submit -> wait() -> iterate the canonical points.

Run it:
    export THRUSTLAB_API_KEY=key_...        # never hard-code the key
    python examples/sweeps/run_and_poll.py

Sweeps a single throttle axis 10 -> 100% (10 steps) over the verification combo.
Swap in your own component IDs, or resolve them by name with
client.components.find(...).
"""

from thrustlab import Client

client = Client()  # reads $THRUSTLAB_API_KEY from the environment

project = client.projects.create(name="sdk sweep example")

# Resolve by name, or paste explicit IDs: motor_id = "comp_motor_xxx"
motor = client.components.find(name="Spektrum Avian 4260 800Kv")
prop = client.components.find(name="10.5x4.5")
battery = client.components.find(name="4S 5000mAh")

sweep = client.sweeps.create(
    project_id=project["id"],
    battery_component_id=battery["id"],
    airspeed_m_s=0.0,
    density_kg_m3=1.225,
    battery_charge_pct=100,
    rotor_groups=[
        {
            "label": "main",
            "count": 4,
            "motor_component_id": motor["id"],
            "propeller_component_id": prop["id"],
            "throttle_pct": 70,
        }
    ],
    sweep={
        "rotor_sweep_mask": [True],
        "throttle": {"mode": "range", "start": 10, "stop": 100, "steps": 10},
    },
)
print(f"created {sweep['id']}")

result = client.sweeps.wait(sweep["id"], timeout=600)
print(f"final status: {result['status']}")

# list_points() lazily walks every cursor page. Each point's `rotors` mirrors a
# single-point result: per-rotor group under "1"/"2"/... + "All"/"Battery"
# aggregates, all canonical snake_case (post-D-01).
if result["status"] == "completed":
    print("point | inputs | per-rotor thrust (N)")
    for pt in client.sweeps.list_points(sweep["id"]):
        thrust = pt["rotors"]["1"]["thrust_n"]
        print(f"  {pt['index']:>2} | {pt['inputs']} | {thrust:.2f}")
