from nac.instructions.base import Instruction
from nac.fpqa import FPQA
from nac.atom import Atom

class Bind(Instruction):
    def __init__(self, fpqa: FPQA, is_slm: bool, row: int, col: int):
        self.fpqa = fpqa
        self.is_slm = is_slm
        self.row = row
        self.col = col

    def apply(self):
        pass

    def verify(self) -> bool:
        pass

    def qams(self) -> str:
        pass

    def avg_fidelity(self) -> float:
        pass

    def duration(self) -> float: