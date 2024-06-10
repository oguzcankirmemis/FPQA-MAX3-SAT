from nac.instructions.base import Instruction
from nac.fpqa import FPQA

class TrapTransfer(Instruction):
    def __init__(fpqa: FPQA, slm_row: int, slm_col: int, aod_row: int, aod_col: int):
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