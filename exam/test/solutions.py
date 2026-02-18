from collections import deque


def bfs_undirected_1(graph: list[list[int]], start: int):
    n = len(graph)
    visited = [False] * n
    order: list[int] = []
    q: deque[int] = deque([start])
    visited[start] = True

    while q:
        v = q.popleft()
        order.append(v)
        for u in graph[v]:
            if not visited[u]:
                visited[u] = True
                q.append(u)

    return order


def bfs_undirected_2(graph: list[list[int]], start: int):
    n = len(graph)
    distances = [-1] * n
    visited = [False] * n
    q: deque[int] = deque([start])
    visited[start] = True
    distances[start] = 0

    while q:
        v = q.popleft()
        for u in graph[v]:
            if not visited[u]:
                visited[u] = True
                distances[u] = distances[v] + 1
                q.append(u)

    return distances


def topological_sort_1(graph: list[list[int]]):
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
            return None

    return reversed(result)


def process_data(data):
    return [item * 2 for item in data if item > 0]


def find_duplicates(items):
    from collections import Counter

    counter = Counter(items)
    return [item for item, count in counter.items() if count > 1]


def process_large_dataset(data):
    return list(set(data))


class Database:
    def __init__(self):
        self.data = {}

    def insert(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)

    def delete(self, key):
        if key in self.data:
            del self.data[key]
            return True
        return False


def process_data(db, items):
    result = []
    for item in items:
        db.insert(item, item * 2)
        result.append(db.get(item))
    return result
