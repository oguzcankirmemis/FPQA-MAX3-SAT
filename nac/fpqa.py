from math import pow, sqrt
from nac.atom import Atom
from nac.slm.base import SLM
from nac.aod import AOD
from nac.config import FPQAConfig

class FPQA:
    def __init__(self,  slm: SLM, aod: AOD, atoms: list[Atom], config: FPQAConfig):
        self.aod = aod
        self.slm = slm
        self.atoms = atoms
        for atom in self.atoms:
            if atom.is_slm:
                if self.slm.occupied(atom.col, atom.row):
                    raise ValueError("SLM Trap already occupied.")
                self.slm.set_trap(atom.col, atom.row, atom)
            else:
                if self.aod.occupied(atom.col, atom.row):
                    raise ValueError("AOD Trap already occupied.")
                self.aod.set_trap(atom.col, atom.row, atom)
        self.config = config

    def get_atom(self, index: int) -> Atom:
        return self.atoms[index]
    
    def shuttle_row(self, row: int, delta: float):
        next_pos = self.aod.rows[row] + delta
        if row > 0:
            if self.aod.rows[row - 1] > next_pos:
                raise ValueError(f"AOD row constraint violated between rows {row - 1} and {row}.")
            if abs(self.aod.rows[row - 1] - next_pos):
                raise ValueError(f"AOD rows {row - 1} and {row} are too close to each other.")
        if row < len(self.aod.rows) - 1 and self.aod.rows[row + 1] < next_pos:
            if self.aod.rows[row + 1] < next_pos:
                raise ValueError(f"AOD row constraint violated between rows {row} and {row + 1}.")
            if abs(self.aod.rows[row + 1] - next_pos) < _AOD_BEAM_PROXIMITY:
                raise ValueError(f"AOD rows {row} and {row + 1} are too close to each other.")
        self.aod.rows[row] = next_pos

    def shuttle_column(self, col: int, delta: float):
        next_pos = self.aod.cols[col] + delta
        if col > 0:
            if self.aod.cols[col - 1] > next_pos:
                raise ValueError(f"AOD column constraint violated between columns {col - 1} and {column}.")
            if abs(self.aod.cols[col - 1] - next_pos) < _AOD_BEAM_PROXIMITY:
                raise ValueError(f"AOD columns {col - 1} and {col} are too close to each other.")
        if col < len(self.aod.cols) - 1 and self.aod.cols[col + 1] < next_pos:
            if self.aod.cols[col + 1] < next_pos:
                raise ValueError(f"AOD column constraint violated between columns {col} and {column + 1}.")
            if abs(self.aod.col[col + 1] - next_pos) < _AOD_BEAM_PROXIMITY:
                raise ValueError(f"AOD columns {col} and {col + 1} are too close to each other.")
        self.aod.rows[row] = next_pos

    def transfer_traps(self, aod_row: int, aod_column: int, slm_row: int, slm_column: int):
        if self.aod.occupied(aod_column, aod_row) and self.slm.occupied(slm_column, slm_row):
            raise ValueError(f"Cannot transfer traps when both traps are occupied.")
        if not self.aod.occupied(aod_column, aod_row) and not self.slm.occupied(slm_column, slm_row):
            raise ValueError(f"No atom to transfer.")
        slm_x, slm_y = self.slm.position(slm_column, slm_row)
        aod_x, aod_y = self.aod.position(aod_column, aod_row)
        distance = pow(slm_x - aod_x, 2) + pow(slm_y - aod_y, 2)
        if distance > _TRAP_TRANSFER_PROXIMITY:
            raise ValueError(f"Traps are too far away from each other to perform transfer.")
        aod_atom = self.aod.get_atom_at_trap(aod_column, aod_row)
        slm_atom = self.slm.get_atom_at_trap(slm_column, slm_row)
        self.slm.set_trap(slm_column, slm_row, aod_atom)
        self.aod.toggle(aod_column, aod_row, slm_atom)
        if aod_atom is not None:
            aod_atom.assign_trap(True, slm_row, slm_column)
        if slm_atom is not None:
            slm_atom.assign_trap(False, aod_row, aod_column)

    def is_interacting(self, atom1: Atom, atom2: Atom) -> bool:
        pos1 = 0.0, 0.0
        if atom1.is_slm:
            pos1 = self.slm.position(self.atom.col, self.atom.row)
        else:
            pos1 = self.aod.position(self.atom.col, self.atom.row)
        pos2 = 0.0, 0.0
        if atom2.is_slm:
            pos2 = self.slm.position(self.atom.col, self.atom.row)
        else:
            pos2 = self.aod.position(self.atom.col, self.atom.row)
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        distance = sqrt(dx * dx + dy * dy)
        return distance <= self.config["INTERACTION_RADIUS"]

    def apply_local_raman(self):
        pass
        
    def apply_global_raman(self):
        pass

    def apply_global_rydberg(self):
        pass
        
            