from collections import deque
from typing import List, Optional


def bfs_undirected(
    graph: List[List[int]],
    start: int,
    n: Optional[int] = None,
) -> List[int]:
    n = n if n is not None else len(graph)
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


def dfs_undirected(
    graph: List[List[int]],
    start: int,
    n: Optional[int] = None,
) -> List[int]:
    n = n if n is not None else len(graph)
    order: List[int] = []
    visited = [False] * n

    def dfs_recursive(v: int) -> None:
        visited[v] = True
        order.append(v)
        for u in graph[v]:
            if not visited[u]:
                dfs_recursive(u)

    dfs_recursive(start)
    return order


def bfs_directed(
    graph: List[List[int]],
    start: int,
    n: Optional[int] = None,
) -> List[int]:
    n = n if n is not None else len(graph)
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


def dfs_directed(
    graph: List[List[int]],
    start: int,
    n: Optional[int] = None,
) -> List[int]:
    n = n if n is not None else len(graph)
    order: List[int] = []
    visited = [False] * n

    def dfs_recursive(v: int) -> None:
        visited[v] = True
        order.append(v)
        for u in graph[v]:
            if not visited[u]:
                dfs_recursive(u)

    dfs_recursive(start)
    return order


def topological_sort(
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


def find_connected_components(
    graph: List[List[int]],
    n: Optional[int] = None,
) -> List[List[int]]:
    n = n if n is not None else len(graph)
    visited = [False] * n
    components: List[List[int]] = []

    def dfs(v: int, component: List[int]) -> None:
        visited[v] = True
        component.append(v)
        for u in graph[v]:
            if not visited[u]:
                dfs(u, component)

    for start in range(n):
        if not visited[start]:
            component: List[int] = []
            dfs(start, component)
            components.append(component)

    return components


def shortest_path(
    graph: List[List[int]],
    start: int,
    end: int,
    n: Optional[int] = None,
) -> Optional[List[int]]:
    n = n if n is not None else len(graph)
    visited = [False] * n
    parent = [-1] * n
    queue: deque[int] = deque([start])
    visited[start] = True

    while queue:
        v = queue.popleft()
        if v == end:
            path: List[int] = []
            current = end
            while current != -1:
                path.append(current)
                current = parent[current]
            return path[::-1]

        for u in graph[v]:
            if not visited[u]:
                visited[u] = True
                parent[u] = v
                queue.append(u)

    return None


def has_cycle(
    graph: List[List[int]],
    n: Optional[int] = None,
) -> bool:
    n = n if n is not None else len(graph)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n

    def dfs(v: int) -> bool:
        color[v] = GRAY
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


if __name__ == "__main__":
    print("=== Задание 1: BFS неориентированный граф ===")
    graph1 = [[1, 2], [0, 3], [0, 4], [1], [2]]
    print(f"Граф: {graph1}")
    print(f"BFS от вершины 0: {bfs_undirected(graph1, 0)}")
    print()

    print("=== Задание 2: DFS неориентированный граф ===")
    graph2 = [[1, 2], [0, 3], [0, 4], [1], [2]]
    print(f"Граф: {graph2}")
    print(f"DFS от вершины 0: {dfs_undirected(graph2, 0)}")
    print()

    print("=== Задание 3: BFS ориентированный граф ===")
    graph3 = [[1, 2], [3], [4], [], []]
    print(f"Граф: {graph3}")
    print(f"BFS от вершины 0: {bfs_directed(graph3, 0)}")
    print()

    print("=== Задание 4: DFS ориентированный граф ===")
    graph4 = [[1, 2], [3], [4], [], []]
    print(f"Граф: {graph4}")
    print(f"DFS от вершины 0: {dfs_directed(graph4, 0)}")
    print()

    print("=== Задание 5: Топологическая сортировка ===")
    graph5 = [[], [0], [0], [1, 2], [1, 3]]
    n5 = 5
    print(f"Граф: {graph5}")
    print(f"Топологическая сортировка: {topological_sort(graph5, n5)}")
    print()

    print("=== Задание 6: Компоненты связности ===")
    graph6 = [[1], [0], [3], [2], []]
    print(f"Граф: {graph6}")
    print(f"Компоненты связности: {find_connected_components(graph6)}")
    print()

    print("=== Задание 7: Кратчайший путь ===")
    graph7 = [[1, 2], [0, 3], [0, 4], [1], [2]]
    print(f"Граф: {graph7}")
    print(f"Кратчайший путь от 0 до 4: {shortest_path(graph7, 0, 4)}")
    print()

    print("=== Задание 8: Проверка цикла ===")
    graph8_cycle = [[1], [2], [0]]
    graph8_no_cycle = [[1], [2], []]
    print(f"Граф с циклом {graph8_cycle}: {has_cycle(graph8_cycle)}")
    print(f"Граф без цикла {graph8_no_cycle}: {has_cycle(graph8_no_cycle)}")
