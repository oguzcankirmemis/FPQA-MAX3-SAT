from nac.instructions.base import Instruction
from nac.fpqa import FPQA

class AODInit(Instruction):
    def __init__(self, fpqa: FPQA):
        self.fpqa = fpqa

    def apply(self):
        pass

    def verify(self) -> bool:
        pass

    def qasm(self) -> str:
        pass

    def avg_fidelity(self) -> float:
        pass

    def duration() -> float:
        pass