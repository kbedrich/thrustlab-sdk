# Betaflight SITL on ThrustLab FMU physics

Run this example to arm a quad, climb, hold altitude for a minute with
Betaflight's `ALTHOLD`, and land. The exported ThrustLab FMU calculates every
newton of thrust, every amp and the battery state of charge instead of using a
thrust constant.

Betaflight SITL uses the bridge as its simulator half. Betaflight sends raw
motor PWM to the bridge. The bridge advances the FMU and a 6DOF rigid body, then
returns the IMU, attitude, velocity and virtual-GPS state used by the flight
controller.

```
  Betaflight SITL  ──9001 servo_packet_raw (PWM µs)──►  thrustlab.sitl
        ▲  ▲                                                   │ FMU + 6DOF
        │  └──────9003 fdm_packet (18 doubles)─────────────────┘
        │                                                      └──9005 truth JSON──► fly_hover.py
        ├──9004 rc_packet ◄── fly_hover.py (the transmitter)
        └──5761 TCP MSP ◄──── fly_hover.py (arm state, accel calibration)
```

## What is in here

| File | What it is |
| --- | --- |
| `betaflight_quad_x.yaml` | The airframe: mass, inertia, rotor geometry, and the rotor→Betaflight-motor map |
| `betaflight_config.txt` | Betaflight CLI settings the demo needs, provisioned in a one-shot run |
| `fly_hover.py` | The pilot: RC over UDP, MSP over TCP, the flight script, the assertions |

## Prerequisites

**Linux, or WSL2 on Windows.** Run Betaflight SITL on Linux. The bridge is pure
Python and can run anywhere. This example runs both on the same host.

**Build Betaflight SITL.** Install `gcc`, `make`, `ruby` and `git`:

```bash
sudo apt install build-essential ruby git
git clone https://github.com/betaflight/betaflight.git ~/bfsitl
cd ~/bfsitl
make TARGET=SITL
# -> obj/main/betaflight_SITL.elf
```

For this example, the bare `TARGET=SITL` build is the right one. It sets
`ENABLE_GAZEBO_BRIDGE=1`, which selects the frame convention encoded by the
bridge. It also sets `FEATURE_RX_UDP`, so `fly_hover.py` can send transmitter
input. The build defines `USE_VIRTUAL_GPS`, `USE_ALTITUDE_HOLD` and
`USE_POSITION_HOLD` too.

**Install the bridge.**

```bash
pip install thrustlab
```

The SDK ships the bridge; no extra is needed.

**Export an FMU.** Use any ThrustLab schema-3 per-rotor export with four rotors.
You can create one with `examples/fmu/export_and_download.py`. This demo used a
450-class quad: 1.20 kg, four rotors on 10×4.7 props, 6S.

## Running it

Three processes must start in this order. Start the bridge before Betaflight so
the flight controller can set its GPS origin from the first `fdm_packet` it
receives.

**1. Provision the flight controller.** The binary reads the CLI file, writes
`eeprom.bin` next to itself, then exits.

```bash
mkdir -p ~/bf_demo && cd ~/bf_demo
cp <example>/betaflight_config.txt .
~/bfsitl/obj/main/betaflight_SITL.elf --config betaflight_config.txt
ls eeprom.bin
```

**2. Start the bridge.**

```bash
python -m thrustlab.sitl \
  --target betaflight \
  --fmu ../validation-quad.fmu \
  --vehicle betaflight_quad_x.yaml \
  --rpm-log mission_rpm_log.csv \
  --truth-port 9005 \
  --step 0.01 --speedup 1.0
```

**3. Start Betaflight, then fly.** Start it from the directory that contains
`eeprom.bin`.

```bash
cd ~/bf_demo && stdbuf -oL ~/bfsitl/obj/main/betaflight_SITL.elf > sitl.log 2>&1 &
python fly_hover.py --hold-seconds 60
```

## What you should see

