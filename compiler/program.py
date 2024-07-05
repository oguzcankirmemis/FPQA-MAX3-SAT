from nac.instructions.base import Instruction

class FPQAProgram:
    def __init__(self):
        self.instructions = []

    def add_instruction(self, instruction: Instruction):
        self.instructions.append(instruction)
        
    def write(self):
        pass

    def load(self):
        pass

    def to_string(self):
        pass        