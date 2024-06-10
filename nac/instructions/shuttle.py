from nac.instructions.base import Instruction
from nac.fpqa import FPQA

class Shuttle(Instruction):
    def __init__(fpqa: FPQA, is_row: bool, index: int, offset: float):
        pass
    
    def apply():
        pass

    def verify() -> bool:
        pass

    def qasm() -> str:
        pass

    def avg_fidelity() -> float:
        pass

    def duration() -> float:
        pass