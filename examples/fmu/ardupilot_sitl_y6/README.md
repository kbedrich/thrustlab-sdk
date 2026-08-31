# Y6 coax hexacopter — three contra-rotating stacks in ArduPilot SITL

The coaxial version of the SITL example: a Y6 whose six rotors are three
contra-rotating pairs from a coax export. Each lower rotor flies in its upper
partner's induced flow, and the FMU carries that coupling per rotor — thrust,
torque and rpm split between the pair the way a real stack splits them.

## What you need

Everything the quad example needs (`../ardupilot_sitl/README.md`), plus a
**coax export**: a completed simulation with three two-rotor stacks
(FRAME_CLASS 5 geometry), exported from the dashboard or the API. The
export's `rotor_manifest` must order rotors (stack1 upper, stack1 lower,
stack2 upper, ...) with top rotors CW — that is what `y6.yaml` maps to
ArduPilot's Y6B motor order, and the mapping is documented line by line in
the YAML.

## Run it

Same three terminals as the quad example, swapping in this directory's files:

```sh
mkdir -p mission_out
python -m thrustlab.sitl \
  --fmu example-y6.fmu --vehicle y6.yaml \
  --rpm-log mission_out/mission_rpm_log.csv
```

```sh
./build/sitl/bin/arducopter --model JSON:127.0.0.1 \
  --defaults Tools/autotest/default_params/copter.parm,/path/to/ardupilot_sitl_y6/y6.parm -I0
```

```sh
python ../ardupilot_sitl/fly_mission.py --out-dir ./mission_out --speed-scale 0.42
```

`--speed-scale 0.42` uses the bundled FMU's wider sampled coax envelope: at
hover rotor speed, it covers level edgewise flight to about 7 m/s, descent to
3 m/s, and gentle approach legs (about 1.5 m/s down) to about 4.5 m/s
edgewise. The entire 397-second demo mission stays on measured physics, with
99.2% of armed frames `all_in_envelope`; the remainder are brief arm/disarm
spool transients. The binding limit is the slowest rotor because the edgewise
axis scales with rotor speed, advance-ratio style: in forward flight the
unloaded rear-lower rotor reaches the envelope edge near 6.3 m/s, while
loaded rotors remain covered to about 7.3 m/s. Beyond the envelope, outputs
clamp to its edge and set `all_in_envelope=false` rather than extrapolating.

## The plots

The standard flight report works unchanged (set `WEIGHT_N` to your Y6's
weight first):

```sh
python ../ardupilot_sitl/plot_mission.py ./mission_out ./mission_out/plots
```

The coax-specific figure is this directory's:

```sh
python plot_coax_split.py ./mission_out ./mission_out/plots
```

Its bottom panel is the point of the whole example: the lower rotor's share
of each stack's thrust sits below 50% for the entire flight — the wake
coupling, resolved per rotor, in a model the autopilot drives at 400 Hz.

## The bundled FMU

This example ships with a ready-to-fly FMU exported from ThrustLab
(`example-y6.fmu`). The exact powertrain it reproduces is documented in the
archive's own `resources/README.md`; unzip the FMU to read it. To recreate
the FMU, build the same powertrain in ThrustLab or through the API/SDK, then
export it with **Export → FMU** or `client.fmu`; your export will fly these
examples identically.
