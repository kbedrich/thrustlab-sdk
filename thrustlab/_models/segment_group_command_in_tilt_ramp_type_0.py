from enum import Enum


class SegmentGroupCommandInTiltRampType0(str, Enum):
    LINEAR = "linear"
    STEP = "step"

    def __str__(self) -> str:
        return str(self.value)
