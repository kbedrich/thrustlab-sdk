from enum import Enum


class DesignRequestTargetMode(str, Enum):
    POWER = "power"
    THRUST = "thrust"

    def __str__(self) -> str:
        return str(self.value)
