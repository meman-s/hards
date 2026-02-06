from collections import deque
from typing import List


def bfs_directed(
    graph: List[List[int]],
    start: int,
    n: int,
) -> List[int]:
    order: List[int] = []
    visited = [False] * n
    queue: deque[int] = deque([start])
    visited[start] = True

    while queue:
        v = queue.popleft()
        order.append(v)
        for u in graph[v]:
            if not visited[u]:
                visited[u] = True
                queue.append(u)

    return order


def bfs_directed_all_reachable(
    graph: List[List[int]],
    n: int,
) -> List[int]:
    order: List[int] = []
    visited = [False] * n

    for start in range(n):
        if visited[start]:
            continue
        queue: deque[int] = deque([start])
        visited[start] = True
        while queue:
            v = queue.popleft()
            order.append(v)
            for u in graph[v]:
                if not visited[u]:
                    visited[u] = True
                    queue.append(u)

    return order


if __name__ == "__main__":
    n = 5
    edges = [(0, 1), (0, 2), (1, 3), (2, 4), (4, 1)]
    graph: List[List[int]] = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)

    print(bfs_directed(graph, 0, n))
    print(bfs_directed_all_reachable(graph, n))
