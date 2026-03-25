import heapq
from collections import deque


def get_neighbors(node, size):
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    neighbors = []

    for dr, dc in directions:
        row = node[0] + dr
        col = node[1] + dc

        if 0 <= row < size and 0 <= col < size:
            neighbors.append((row, col))

    return neighbors


def _reconstruct_path(came_from, current):
    path = [current]

    while current in came_from:
        current = came_from[current]
        path.append(current)

    path.reverse()
    return path


def bfs(start, goal, obstacles, size):
    queue = deque([start])
    visited = {start}
    came_from = {}

    while queue:
        current = queue.popleft()

        if current == goal:
            return _reconstruct_path(came_from, current)

        for neighbor in get_neighbors(current, size):
            if neighbor in obstacles or neighbor in visited:
                continue

            visited.add(neighbor)
            came_from[neighbor] = current
            queue.append(neighbor)

    return None


def dfs(start, goal, obstacles, size):
    stack = [(start, [start])]
    visited = set()

    while stack:
        current, path = stack.pop()

        if current in visited:
            continue

        visited.add(current)

        if current == goal:
            return path

        for neighbor in reversed(get_neighbors(current, size)):
            if neighbor in obstacles or neighbor in visited:
                continue

            stack.append((neighbor, path + [neighbor]))

    return None


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(start, goal, obstacles, size):
    open_set = []
    heapq.heappush(open_set, (heuristic(start, goal), 0, start))

    came_from = {}
    g_score = {start: 0}
    closed_set = set()

    while open_set:
        _, current_cost, current = heapq.heappop(open_set)

        if current in closed_set:
            continue

        if current == goal:
            return _reconstruct_path(came_from, current)

        closed_set.add(current)

        for neighbor in get_neighbors(current, size):
            if neighbor in obstacles or neighbor in closed_set:
                continue

            tentative_cost = current_cost + 1

            if tentative_cost < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_cost
                f_score = tentative_cost + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, tentative_cost, neighbor))

    return None
