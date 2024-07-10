from compiler.program import FPQAProgram
from compiler.color_mapper import Max3satQaoaMapper
from pysat.formula import CNF
from nac.fpqa import FPQA
from utils.hamiltonians import Max3satHamiltonian
from nac.instructions.raman import GlobalRaman, LocalRaman
from nac.instructions.rydberg import Rydberg
from nac.instructions.shuttle import Shuttle
from nac.instructions.parallel import Parallel
from nac.instructions.trap_transfer import TrapTransfer

class Max3satQaoaExecutor:
    def __init__(self, fpqa: FPQA, formula: CNF, mapper: Max3satQaoaMapper, program: FPQAProgram):
        self.fpqa = fpqa
        self.formula = formula
        self.mapper = mapper
        self.program = program
        self.hamiltonian = Max3satHamiltonian(formula=formula)
        self.implemented_quadratic_terms = {}
        self.single_term_corrections = {}

    def execute_color(self, color: int, parameter: float):
        atom_map, rev_atom_map = self.mapper.get_atom_map()
        color_groups = self.mapper.color_groups
        clauses = color_groups[color]
        slm_atoms = []
        aod_atoms = []
        for clause in clauses:
            literals = map(abs, self.formula.clauses[clause])
            aod_pair = []
            for literal in literals:
                if atom_map[literal].is_slm:
                    slm_atoms.append(atom_map[literal])
                else:
                    aod_pair.append(atom_map[literal])
                aod_atoms.append(tuple(aod_pair))
        for atom in slm_atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom, np.pi / 2.0, 0.0, np.pi))
        self.program.add_instruction(Rydberg(self.fpqa))
        for atom in slm_atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom, 4.0 * parameter, 0.0, 0.0))
        self.program.add_instruction(Rydberg(self.fpqa))
        for atom in slm_atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom, np.pi / 2.0, 0.0, np.pi))
        self.program.add_instruction(Shuttle(self.fpqa, True, 0, -self.fpqa.config["RESTRICTION_RADIUS"]))
        for atom1, atom2 in aod_atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom2, np.pi / 2.0, 0.0, np.pi))
        self.program.add_instruction(Rydberg(self.fpqa))
        for atom1, atom2 in aod_atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom2, 2.0 * parameter, 0.0, 0.0))
        self.program.add_instruction(Rydberg(self.fpqa))
        for atom1, atom2 in aod_atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom2, np.pi / 2.0, 0.0, np.pi))
        for atom1, atom2 in aod_atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom2, 0.0, 0.0, -2.0 * parameter)
            self.program.add_instruction(LocalRaman(self.fpqa, atom2, 0.0, 0.0, 2.0 * parameter)
        for atom in slm_atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom, 0.0, 0.0, -4 * parameter)
        offset = self.fpqa.slm.traps[slm_atoms[0].row][slm_atoms[0].col].y - self.fpqa.aod.rows[0]
        self.program.add_instruction(Shuttle(self.fpqa, True, 0, offset))
        instructions = []
        slm_atoms.sort(key: lambda atom: atom.col)
        aod_col = len(self.fpqa.aod.cols) - 2
        for atom in reversed(slm_atoms):
            instructions.append(TrapTransfer(self.fpqa, atom.row, atom.col, 0, aod_col))
            aod_col -= 2
        parallel = Parallel(instructions)
        self.program.add_instruction(parallel)
        # TO-DO: Handle clause types
        
            
            