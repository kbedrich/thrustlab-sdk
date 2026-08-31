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
  --fmu my-y6-powertrain.fmu --vehicle y6.yaml \
  --rpm-log mission_out/mission_rpm_log.csv
```

```sh
./build/sitl/bin/arducopter --model JSON:127.0.0.1 \
  --defaults Tools/autotest/default_params/copter.parm,/path/to/ardupilot_sitl_y6/y6.parm -I0
```

```sh
python ../ardupilot_sitl/fly_mission.py --out-dir ./mission_out --speed-scale 0.3
```

`--speed-scale 0.3` matters here: a coax lane's sampled envelope is tighter
than a solo rotor's map — edgewise speed caps near 5 m/s at this scale and
descent states are not sampled at all — so the full-speed mission spends
most of its time flagged `all_in_envelope=false` (outputs clamp to the
envelope edge instead of being measured). Scaled down, the flight stays on
sampled physics except for brief descents.

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
