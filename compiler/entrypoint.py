from pysat.formula import CNF
from compiler.program import FPQAProgram
from compiler.color_mapper import MAX3SATQAOAMapper
from compiler.color_shuttler import MAX3SATQAOAShuttler
from utils.sat_utils import get_color_map
from nac.fpqa import FPQA
from nac.aod import AOD
from nac.slm.triangular_layout import TriangularLayout
from nac.config import FPQAConfig
from nac.atom import Atom


class MAX3SATQAOACompiler:
    def __init__(self, formula: CNF):
        self.formula = formula

    def compile(self) -> FPQAProgram:
        num_colors, color_map = get_color_map(self.formula)
        num_slm_rows = (num_colors + 1) * 2
        num_slm_cols = len(self.formula.clauses) * 3 + self.formula.nv * 2
        num_aod_rows = 1
        num_aod_cols = self.formula.nv
        config = FPQAConfig()
        aod = AOD(config.INTERACTION_RADIUS, num_aod_rows, num_aod_cols)
        slm = TriangularLayout(config.INTERACTION_RADIUS, num_slm_rows, num_slm_cols)
        atoms = [Atom(i + 1, False, 0, i) for i in range(self.formula.nv)]
        fpqa = FPQA(slm, aod, atoms, config)
        program = FPQAProgram(fpqa)
        mapper = MAX3SATQAOAMapper(fpqa, self.formula)
        shuttler = MAX3SATQAOAShuttler(fpqa, mapper, self.formula)
        # TO-DO: Execution pipeline