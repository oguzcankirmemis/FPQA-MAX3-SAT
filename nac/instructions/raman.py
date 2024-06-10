from nac.instructions.base import Instruction
from nac.fpqa import FPQA
from nac.atom import Atom

class LocalRaman(Instruction):
    def __init__(fpqa: FPQA, atom: Atom, x_angle: float, y_angle: float, z_angle: float):
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

class GlobalRaman(Instruction):
    def __init__(fpqa: FPQA, x_angle: float, y_angle: float, z_angle: float):
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