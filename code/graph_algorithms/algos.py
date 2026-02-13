from collections import deque


def bfs_undirected(
    grahp: list[list[int]],
    start: int,
    n: int
) -> list[int]:
    order: list[int] = []
    visited = [False] * n
    queue: deque[int] = deque([start])
    visited[start] = True

    while queue:
        v = queue.popleft()
        order.append(v)
        for u in grahp[v]:
            if not visited[u]:
                visited[u] = True
                queue.append(u)
    return order


def bfs_undirected_all_components(
    graph: list[list[int]],
    n: int
) -> list[int]:
    order: list[int] = []
    visited = [False] * n

    for start in range(n):
        if visited[n]:
            continue
        queue: deque[int] = deque([start])
        visited[start] = True

        while queue:
            v = queue.popleft()
            for u in graph[v]:
                if not visited[u]:
                    visited[u] = True
                    queue.append(u)
    return order


def dfs_directed_recursive(
    graph: list[list[int]],
    start: int,
    visited: list[bool],
    order: list[int]
):
    order.append(start)
    visited[start] = True
    for u in graph[start]:
        if not visited[u]
        dfs_directed_recursive(graph, u, visited, order)


def bfs_undirected(
    graph,
    start,
    n
):
    order = []
    visited = [False] * n

    for start in range(n):
        if visited[start]:
            continue
        visited[start] = True
        queue = deque([start])
    
        while queue:
            v = queue.popleft()
            order.append(v)
            for u in graph[v]:
                if not visited[u]:
                    visited[u] = True
                    queue.append(u)
    return order

def dfs_undirected(
        graph,
        start,
        visited,
        order
):
    visited[start] = True
    order.append(start)
    for u in graph[start]:
        if not visited[u]:
            dfs_undirected(graph, u, visited, order)


if __name__ == "main":
    n = 5
    edges = [(0, 1), (1, 2), (0, 2), (1, 3), (2, 4)]
    graph = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append[b]
        graph[b].append[a]



