from enum import Enum


class SimulationResourceStatus(str, Enum):
    CANCELED = "canceled"
    COMPLETED = "completed"
    DRAFT = "draft"
    FAILED = "failed"
    QUEUED = "queued"
    RUNNING = "running"

    def __str__(self) -> str:
        return str(self.value)
