import random
from pysat.formula import CNF

random.seed()

def uniformly_random_independent_clauses(num_clauses: int, start_literal_id: int=1) -> list[tuple[int]]:
    literal = start_literal_id
    clauses = []
    for _ in range(num_clauses):
        signs = list(map(lambda s: 1 if s == 1 else -1, [random.getrandbits(1) for _ in range(3)]))
        clause = [signs[i] * (literal + i) for i in range(3)]
        clauses.append(tuple(clause))
        literal += 3
    return clauses

def get_graph(formula: CNF) -> tuple[list[int], list[list[bool]]]
    N = len(formula.clauses)
    V = [i for i in range(N)]
    E = [[False] * N for _ in range(N)]
    for u in range(N):
        for v in range(u + 1, N):
            E[u][v] = True
            E[v][u] = True 
    return V, E

def get_color_map(formula: CNF) -> list[int]:
    V, E = get_graph(formula)
    color_map = [None for clause in formula.clauses]
    color_map[0] = 0
    colored = set([0])
    uncolored = set(i for i in range(1, len(formula.clauses)))
    while len(uncolored) > 0:
        choosen, curr_saturation = -1, 0 
        for clause in uncolored:
            saturation = 0
            for colored_clause in colored:
                if E[clause][colored_clause]:
                    saturation += 1
            if saturation > curr_saturation:
                choosen = clause
                curr_saturation = saturation
            used_colors = filter(lambda v: color_map[v] is not None, E[choosen])
            used_colors.sort()
            color_map[choosen] = used_colors[-1] + 1
            prev_used_color = -1
            for curr_used_color in used_colors:
                if curr_used_color - prev_used_color > 1:
                    color_map[choosen] = prev_used_color + 1
                    break
                prev_used_color = curr_used_color
            colored.add(choosen)
            uncolored.remove(chosen)
    return color_map