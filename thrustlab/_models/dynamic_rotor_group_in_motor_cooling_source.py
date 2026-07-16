from enum import Enum


class DynamicRotorGroupInMotorCoolingSource(str, Enum):
    COWLING = "cowling"
    CUSTOM = "custom"
    PROP_EXIT_VELOCITY = "prop_exit_velocity"

    def __str__(self) -> str:
        return str(self.value)
