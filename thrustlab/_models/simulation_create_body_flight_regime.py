from enum import Enum


class SimulationCreateBodyFlightRegime(str, Enum):
    FORCED_AIR = "forced_air"
    PROP_WASH_MILD = "prop_wash_mild"
    PROP_WASH_STRONG = "prop_wash_strong"
    STATIC_BENCH = "static_bench"

    def __str__(self) -> str:
        return str(self.value)
