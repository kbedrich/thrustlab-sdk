from enum import Enum


class AnalyzeGeometryResponseEnvelopeLimitingFactorType0(str, Enum):
    ADVANCE_RATIO = "advance_ratio"
    BLADE_COUNT = "blade_count"
    DIAMETER = "diameter"
    PITCH_DIAMETER = "pitch_diameter"
    THRUST_COEFFICIENT = "thrust_coefficient"
    TIP_MACH = "tip_mach"

    def __str__(self) -> str:
        return str(self.value)
