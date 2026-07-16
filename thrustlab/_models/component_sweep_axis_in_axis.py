from enum import Enum


class ComponentSweepAxisInAxis(str, Enum):
    BATTERY = "battery"
    MOTOR = "motor"
    PROPELLER = "propeller"

    def __str__(self) -> str:
        return str(self.value)
