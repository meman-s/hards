from typing import List


def dfs_undirected_recursive(
    graph: List[List[int]],
    start: int,
    visited: List[bool],
    order: List[int],
) -> None:
    visited[start] = True
    order.append(start)
    for u in graph[start]:
        if not visited[u]:
            dfs_undirected_recursive(graph, u, visited, order)


def dfs_undirected_iterative(
    graph: List[List[int]],
    start: int,
    n: int,
) -> List[int]:
    order: List[int] = []
    visited = [False] * n
    stack: List[int] = [start]

    while stack:
        v = stack.pop()
        if visited[v]:
            continue
        visited[v] = True
        order.append(v)
        for u in reversed(graph[v]):
            if not visited[u]:
                stack.append(u)

    return order


def dfs_undirected_all_components(
    graph: List[List[int]],
    n: int,
) -> List[int]:
    order: List[int] = []
    visited = [False] * n

    def dfs(v: int) -> None:
        visited[v] = True
        order.append(v)
        for u in graph[v]:
            if not visited[u]:
                dfs(u)

    for start in range(n):
        if not visited[start]:
            dfs(start)

    return order


if __name__ == "__main__":
    n = 5
    edges = [(0, 1), (0, 2), (1, 3), (2, 4)]
    graph: List[List[int]] = [[] for _ in range(n)]
    for a, b in edges:
        graph[a].append(b)
        graph[b].append(a)

    visited = [False] * n
    order_rec: List[int] = []
    dfs_undirected_recursive(graph, 0, visited, order_rec)
    print(order_rec)
    print(dfs_undirected_iterative(graph, 0, n))
    print(dfs_undirected_all_components(graph, n))
