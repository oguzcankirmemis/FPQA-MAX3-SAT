from nac.fpqa import FPQA
from functools import reduce
import numpy as np

class ColorExecutor:
    def __init__(self, color_map: list[list[tuple[int]]], fpqa: FPQA):
        self.color_map = color_map
        self.fpqa = fpqa

    def execute_row_aligned_color(self, color: int, cost_param: float) -> tuple[float]:
        busy_times = [2 * FPQA.CCZ_GATE_DURATION + 2 * FPQA.CZ_GATE_DURATION for atom in self.fpqa.atoms]
        fidelity, duration = 1.0, 0.0
        clauses = self.color_map[color]
        # get the AOD the row
        aod_row = None
        for literal in clauses[0]:
            print(literal)
            atom = self.fpqa.get_atom(abs(literal) - 1)
            if not atom.is_slm:
                aod_row = atom.row
        for clause in clauses:
            signs = {abs(literal): literal for literal in clause}
            slm_atom, aod_atom1, aod_atom2 = tuple(map(lambda l : self.fpqa.get_atom(abs(l) - 1), clause))
            if aod_atom1.is_slm:
                slm_atom, aod_atom1 = aod_atom1, slm_atom
            if aod_atom2.is_slm:
                slm_atom, aod_atom2 = aod_atom2, slm_atom
            if aod_atom1.col > aod_atom2.col:
                aod_atom1, aod_atom2 = aod_atom2, aod_atom1
            # TODO: apply opening/closing Hadamard to CCZ Target
            self.fpqa.apply_local_raman()
            fidelity *= 2 * FPQA.U3_GATE_FIDELITY
            duration += 2 * FPQA.U3_GATE_DURATION
            busy_times[slm_atom.id] += 2 * FPQA.U3_GATE_DURATION
            num_positive = reduce(lambda acc, curr: 1 + acc if curr > 0 else acc, clause, 0)
            if num_positive > 0 and num_positive < 3:
                # TODO: apply opening/closing X to Control 1
                self.fpqa.apply_local_raman()
                fidelity *= 2 * FPQA.U3_GATE_FIDELITY
                duration += 2 * FPQA.U3_GATE_DURATION
                busy_times[aod_atom1.id] += 2 * FPQA.U3_GATE_DURATION
            # TODO: apply Z Cost Hamiltonian
            fidelity *= 3 * FPQA.U3_GATE_FIDELITY
            duration += 3 * FPQA.U3_GATE_DURATION
            for l in clause:
                busy_times[abs(l) - 1] += FPQA.U3_GATE_DURATION
            # TODO: apply CCZ Cost Hamiltonian
            fidelity *= 2 * FPQA.CCZ_GATE_FIDELITY
            fidelity *= FPQA.U3_GATE_FIDELITY
            duration *= FPQA.U3_GATE_DURATION
            busy_times[slm_atom.id] += FPQA.U3_GATE_DURATION
            # TODO: apply shuttling
            # TODO: apply CZ Cost Hamiltonian
            fidelity *= 2 * FPQA.U3_GATE_FIDELITY
            duration += 2 * FPQA.U3_GATE_FIDELITY
            busy_times[aod_atom2.id] += FPQA.U3_GATE_DURATION
            fidelity *= 2 * FPQA.CZ_GATE_FIDELITY
            fidelity *= FPQA.U3_GATE_FIDELITY
            duration *= FPQA.U3_GATE_DURATION
            busy_times[aod_atom2.id] += FPQA.U3_GATE_DURATION
        duration += FPQA.INTERACTION_RADIUS / FPQA.SHUTTLING_SPEED
        fidelity *= FPQA.SHUTTLE_FIDELITY
        duration += 2 * FPQA.CCZ_GATE_DURATION
        duration += 2 * FPQA.CZ_GATE_DURATION
        idle_times = [duration - idle_time for idle_time in busy_times]
        t_idle = reduce(lambda acc, curr: acc + curr, idle_times)
        t_eff = (FPQA.QUBIT_DECAY * FPQA.QUBIT_DEPHASING) / (FPQA.QUBIT_DECAY + FPQA.QUBIT_DEPHASING)
        idle_fidelity = np.exp(-t_idle / t_eff)
        fidelity *= idle_fidelity
        return fidelity, duration, t_idle, t_eff, idle_fidelity
                    

            
        
        