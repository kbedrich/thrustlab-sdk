from enum import Enum


class SweepRotorGroupInEscType(str, Enum):
    FOC = "foc"
    SIX_STEP = "six_step"

    def __str__(self) -> str:
        return str(self.value)
