"""``python -m thrustlab.sitl`` — run the SITL external-physics backend.

``--target ardupilot`` (the default) is the original behaviour, flags included.
``--target betaflight`` swaps the protocol seams for Betaflight SITL's binary
UDP triple; see :mod:`thrustlab.sitl.targets.betaflight`.
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
from pathlib import Path
from types import FrameType

from .bridge import Bridge, BridgeServer
from .fmu import FmuError, FmuRotorModel
from .rpmlog import RotorLog
from .targets import betaflight as bf
from .vehicle import VehicleConfig, VehicleConfigError, load_vehicle_config

logger = logging.getLogger("thrustlab.sitl")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m thrustlab.sitl",
        description=(
            "ArduPilot SITL external-physics backend driven by a ThrustLab FMI 3.0 "
            "per-rotor propulsion FMU. Start this first, then: "
            "sim_vehicle.py -v ArduCopter -f quad --model JSON:127.0.0.1 --map --console"
        ),
    )
    parser.add_argument("--fmu", required=True, type=Path, help="path to the exported .fmu")
    parser.add_argument("--vehicle", required=True, type=Path, help="path to the vehicle YAML")
    parser.add_argument(
        "--target",
        default="ardupilot",
        choices=["ardupilot", "betaflight"],
        help="autopilot wire protocol (default ardupilot)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="UDP listen port (default 9002 for ArduPilot, 9001 for Betaflight)",
    )
    parser.add_argument("--host", default="0.0.0.0", help="UDP bind address (default 0.0.0.0)")
    parser.add_argument(
        "--rpm-log",
        type=Path,
        default=None,
        help="write per-rotor RPM/thrust/torque CSV here (the wire protocol has no RPM lane)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="python logging level (default INFO)",
    )

    group = parser.add_argument_group(
        "betaflight", "ignored unless --target betaflight"
    )
    group.add_argument(
        "--sitl-host",
        default="127.0.0.1",
        help="where the fdm_packet goes (default 127.0.0.1)",
    )
    group.add_argument(
        "--state-port",
        type=int,
        default=bf.PORT_STATE,
        help=f"fdm_packet destination port (default {bf.PORT_STATE})",
    )
    group.add_argument(
        "--step",
        type=float,
        default=0.004,
        help=(
            "sim seconds per fdm_packet (default 0.004). Betaflight stops "
            "tracking simRate at 0.02, so keep this well under it"
        ),
    )
    group.add_argument(
        "--speedup",
        type=float,
        default=1.0,
        help="sim seconds per wall second (default 1.0 — Betaflight SITL is soft real time)",
    )
    group.add_argument(
        "--truth-port",
        type=int,
        default=None,
        help="UDP port for a ground-truth JSON fan-out (default off)",
    )
    group.add_argument("--home-lat", type=float, default=-27.5, help="home latitude, degrees")
    group.add_argument("--home-lon", type=float, default=153.0, help="home longitude, degrees")
    group.add_argument("--home-alt", type=float, default=30.0, help="home altitude, metres")
    return parser


def _run_betaflight(args: argparse.Namespace, vehicle: VehicleConfig, model, rotor_log):
    bridge = bf.BetaflightBridge(
        vehicle,
        model,
        home=bf.HomeOrigin(
            latitude_deg=args.home_lat,
            longitude_deg=args.home_lon,
            altitude_m=args.home_alt,
        ),
        rotor_log=rotor_log,
    )
    server = bf.BetaflightServer(
        bridge,
        host=args.host if args.host != "0.0.0.0" else "0.0.0.0",
        motor_port=args.port if args.port is not None else bf.PORT_PWM_RAW,
        sitl_host=args.sitl_host,
        state_port=args.state_port,
        step_s=args.step,
        speedup=args.speedup,
        truth_port=args.truth_port,
    )
    return bridge, server


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )

    try:
        vehicle = load_vehicle_config(args.vehicle)
    except VehicleConfigError as exc:
        logger.error("%s", exc)
        return 2

    logger.info(
        "vehicle %s: %d rotors, %.3f kg, servo channels %s",
        vehicle.name or args.vehicle.name,
        vehicle.rotor_count,
        vehicle.mass_kg,
        [r.servo_channel for r in vehicle.rotors],
    )
    if args.target == "ardupilot" and vehicle.max_servo_channel > 16:
        logger.warning(
            "servo channel %d needs the 32-channel servo packet; set SERVO_32_ENABLE=1 in "
            "ArduPilot or the bridge will reject every frame",
            vehicle.max_servo_channel,
        )
    if args.target == "betaflight" and vehicle.max_servo_channel > 16:
        logger.error(
            "output channel %d is outside the 16 a Betaflight servo_packet_raw carries",
            vehicle.max_servo_channel,
        )
        return 2

    try:
        model = FmuRotorModel.from_file(
            args.fmu,
            vehicle.rotor_count,
            air_density_kg_m3=vehicle.air_density_kg_m3,
            ambient_temp_C=vehicle.ambient_temp_C,
        )
    except FmuError as exc:
        logger.error("%s", exc)
        return 3

    rotor_log = RotorLog(args.rpm_log, vehicle.rotor_count) if args.rpm_log else None
    if args.target == "betaflight":
        bridge, server = _run_betaflight(args, vehicle, model, rotor_log)
    else:
        bridge = Bridge(vehicle, model, rotor_log=rotor_log)
        server = BridgeServer(
            bridge, host=args.host, port=args.port if args.port is not None else 9002
        )

    def _shutdown(signum: int, frame: FrameType | None) -> None:
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, _shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _shutdown)

    try:
        server.open()
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("shutting down")
    finally:
        server.close()
        if rotor_log is not None:
            rotor_log.close()
            logger.info("wrote %d rotor log rows to %s", rotor_log.rows_written, rotor_log.path)
        try:
            model.terminate()
        except FmuError as exc:  # pragma: no cover - shutdown path
            logger.warning("FMU terminate failed: %s", exc)
        counters = bridge.counters
        logger.info(
            "packets=%d advanced=%d duplicates=%d restarts=%d skipped=%d capped=%d malformed=%d",
            counters.packets_received,
            counters.frames_advanced,
            counters.duplicates_resent,
            counters.restarts,
            counters.frames_skipped,
            counters.steps_capped,
            counters.malformed_packets,
        )
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
