"""Quickstart: install thrustlab, set $THRUSTLAB_API_KEY, run this file.

    export THRUSTLAB_API_KEY=key_...        # never hard-code the key
    python examples/quickstart.py
"""

from itertools import islice

from thrustlab import Client

client = Client()  # reads $THRUSTLAB_API_KEY from the environment

project = client.projects.create(name="my first project")
print(f"created project {project['id']}")

print("first 5 motors:")
for component in islice(client.components.list(type="motor"), 5):
    brand = component["spec_json"].get("brand", "?")
    print(f"  {component['id']} — {brand} {component['name']}")

# One-hit lookup: find() returns the single match (or raises
# AmbiguousComponentError on >1, NotFoundError on 0) so you don't have to
# round-trip the list yourself. Or paste explicit IDs from the catalog.
motor = client.components.find(name="Spektrum Avian 4260 800Kv")
prop = client.components.find(name="10.5x4.5")
battery = client.components.find(name="Liperior 5000mAh 4S 35C")

# Run a single-point simulation and wait for the result.
sim = client.simulations.create(
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
)
result = client.simulations.wait(sim["id"], timeout=300)
print(f"status: {result['status']}")
if result["status"] == "completed":
    # Canonical snake_case keys: per-rotor under "1", roll-ups under "All".
    print(f"per-rotor thrust: {result['result']['1']['thrust_n']:.2f} N")
    print(f"total thrust:     {result['result']['All']['total_thrust_n']:.2f} N")
