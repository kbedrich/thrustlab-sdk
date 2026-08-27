from enum import Enum


class AnalyzeGeometryResponseEnvelopeStatusType0(str, Enum):
    OUTSIDE = "outside"
    PARTIAL = "partial"
    VALIDATED = "validated"

    def __str__(self) -> str:
        return str(self.value)
