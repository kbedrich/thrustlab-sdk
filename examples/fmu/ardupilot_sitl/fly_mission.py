"""Fly a multi-leg AUTO mission against a running ArduPilot SITL whose physics
is your exported ThrustLab FMU (via thrustlab.sitl), recording MAVLink
telemetry for the plot script.

Usage: python fly_mission.py [--connect tcp:127.0.0.1:5760] [--out-dir .]

Writes <out-dir>/mission_telemetry.csv and <out-dir>/mission_events.csv; the
per-rotor truth (rpm, thrust, bus V/I, SOC) is the bridge's own --rpm-log CSV.
"""
import argparse
import csv
import math
import sys
import time
from pathlib import Path

from pymavlink import mavutil

M_PER_DEG_LAT = 111320.0
WALL_CAP_S = 900.0


def build_mission(home_lat, home_lon, speed_scale=1.0):
    frame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT
    mav = mavutil.mavlink
    items = []

    def spd(m_s):
        return max(2.0, m_s * speed_scale)

    def add(cmd, p1=0, p2=0, p3=0, p4=0, dn=0.0, de=0.0, alt=0.0):
        lat = home_lat + dn / M_PER_DEG_LAT
        lon = home_lon + de / (M_PER_DEG_LAT * math.cos(math.radians(home_lat)))
        items.append((len(items), frame, cmd, p1, p2, p3, p4,
                      int(lat * 1e7), int(lon * 1e7), float(alt)))

    add(mav.MAV_CMD_NAV_WAYPOINT)                                   # home slot
    add(mav.MAV_CMD_NAV_TAKEOFF, alt=10.0)
    add(mav.MAV_CMD_DO_CHANGE_SPEED, p1=1, p2=spd(13.0))
    add(mav.MAV_CMD_NAV_WAYPOINT, dn=220.0, de=0.0, alt=15.0)       # fast dash
    add(mav.MAV_CMD_DO_CHANGE_SPEED, p1=1, p2=spd(6.0))
    add(mav.MAV_CMD_NAV_WAYPOINT, dn=220.0, de=140.0, alt=32.0)     # slow climb
    add(mav.MAV_CMD_NAV_LOITER_TURNS, p1=2, p3=25.0, dn=220.0, de=140.0, alt=32.0)
    add(mav.MAV_CMD_DO_CHANGE_SPEED, p1=1, p2=spd(14.0))
    add(mav.MAV_CMD_NAV_WAYPOINT, dn=60.0, de=60.0, alt=14.0)       # fast descent
    add(mav.MAV_CMD_DO_CHANGE_SPEED, p1=1, p2=spd(5.0))
    add(mav.MAV_CMD_NAV_WAYPOINT, dn=25.0, de=0.0, alt=8.0)         # slow approach
    add(mav.MAV_CMD_NAV_RETURN_TO_LAUNCH)
    return items


