from enum import Enum


class ExportGeometryRequestFormat(str, Enum):
    IGES = "iges"
    STEP = "step"
    STL = "stl"

    def __str__(self) -> str:
        return str(self.value)
