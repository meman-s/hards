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
