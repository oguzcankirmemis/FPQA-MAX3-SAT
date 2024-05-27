class AOD:
    def __init__(self, rows: int, cols: int, distance: float):
        self.rows = [distance * row for row in rows]
        self.cols = [distance * col for col in cols]
        self.atom_map = [[False for _ in range(cols)] for _ in range(rows)]

    def toggle(self, x: int, y: int):
        self.atom_map[y][x] = not self.atom_map[y][x]
    