def upload_mission(m, items):
    m.mav.mission_clear_all_send(m.target_system, m.target_component)
    m.recv_match(type="MISSION_ACK", blocking=True, timeout=5)
    m.mav.mission_count_send(m.target_system, m.target_component, len(items))
    t0 = time.time()
    while time.time() - t0 < 60:
        msg = m.recv_match(
            type=["MISSION_REQUEST", "MISSION_REQUEST_INT", "MISSION_ACK"],
            blocking=True, timeout=10,
        )
        if msg is None:
            raise RuntimeError("mission upload stalled")
        if msg.get_type() == "MISSION_ACK":
            if msg.type == mavutil.mavlink.MAV_MISSION_ACCEPTED:
                print(f"mission accepted ({len(items)} items)", flush=True)
                return
            raise RuntimeError(f"mission rejected: ack type {msg.type}")
        s, frame, cmd, p1, p2, p3, p4, lat, lon, alt = items[msg.seq]
        m.mav.mission_item_int_send(
            m.target_system, m.target_component, s, frame, cmd,
            1 if s == 0 else 0, 1, p1, p2, p3, p4, lat, lon, alt,
        )
    raise RuntimeError("mission upload timed out")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--connect", default="tcp:127.0.0.1:5760")
    ap.add_argument("--out-dir", type=Path, default=Path("."))
    ap.add_argument("--speed-scale", type=float, default=1.0,
                    help="scale every mission leg speed (floor 2 m/s). A coax "
                         "export's edgewise envelope is tighter than a solo "
                         "rotor's; ~0.3 keeps a Y6 inside it.")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    m = mavutil.mavlink_connection(args.connect, source_system=250)
    m.wait_heartbeat(timeout=120)
    print(f"heartbeat from sys {m.target_system}", flush=True)

    # Let the EKF settle; keep the streams coming at 10 Hz.
    t0 = time.time()
    while time.time() - t0 < 40:
        m.mav.request_data_stream_send(
            m.target_system, m.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1,
        )
        st = m.recv_match(type="STATUSTEXT", blocking=False)
        if st:
            print("statustext:", st.text, flush=True)
        time.sleep(0.5)

    # Home = where the vehicle sits now.
    gpi = m.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=10)
    home_lat, home_lon = gpi.lat / 1e7, gpi.lon / 1e7
    upload_mission(m, build_mission(home_lat, home_lon, args.speed_scale))

    m.set_mode("GUIDED")
    # GUIDED refuses to arm until the EKF is actually fusing GPS, and how
    # long that takes in SIM time depends on the machine (a heavy FMU lowers
    # the effective speedup). Retry instead of racing, and surface every
    # refusal text instead of hanging in motors_armed_wait().
    arm_deadline = time.time() + 300
    armed = False
    while not armed:
        if time.time() > arm_deadline:
            raise RuntimeError("arming timed out — see the refusal texts above")
        m.arducopter_arm()
        drain_until = time.time() + 5.0
        while time.time() < drain_until:
            msg = m.recv_match(type=["HEARTBEAT", "STATUSTEXT"],
                               blocking=True, timeout=1)
            if msg is None:
                continue
            if msg.get_type() == "STATUSTEXT":
                print("statustext:", msg.text, flush=True)
            elif (msg.get_srcSystem() == m.target_system
                  and msg.base_mode
                  & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED):
                armed = True
                break
    print("armed", flush=True)
    m.set_mode("AUTO")
    for _ in range(10):
        m.mav.command_long_send(
            m.target_system, m.target_component,
            mavutil.mavlink.MAV_CMD_MISSION_START, 0, 0, 0, 0, 0, 0, 0, 0,
        )
        ack = m.recv_match(type="COMMAND_ACK", blocking=True, timeout=3)
        if ack and ack.command == mavutil.mavlink.MAV_CMD_MISSION_START:
            if ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                break
        time.sleep(1)

    tele = open(args.out_dir / "mission_telemetry.csv", "w", newline="")
    tw = csv.writer(tele)
    tw.writerow(["t_s", "lat", "lon", "alt_rel_m", "vn_m_s", "ve_m_s", "vd_m_s",
                 "groundspeed_m_s", "climb_m_s", "throttle_pct",
                 "roll_deg", "pitch_deg", "yaw_deg",
                 "voltage_V", "current_A", "battery_pct", "mode"])
    ev = open(args.out_dir / "mission_events.csv", "w", newline="")
    ew = csv.writer(ev)
    ew.writerow(["t_s", "kind", "detail"])

    last = {"vfr": None, "att": None, "sys": None, "mode": None, "gpi": None}
    armed, was_flying, rows = True, False, 0
    wall0 = time.time()

    def now_s():
        return last["gpi"].time_boot_ms / 1000.0 if last["gpi"] else 0.0

    while time.time() - wall0 < WALL_CAP_S:
        msg = m.recv_match(blocking=True, timeout=10)
        if msg is None:
            continue
        t = msg.get_type()
        if t == "VFR_HUD":
            last["vfr"] = msg
        elif t == "ATTITUDE":
            last["att"] = msg
        elif t == "SYS_STATUS":
            last["sys"] = msg
        elif t == "HEARTBEAT":
            mode = mavutil.mode_string_v10(msg)
            if mode != last["mode"]:
                ew.writerow([f"{now_s():.2f}", "mode", mode])
                print(f"mode -> {mode}", flush=True)
                last["mode"] = mode
            armed = bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
            if was_flying and not armed:
                print("disarmed after flight — mission complete", flush=True)
                break
        elif t == "MISSION_ITEM_REACHED":
            ew.writerow([f"{now_s():.2f}", "wp", msg.seq])
            print(f"reached wp {msg.seq}", flush=True)
        elif t == "STATUSTEXT":
            ew.writerow([f"{now_s():.2f}", "text", msg.text])
        elif t == "GLOBAL_POSITION_INT":
            last["gpi"] = msg
            if msg.relative_alt / 1000.0 > 2.0:
                was_flying = True
            vfr, att, s = last["vfr"], last["att"], last["sys"]
            tw.writerow([
                f"{msg.time_boot_ms / 1000.0:.2f}", msg.lat / 1e7, msg.lon / 1e7,
                f"{msg.relative_alt / 1000.0:.2f}",
                f"{msg.vx / 100.0:.2f}", f"{msg.vy / 100.0:.2f}", f"{msg.vz / 100.0:.2f}",
                f"{vfr.groundspeed:.2f}" if vfr else "",
                f"{vfr.climb:.2f}" if vfr else "",
                vfr.throttle if vfr else "",
                f"{math.degrees(att.roll):.1f}" if att else "",
                f"{math.degrees(att.pitch):.1f}" if att else "",
                f"{math.degrees(att.yaw):.1f}" if att else "",
                f"{s.voltage_battery / 1000.0:.3f}" if s else "",
                f"{s.current_battery / 100.0:.2f}" if s else "",
                s.battery_remaining if s else "",
                last["mode"] or "",
            ])
            rows += 1

    tele.close()
    ev.close()
    print(f"telemetry rows: {rows}", flush=True)
    if not was_flying:
        print("FAIL: never left the ground", flush=True)
        return 2
    if armed:
        print("FAIL: still armed at wall cap", flush=True)
        return 1
    print("MISSION COMPLETE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
