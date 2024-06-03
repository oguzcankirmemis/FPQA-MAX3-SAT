from nac.fpqa import FPQA
from functools import reduce
from qiskit import QuantumCircuit, transpile
from utils.fake_backend import create_fake_heavy_hex_backend
from qiskit.converters import circuit_to_dag
import numpy as np
import random

random.seed()

class ColorExecutor:
    def __init__(self, color_map: list[list[tuple[int]]], fpqa: FPQA):
        self.color_map = color_map
        self.fpqa = fpqa

    def execute_color(self, color: int, cost_param: float) -> tuple[float]:
        pass

    def multi_qubit_execution_stats(self, color: int) -> dict:
        busy_times = [2 * FPQA.CCZ_GATE_DURATION + 2 * FPQA.CZ_GATE_DURATION for atom in self.fpqa.atoms]
        fidelity, duration = 1.0, 0.0
        num_local_raman_pulses, num_global_rydberg_pulses = 0, 4
        clauses = self.color_map[color]
        for clause in clauses:
            slm_atom, aod_atom1, aod_atom2 = tuple(map(lambda l : self.fpqa.get_atom(abs(l) - 1), clause))
            if aod_atom1.is_slm:
                slm_atom, aod_atom1 = aod_atom1, slm_atom
            if aod_atom2.is_slm:
                slm_atom, aod_atom2 = aod_atom2, slm_atom
            if aod_atom1.col > aod_atom2.col:
                aod_atom1, aod_atom2 = aod_atom2, aod_atom1
            num_positive = reduce(lambda acc, curr: 1 + acc if curr > 0 else acc, clause, 0)
            # Single Qubit Cost Hamiltonian
            fidelity *= FPQA.U3_GATE_FIDELITY
            duration += FPQA.U3_GATE_DURATION
            busy_times[aod_atom1.id] += FPQA.U3_GATE_DURATION
            # CZ Target Hadamard
            fidelity *= FPQA.U3_GATE_FIDELITY ** 2
            duration += 2 * FPQA.U3_GATE_DURATION
            busy_times[slm_atom.id] += FPQA.U3_GATE_DURATION
            # Two Qubit Cost Hamiltonian
            fidelity *= FPQA.CZ_GATE_FIDELITY ** 2
            fidelity *= FPQA.U3_GATE_FIDELITY
            duration += FPQA.U3_GATE_DURATION
            busy_times[aod_atom2.id] += FPQA.U3_GATE_DURATION
            # CCZ Target Hadamard
            fidelity *= FPQA.U3_GATE_FIDELITY ** 2
            duration += 2 * FPQA.U3_GATE_DURATION
            busy_times[slm_atom.id] += 2 * FPQA.U3_GATE_DURATION
            if num_positive > 0 and num_positive < 3:
                # Control1 X
                fidelity *= FPQA.U3_GATE_FIDELITY ** 2
                duration += 2 * FPQA.U3_GATE_DURATION
                busy_times[aod_atom1.id] += 2 * FPQA.U3_GATE_DURATION
            # Three Qubit Cost Hamiltonian
            fidelity *= self.fpqa.CCZ_GATE_FIDELITY ** 2
            fidelity *= FPQA.U3_GATE_FIDELITY
            duration += FPQA.U3_GATE_DURATION
            busy_times[slm_atom.id] += FPQA.U3_GATE_DURATION
            # Count raman pulses
            if num_positive > 0 and num_positive < 3:
                num_local_raman_pulses += 11
            else:
                num_local_raman_pulses += 9
        # Shuttling
        duration += FPQA.INTERACTION_RADIUS / FPQA.SHUTTLING_SPEED
        fidelity *= FPQA.SHUTTLE_FIDELITY
        # Global Rydberg Laser Durations
        duration += 2 * FPQA.CCZ_GATE_DURATION
        duration += 2 * FPQA.CZ_GATE_DURATION
        # Idle Fidelity Estimation
        idle_times = [duration - idle_time for idle_time in busy_times]
        t_idle = reduce(lambda acc, curr: acc + curr, idle_times)
        t_eff = (FPQA.QUBIT_DECAY * FPQA.QUBIT_DEPHASING) / (FPQA.QUBIT_DECAY + FPQA.QUBIT_DEPHASING)
        idle_fidelity = np.exp(-t_idle / t_eff)
        fidelity *= idle_fidelity
        # Return result
        stats = {
            "duration": duration,
            "idle_fidelity": idle_fidelity,
            "fidelity": fidelity,
            "num_local_raman_pulses": num_local_raman_pulses,
            "num_global_rydberg_pulses": num_global_rydberg_pulses
        }
        return stats

    def two_qubit_execution_stats(self, color: int) -> dict:
        busy_times = [8 * FPQA.CZ_GATE_DURATION for atom in self.fpqa.atoms]
        fidelity, duration = 1.0, 0.0
        num_local_raman_pulses, num_global_rydberg_pulses = 0, 8
        clauses = self.color_map[color]
        for clause in clauses:
            slm_atom, aod_atom1, aod_atom2 = tuple(map(lambda l : self.fpqa.get_atom(abs(l) - 1), clause))
            if aod_atom1.is_slm:
                slm_atom, aod_atom1 = aod_atom1, slm_atom
            if aod_atom2.is_slm:
                slm_atom, aod_atom2 = aod_atom2, slm_atom
            if aod_atom1.col > aod_atom2.col:
                aod_atom1, aod_atom2 = aod_atom2, aod_atom1
            num_positive = reduce(lambda acc, curr: 1 + acc if curr > 0 else acc, clause, 0)
            # Execution based on QAOA Two-Qubit Compilation
            fidelity *= FPQA.CZ_GATE_FIDELITY ** 8
            fidelity *= FPQA.U3_GATE_FIDELITY ** 10
            duration += 10 * FPQA.U3_GATE_DURATION
            busy_times[slm_atom.id] += 4 * FPQA.U3_GATE_DURATION
            busy_times[aod_atom1.id] += 3 * FPQA.U3_GATE_DURATION
            busy_times[aod_atom2.id] += 3 * FPQA.U3_GATE_DURATION
            num_local_raman_pulses += 9
        # Shuttling
        duration += 2 * (FPQA.INTERACTION_RADIUS / FPQA.SHUTTLING_SPEED)
        fidelity *= FPQA.SHUTTLE_FIDELITY ** 2
        # Global Rydberg Laser Durations
        duration += 8 * FPQA.CZ_GATE_DURATION
        # Idle Fidelity Estimation
        idle_times = [duration - idle_time for idle_time in busy_times]
        t_idle = reduce(lambda acc, curr: acc + curr, idle_times)
        t_eff = (FPQA.QUBIT_DECAY * FPQA.QUBIT_DEPHASING) / (FPQA.QUBIT_DECAY + FPQA.QUBIT_DEPHASING)
        idle_fidelity = np.exp(-t_idle / t_eff)
        fidelity *= idle_fidelity
        # Return result
        stats = {
            "duration": duration,
            "idle_fidelity": idle_fidelity,
            "fidelity": fidelity,
            "num_local_raman_pulses": num_local_raman_pulses,
            "num_global_rydberg_pulses": num_global_rydberg_pulses
        }
        return stats

    def superconducting_execution_stats(self, color: int) -> dict:
        basis_gates = ["u3", "cz"]
        fidelity, duration = 1.0, 0.0
        angle = random.random()
        clauses = self.color_map[color]
        backend = create_fake_heavy_hex_backend(1, int(len(clauses) / 2))
        busy_times = [0.0 for qubit in range(backend.num_qubits)]
        num_qubits = 0
        for clause in clauses:
            for literal in clause:
                num_qubits = max(num_qubits, abs(literal) + 1)
        circuit = QuantumCircuit(num_qubits)
        for clause in clauses:
            q0, q1, q2 = abs(clause[0]), abs(clause[1]), abs(clause[2])
            circuit.h(q1)
            circuit.cz(q0, q1)
            circuit.h(q1)
            circuit.rz(2 * angle * np.pi, q1)
            circuit.h(q1)
            circuit.cz(q0, q1)
            circuit.h(q1)
            circuit.h(q2)
            circuit.cz(q0, q2)
            circuit.h(q2)
            circuit.rz(2 * angle * np.pi, q2)
            circuit.h(q2)
            circuit.cz(q0, q2)
            circuit.h(q2)
            circuit.h(q2)
            circuit.cz(q1, q2)
            circuit.h(q2)
            circuit.rz(-2 * angle * np.pi, q2)
            circuit.h(q2)
            circuit.cz(q1, q2)
            circuit.h(q0)
            circuit.cz(q2, q0)
            circuit.h(q0)
            circuit.rz(2 * angle * np.pi, q0)
            circuit.h(q0)
            circuit.cz(q2, q0)
            circuit.h(q0)
            circuit.rz(-2 * angle * np.pi, q0)
            circuit.rz(-2 * angle * np.pi, q1)
            circuit.rz(-2 * angle * np.pi, q2)
        transpiled_circuit = transpile(circuit, backend=backend, basis_gates=basis_gates, optimization_level=3)
        dag = circuit_to_dag(transpiled_circuit)
        for gate in dag.gate_nodes():
            if gate.name == "cz":
                q1, q2 = gate.qargs[0]._index, gate.qargs[1]._index
                fidelity *= FPQA.CZ_GATE_FIDELITY
                duration += FPQA.CZ_GATE_DURATION
                busy_times[q1] += FPQA.CZ_GATE_DURATION
                busy_times[q2] += FPQA.CZ_GATE_DURATION
            if gate.name == "u3":
                q1 = gate.qargs[0]._index
                fidelity *= FPQA.U3_GATE_FIDELITY
                duration += FPQA.U3_GATE_DURATION
                busy_times[q1] += FPQA.U3_GATE_DURATION
        idle_times = [duration - idle_time for idle_time in busy_times]
        t_idle = reduce(lambda acc, curr: acc + (curr if curr < duration else 0.0), idle_times, 0.0)
        t_eff = (FPQA.QUBIT_DECAY * FPQA.QUBIT_DEPHASING) / (FPQA.QUBIT_DECAY + FPQA.QUBIT_DEPHASING)
        idle_fidelity = np.exp(-t_idle / t_eff)
        fidelity *= idle_fidelity
        swap_overhead = (transpiled_circuit.count_ops()["cz"] - circuit.count_ops()["cz"])
        stats = {
            "duration": duration,
            "idle_fidelity": idle_fidelity,
            "fidelity": fidelity,
            "swap_overhead": swap_overhead
        }
        return stats

                    

            
        
        