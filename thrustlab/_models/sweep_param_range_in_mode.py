from enum import Enum


class SweepParamRangeInMode(str, Enum):
    CUSTOM = "custom"
    RANGE = "range"

    def __str__(self) -> str:
        return str(self.value)
