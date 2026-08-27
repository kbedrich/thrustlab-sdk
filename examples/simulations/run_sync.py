"""Single-point simulation: auth -> submit -> wait() -> read the canonical result.

Run it:
    export THRUSTLAB_API_KEY=key_...        # never hard-code the key
    python examples/simulations/run_sync.py

The verification combo below (BadAss 2826-820Kv + 10.5x4.5 + Liperior
4S 5000 mAh @ 70% throttle, static) converges to ~9.07 N / ~8505 rpm. Swap in
your own component IDs, or resolve them by name with client.components.find(...).
"""

from thrustlab import Client

client = Client()  # reads $THRUSTLAB_API_KEY from the environment

project = client.projects.create(name="sdk single-point example")

# Resolve components by name (find() returns the single match or raises
# AmbiguousComponentError / NotFoundError). Or paste explicit IDs instead:
#   motor_id = "comp_motor_xxx"
motor = client.components.find(name="BadAss 2826-820Kv")
prop = client.components.find(name="10.5x4.5")
battery = client.components.find(
    name="Liperior 5000mAh 4S 35C 14.8V Lipo Battery With XT90 Plug"
)

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
print(f"created {sim['id']}, status={sim['status']}")

# wait() polls until completed / failed / canceled (or a timeout sentinel).
result = client.simulations.wait(sim["id"], timeout=300)
print(f"final status: {result['status']}")

if result["status"] == "completed":
    # Canonical snake_case result (post-D-01): per-rotor group under its label
    # index ("1", "2", ...); aggregate roll-ups under "All".
    per_rotor = result["result"]["1"]
    aggregate = result["result"]["All"]
    print(f"per-rotor thrust: {per_rotor['thrust_n']:.2f} N")
    print(f"per-rotor rpm:    {per_rotor['rpm']:.0f}")
    print(f"total thrust:     {aggregate['total_thrust_n']:.2f} N")
