from enum import Enum


class AnalyzeGeometryRequestMode(str, Enum):
    POINT = "point"
    SOLVE_TO_TARGET = "solve_to_target"
    SWEEP = "sweep"

    def __str__(self) -> str:
        return str(self.value)
