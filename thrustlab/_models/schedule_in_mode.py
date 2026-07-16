from enum import Enum


class ScheduleInMode(str, Enum):
    CSV = "csv"
    SEGMENTS = "segments"

    def __str__(self) -> str:
        return str(self.value)
