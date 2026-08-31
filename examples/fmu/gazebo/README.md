# Gazebo (gz-sim) — your exported powertrain as a System plugin

Wire your ThrustLab FMU into a gz-sim vehicle: the plugin reads each rotor's
air-relative velocity from the physics world, asks the FMU for per-rotor
thrust, in-plane force and reaction torque, and applies them to the rotor
links — spin-up dynamics, battery state and envelope flags included.

## What you need

- An exported FMU, **unzipped** (`unzip ../validation-quad.fmu -d validation-quad/`).
- The `fmu-gz-plugin` ThrustlabFmuSystem plugin, built against gz-sim ≥ 9
  (see its README for the CMake build; it dlopens the FMU's own
  `binaries/x86_64-linux/*.so`).

## Wire it into a world

Start from `quad_fmu.sdf` in this directory (an x500-class quad). The plugin
block on the vehicle model:

```xml
<plugin filename="thrustlab-fmu-gz-system"
        name="thrustlab::fmu_gz::ThrustlabFmuSystem">
  <fmu_dir>${TL_FMU_DIR}</fmu_dir>
  <command_topic>/quad/command/throttle</command_topic>
  <command_field>position</command_field>
  <air_density>1.225</air_density>
  <rotor>
    <index>0</index>
    <link_name>rotor_0</link_name>
    <joint_name>rotor_0_joint</joint_name>
    <actuator_index>0</actuator_index>
    <sense>ccw</sense>
  </rotor>
  <!-- rotors 1-3 alike; senses per your airframe -->
</plugin>
```

Rotor `index` order and `sense` must agree with the FMU's `rotor_manifest`
(constant String output; also printed in the FMU's README.md). The rotor
links' poses give the plugin its moment arms — match your airframe.

## Run

```sh
export GZ_SIM_SYSTEM_PLUGIN_PATH=/path/to/fmu-gz-plugin/build
TL_FMU_DIR=$PWD/my-powertrain gz sim -r quad_fmu.sdf
```

Command per-rotor throttle (0–1) as a `gz.msgs.Actuators` message on the
command topic:

```sh
gz topic -t /quad/command/throttle -m gz.msgs.Actuators \
  -p 'position: [0.6, 0.6, 0.6, 0.6]'
```

Headless (`gz sim -s -r --iterations 4000 quad_fmu.sdf`) works the same and
is what the plugin's own smoke suite drives.

For an ArduPilot- or PX4-controlled Gazebo vehicle, keep their standard
Gazebo integration for control surfaces and use this plugin as the
propulsion + battery physics; the ArduPilot JSON bridge
(`thrustlab.sitl`) is the lighter path when you don't need a 3D world.

## The bundled FMU

This example ships with a ready-to-fly FMU exported from ThrustLab
(`../validation-quad.fmu`). The exact powertrain it reproduces is documented
in the archive's own `resources/README.md`; unzip the FMU to read it. To
recreate the FMU, build the same powertrain in ThrustLab or through the
API/SDK, then export it with **Export → FMU** or `client.fmu`; your export
will fly these examples identically.