```
[mission] ok: arming flags clear (GPS fix + RX)
[mission] ok: accelerometer recalibration complete
[mission] ok: armed
[mission] ok: climbed above 3.0 m
[mission] ok: ALTHOLD engaged
[mission] modes: ['ALTHOLD', 'ANGLE', 'ARM']
[mission] hold t=  0.0 s  altitude   3.37 m  heading    0.0 deg
[mission] roll probe: commanding right from east +0.00 m
[mission] roll probe: east now +9.09 m
[mission] yaw probe: commanding right from 0.0 deg
[mission] yaw probe: released at 248.7 deg
[mission] hold t= 57.5 s  altitude   3.04 m  heading  261.4 deg
[mission] ok: landed (truth altitude back under 0.5 m)
[mission] ok: disarmed
[mission] hold altitude: mean 3.08 m, band 2.45-4.00 m
[mission] roll probe: commanded RIGHT, east +0.00 -> +9.09 m (+9.09 m)
[mission] yaw probe: commanded RIGHT, mean body yaw rate +108.9 deg/s over 8 samples
[mission] peak body yaw rate over the flight: 3.00 rad/s
[mission] PASS: armed, climbed, held altitude, landed and disarmed
```

Three files are written to the working directory:

- **`mission_rpm_log.csv`** contains one row per physics frame with per-rotor
  throttle, RPM, thrust, torque, in-plane force, axial and edgewise inflow, and
  the per-rotor envelope flag. It also records bus voltage, bus current and
  battery state of charge. The wire protocol carries none of these values.
- **`mission_telemetry.csv`** records ground truth at 20 Hz: NED position,
  velocity, altitude, heading, body rates, and the PWM commanded by the flight
  controller.
- **`mission_events.csv`** records wall-clock timestamps for arm, climb,
  althold, land and disarm.

### The assertions are qualitative on purpose

The assertions check that the vehicle arms, stays within the altitude band
during the hold, then lands and disarms cleanly. The script also runs two
probes. It does not use the upstream SITL harness's numeric tolerances. Those
tolerances target that harness's scheduler and toy motion model, not FMU
physics.

The two probes check the sign conventions. In a deterministic, symmetric hover,
the axes remain at exactly zero unless a disturbance exposes a bad sign
convention. The script therefore commands a right roll (the airframe must move
**east**) and a right yaw (the body yaw rate must be **positive** and must not
run away). These probes exposed both sign bugs in the bridge. Neither appeared
during hover.

## Frames, in one place

The bridge uses world NED and body FRD frames, a `(w, x, y, z)` body→NED
quaternion, and accelerometer measurements as specific force. Betaflight
expects the Gazebo plugin's conventions. The module docstring in
`thrustlab/sitl/targets/betaflight.py` derives every conversion against
Betaflight master `6aeffc36`. The conversions are:

| Field | Conversion |
| --- | --- |
| `imu_angular_velocity_rpy` | `(p, q, −r)` — roll and pitch pass through, **yaw is negated** |
| `imu_linear_acceleration_xyz` | `(−fx, +fy, +fz)` of the FRD specific force |
| `imu_orientation_quat` | `conj_x180(Rz(−90°) ⊗ q_nwu)`, `q_nwu = (w, x, −y, −z)` of `q_ned` |
| `velocity_xyz` | ENU `(Ve, Vn, Vup)` — the virtual-GPS layout, not NED |
| `position_xyz` | `(lon, lat, alt_m)`, lat/lon **mirrored** about home |
| `pressure` | Ignored. The barometer is derived from `position_xyz[2]` via ISA |

Yaw negation is the one detail to remember. `sitl_gyro.h` describes its `+wz`
mapping as "CW viewed from above". However, `mixer.c` negates the yaw PID sum
before the mixer. Betaflight therefore uses counter-clockwise-positive yaw where
the rate loop closes.

## Troubleshooting

