from typing import List, Optional


def topological_sort_dfs(
    graph: List[List[int]],
    n: int,
) -> Optional[List[int]]:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n
    result: List[int] = []

    def dfs(v: int) -> bool:
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
            return None

    return result[::-1]


def topological_sort_kahn(
    graph: List[List[int]],
    n: int,
) -> Optional[List[int]]:
    in_degree = [0] * n
    for v in range(n):
        for u in graph[v]:
            in_degree[u] += 1

    queue: List[int] = [v for v in range(n) if in_degree[v] == 0]
    result: List[int] = []
    idx = 0

    while idx < len(queue):
        v = queue[idx]
        idx += 1
        result.append(v)
        for u in graph[v]:
            in_degree[u] -= 1
            if in_degree[u] == 0:
                queue.append(u)

    return result if len(result) == n else None


if __name__ == "__main__":
    n = 6
    edges = [(5, 2), (5, 0), (4, 0), (4, 1), (2, 3), (3, 1)]
    graph: List[List[int]] = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)

    print(topological_sort_dfs(graph, n))
    print(topological_sort_kahn(graph, n))
