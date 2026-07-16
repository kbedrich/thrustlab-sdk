from enum import Enum


class SimulationCreateBodyCoolingSourceType0(str, Enum):
    AIRSPEED = "airspeed"
    FORCED_AIR = "forced_air"
    PROP_SLIPSTREAM = "prop_slipstream"
    STATIC = "static"

    def __str__(self) -> str:
        return str(self.value)
