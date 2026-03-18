import heapq

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def get_neighbors(node, size):
    neighbors = []
    directions = [(-1,0), (1,0), (0,-1), (0,1)]

    for d in directions:
        r = node[0] + d[0]
        c = node[1] + d[1]

        if 0 <= r < size and 0 <= c < size:
            neighbors.append((r, c))

    return neighbors

def a_star(start, goal, obstacles, size):
    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        for neighbor in get_neighbors(current, size):
            if neighbor in obstacles:
                continue

            temp_g = g_score[current] + 1

            if neighbor not in g_score or temp_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g
                f_score = temp_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))

    return None

def bfs(start, goal, obstacles, size):
    queue = [(start, [start])]
    visited = set()

    while queue:
        current, path = queue.pop(0)

        if current == goal:
            return path

        if current in visited:
            continue

        visited.add(current)

        for neighbor in get_neighbors(current, size):
            if neighbor not in obstacles and neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))

    return None

def dfs(start, goal, obstacles, size):
    stack = [(start, [start])]
    visited = set()

    while stack:
        current, path = stack.pop()

        if current == goal:
            return path

        if current in visited:
            continue

        visited.add(current)

        for neighbor in get_neighbors(current, size):
            if neighbor not in obstacles and neighbor not in visited:
                stack.append((neighbor, path + [neighbor]))

    return None

def calculate_risk(path, obstacles, size):
    risk = 0

    directions = [(-1,0), (1,0), (0,-1), (0,1)]

    for (r, c) in path:
        for d in directions:
            nr = r + d[0]
            nc = c + d[1]

            if 0 <= nr < size and 0 <= nc < size:
                if (nr, nc) in obstacles:
                    risk += 1

    return risk