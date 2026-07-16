from enum import Enum


class SimulationCreateBodyInflowMode(str, Enum):
    COMPONENTS = "components"
    GROUND = "ground"

    def __str__(self) -> str:
        return str(self.value)
