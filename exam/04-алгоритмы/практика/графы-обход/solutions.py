from collections import deque


def bfs_undirected(graph: list[list[int, int]], start: int):
    n = len(graph)
    q: deque[int] = deque[start]
    visited = [False] * n
    order: list[int] = []
    visited[start] = True

    while q:
        v = q.popleft()
        order.append(v)
        for u in graph[v]:
            if u not in visited:
                visited[u] = True
                q.append(u)

    return order


def dfs_undirecte(graph: list[list[int, int]], start: int):
    n = len(graph)
    order: list[int] = []
    visited = [False] * n

    def dfs(v: int):
        visited[v] = True
        order.append(v)
        for u in graph[v]:
            if not visited[u]:
                dfs(u)
    dfs(start)
    return order


def bfs_directed(graph: list[list[int, int]], start: int):
    n = len(graph)
    q: deque[int] = deque([start])
    visited = [False] * n
    order: list[int] = []
    visited[start] = True

    while q:
        v = q.popleft()
        order.append(v)
        for u in graph(v):
            if u not in visited:
                visited[u] = True
                q.append(u)
    return order


def dfs_directed(graph: list[list[int, int]], start: int):
    n = len(graph)
    order: list[int] = []
    visited = [False] * n

    def dfs(v: int):
        visited[v] = True
        order.append(v)
        for u in graph[v]:
            if u not in visited:
                dfs(u)

    dfs(start)
    return order


def topological_sort(graph: list[list[int]]):
    n = len(graph)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n
    result: list[int] = []

    def dfs(v: int):
        color[v] = GRAY
        for u in graph[v]:
            if color[u] == GRAY:
                return False
            if color[u] == WHITE and not dfs(u):
                return False
        color[v] = BLACK
        result.append(v)
        return True

    for start in range(n):
        if color[start] == WHITE and not dfs(start):
            return False

    return reversed(result)


def find_connected_components(graph: list[list[int]]):
    n = len(graph)
    visited = [False] * n
    components: list[list[int]] = []

    def dfs(v: int, component: list[int]):
        visited[v] = True
        component.append(v)
        for u in graph[v]:
            if not visited[u]:
                dfs(u, component)

    for start in range(n):
        if not visited[start]:
            component: list[int] = []
            dfs(start, component)
            components.append(component)

    return components


def shortest_path(graph: list[list[int]], start: int, end: int):
    n = len(graph)
    visited = [False] * n
    parent = [-1] * n
    q: deque[int] = deque([start])
    visited[start] = True

    while q:
        v = q.popleft()
        if v == end:
            path: list[int] = []
            current = end
            while current != -1:
                path.append(current)
                current = parent[current]
            return reversed(path)

        for u in graph[v]:
            if not visited[u]:
                visited[u] = True
                parent[u] = v
                q.append(u)
    return None


def has_cycle(graph: list[list[int]]):
    n = len(graph)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n

    def dfs(v: int):
        color[v] == GRAY
        for u in graph[v]:
            if color[u] == GRAY:
                return True
            if color[u] == WHITE and dfs(u):
                return True
        color[v] = BLACK
        return False

    for start in range(n):
        if color[start] == WHITE and dfs(start):
            return True

    return False


graph = [[1, 2], [0, 3], [0, 4], [1], [2]]
start = 0
