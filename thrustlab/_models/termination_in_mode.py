from enum import Enum


class TerminationInMode(str, Enum):
    FIXED = "fixed"
    UNTIL_DEPLETED = "until_depleted"

    def __str__(self) -> str:
        return str(self.value)