**`FAILSAFE RXLOSS` in `sitl.log`, or arming that never sticks.** The flight
controller's clock may be running fast. `sitl.c` computes `simRate` from a single
packet pair using `deltaSim / wall_gap`, then scales `micros64()` by that value
until the next packet. The resulting value is `1/wall_gap`: a gap half as long
as intended doubles the clock, and a later long gap does not compensate for it.
Two closely spaced `fdm_packet`s therefore make the RC stream appear stalled to
a receiver whose clock is running too fast. The bridge sends each packet as the
first action after sleeping and includes state computed on the previous tick.
This keeps FMU step variance away from the clock. If the problem remains, the
host cannot maintain `--step 0.01`. Increase the step but keep it well under
0.02 s because Betaflight stops refreshing `simRate` beyond that point, or
reduce the host load.

**The vehicle free-falls out of `ALTHOLD`, or bounces divergently.**
`ap_hover_throttle` does not match the airframe. This value is the throttle that
Betaflight's altitude controller treats as hover; its remaining output is
correction. The stock 1275 matches a 5-inch racer with thrust-to-weight near 4.
Use `mission_rpm_log.csv` to find the throttle where the four `thrust_N_*`
columns sum to `mass_kg × 9.80665`, then convert that value to microseconds. At
the default on a 1.2 kg airframe, the controller commanded about a quarter of
the required thrust, and the craft fell 11 m in a second.

**A commanded yaw does nothing, or the airframe spins up and departs.** These
are the two possible yaw-chain failures, and their symptoms differ.

*Nothing* indicates that the rotors' reaction torques cancelled because
`rotor_index` no longer matches the airframe's diagonal pairs. `rotor_index` is
the FMU export's own array order and must **not** be renumbered to match
Betaflight's motor numbering. Only `servo_channel` should move. With
`torque_convention: signed`, the FMU emits `torque_Nm` with the sign defined by
its export. Renumbering then pairs the wrong rotors.
`betaflight_quad_x.yaml` contains the full derivation.

*Departure* indicates that the yaw loop has the wrong sign. In
`mission_telemetry.csv`, the commanded PWM saturates and remains saturated after
the stick centres while `r_rad_s` grows monotonically. The yaw probe's
`peak body yaw rate` check detects this condition.

**The MSP port never opens.** Betaflight's TCP listener omits `SO_REUSEADDR`. A
socket left in `TIME_WAIT` by a previous run can therefore prevent the bind.
The failure is quiet, so the process remains running but unreachable. Retry the
whole launch instead of polling the port. Usually, two or three attempts spaced
a few seconds apart are enough.

**Arming clears, then the craft drifts vertically for no reason.** Run the
accelerometer calibration (`MSP_ACC_CALIBRATION`, command 205) *after* the FDM
feed is live. The boot-time calibration otherwise samples before the feed is
active. The stored bias integrates into a false vertical velocity, which
alt-hold then follows. `fly_hover.py` performs this calibration; a manual
session must do the same.

**The bridge rejects every datagram.** The bridge listens on **9001** for
`servo_packet_raw` (68 bytes, real microseconds), not 9002. Port 9002 carries
`servo_packet`: four normalised floats, hard-capped at four motors, with no
servo channels at all. The error reports the received size.

## Limitations

- The 6DOF model includes drag and a flat ground plane. It has no rotational
  damping beyond the rotor effects. The model supports arming, flight and
  landing but does not model the full airframe.
- Betaflight SITL runs in soft real time rather than lockstep. A 60-second hover
  takes 60 seconds. `--speedup` is available, but it can disrupt the flight
  controller's scheduler.
- Betaflight synthesises the magnetometer from the supplied attitude. The bridge
  does not provide one.
- Betaflight master provides waypoint navigation through `BOX_AUTOPILOT` and
  `waypoint insert` in the CLI. The bridge supplies the required data, but this
  example does not test it.

## The bundled FMU

This example ships with a ready-to-fly FMU exported from ThrustLab
(`../validation-quad.fmu`). The exact powertrain it reproduces is documented
in the archive's own `resources/README.md`; unzip the FMU to read it. To
recreate the FMU, build the same powertrain in ThrustLab or through the
API/SDK, then export it with **Export → FMU** or `client.fmu`; your export
will fly these examples identically.
