from enum import Enum


class CreditBucketBreakdownType(str, Enum):
    FREE = "free"
    MONTHLY = "monthly"

    def __str__(self) -> str:
        return str(self.value)
