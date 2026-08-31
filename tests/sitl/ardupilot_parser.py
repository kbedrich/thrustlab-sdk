"""A faithful Python re-implementation of ArduPilot's JSON sensor parser.

This is the only way to prove wire compatibility without running SITL, and it
earns its keep: ``parse_sensors`` is a ``strstr`` walk, not a JSON parser, so a
payload that ``json.loads`` accepts can still be misread by ArduPilot.

Transcribed from ``libraries/SITL/SIM_JSON.cpp`` on ArduPilot master
(2026-08-29): :func:`frame_payload` is ``recv_fdm``'s newline framing,
:func:`find_value_text` is the keytable walk, :func:`parse_array` is the
template of the same name, and :func:`strtod` is the C library call the parser
leans on.
"""

from __future__ import annotations

import re

#: ``SIM_JSON.h::keytable``, in declaration order: (section, key, required).
KEYTABLE: tuple[tuple[str, str, bool], ...] = (
    ("", "timestamp", True),
    ("", "latitude", False),
    ("", "longitude", False),
    ("", "altitude", False),
    ("imu", "gyro", True),
    ("imu", "accel_body", True),
    ("", "position", False),
    ("", "attitude", False),
    ("", "quaternion", False),
    ("", "velocity", True),
    ("", "rng_1", False),
    ("", "rng_2", False),
    ("", "rng_3", False),
    ("", "rng_4", False),
    ("", "rng_5", False),
    ("", "rng_6", False),
    ("", "velocity_wind", False),
    ("windvane", "direction", False),
    ("windvane", "speed", False),
    ("", "airspeed", False),
    ("", "no_time_sync", False),
    ("", "no_lockstep", False),
    ("rc", "rc_1", False),
    ("rc", "rc_2", False),
    ("rc", "rc_3", False),
    ("rc", "rc_4", False),
    ("rc", "rc_5", False),
    ("rc", "rc_6", False),
    ("rc", "rc_7", False),
    ("rc", "rc_8", False),
    ("rc", "rc_9", False),
    ("rc", "rc_10", False),
    ("rc", "rc_11", False),
    ("rc", "rc_12", False),
    ("battery", "voltage", False),
    ("battery", "current", False),
)

_LEADING_NUMBER = re.compile(r"\s*[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


class FramingError(AssertionError):
    """``recv_fdm`` would have dropped this datagram before parsing it."""


def frame_payload(datagram: bytes) -> str:
    """``recv_fdm``'s framing: the text between the LAST two newlines.

    ``recv_fdm`` turns every ``'\\n'`` into NUL, takes ``p2 = memrchr(buf, 0)``
    and ``p1 = memrchr(buf, 0, p2 - buf)``, then parses from ``p1 + 1``.  A
    datagram with fewer than two newlines yields ``p1 == nullptr`` and is
    dropped without a word.
    """
    text = datagram.decode("ascii")
    last = text.rfind("\n")
    if last <= 0:
        raise FramingError(
            "ArduPilot would drop this datagram: recv_fdm needs a NUL (newline) "
            "before and after the JSON object"
        )
    previous = text.rfind("\n", 0, last)
    if previous < 0:
        raise FramingError(
            "ArduPilot would drop this datagram: only one newline, so memrchr for "
            "the second delimiter returns nullptr"
        )
    return text[previous + 1 : last]


def find_value_text(payload: str, section: str, key: str) -> str | None:
    """The keytable walk for one row, returning the text ``strtod`` would see."""
    section_at = payload.find(section)
    if section_at < 0:
        return None
    cursor = section_at + len(section) + 1
    key_at = payload.find(key, cursor)
    if key_at < 0:
        return None
    return payload[key_at + len(key) + 2 :]


def strtod(text: str) -> float:
    """``strtod``: skip leading space, parse the longest valid prefix."""
    match = _LEADING_NUMBER.match(text)
    if match is None:
        return 0.0
    return float(match.group(0))


def parse_array(text: str, count: int) -> list[float] | None:
    """``template <typename T> bool parse_array(const char*, T&, int)``."""
    values: list[float] = []
    cursor = 0
    for i in range(count):
        while cursor < len(text) and text[cursor] != "-" and not text[cursor].isdigit():
            cursor += 1
        if cursor >= len(text):
            return None
        values.append(strtod(text[cursor:]))
        while cursor < len(text) and text[cursor] not in ",]":
            cursor += 1
        if i < count - 1:
            if cursor >= len(text) or text[cursor] != ",":
                return None
            cursor += 1
    return values


def parse_sensors(datagram: bytes) -> dict[str, object]:
    """Every keytable row ArduPilot would resolve, keyed ``section/key``.

    Vector-valued rows come back as lists so a caller can compare against what
    it meant to send; anything absent is simply missing from the mapping.
    """
    payload = frame_payload(datagram)
    vector3 = {
        "imu/gyro",
        "imu/accel_body",
        "/position",
        "/attitude",
        "/velocity",
        "/velocity_wind",
    }
    result: dict[str, object] = {}
    for section, key, required in KEYTABLE:
        text = find_value_text(payload, section, key)
        name = f"{section}/{key}"
        if text is None:
            if required:
                raise AssertionError(f"ArduPilot requires {name} and could not find it")
            continue
        if name in vector3:
            parsed = parse_array(text, 3)
        elif name == "/quaternion":
            parsed = parse_array(text, 4)
        elif key in ("no_time_sync", "no_lockstep"):
            parsed = text.lower().startswith("true")
        else:
            parsed = strtod(text)
        result[name] = parsed
    return result
