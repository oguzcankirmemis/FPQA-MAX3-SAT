from nac.instructions.base import Instruction
from nac.fpqa import FPQA

class Shuttle(Instruction):
    def __init__(self, fpqa: FPQA, is_row: bool, index: int, offset: float):
        self.fpqa = fpqa
        self.is_row = is_row
        self.index = index
        self.offset = offset
    
    def apply(self):
        if not self.verify():
            raise ValueError("Cannot apply shuttle in current FPQA setting")
        if self.is_row:
            self.fpqa.aod.rows[self.index += offset
        else:
            self.fpqa.aod.cols[self.index] += offset
    
    def verify(self) -> bool:
        if self.is_row():
            return self._verify_row()
        return self._verify_column()

    def _verify_row(self) -> bool:
        next_pos = self.fpqa.aod.rows[self.index] + self.offset
        if self.index > 0:
            if self.fpqa.aod.rows[self.index - 1] > next_pos:
                return False
            if abs(self.fpqa.aod.rows[self.index - 1] - next_pos) < self.fpqa.config["AOD_BEAM_PROXIMITY"]:
                return False
        if self.index < len(self.fpqa.aod.rows) - 1:
            if self.fpqa.aod.rows[self.index + 1] < next_pos:
                return False
            if abs(self.fpqa.aod.rows[self.index + 1] - next_pos) < self.fpqa.config["AOD_BEAM_PROXIMITY"]:
                return False
        return True

    def _verify_column(self) -> bool:
        next_pos = self.fpqa.aod.cols[self.index] + self.offset
        if self.index > 0:
            if self.fpqa.aod.cols[self.index - 1] > next_pos:
                return False
            if abs(self.fpqa.aod.cols[self.index - 1] - next_pos) < self.fpqa.config["AOD_BEAM_PROXIMITY"]:
                return False
        if self.index < len(self.fpqa.aod.cols) - 1:
            if self.fpqa.aod.cols[self.index + 1] < next_pos:
                return False
            if abs(self.fpqa.aod.cols[self.index + 1] - next_pos) < self.fpqa.config["AOD_BEAM_PROXIMITY"]:
                return False
        return True

    def qasm(self) -> str:
        row_or_col = "row" if self.is_row else "col"
        return f"@shuttle {row_or_col} {self.index} {self.offset}"

    def avg_fidelity() -> float:
        return self.fpqa.config["SHUTTLING_FIDELITY"]

    def duration() -> float:
        return self.offset / self.fpqa.config["SHUTTLING_SPEED"]