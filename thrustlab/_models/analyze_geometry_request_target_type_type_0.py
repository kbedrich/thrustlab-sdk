from enum import Enum


class AnalyzeGeometryRequestTargetTypeType0(str, Enum):
    POWER = "power"
    THRUST = "thrust"

    def __str__(self) -> str:
        return str(self.value)
