from enum import Enum


class CreditUsageEventResourceUnitType(str, Enum):
    FREE = "free"
    MONTHLY = "monthly"

    def __str__(self) -> str:
        return str(self.value)
