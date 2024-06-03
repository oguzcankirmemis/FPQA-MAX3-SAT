from nac.instructions.base import Instruction

class Rydberg(Instruction):
    def apply(fpqa: FPQA):
        pass

    def verify(fpqa: FPQA):
        return True

    def qasm(fpqa: FPQA) -> str:
        return ""

    def avg_fidelity(fpqa: FPQA) -> float:
        pass

    def duration(fpqa: FPQA) -> float:
        pass
    