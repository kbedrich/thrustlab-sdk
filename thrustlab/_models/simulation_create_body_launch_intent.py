from enum import Enum


class SimulationCreateBodyLaunchIntent(str, Enum):
    DRAFT = "draft"
    QUEUE = "queue"
    RUN = "run"

    def __str__(self) -> str:
        return str(self.value)
