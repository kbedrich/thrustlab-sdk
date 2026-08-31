"""Betaflight SITL's own receive side, re-implemented for the tests.

The bridge's encoder is only correct if the FLIGHT CONTROLLER recovers the truth
from it, so the tests decode with this module rather than restating the
encoder's arithmetic back at itself.  Every function is a transcription of
Betaflight master ``6aeffc36``; the source line is named in each docstring.

Nothing here may import the bridge.
"""

from __future__ import annotations

import math

GRAVITY = 9.80665


def fc_accel(packet_accel: tuple[float, float, float]) -> tuple[float, float, float]:
    """``sitl.c::updateState``: all three accelerometer axes are negated on read.

        x = constrain(-pkt->imu_linear_acceleration_xyz[0] * ACC_SCALE, ...)

    The result is the specific force in the flight controller's own body frame
    (FLU / NWU-body), so a level vehicle at rest gives ``(0, 0, +g)``.
    """
    return (-packet_accel[0], -packet_accel[1], -packet_accel[2])


def fc_gyro(packet_gyro: tuple[float, float, float]) -> tuple[float, float, float]:
    """``sitl_gyro.h::sitlGyroBodyFromSim`` with ``gazeboBridge = true``.

        roll = +rpy[0];  pitch = -rpy[1];  yaw = +rpy[2];

    Pinned by ``src/test/unit/sitl_gyro_unittest.cc``, which asserts that a
    positive simulator yaw rate stays positive under the Gazebo bridge.

    The result is Betaflight's internal convention: roll right +, pitch
    nose-DOWN +, and yaw COUNTER-CLOCKWISE + — the last one despite the "CW
    viewed from above" annotation in ``sitl_gyro.h``, because ``mixer.c``
    negates the yaw PID sum before the mixer and a right-stick command lands on
    the counter-clockwise diagonal.  A flight with the un-negated rate diverged
    with the mixer saturated; see ``targets/betaflight.py``'s docstring.
    """
    return (packet_gyro[0], -packet_gyro[1], packet_gyro[2])


def fc_attitude_quaternion(
    packet_quaternion: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    """``sitl.c::updateState``, the ``ENABLE_GAZEBO_BRIDGE`` quaternion branch.

        pktQy = -q[2];  pktQz = -q[3];   k = 0.70710678f;
        attQw = k * (pktQw - pktQz);   attQx = k * (pktQx - pktQy);
        attQy = k * (pktQy + pktQx);   attQz = k * (pktQz + pktQw);

    i.e. ``Rz(π/2) ⊗ conj_x180(q_packet)``.  The result is the body(FLU) ->
    world(NWU) rotation the flight controller flies on.
    """
    qw = packet_quaternion[0]
    qx = packet_quaternion[1]
    qy = -packet_quaternion[2]
    qz = -packet_quaternion[3]
    k = math.sqrt(0.5)
    return (k * (qw - qz), k * (qx - qy), k * (qy + qx), k * (qz + qw))


def fc_baro_pressure_pa(packet_altitude_m: float) -> int:
    """``sitl.c``: the Gazebo bridge IGNORES ``pkt->pressure``.

        const double altMeters = pkt->position_xyz[2];
        pressure = (int32_t)(101325.0 * pow(1.0 - 2.25577e-5 * altMeters, 5.25588));
    """
    return int(101325.0 * math.pow(1.0 - 2.25577e-5 * packet_altitude_m, 5.25588))


def fc_gps_degrees(
    packet_longitude: float,
    packet_latitude: float,
    origin_longitude: float,
    origin_latitude: float,
) -> tuple[float, float]:
    """``sitl.c``, ``USE_VIRTUAL_GPS`` + ``ENABLE_GAZEBO_BRIDGE``.

        correctedLat = 2.0 * originLat - latitude;
        correctedLon = 2.0 * originLon - longitude;

    ``origin`` is latched from the FIRST fdm_packet of the run.  Returns
    ``(longitude, latitude)``.
    """
    return (
        2.0 * origin_longitude - packet_longitude,
        2.0 * origin_latitude - packet_latitude,
    )


def fc_gps_is_valid(packet_longitude: float, packet_latitude: float) -> bool:
    """``sitl.c``: ``if (fabs(latitude) <= 90.0 && fabs(longitude) <= 180.0)``."""
    return abs(packet_latitude) <= 90.0 and abs(packet_longitude) <= 180.0


def fc_velocity_ned(packet_velocity: tuple[float, float, float]) -> tuple[float, float, float]:
    """``sitl.c``: ``velocity_xyz`` is ENU, and the flight controller reads

        setVirtualGPS(..., pkt->velocity_xyz[1],   // velN
                           pkt->velocity_xyz[0],   // velE
                          -pkt->velocity_xyz[2]);  // velD
    """
    return (packet_velocity[1], packet_velocity[0], -packet_velocity[2])


def fc_ground_course_deg(packet_velocity: tuple[float, float, float]) -> float:
    """``sitl.c``: ``course = atan2(velocity_xyz[0], velocity_xyz[1]) * RAD2DEG``."""
    course = math.degrees(math.atan2(packet_velocity[0], packet_velocity[1]))
    return course + 360.0 if course < 0.0 else course


def fc_updates_sim_rate(delta_sim_s: float) -> bool:
    """``sitl.c``: ``if (deltaSim < 0.02 && deltaSim > 0)``."""
    return 0.0 < delta_sim_s < 0.02
