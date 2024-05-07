from qiskit.converters import circuit_to_dag
import numpy as np

DESIRED_SUCCESS_PROBABILITY = 0.666
    
def calculate_expected_fidelity(circuit, backend):
    dag = circuit_to_dag(circuit)
    fidelity = 1
    decoherence_fidelity = 1
    for gate in dag.gate_nodes():
        if gate.name == "ecr":
            q1, q2 = gate.qargs[0]._index, gate.qargs[1]._index
            fidelity *= (1 - backend.target["ecr"][(q1, q2)].error)
        else:
            q = gate.qargs[0]._index
            fidelity *= (1 - backend.target[gate.name][(q,)].error)
    for wire in dag.wires:
        duration = 0.0
        for gate in dag.nodes_on_wire(wire, only_ops=True):
            if gate.name == "barrier":
                continue
            elif gate.name == "ecr":
                q1, q2 = gate.qargs[0]._index, gate.qargs[1]._index
                q = gate.qargs[0]._index
                duration += backend.target["ecr"][(q1, q2)].duration
            else:
                q = gate.qargs[0]._index
                duration += backend.target[gate.name][(q,)].duration
        if duration > 0:
            qp = backend.qubit_properties(wire._index)
            t1 = np.exp(-duration / qp.t1)
            t2 = np.exp(-duration / qp.t2)
            decoherence_fidelity *= t1 * t2                
    estimated_shots_without_decoherence = np.log(1 - DESIRED_SUCCESS_PROBABILITY) / np.log(1 - fidelity)
    estimated_shots = np.log(1 - DESIRED_SUCCESS_PROBABILITY) / np.log(1 - fidelity * decoherence_fidelity)
    return fidelity * decoherence_fidelity, fidelity, int(np.ceil(estimated_shots)), int(np.ceil(estimated_shots_without_decoherence))

def calculate_swap_overhead(actual_circuit, transpiled_circuit):
    actual_ops = actual_circuit.count_ops()
    transpiled_ops = transpiled_circuit.count_ops()
    return int((transpiled_ops["ecr"] - actual_ops["cz"]) / 3)