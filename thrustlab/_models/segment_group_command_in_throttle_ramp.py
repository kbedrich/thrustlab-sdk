from enum import Enum


class SegmentGroupCommandInThrottleRamp(str, Enum):
    LINEAR = "linear"
    STEP = "step"

    def __str__(self) -> str:
        return str(self.value)
