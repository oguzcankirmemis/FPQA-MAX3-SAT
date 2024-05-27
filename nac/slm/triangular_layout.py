from math import sqrt
from slm.base import SLM
from nac.slm.trap import Trap

class TriangularLayout(SLM):
    def __init__(self, rows: int, cols: int):
        if distance <= 0:
            raise ValueError("Invalid distance.")
        if rows <= 0:
            raise ValueError("Invalid number of rows.")
        if cols <= 0:
            raise ValueError("Invalid number of cols.")
        xy_distance = distance / sqrt(2)
        self.traps = [
            [
                Trap(col * xy_distance + xy_distance if row % 2 == 0 else 0, row * xy_distance, False) 
                for col in range(cols)
            ] 
            for row in rows
        ]

    def toggle(self, x: int, y: int):
        self.traps[y][x].has_atom = not self.traps[y][x].has_atom
        
        