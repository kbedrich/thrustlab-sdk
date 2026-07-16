from enum import Enum


class CreditUsageEventResourceType(str, Enum):
    ADJUSTMENT = "adjustment"
    BOUNTY_GRANT = "bounty_grant"
    DEBIT = "debit"
    MONTHLY_GRANT = "monthly_grant"
    REFUND = "refund"
    SIGNUP_GRANT = "signup_grant"
    SIMULATION_DEBIT = "simulation_debit"
    SWEEP_DEBIT = "sweep_debit"
    TOPUP = "topup"

    def __str__(self) -> str:
        return str(self.value)
