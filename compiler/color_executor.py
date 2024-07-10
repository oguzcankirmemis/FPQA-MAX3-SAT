from compiler.program import FPQAProgram
from pysat.formula import CNF
from nac.fpqa import FPQA

class MAX3SATQAOAExecutor:
    def __init__(self, fpqa: FPQA, formula: CNF, program: FPQAProgram):
        self.fpqa = fpqa
        self.formula = formula
        self.program = formula


    def execute(self, color: int):
        pass