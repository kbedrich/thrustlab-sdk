from enum import Enum


class SweepCreateBodyInflowMode(str, Enum):
    COMPONENTS = "components"
    GROUND = "ground"

    def __str__(self) -> str:
        return str(self.value)
