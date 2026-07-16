from enum import Enum


class ExportGeometryRequestRotationType0(str, Enum):
    CCW = "ccw"
    CW = "cw"

    def __str__(self) -> str:
        return str(self.value)
