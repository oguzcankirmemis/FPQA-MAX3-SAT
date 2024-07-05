from nac.fpqa import FPQA
from nac.atom import Atom
from pysat.formula import CNF

class MAX3SATQAOAMapper:
    def __init__(self, fpqa: FPQA, formula: CNF, num_colors: int, color_map: list[int]):
        self.fpqa = fpqa
        self.formula = formula
        self.color_groups = [set() for i in range(num_colors)]
        self.max_color_group_size = 0
        self.last_unused_atom = len(fpqa.atoms) - 1
        for clause in range(len(formula.clauses)):
            self.color_groups[color_map[clause]].add(clause)
            self.max_color_group_size = max(self.max_color_group_size, len(self.color_groups[color_map[clause]]))
        if len(fpqa.aod.cols) < max_color_group_size:
            raise ValueError("Cannot map formula to FPQA")

    def get_atom_map(self) -> list[Atom]:
        if hasattr(self, "atom_map"):
            return self.atom_map
        atom_map = [None for _ in range(formula.nv)
        for color in range(len(self.color_groups)):
            for clause in self.color_groups[color]:
                literals = list(map(abs, self.formula.clauses[clause]))
                for literal in literals
                    if atom_map[literal] is not None:
                        continue
                    atom_map[literal] = self.fpqa.atoms[self.last_unused_atom]
                    self.last_unused_atom -= 1
        self.atom_map = atom_map
        return atom_map
        
                    
                
        
        
        
    