# Hover endurance — drive the FMU with nothing but fmpy

No simulator, no autopilot: `hover_endurance.py` steps your exported
powertrain directly through FMI 3.0 Co-Simulation and answers a design
question the datasheet can't — how long does this aircraft hover, per gram
of payload, with the battery sagging under it the whole time?

A proportional governor trims total thrust to vehicle weight each step, the
way a flight controller's altitude hold would; as the pack drains, the
throttle creeps up on its own. Endurance is the integrated time from full
charge to the SOC cutoff. When the sagging pack can no longer carry the
weight at full throttle, the payload point is reported as unflyable instead
of extrapolated.

## Run it

```sh
pip install fmpy numpy matplotlib
python hover_endurance.py my-powertrain.fmu --mass-kg 1.20
```

`--mass-kg` is the all-up mass WITHOUT payload (airframe + battery).
Optional: `--payloads-g 0,100,...` (default sweeps 0-500 g),
`--soc-cutoff 0.20`, `--out hover_endurance.png`.

The output chart plots endurance and mean electrical power against payload;
the console table adds the trimmed hover throttle at the start and end of
each flight — the spread between the two is the battery sag made visible.

Export an FMU with `examples/fmu/export_and_download.py` or the dashboard's
Share menu.
