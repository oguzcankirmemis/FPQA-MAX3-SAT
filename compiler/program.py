from nac.instructions.base import Instruction
from nac.instructions.aod_init import AODInit
from nac.instructions.slm_init import SLMInit
from nac.instructions.bind import Bind
from nac.fpqa import FPQA

class FPQAProgram:
    def __init__(self, fpqa: FPQA):
        self.fpqa = fpqa
        self.instructions = []

    def _slm_init(self):
        self.instructions.append(SLMInit(self.fpqa))

    def _aod_init(self):
        self.instructions.append(AODInit(self.fpqa))

    def _bind_init(self):
        for i in len(self.fpqa.atoms):
            atom = self.fpqa.atoms[i]
            self.instructions.append(Bind(self.fpqa, f"q[{i}]", atom, atom.is_slm, atom.row, atom.col))

    def _qubits_init(self) -> str:
        num_qubits = len(self.fpqa.atoms)
        return f"qubit[{num_qubits}] q;\nreset q;\n"
        
    def _wqasm_init(self) -> str:
        lines = ["OpenQASM 3.0;\n"]
        num_qubits = len(self.fpqa.atoms)
        qubit_args = ", ".join([f"q{i}" for i in range(num_qubits)])
        lines.append(f"gate u3_global(a1, a2, a3) {qubit_args} {{")
        for i in range(num_qubits):
            lines.append(f"    U(a1, a2, a3) q{i};")
        lines.append("}\n")
        return "\n".join(line)

    def add_measurement(self):
        num_qubits = len(self.fpqa.atoms)
        lines = [f"bit[{num_qubits}] b;", "b = measure q;"]
        return "\n".join(line)

    def add_instruction(self, instruction: Instruction):
        instruction.apply()
        self.instructions.append(instruction)
        
    def write(self):
        pass

    def load(self):
        pass

    def to_string(self):
        num_qubits = len(self.fpqa.atoms)
        lines = [self._wqasm_init()]
        init_instructions = filter(lambda instr: type(instr) in {SLMInit, AODInit, Bind}, self.instructions)
        exec_instruction = filter(lambda instr: type(instr) not in {SLMInit, AODInit, Bind}, self.instructions)
        for instr in init_instructions:
            lines.append(instr.qasm())
        lines.append(self._qubits_init())
        for instr in exec_instructions:
            lines.append(instr.qasm())
        lines.append(self.add_measurement())
        lines.append("")
        return "\n".join(lines)
        
        