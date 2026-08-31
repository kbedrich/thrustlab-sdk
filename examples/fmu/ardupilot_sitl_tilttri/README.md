# Tilt-rotor tricopter — hover to forward flight and back

The VTOL transition, end to end: vertical takeoff on three rotors, the front
pair tilts forward while a wing takes over the weight, a fixed-wing cruise
circuit, then the reverse transition to a vertical landing. The rotors —
thrust, torque, rpm, battery — are your exported FMU at every tilt angle:
schema 3's per-rotor axial + edgewise inflow is exactly what a tilting rotor
sweeps through.

## What's modelled by whom

- **The FMU (your export)**: every rotor's thrust, in-plane force, reaction
  torque, spin-up, and the shared battery — the product physics.
- **The vehicle YAML (demo scaffolding)**: a plausible 1.4 m flying wing
  (`wing:` block — linear lift, stall clamp, parabolic drag, and textbook
  static + damping stability derivatives so the airframe holds a heading
  instead of drifting into sideslip) and q-scaled control-surface moments so
  the autopilot has something to fly in cruise. Replace with your airframe's
  numbers; no fidelity is claimed for them.

## What you need

Everything the quad example needs (`../ardupilot_sitl/README.md`), plus:

- a **3-rotor export** (front-right CCW, front-left CW, rear CCW — the
  rotor_manifest order `tilttri.yaml` maps),
- an ArduPilot **plane** SITL build (`./waf plane`).

## Run it

```sh
mkdir -p mission_out
python -m thrustlab.sitl \
  --fmu my-tri-powertrain.fmu --vehicle tilttri.yaml \
  --rpm-log mission_out/mission_rpm_log.csv
```

```sh
./build/sitl/bin/arduplane --model JSON:127.0.0.1 \
  --defaults Tools/autotest/default_params/quadplane.parm,Tools/autotest/default_params/quadplane-tilttri.parm,/path/to/ardupilot_sitl_tilttri/tilttri.parm -I0
```

```sh
python fly_transition.py --out-dir ./mission_out
```

## The plots

The standard flight report works unchanged (set `WEIGHT_N` to your weight,
12.26 N for the YAML as shipped):

```sh
python ../ardupilot_sitl/plot_mission.py ./mission_out ./mission_out/plots
```

Watch the rotor-speed panel through the transition: the front pair keeps
flying at full tilt — axial inflow at cruise speed — while the rear rotor
winds down as the wing takes the weight. That hand-over is the whole point
of the example, and every line of it is the FMU answering a flight condition
the autopilot chose on its own.

A note on speeds: `tilttri.parm` pins the cruise and transition speeds
(`AIRSPEED_CRUISE` 13, `Q_ASSIST_SPEED` 9) to what the shipped 10x4.7
powertrain can actually sustain — QuadPlane defaults ask for 25 m/s, which
this propeller cannot reach. Flying your own export? Retune those numbers
to your propeller's speed range first.

One honest caveat: ArduPilot's VTOL approach holds the lift rotors spinning
at 10–14 m/s of edgewise flow — beyond what the export samples — so
`rotor_in_envelope` drops there for a few seconds (about 9% of this
mission's armed frames); outputs clamp to the envelope edge rather than
being measured. Hover, transition, cruise and landing all fly on sampled
physics. And a stopped rotor's flag means nothing: the rear rotor is
deliberately stopped for most of the circuit while the wing carries the
weight, so judge the envelope over spinning rotors only — the replay video
does exactly that.
