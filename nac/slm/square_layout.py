from slm.base import SLM
from nac.slm.trap import Trap

class SquareGrid(SLM):
    def __init__(self, distance: float, rows: int, cols: int):
        if distance <= 0:
            raise ValueError("Invalid distance.")
        if rows <= 0:
            raise ValueError("Invalid number of rows.")
        if cols <= 0:
            raise ValueError("Invalid number of cols.")
        self.traps = [
            [
                Trap(distance * col, distance * row, False) 
                for col in range(cols)
            ]
            for row in range(rows)
        ]

    def toggle(self, x: int, y: int):
        self.traps[y][x].has_atom = not self.traps[y][x].has_atom