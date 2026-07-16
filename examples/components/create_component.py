"""Create your own custom motor, battery, and propeller from spec_json.

Run it:
    export THRUSTLAB_API_KEY=key_...        # never hard-code the key
    python examples/components/create_component.py

A custom component is `POST /v1/components` with three fields: `type`
(motor | battery | propeller), `name`, and a type-specific `spec_json` map. The
create is scoped to your account (source="user", visibility="private"); the
returned resource echoes back an `id` (comp_...) you pass to a simulation.

Each create below is `client.components.create(...)`. Field names, units, and
accepted ranges come from the server-side validators — see the reference page
for the full tables.

Notes on validation:
  * Battery: a physical pack needs chemistry, cell layout, capacity, weight_g,
    one resistance figure (c_rating or pack_resistance_mOhm), and bounding-box
    dims; form_factor is derived from chemistry when omitted.
  * Propeller: per-station radius/chord/twist and rotation are required, and
    persisting a propeller needs the hobbyist tier or higher — the create below
    reports the tier gate cleanly on a free account.
"""

from thrustlab import Client
from thrustlab.exceptions import APIError

client = Client()  # reads $THRUSTLAB_API_KEY from the environment

# ---- motor ---------------------------------------------------------------
# Required: kv, n (pole count), R (phase-to-phase winding resistance, ohms),
# weight, diameter, length, u_nominal, iq_nominal, and one of iq_max /
# power_max. Inductance L and rotor inertia are auto-estimated from
# kv/n/diameter/length/weight — inertia is required for dynamic (time-domain)
# runs, so give real dimensions and mass.
motor = client.components.create(
    type="motor",
    name="My Custom 4260 800Kv",
    spec_json={
        "brand": "Custom",
        "kv": 800.0,            # rpm per volt
        "n": 14,                # magnet pole count
        "R": 0.042,             # phase-to-phase winding resistance (ohm)
        "weight": 120.0,        # g
        "diameter": 42.0,       # mm (drives L / inertia estimation)
        "length": 25.0,         # mm
        "u_nominal": 14.8,      # nominal voltage (V)
        "iq_nominal": 1.1,      # no-load / idle current (A)
        "iq_max": 65.0,         # max quadrature current (A)
        "power_max": 960.0,     # max electrical power (W)
        "topology": "outrunner",
    },
)
print(f"created motor {motor['id']}")

# ---- battery -------------------------------------------------------------
# chemistry in {lipo, lihv, nmc, nca, lfp, nimh, source}. A physical pack needs
# its cell layout, capacity, weight_g, one resistance figure (c_rating or
# pack_resistance_mOhm), and length/width/height_mm (1..2000 mm). form_factor
# is derived (lipo -> pouch) when omitted. Pack cap: series <= 24, S*P <= 256.
battery = client.components.create(
    type="battery",
    name="My Custom 4S 5000mAh",
    spec_json={
        "brand": "Custom",
        "chemistry": "lipo",
        "series_cells": 4,
        "parallel_cells": 1,
        "total_capacity_mAh": 5000.0,
        "c_rating": 75.0,
        "weight_g": 480.0,
        "length_mm": 145.0,     # required for a physical chemistry
        "width_mm": 49.0,
        "height_mm": 33.0,
    },
)
print(f"created battery {battery['id']}")

# ---- propeller (hobbyist tier or higher) ---------------------------------
# Required: diameter, pitch, rotation, weight, and the per-station blade
# geometry — parallel radius/chord/twist arrays, hub -> tip (<= 50 stations;
# radius and chord in METERS, twist in degrees). inertia is required for
# dynamic (time-domain) runs and is estimated from weight + diameter when
# omitted.
try:
    prop = client.components.create(
        type="propeller",
        name="My Custom 10.5x4.5",
        spec_json={
            "brand": "Custom",
            "diameter": 10.5,   # inch
            "pitch": 4.5,       # inch
            "num_blades": 2,
            "rotation": "ccw",  # top view; "cw" | "ccw" | "both"
            "weight": 14.0,     # g
            "inertia": 8.3e-5,  # kg*m^2 — required for dynamic runs
            # per-station geometry, hub -> tip (r/R = 0.20 .. 1.00)
            "radius": [0.0267, 0.0400, 0.0600, 0.0800, 0.1000, 0.1200, 0.1334],  # m
            "chord": [0.016, 0.019, 0.022, 0.021, 0.018, 0.014, 0.008],          # m
            "twist": [30.0, 24.0, 17.0, 12.8, 10.3, 8.6, 7.8],                   # deg
        },
    )
    print(f"created propeller {prop['id']}")
except APIError as exc:
    # A free account 402s here (propeller persistence is a creator_edit gate).
    print(f"propeller create skipped: {exc}")
