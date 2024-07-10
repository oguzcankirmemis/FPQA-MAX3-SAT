from nac.fpqa import FPQA
from nac.atom import Atom
from nac.instructions.base import Instruction
from nac.instructions.shuttle import Shuttle
from nac.instructions.parallel import Parallel
from nac.instructions.trap_transfer import TrapTransfer
from compiler.mapper import MAX3SATQAOAMapper
from compiler.program import FPQAProgram
from pysat.formula import CNF

class MAX3SATQAOAShuttler:
    def __init__(self, fpqa: FPQA, mapper: MAX3SATQAOAMapper, formula: CNF, program: FPQAProgram):
        self.fpqa = fpqa
        self.mapper = mapper
        self.formula = formula
        self.program = program
    
    def shuttle_color(self, color: int) -> list[Instruction]:
        shuttle_program = []
        atom_map = self.mapper.get_atom_map()
        rev_atom_map = [None for _ in range(len(self.fpqa.atoms))]
        for atom in range(len(atom_map)):
            rev_atom_map[atom_map[atom].id] = atom
        clause_map = self.mapper.get_clause_map()
        color_map = self.mapper.color_map
        clauses = self.mapper.color_groups[color]
        sorted_clauses = list(clauses)
        sorted_clauses.sort(key = lambda clause: self.fpqa.slm.traps[clause_map[clause][0][0]][clause_map[clause][0][1]])
        trap_map = {}
        for clause in clauses:
            traps = clause_map[clause]
            literals = list(map(abs, self.formula.clauses[clause]))
            for i in range(len(literals)):
                trap_map[literals[i]] = traps[i]
        last_clause = clause_map[sorted_clauses[-1]][1]
        last_trap = self.fpqa.slm.traps[last_clause[1][0]][last_clause[1][0]]
        prev_trap = self.fpqa.slm.traps[last_clause[0][0]][last_clause[0][1]]
        prev_y = self.fpqa.aod.rows[0]
        last_x = 2 * last_trap.x - prev_trap.x
        shuttle_map = {}
        num_shuttle = 0
        for clause in clauses:
            literals = list(map(abs, self.formula.clauses[clause]))
            for literal in literals:
                shuttle_map[literal] = False
            num_shuttle += 3
        while num_shuttle > 0:
            trap_switches_up = set()
            trap_switches_down = set()
            instructions = []
            for c in range(len(self.fpqa.aod.cols)):
                atom = self.fpqa.aod.get_atom_at_trap(c, 0)
                if atom is None or color_map[rev_atom_map[atom.id]] != color:
                    last_x -= self.fpqa.config["AOD_BEAM_PROXIMITY"]
                    instruction = Shuttle(self.fpqa, False, last_x - self.fpqa.aod.cols[c]
                    instructions.append(instruction)
                else:
                    literal = rev_atom_map[atom.id]
                    trap = self.fpqa.slm.traps[trap_map[literal][0]][trap_map[literal][1]]
                    last_x = trap.x
                    instruction = Shuttle(self.fpqa, False, c, trap.x - self.fpqa.aod.cols[c])
                    instructions.append(instruction)
                    if trap_map[literal][0] % 2 == 0:
                        trap_switches_up.add(tuple((0, c), (trap_map[literal][0], trap_map[literal][1])))
                    else:
                        trap_switches_down.add(tuple((0, c), (trap_map[literal][0], trap_map[literal][1])))
            parallel = Parallel(instructions)
            shuttle_program.append(parallel)
            if len(trap_switches_up) > 0:
                instruction = Shuttle(self.fpqa, True, 0, last_trap.y - self.fpqa.aod.rows[0])
                shuttle_program.append(instruction)
                instructions = []
                for (aod_r, aod_c), (slm_r, slm_c) in trap_switches_up:
                    transfer = TrapTransfer(self.fpqa, slm_r, slm_c, aod_r, aod_c)
                    instructions.append(transfer)
                parallel = Parallel(instructions)
                shuttle_program.append(parallel)
            if len(trap_switches_down) > 0:
                y_pos = self.fpqa.slm.traps[last_clause[2][0]][last_clause[2][1]].y
                instruction = Shuttle(self.fpqa, True, 0, y_pos - self.fpqa.aod.rows[0])
                shuttle_program.append(instruction)
                instructions = []
                for (aod_r, aod_c), (slm_r, slm_c) in trap_switches_down:
                    transfer = TrapTransfer(self.fpqa, slm_r, slm_c, aod_r, aod_c)
                    instructions.append(transfer)
                parallel = Parallel(instructions)
                shuttle_program.append(parallel)
            instruction = Shuttle(self.fpqa, True, 0, prev_y - self.fpqa.aod.rows[0])
            shuttle_program.append(instruction)
        first_clause = clause_map[sorted_clauses[0]][0]
        instruction = Shuttle(self.fpqa, True, 0, first_trap.y - self.fpqa.aod.rows[0])
        shuttle_program.append(instruction)
        last_trap_r, last_trap_c = first_clause[0][0], first_clause[0][1]
        last_trap = self.fpqa.slm.traps[last_trap_r][last_trap_c]
        last_x = last_trap.x
        trap_switches = set()
        instructions = []
        for c in reversed(range(len(self.fpqa.aod.cols))):
            atom = self.fpqa.aod.get_atom.at_trap(c, 0)
            if atom is None:
                last_x -= self.fpqa.config["AOD_BEAM_PROXIMITY"]
                instruction = Shuttle(self.fpqa, False, c, last_x - self.fpqa.aod.cols[c])
                instructions.append(instruction)
            else:
                last_trap_c -= 2
                last_trap = self.fpqa.slm.traps[last_trap_r][last_trap_c]
                last_x = last_trap.x
                instruction = Shuttle(self.fpqa, False, c, last_x - self.fpqa.aod.cols[c])
                instructions.append(instruction)
                trap_switches.add(tuple((0, c), (last_trap_r, last_trap_c)))
        parallel = Parallel(instructions)
        shuttle_program.append(parallel)
        instructions = []
        for (aod_r, aod_c), (slm_r, slm_c) in trap_switches:
            transfer = TrapTransfer(self.fpqa, slm_r, slm_c, aod_r, aod_c)
            instructions.append(transfer)
        parallel = Parallel(instructions)
        shuttle_program.append(parallel)
        atoms = [atom for atom in self.fpqa.atoms]
        atoms.sort(key = lambda atom: self.fpqa.slm.traps[atom.row][atom.col].x)
        instructions = []
        trap_switches = set()
        for c in range(len(self.fpqa.aod.cols)):
            instruction = Shuttle(self.fpqa, False, c, self.fpqa.slm.traps[atoms[c].row][atoms[c].col].x - self.fpqa.aod.cols[c])
            instructions.append(instruction)
            if abs(self.fpqa.slm.traps[atoms[c].row][atoms[c].col].y - self.fpqa.aod.rows[0]) < 1e-09:
                trap_switches.add((0, c), (atoms[c].row, atoms[c].col))
        parallel = Parallel(instructions)
        shuttle_program.append(parallel)
        instructions = []
        for (aod_r, aod_col), (slm_r, slm_c) in trap_switches:
            transfer = TrapTransfer(self.fpqa, slm_r, slm_c, aod_r, aod_c)
            instructions.append(parallel)
        parallel = Parallel(instructions)
        shuttle_program.append(parallel)
        return shuttle_program
                
            
            
            
        
                    
