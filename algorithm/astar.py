"""
A* heuristic search for risk-aware fire evacuation.

f(n) = g(n) + h(n)
g(n): accumulated movement cost; h(n): Manhattan distance; f(n): estimated total cost.
"""
import heapq

MOVE_COST = {"safe": 1, "crowd": 3, "smoke": 5, "risk": 10, "exit": 1}
IMPASSABLE = {"fire", "blocked"}
VALID_TYPES = set(MOVE_COST) | IMPASSABLE
NEAR_FIRE_COST = 10


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def neighbours(grid, r, c):
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
            yield nr, nc


def is_near_fire(grid, r, c):
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            nr, nc = r + dr, c + dc
            if (dr or dc) and 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if grid[nr][nc] == "fire":
                    return True
    return False


def step_cost(grid, r, c):
    kind = grid[r][c]
    if kind in IMPASSABLE:
        return None
    cost = MOVE_COST[kind]
    if is_near_fire(grid, r, c):
        cost = max(cost, NEAR_FIRE_COST)
    return cost


def astar(grid, start, goal):
    if step_cost(grid, *start) is None:
        return None
    h_start = manhattan(start, goal)
    counter = 0
    open_list = [(h_start, h_start, counter, start)]
    g_score = {start: 0}
    parent = {}
    closed = set()
    explored = []

    while open_list:
        f, h, _, node = heapq.heappop(open_list)
        if node in closed:
            continue
        closed.add(node)
        g = f - h
        explored.append({"r": node[0], "c": node[1], "g": g, "h": h, "f": f})
        if node == goal:
            path = [node]
            while node in parent:
                node = parent[node]
                path.append(node)
            path.reverse()
            return _summarise(grid, path, g, explored)

        for nb in neighbours(grid, *node):
            cost = step_cost(grid, *nb)
            if cost is None or nb in closed:
                continue
            new_g = g + cost
            if new_g < g_score.get(nb, float("inf")):
                g_score[nb] = new_g
                parent[nb] = node
                new_h = manhattan(nb, goal)
                counter += 1
                heapq.heappush(open_list, (new_g + new_h, new_h, counter, nb))
    return None


def _summarise(grid, path, total_cost, explored):
    risk = sum(step_cost(grid, r, c) - 1 for r, c in path[1:])
    return {
        "path": [list(p) for p in path],
        "cost": total_cost,
        "distance": len(path) - 1,
        "risk": risk,
        "explored": explored,
    }


def find_best_route(grid, start, exits):
    best, best_exit, alternatives = None, None, []
    for ex in exits:
        res = astar(grid, tuple(start), tuple(ex))
        if res is None:
            alternatives.append({"exit": list(ex), "reachable": False})
            continue
        alternatives.append({"exit": list(ex), "reachable": True,
                             "cost": res["cost"], "distance": res["distance"],
                             "risk": res["risk"]})
        if best is None or (res["cost"], res["distance"]) < (best["cost"], best["distance"]):
            best, best_exit = res, ex
    if best is None:
        return {"found": False, "alternatives": alternatives}
    return {"found": True, "exit": list(best_exit), "alternatives": alternatives, **best}
