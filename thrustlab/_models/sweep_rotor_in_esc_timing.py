from enum import Enum


class SweepRotorInEscTiming(str, Enum):
    AUTO = "auto"
    HIGH = "high"
    LOW = "low"
    MEDIUM = "medium"

    def __str__(self) -> str:
        return str(self.value)
