from enum import Enum


class ScheduleInInterpolationType0(str, Enum):
    HOLD = "hold"
    LINEAR = "linear"

    def __str__(self) -> str:
        return str(self.value)
