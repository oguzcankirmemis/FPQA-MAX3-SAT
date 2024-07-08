from nac.fpqa import FPQA
from nac.atom import Atom
from nac.instructions.base import Instruction
from nac.instructions.shuttle import Shuttle
from nac.instructions.parallel import Parallel
from compiler.mapper import MAX3SATQAOAMapper
from pysat.formula import CNF

class MAX3SATQAOAShuttler:
    def __init__(self, fpqa: FPQA, mapper: MAX3SATQAOAMapper, formula: CNF):
        self.fpqa = fpqa
        self.mapper = mapper
        self.formula = formula
    
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
            for c in len(self.fpqa.aod.cols):
                atom = self.fpqa.aod.get_atom_at_trap(c, 0)
                if atom is None or color_map[rev_atom_map[atom.id]] != color:
                    last_x -= self.fpqa.config["AOD_BEAM_PROXIMITY"]
                    instruction = Shuttle(self.fpqa, False, last_x - self.fpqa.aod.cols[c]
                    instructions.append(instruction)
                else:
                    literal = rev_atom_map[atom.id]
                    trap = self.fpqa.slm.traps[trap_map[literal][0]][trap_map[literal][1]]
                    last_x = trap.x
                    instruction = Shuttle(self.fpqa, False, trap.x - self.fpqa.aod.cols[c])
                    instructions.append(instruction)
                    if trap_map[literal][0] % 2 == 0:
                        trap_switches_up.add(tuple((0, c), (trap_map[literal][0], trap_map[literal][1])))
                    else:
                        trap_switches_down.add(tuple((0, c), (trap_map[literal][0], trap_map[literal][1])))
            parallel = Parallel(instructions)
            shuttle_program.append(parallel)
            # TO-DO: Actual trap transfer
            # TO-DO: Reversing traps
            # TO-DO: Prepare for next execution
                    
                    
