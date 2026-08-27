"""Read a steady-state result: single-point AND sweep share one snake_case schema.

Run it:
    export THRUSTLAB_API_KEY=key_...        # never hard-code the key
    python examples/outputs/read_steady_state.py

A completed single-point simulation carries two siblings:
  * result           — a dict keyed per-rotor ("1", "2", ...) plus the "All"
                       and "Battery" aggregates. Every per-rotor and "All" key
                       is canonical snake_case (e.g. thrust_n, total_current_a).
  * display_labels    — {snake_key: human_string}, the single source of truth for
                       a human-readable column header (thrust_n -> "Thrust (N)").

A sweep reuses the EXACT same per-point shape: each point's `rotors` mirrors a
single-point `result`, and the same display_labels vocabulary applies. Swap in
your own component IDs, or resolve them by name with client.components.find(...).
"""

from thrustlab import Client

client = Client()  # reads $THRUSTLAB_API_KEY from the environment


def print_group(name: str, group: dict, labels: dict) -> None:
    """Print each key -> value alongside its human display label.

    Scalar keys print as `snake_key   Human Label   value`. Nested blocks
    (the relocated `diagnostics` sub-object) print their key set only.
    """
    print(f"\n[{name}]")
    for key, value in group.items():
        label = labels.get(key, key)  # "Battery" keys are already human strings
        if isinstance(value, (dict, list)):
            kind = "dict" if isinstance(value, dict) else "list"
            print(f"  {key:<28} {label:<28} <{kind}, {len(value)} entries>")
        else:
            print(f"  {key:<28} {label:<28} {value}")


project = client.projects.create(name="sdk read-steady-state example")

# Resolve by name, or paste explicit IDs: motor_id = "comp_motor_xxx"
motor = client.components.find(name="BadAss 2826-820Kv")
prop = client.components.find(name="10.5x4.5")
battery = client.components.find(
    name="Liperior 5000mAh 4S 35C 14.8V Lipo Battery With XT90 Plug"
)

# ---- single point ---------------------------------------------------------
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
print(f"single-point status: {result['status']}")

if result["status"] == "completed":
    blob = result["result"]
    labels = result["display_labels"]  # {snake_key: human_string}

    # Per-rotor group under its label index ("1", "2", ...).
    print_group("rotor 1", blob["1"], labels)
    # Aggregate roll-ups across all rotors.
    print_group("All", blob["All"], labels)
    # The "Battery" entry is passed through as-is: per-cell arrays keyed by human
    # strings ("Cell voltages (V)", "Charge levels (%)") that are NOT in
    # display_labels — read them directly.
    print_group("Battery", blob["Battery"], labels)

# ---- sweep (same schema, one point per grid cell) -------------------------
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
sweep_result = client.sweeps.wait(sweep["id"], timeout=600)
print(f"\nsweep status: {sweep_result['status']}")

if sweep_result["status"] == "completed":
    # Each point's `rotors` is a single-point result dict; the same snake_case
    # keys (and the same display_labels vocabulary read above) apply per point.
    print("\npoint | throttle in | per-rotor thrust_n | total_thrust_n")
    for pt in client.sweeps.list_points(sweep["id"]):
        rotor = pt["rotors"]["1"]
        agg = pt["rotors"]["All"]
        print(
            f"  {pt['index']:>2} | {pt['inputs']} | "
            f"{rotor['thrust_n']:.2f} | {agg['total_thrust_n']:.2f}"
        )
