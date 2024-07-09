from nac.fpqa import FPQA
from nac.instructions.base import Instruction

_global_rydberg_gate_id = 0

class Rydberg(Instruction):
    def __init__(self, fpqa: FPQA):
        self.fpqa = fpqa
        self.gate_name = f"global_rydberg_{_rydberg_gate_id}"
        _global_rydberg_gate_id += 1
        
    def apply(self):
        if not self.verify():
            raise ValueError("Cannot apply global Rydberg pulse in current FPQA setting.")
        self.gates, self.atoms = self.get_gates_and_atoms()

    def verify(self) -> bool:
        return True

    def qasm(self) -> str:
        lines = ["@rydberg", f"gate {self.gate_name} {", ".join(self.atoms)} {{"]
        for gate in self.gates:
            if len(gate) == 2:
                lines.append(f"    ctrl @ U(0, 0, π) q[{gate[0]}], q[{gate[1]}];")
            if len(gate) == 3:
                lines.append(f"    ctrl(2) @ U(0, 0, π) q[{gate[0]}], q[{gate[1]}], q[{gate[2]}];")
        lines.append("}")
        lines.append(f"{self.gate_name} {", ".join(self.atoms)}\n")
        return "\n".join(lines)

    def avg_fidelity(self) -> float:
        fidelity = 1.0
        for atoms in self.interacting_atoms:
            if len(atoms) == 3:
                fidelity *= self.fpqa.config["CCZ_GATE_FIDELITY"]
            else:
                fidelity *= self.fpqa.config["CZ_GATE_FIDELITY"]
        return fidelity

    def duration(self) -> float:
        for atoms in self.interacting_atoms:
            if len(atoms) == 3:
                return self.fpqa.config["CCZ_GATE_DURATION"]
        return self.fpqa.config["CZ_GATE_DURATION"]

    def get_gates_and_atoms(self) -> tuple[set, set]:
        parents = {atom.id: set([atom.id]) for atom in fpqa.atoms}
        for i in range(len(self.atoms)):
            for j in range(i + 1, len(self.atoms)):
                atom1 = self.atoms[i]
                atom2 = self.atoms[j]
                if atom2.id < atom1.id:
                    atom1, atom2 = atom2, atom1
                if fpqa.is_interacting(atom1, atom2):
                    parents[atom2.id] = parents[atom1.id]
                    parents[atom1.id].add(atom2.id)
        gates = set()
        atoms = set()
        for atom in parents:
            interacting_atoms = tuple(parents[atom])
            if len(interacting_atoms > 3):
                raise ValueError(f"More than 3 qubit interaction between atoms: {interacting_atoms}")
            if len(interacting_atoms > 1):
                gates.add(tuple(parents[atom]))
                atoms = atoms.union(parents[atom])
        return gates, atoms
            
                
    