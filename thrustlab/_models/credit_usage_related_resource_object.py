from enum import Enum


class CreditUsageRelatedResourceObject(str, Enum):
    COMPONENT_SUBMISSION = "component_submission"
    SIMULATION = "simulation"

    def __str__(self) -> str:
        return str(self.value)
