from compiler.program import FPQAProgram
from compiler.color_mapper import Max3satQaoaMapper
from pysat.formula import CNF
from nac.fpqa import FPQA
from nac.atom import Atom
from utils.hamiltonians import Max3satHamiltonian
from nac.instructions.raman import GlobalRaman, LocalRaman
from nac.instructions.rydberg import Rydberg
from nac.instructions.shuttle import Shuttle
from nac.instructions.parallel import Parallel
from nac.instructions.trap_transfer import TrapTransfer
import numpy as np

class Max3satQaoaExecutor:
    def __init__(self, fpqa: FPQA, mapper: Max3satQaoaMapper, formula: CNF,  program: FPQAProgram):
        self.fpqa = fpqa
        self.formula = formula
        self.mapper = mapper
        self.program = program
        self.hamiltonian = Max3satHamiltonian(formula=formula)
        # TO-DO: Optimize fidelity in single/quadratic terms
        self.implemented_quadratic_terms = {}
        self.single_term_corrections = {}

    def _get_slm_qubit_errors(self, aod_pairs: list[tuple[Atom, Atom]], slm_atoms: list[Atom], clauses: list[list[int]]) -> list[float]:
        atom_map, rev_atom_map = self.mapper.get_atom_map()
        slm_qubit_errors = [0.0 for _ in clauses]
        for i, clause in enumerate(clauses):
            literal_sign = {abs(l): 1 if l > 0 else -1 for l in self.formula.clauses[clause]}
            pos_count = sum(map(lambda l: 1 if l > 0 else 0, self.formula.clauses[clause]))
            if pos_count == 3:
                slm_qubit_errors[i] = 1.0
            elif pos_count == 2 and literal_sign[rev_atom_map[slm_atoms[i].id]] == -1:
                slm_qubit_errors[i] = -1.0
            elif pos_count == 2 and literal_sign[rev_atom_map[aod_pairs[i][0].id]] == -1:
                slm_qubit_errors[i] = 1.0
            elif pos_count == 2 and literal_sign[rev_atom_map[aod_pairs[i][1].id]] == -1:
                slm_qubit_errors[i] = 1.0
            elif pos_count == 1 and literal_sign[rev_atom_map[slm_atoms[i].id]] == 1:
                slm_qubit_errors[i] = 1.0
            elif pos_count == 1 and literal_sign[rev_atom_map[aod_pairs[i][0].id]] == 1:
                slm_qubit_errors[i] = -1.0
            elif pos_count == 1 and literal_sign[rev_atom_map[aod_pairs[i][1].id]] == 1:
                slm_qubit_errors[i] = -1.0
            else:
                slm_qubit_errors[i] = -1.0
        return slm_qubit_errors
    
    def _get_ccnot_angle_signs(self, aod_pairs: list[tuple[Atom, Atom]], slm_atoms: list[Atom], clauses: list[list[int]]) -> list[float]:
        atom_map, rev_atom_map = self.mapper.get_atom_map()
        angle_signs = [1.0 for _ in clauses]
        for i, clause in enumerate(clauses):
            literal_sign = {abs(l): 1 if l > 0 else -1 for l in self.formula.clauses[clause]}
            pos_count = sum(map(lambda l: 1 if l > 0 else 0, self.formula.clauses[clause]))
            if pos_count == 3:
                angle_signs[i] = -1.0
            elif pos_count == 2 and literal_sign[rev_atom_map[slm_atoms[i].id]] == -1:
                pass
            elif pos_count == 2 and literal_sign[rev_atom_map[aod_pairs[i][0].id]] == -1:
                angle_signs[i] = -1.0
            elif pos_count == 2 and literal_sign[rev_atom_map[aod_pairs[i][1].id]] == -1:
                angle_signs[i] = -1.0
            elif pos_count == 1 and literal_sign[rev_atom_map[slm_atoms[i].id]] == 1:
                angle_signs[i] = -1.0
            elif pos_count == 1 and literal_sign[rev_atom_map[aod_pairs[i][0].id]] == 1:
                pass
            elif pos_count == 1 and literal_sign[rev_atom_map[aod_pairs[i][1].id]] == 1:
                pass
            else:
                pass
        return angle_signs

    def _get_cnot_angle_signs(self, aod_pairs: list[tuple[Atom, Atom]], clauses: list[list[int]]) -> list[float]:
        atom_map, rev_atom_map = self.mapper.get_atom_map()
        angle_signs = [1.0 for _ in clauses]
        for i, clause in enumerate(clauses):
            literal_sign = {abs(l): 1 if l > 0 else -1 for l in self.formula.clauses[clause]}
            angle_signs[i] = literal_sign[rev_atom_map[aod_pairs[i][0].id]] * literal_sign[rev_atom_map[aod_pairs[i][1].id]]
        return angle_signs
    
    def _implement_ccnot_control(self, aod_pairs: list[tuple[Atom, Atom]], slm_atoms: list[Atom], clauses: list[list[int]]):
        atom_map, rev_atom_map = self.mapper.get_atom_map()
        for i, clause in enumerate(clauses):
            literal_sign = {abs(l): 1 if l > 0 else -1 for l in self.formula.clauses[clause]}
            pos_count = sum(map(lambda l: 1 if l > 0 else 0, self.formula.clauses[clause]))
            if pos_count == 3:
                pass
            elif pos_count == 2 and literal_sign[rev_atom_map[slm_atoms[i].id]] == -1:
                pass
            elif pos_count == 2 and literal_sign[rev_atom_map[aod_pairs[i][0].id]] == -1:
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][0], np.pi, 0.0, 0.0))
            elif pos_count == 2 and literal_sign[rev_atom_map[aod_pairs[i][1].id]] == -1:
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][1], np.pi, 0.0, 0.0))
            elif pos_count == 1 and literal_sign[rev_atom_map[slm_atoms[i].id]] == 1:
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][0], np.pi, 0.0, 0.0))
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][1], np.pi, 0.0, 0.0))
            elif pos_count == 1 and literal_sign[rev_atom_map[aod_pairs[i][0].id]] == 1:
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][1], np.pi, 0.0, 0.0))
            elif pos_count == 1 and literal_sign[rev_atom_map[aod_pairs[i][1].id]] == 1:
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][0], np.pi, 0.0, 0.0))
            else:
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][0], np.pi, 0.0, 0.0))
                self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][1], np.pi, 0.0, 0.0))

    def _implement_single_qubit_terms(self, parameter: float, aod_pairs: list[tuple[Atom, Atom]], slm_atoms: list[Atom], clauses: list[list[int]]):
        atom_map, rev_atom_map = self.mapper.get_atom_map()
        slm_qubit_errors = self._get_slm_qubit_errors(aod_pairs, slm_atoms, clauses)
        for i, clause in enumerate(clauses):
            literal_sign = {abs(l): 1 if l > 0 else -1 for l in self.formula.clauses[clause]}
            term = -literal_sign[rev_atom_map[slm_atoms[i].id]]
            if term != slm_qubit_errors[i]:
                factor = term - slm_qubit_errors[i]
                self.program.add_instruction(LocalRaman(self.fpqa, slm_atoms[i], term * 2.0 * parameter, 0.0, 0.0))  
            term = -literal_sign[rev_atom_map[aod_pairs[i][0].id]]
            self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][0], term * 2.0 * parameter, 0.0, 0.0))
            term = -literal_sign[rev_atom_map[aod_pairs[i][1].id]]
            self.program.add_instruction(LocalRaman(self.fpqa, aod_pairs[i][1], term * 2.0 * parameter, 0.0, 0.0))
                  
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
                if atom_map[literal - 1].is_slm:
                    slm_atoms.append(atom_map[literal - 1])
                else:
                    aod_pair.append(atom_map[literal - 1])
            aod_atoms.append(tuple(aod_pair))
        ccnot_angle_signs = self._get_ccnot_angle_signs(aod_atoms, slm_atoms, clauses)
        cnot_angle_signs = self._get_cnot_angle_signs(aod_atoms, clauses)
        self._implement_ccnot_control(aod_atoms, slm_atoms, clauses)
        for atom in slm_atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom, np.pi / 2.0, 0.0, np.pi))
        self.program.add_instruction(Rydberg(self.fpqa))
        for i, atom in enumerate(slm_atoms):
            self.program.add_instruction(LocalRaman(self.fpqa, atom, ccnot_angle_signs[i] * 4.0 * parameter, 0.0, 0.0))
        self.program.add_instruction(Rydberg(self.fpqa))
        for atom in slm_atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom, np.pi / 2.0, 0.0, np.pi))
        self._implement_ccnot_control(aod_atoms, slm_atoms, clauses)
        self.program.add_instruction(Shuttle(self.fpqa, True, 0, -self.fpqa.config.RESTRICTION_RADIUS))
        for atom1, atom2 in aod_atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom2, np.pi / 2.0, 0.0, np.pi))
        self.program.add_instruction(Rydberg(self.fpqa))
        for i, (atom1, atom2) in enumerate(aod_atoms):
            self.program.add_instruction(LocalRaman(self.fpqa, atom2, cnot_angle_signs[i] * 2.0 * parameter, 0.0, 0.0))
        self.program.add_instruction(Rydberg(self.fpqa))
        for atom1, atom2 in aod_atoms:
            self.program.add_instruction(LocalRaman(self.fpqa, atom2, np.pi / 2.0, 0.0, np.pi))
        self._implement_single_qubit_terms(parameter, aod_atoms, slm_atoms, clauses)
        offset = self.fpqa.slm.traps[slm_atoms[0].row][slm_atoms[0].col].y - self.fpqa.aod.rows[0]
        self.program.add_instruction(Shuttle(self.fpqa, True, 0, offset))
        instructions = []
        slm_atoms.sort(key=lambda atom: atom.col)
        aod_col = len(self.fpqa.aod.cols) - 2
        for atom in reversed(slm_atoms):
            instructions.append(TrapTransfer(self.fpqa, atom.row, atom.col, 0, aod_col))
            aod_col -= 3
        parallel = Parallel(instructions)
        self.program.add_instruction(parallel)
            
            