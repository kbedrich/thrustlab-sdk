# ArduPilot SITL — fly your exported powertrain

Fly a real ArduPilot mission where the vehicle physics is YOUR ThrustLab
powertrain: per-rotor thrust and torque, true rotor spin-up, battery sag and
state of charge — all from the `.fmu` you exported.

## What you need

- An exported FMU (`examples/fmu/export_and_download.py`, or the dashboard's
  Share menu → Export powertrain).
- `pip install thrustlab` — the SDK ships the JSON-backend physics bridge
  (`thrustlab.sitl`).
- An ArduPilot SITL build (`./waf copter`), any recent Copter.
- `pip install pymavlink matplotlib numpy` for the mission script and plots.

## Run it (three terminals)

1. The bridge listens first, with your FMU and a vehicle layout. The rpm log
   goes into `mission_out/` so the plot step finds every recording in one
   place (create the directory first — the bridge won't):

   ```sh
   mkdir -p mission_out
   python -m thrustlab.sitl \
     --fmu ../validation-quad.fmu --vehicle quad_x.yaml \
     --rpm-log mission_out/mission_rpm_log.csv
   ```

   `quad_x.yaml` maps servo outputs to rotors (positions, spin directions,
   mass). Start from the annotated `../quad_5inch_x.yaml` and edit mass
   and geometry to your airframe.

2. ArduPilot with the JSON model — run from your ArduPilot checkout, and
   point at this example directory's `fmu.parm` by absolute path:

   ```sh
   ./build/sitl/bin/arducopter --model JSON:127.0.0.1 \
     --defaults Tools/autotest/default_params/copter.parm,/path/to/examples/fmu/ardupilot_sitl/fmu.parm -I0
   ```

   `fmu.parm` needs at least `BATT_MONITOR 4` (the bridge feeds pack voltage
   and current back into the firmware's battery monitor).

3. The mission:

   ```sh
   python fly_mission.py --out-dir ./mission_out
   ```

   It uploads a multi-leg AUTO mission (takeoff, 13 m/s dash, climb, loiter
   turns, fast descent, RTL), flies it, and records MAVLink telemetry beside
   the bridge's per-rotor log.

## The plots

```sh
python plot_mission.py ./mission_out ./mission_out/plots
```

Three figures from the recorded flight: the mission track colored by
electrical power, the powertrain time series (per-rotor speed, bus voltage
and current, power and state of charge), and the loiter-exit close-up where
the mixer splits the four rotors.

The same recording also renders as an animated replay — the track draws
itself colored by power while live panels play the powertrain through the
mission:

```sh
python render_mission_video.py ./mission_out ./mission_out/video
```

Frames land in `video/frames/`; with ffmpeg on PATH the mp4 is encoded
automatically, otherwise the exact encode command is printed.

Per-rotor RPM never crosses the ArduPilot JSON protocol — the protocol has no
RPM lane — so the bridge logs it to `mission_out/mission_rpm_log.csv` for
reconciliation against flight logs. If you changed the vehicle mass in
`quad_x.yaml`, set `WEIGHT_N` at the top of `plot_mission.py` to match — it
aligns the two recordings' clocks on the takeoff event.

## The bundled FMU

This example ships with a ready-to-fly FMU exported from ThrustLab
(`../validation-quad.fmu`). The exact powertrain it reproduces is documented
in the archive's own `resources/README.md`; unzip the FMU to read it. To
recreate the FMU, build the same powertrain in ThrustLab or through the
API/SDK, then export it with **Export → FMU** or `client.fmu`; your export
will fly these examples identically.
