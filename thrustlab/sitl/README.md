# thrustlab.sitl

An ArduPilot SITL external-physics backend driven by a ThrustLab FMI 3.0
per-rotor propulsion FMU. It speaks ArduPilot's JSON backend over UDP, maps each
servo channel to a rotor, integrates a 6DOF rigid body around the FMU's wrench,
and feeds battery voltage/current and airspeed back into the firmware as real
sensor lanes.

It also flies **Betaflight SITL** — `--target betaflight`, same FMU, same 6DOF,
same vehicle YAML schema, a different wire protocol behind the same seams. See
[Targets](#targets) and
`examples/fmu/betaflight_sitl/README.md`.

The sign and wrench conventions live in exactly one place in this package,
`thrustlab/sitl/kinematics.py`.

## Install

The bridge ships inside the ThrustLab SDK — no extra needed:

```
pip install thrustlab
```

Needs Python ≥ 3.10; the SDK pulls `numpy`, `PyYAML`, and `fmpy >= 0.3.31`.

## Run it

Start the bridge first — ArduPilot resends its servo frame about once a second
until a physics backend answers, so order is forgiving, but the log is clearer
this way.

```
python -m thrustlab.sitl \
    --fmu build/my_quad.fmu \
    --vehicle examples/fmu/quad_5inch_x.yaml \
    --rpm-log flight_rotors.csv
```

Then SITL, pointed at the machine running the bridge:

```
sim_vehicle.py -v ArduCopter -f quad --model JSON:127.0.0.1 --map --console
```

`--model JSON:<ip>` is the address SITL SENDS to; the bridge always replies to
whatever address a servo packet arrived from, so nothing needs configuring on
this side. Other flags:

| flag | default | meaning |
|---|---|---|
| `--target` | `ardupilot` | autopilot wire protocol; see [Targets](#targets) |
| `--port` | `9002` | UDP listen port (`9001` for Betaflight) |
| `--host` | `0.0.0.0` | bind address |
| `--rpm-log` | off | per-rotor CSV (see [No RPM lane](#no-rpm-lane)) |
| `--log-level` | `INFO` | `DEBUG` traces every duplicate and gap |

Relevant ArduPilot parameters: `SIM_RATE_HZ` sets the frame rate the bridge is
told to step at (keep it above the vehicle loop rate — 400 Hz on Copter);
`SERVO_32_ENABLE = 1` switches SITL to the 32-channel servo packet, which you
need if any rotor is on servo channel 17–32.

## Targets

The physics — the FMU step, the disc kinematics, the wrench, the 6DOF, the rotor
log — is one class, `targets.base.PhysicsCore`, and it knows nothing about any
autopilot. A target supplies three seams around it:

* a **channel source**: PWM microseconds for a 1-based output channel, which is
  exactly what `VehicleConfig.throttles` already consumes;
* a **frame clock**: an inbound packet becomes `dt` plus an
  advance/duplicate/restart decision;
* a **state encoder**: a `StateSample` — always in the bridge's own frames —
  becomes the outbound bytes.

| | ArduPilot | Betaflight |
|---|---|---|
| module | `targets/ardupilot.py` | `targets/betaflight.py` |
| in | `servo_packet_16/32`, UDP 9002 | `servo_packet_raw`, UDP 9001 |
| out | JSON state, back to the sender | `fdm_packet`, UDP 9003 |
| clock | lockstep on `frame_count` | soft real time, the bridge's own |
| RC | not needed | `rc_packet`, UDP 9004 — the mission script's job |

Betaflight's frame conventions are NOT the bridge's, and every conversion is
derived from Betaflight master in `targets/betaflight.py`'s module docstring —
including two that are easy to get backwards and were caught only by flying it
(the gyro yaw sign, and the pacing of the FDM feed, which IS the flight
controller's clock). Read that docstring before changing anything in there.

## Frames

This is the part to get right before anything else.

* **World is NED** — x North, y East, **z DOWN**. Gravity is `(0, 0, +9.80665)`.
  Position is metres from the SITL home origin; velocity is m/s NED. Both go on
  the wire unchanged.
* **Body is FRD** — x forward, y right, **z DOWN**. A copter's rotors thrust
  along `[0, 0, -1]` and "up" is negative z everywhere in this package.
* **The vehicle YAML's geometry is body FRD.** `position` and `axis` for every
  rotor are expressed in that frame.
* **The quaternion on the wire is `(w, x, y, z)`** for the body→NED rotation,
  which is what ArduPilot's `Quaternion::rotation_matrix` expects when it fills
  its body-to-earth `dcm`. The bridge sends `quaternion`, not `attitude`;
  ArduPilot prefers the quaternion when both are present.
* **`imu.accel_body` is SPECIFIC FORCE**, not kinematic acceleration — it is
  what an accelerometer reads, so a level vehicle at rest reports
  `(0, 0, -9.80665)`. Verified at the definition site in
  `libraries/SITL/SIM_Aircraft.cpp`:

  ```cpp
  accel_body = dcm.transposed() * (accel_earth + Vector3f(0.0f, 0.0f, -GRAVITY_MSS));
  ```

## Vehicle YAML

`examples/quad_5inch_x.yaml` is a complete, commented generic 5" quad in
ArduPilot's `FRAME_CLASS=1 FRAME_TYPE=1` (quad X) motor order, with the mapping
derived from `AP_MotorsMatrix.cpp` and cited inline. Reference:

### `vehicle:`

| key | required | meaning |
|---|---|---|
| `name` | no | label for the logs |
| `mass_kg` | yes | > 0 |
| `inertia_principal` | one of | `[Ixx, Iyy, Izz]` about the CG, all > 0 |
| `inertia` | one of | full symmetric positive-definite 3×3, kg·m² |
| `drag_area_m2` | no | scalar or `[x, y, z]` body-axis Cd·A; default 0 |

### `environment:`

| key | default | meaning |
|---|---|---|
| `air_density_kg_m3` | `1.225` | constant, fed to the FMU every step |
| `ambient_temp_C` | `25.0` | constant, fed to the FMU every step |
| `wind_ned_m_s` | `[0,0,0]` | steady wind, NED |

### `ground:`

| key | default | meaning |
|---|---|---|
| `enabled` | `true` | flat-plane contact so the vehicle can sit, arm and land |
| `z_ned_m` | `0.0` | plane altitude in NED, so 0 is the home origin |

### `fmu:`

Optional in full — the defaults are the normative sign conventions. See
[Sign conventions](#sign-conventions).

| key | default | values |
|---|---|---|
| `v_axial_sign` | `climb_positive` | `climb_positive`, `dot_product` |
| `inplane_sign` | `drag_positive` | `drag_positive`, `subtracted` |
| `torque_convention` | `signed` | `signed`, `magnitude` |
| `negate_reaction_torque` | `false` | boolean |

### `rotors:` — a list, one entry per rotor

| key | required | meaning |
|---|---|---|
| `rotor_index` | yes | index into the FMU's flat `0..N-1` rotor arrays |
| `servo_channel` | yes | **1-based** ArduPilot output; `SERVO1_FUNCTION` → 1 |
| `pwm_min`, `pwm_max` | yes | channel calibration in microseconds |
| `reversed` | no | flips the normalised throttle; default `false` |
| `spin_arm_threshold` | no | throttle below this becomes a hard 0; default 0 |
| `position` | yes | `[x, y, z]` m, body FRD, from the CG |
| `axis` | yes | unit thrust direction, body FRD |
| `sense` | yes | `+1` CCW viewed against the thrust direction, else `-1` |
| `name` | no | label for the logs |

`rotor_index` must cover `0..N-1` exactly once and `servo_channel` must be
unique: the map is bijective and explicit because ArduPilot permits motor
functions on arbitrary servo outputs, so nothing may be assumed positionally.
Validation failures name the offending YAML path.

PWM becomes throttle as
`clamp((pwm - pwm_min) / (pwm_max - pwm_min), 0, 1)`, then the reversal, then
the spin-arm threshold — in that order.

## Protocol behaviour

One physics advance per NEW `frame_count`. A duplicate packet gets a
**byte-identical** resend of the previous reply and advances nothing. A
`frame_count` regression means SITL restarted, so the bridge does a full restart:
`fmi3Reset` plus re-initialisation, the 6DOF re-seeded, the clock back to zero.
A forward gap advances ONE catch-up step of `gap / frame_rate`, capped just under
100 ms. Reply timestamps are end-of-step.

The cap is `0.0995 s`, **strictly below** 100 ms rather than equal to it, because
ArduPilot's predicate is exclusive: `recv_fdm` runs
`if (is_positive(deltat) && deltat < 0.1)` before calling `time_advance()`. A
reply carrying a timestamp delta of exactly 0.1 s advances `time_now_us` but
never reaches `time_advance()`, so the catch-up frame the cap exists to deliver
would be silently dropped by the very consumer it was sized for.

Coupling is one-sample partitioned ZOH: set the FMU's inputs, one `fmi3DoStep`,
read the wrench, then advance the 6DOF with that wrench held constant. RK4 stage
queries back into the FMU would violate FMI 3 Step Mode's set-then-get rules, so
the 6DOF sub-steps against a frozen wrench instead. Drag and the gyroscopic term
are state-dependent and stay inside the integrator; only the propulsion wrench is
frozen.

The whole output block is read in **two** FMI calls per frame — one
`fmi3GetFloat64` naming every Float64 output, one `fmi3GetBoolean` for the
envelope flags. The DLL computes outputs lazily and each *request* pays one bus
solve (~23.5 µs on the core implementation's bench) regardless of how many
variables it names, so reading lane by lane would multiply the per-frame solve
cost by the number of lanes: ~9 ms/s batched against ~66 ms/s for the seven-lane
schema-3 block at 400 Hz.

### Verified against ArduPilot master (2026-08-29)

Read from `libraries/SITL/SIM_JSON.h`, `SIM_JSON.cpp` and
`examples/JSON/readme.md`. Three things are worth writing down because they are
easy to get wrong and fail silently:

1. **The reply needs a LEADING newline as well as a trailing one.** `recv_fdm`
   turns every `'\n'` into NUL and parses the text between the LAST TWO NULs. A
   datagram with only a trailing newline has one NUL, `memrchr` for the second
   returns `nullptr`, and the frame is dropped without a word.
2. **`parse_sensors` is a `strstr` scanner, not a JSON parser.** It finds the
   section, then the key after it, then skips exactly `strlen(key) + 2` bytes
   past `":` and calls `strtod`. So the payload must use compact separators, and
   a key that is a substring of another key resolves by POSITION in the string,
   not by keytable order — `velocity` inside `velocity_wind` is the live hazard.
   `tests/ardupilot_parser.py` re-implements the whole scanner and
   `tests/test_protocol.py` proves our payload resolves correctly through it.
3. **The resend interval is ~1 second, not the 10 seconds the readme claims.**
   `SIM_JSON.cpp` uses `UDP_TIMEOUT_MS = 100` and resends when `wait_ms > 1000`.
   The readme's "after 10 seconds" is stale. It changes nothing about the
   bridge's behaviour — duplicates are handled either way — but it is the number
   to expect in a stall.

ArduPilot's own `deltat < 0.1` guard in `recv_fdm` means a step at or above
100 ms is ignored by SITL entirely — the same ceiling the spec sets for the
catch-up step, which is why the bridge caps strictly inside it.

## The FMU contract

Decision 9 makes the Appendix-A variable table normative, so the bridge
**refuses to load** an FMU that does not declare every variable it touches, and
the error names what is missing. It substitutes nothing: a fabricated zero
`force_inplane_N` would silently delete the H-force from every wrench, and a
fabricated all-true `rotor_in_envelope` would report a clamped, out-of-envelope
solve as trustworthy. Both would fly, and both would lie.

Required: `throttle`, `v_axial_m_s`, `v_edge_m_s`, `air_density_kg_m3`,
`ambient_temp_C`, `use_vehicle_frame`, `thrust_N`, `torque_Nm`,
`force_inplane_N`, `rpm`, `voltage_bus_V`, `current_bus_A`, `battery_soc`,
`rotor_in_envelope`, `all_in_envelope`. Extents are checked too — the per-rotor
arrays against the vehicle YAML's rotor count, the scalars against 1.

This is the bridge's own contract surface, a subset of the FMU variable table:
the vehicle-mode variables (`v_body_m_s`, `rotor_position_m`, …) are not listed
because the bridge runs the FMU in disc mode and never touches them. Validating
the whole table against an export is the cross-language contract test's job.

## Sign conventions

These conventions are normative and are what the bridge does by default.
The `fmu:` block can be omitted entirely; every value below is the default.

```
v_axial_i = −(U_i · n̂_i)            positive in a climb, negative in descent/windmill
F_i       = T_i n̂_i + H_i ê_i       ê_i is the air-relative in-plane direction,
                                     so a positive H_i is a DRAG
M_total   = Σ_i ( r_i × F_i + Q_i n̂_i )
                                     Q_i is the FMU output torque_Nm[i] = −s_i Q_i^aero,
                                     the SIGNED reaction on the airframe, applied
                                     directly — s_i does NOT reappear in the sum
```

The reaction sign is independently confirmed by ArduPilot: a rotor turning
right-handed about `n̂` puts `−Q^aero n̂` on the airframe, and
`AP_MOTORS_MATRIX_YAW_FACTOR_CCW = +1` requires a CCW rotor to yaw a copter
nose-right (`+z` FRD) — which is exactly what `−Q^aero n̂` gives for
`n̂ = (0,0,−1)`.

Rev 2 had all four of these backwards (`v_axial = +U·n̂`, `F = T n̂ − H ê`, and an
`s_i` in the moment sum), which respectively read a climb as a descent, turned
the H-force into a thrust, and double-applied the rotation sense. Those readings
survive only as **non-default escape hatches**, so an export built against rev 2
can still be flown:

| toggle | default (rev 2.1) | escape hatch (withdrawn rev 2) |
|---|---|---|
| `v_axial_sign` | `climb_positive` | `dot_product` — reads a climb as a descent |
| `inplane_sign` | `drag_positive` | `subtracted` — makes the H-force a thrust |
| `torque_convention` | `signed` | `magnitude` — for an FMU emitting an unsigned aero magnitude; the bridge then forms `−s_i·\|torque_Nm[i]\|` itself |
| `negate_reaction_torque` | `false` | `true` — last-resort flip if an export's axial reaction still comes out backwards in SITL |

## No RPM lane

`keytable[36]` in `SIM_JSON.h` carries timestamp, IMU, position/attitude,
velocity, six rangefinders, twelve RC channels, wind, airspeed and battery — and
nothing rotational. **Per-rotor RPM cannot reach the flight log through this
protocol.** `--rpm-log` writes it alongside the flight instead: one wide CSV row
per physics frame with `timestamp_s`, `frame_count`, `dt_s`, the bus
voltage/current/SOC, and per-rotor `throttle`, `rpm`, `thrust_N`, `torque_Nm`,
`force_inplane_N`, `v_axial_m_s`, `v_edge_m_s` and `in_envelope`. Join it to the
ArduPilot log on the timestamp.

## Limitations

* **No RPM (or per-rotor anything) back to the firmware.** See above.
* **ZOH coupling.** The rotor wrench is constant across a frame. At 400 Hz that
  is standard co-simulation practice, but it is a first-order coupling and the
  effective phase lag grows as `SIM_RATE_HZ` falls.
* **Motor temperatures are equilibrium values** carried by the FMU's map, baked
  at export. The bridge neither integrates nor uses them.
* **Steady wind only**, and it is not forwarded to ArduPilot. The bridge applies
  `environment.wind_ned_m_s` to its own aerodynamics and reports the resulting
  `airspeed`, which is the lane the firmware actually consumes. No gusts, no
  turbulence, no `velocity_wind` field (sending it would risk ArduPilot's
  `strstr` parser reading it as `velocity` — see Protocol behaviour).
* **Constant air density.** No altitude model; `environment.air_density_kg_m3`
  goes to the FMU unchanged every step.
* **The ground model is a plane, not landing gear.** The spec does not cover
  ground contact at all, but the JSON backend gives ArduPilot no ground model of
  its own and without one the vehicle free-falls before it can arm. The bridge
  mirrors ArduPilot's own copter `GROUND_BEHAVIOR_NO_MOVEMENT`: while resting,
  downward acceleration is clipped, roll and pitch are levelled, heading is kept
  and the rates are zeroed. Enough to arm, lift off and land. Not a crash model,
  no ground effect, no slope.
* **No sensor noise or bias.** The reply is the clean physics state; ArduPilot's
  own SITL noise parameters still apply on its side.

## What only U5 can prove

The test suite runs with no network, no ArduPilot binary and no FMU: it drives
the real `FmuRotorModel` over a stub FMI 3 slave, so it proves the wire format,
the state machine, the kinematics, the wrench mapping and the FMI call sequence
— and nothing about a real export. These are U5's to settle on the SITL flight
gate:

* that the export actually follows decision 5 rev 2.1, so none of the
  [escape hatches](#sign-conventions-decision-5-rev-21) is needed;
* that hover throttle lands inside the product's hover-prediction band;
* that battery sag is visible and monotone with load in the ArduPilot log;
* that lockstep sustains ≥ 400 Hz with the real FMU in the loop (the bridge's own
  overhead is not the constraint — measured 2026-08-29 on the dev laptop, the
  full UDP round trip against a stub model ran ~1900 frames/s);
* that the FMU's variable names, extents and Initialization Mode behaviour match
  Appendix A as exported.

## Tests

```
cd backend/sdks/python
python -m pytest tests/sitl -ra --tb=short
```

149 tests, ~2 s, no network. Coverage by file:

| file | what it pins |
|---|---|
| `test_protocol.py` | both packet sizes, magic/length rejection, and the state JSON checked through a transcription of ArduPilot's own `parse_sensors` |
| `test_vehicle.py` | PWM→throttle including reversal and the spin threshold, and every validation rejection |
| `test_kinematics.py` | decision 5 against hand-computed hover, climb, forward flight, pure yaw rate and canted-rotor cases |
| `test_rigidbody.py` | the accelerometer convention, free fall, hover, gyroscopic coupling, drag, wind, ground |
| `test_state_machine.py` | every clause of decision 12: new/duplicate/regression/gap/cap/rate-change |
| `test_step_path.py` | the full frame path over the stub slave, incl. wrench mapping, battery feedback and the rotor CSV |
