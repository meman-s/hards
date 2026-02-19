import random
import time
from functools import wraps
from tkinter import N
from pymongo.synchronous import database
import pytest
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


def process_data_1(data):
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


@pytest.fixture(scope="function")
def db():
    database = Database()
    yield database
    database.data.clear()


@pytest.mark.unit
@pytest.mark.parametrize("items, result", [
    ([1, 2, 3], [2, 4, 6]),
    ([2, 7], [4, 14]),
    ([0, 0, 0], [0, 0, 0]),
    (["q", "ss"], ["qq", "ssss"])
])
def test_precess_data(db, items, result):
    assert process_data(db, items) == result
    for idx, item in enumerate(items):
        assert db.get(item) == result[idx]


@pytest.fixture
def sample_prices():
    return [1, 2, 3, 4]


def validate_email(email):
    if not email or '@' not in email:
        return False
    parts = email.split('@')
    if len(parts) != 2:
        return False
    local, domain = parts
    if not local or not domain:
        return False
    if '.' not in domain:
        return False
    return True


def calculate_total(prices, discount=0):
    if not prices:
        return 0
    total = sum(prices)
    if discount > 0:
        total = total * (1 - discount / 100)
    return total


@pytest.mark.parametrize("email, result", [
    ("test@example.com", True),
    ("user@domain.co.uk", True),
    ("invalid", False),
    ("@domain.com", False),
    ("user@", False),
    ("user@domain", False),
    ("", False),
    (None, False)
])
def test_validate_email(email, result):
    assert validate_email(email) == result


class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Division by zero")
        return a / b

    def power(self, a, b):
        return a ** b


# class TestCalculator():


def elapsed_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter() - start
        print(f"{func.__name__} took {end} sec")
        return result
    return wrapper


@elapsed_decorator
def count_pairs_with_sum(arr, target):
    from itertools import combinations
    from functools import reduce
    from collections import Counter

    s = sorted(arr)
    n = len(arr)
    x = 0
    y = n - 1
    count = 0
    while x != y:
        if s[x] + s[y] == target:
            count += 1
            print(s[x:x+2], s[y-2:y])
            if s[y-1] != s[y]:
                x += 1
            elif s[x+1] != s[x]:
                y -= 1
            else:
                x += 1
        if s[x] + s[y] < target:
            x += 1
        if s[x] + s[y] > target:
            y -= 1
    return count

    # res = reduce(lambda x, y: x+y, list(combinations(arr, 2)))
    # c = Counter(res)
    # return c[target]

    # count = 0
    # for i in range(len(arr)):
    #     for j in range(i + 1, len(arr)):
    #         if arr[i] + arr[j] == target:
    #             count += 1
    # return count

    # from collections import Counter
    # freq = Counter(arr)
    # count = 0
    # for x in freq:
    #     y = target - x
    #     if y < x:
    #         continue
    #     if y == x:
    #         count += freq[x] * (freq[x] - 1) // 2
    #     elif y in freq:
    #         count += freq[x] * freq[y]
    # return count


@elapsed_decorator
def merge_sorted_lists(lists):
    from itertools import chain
    return sorted(chain(*lists))

    # result = []
    # for lst in lists:
    #     for val in lst:
    #         result.append(val)
    # return sorted(result)


lists = [random.randint(1, 100) for _ in range(10000)]
# print(count_pairs_with_sum(lists, target=50))


def is_bipartite(graph: list[list[int]]):
    n = len(graph)
    color = [-1] * n

    for start in range(n):
        if color[start] != -1:
            continue

        q: deque[int] = deque([start])
        color[start] = 0

        while q:
            v = q.popleft()
            for u in graph[v]:
                if color[u] == -1:
                    color[u] = 1 - color[v]
                elif color[u] == color[v]:
                    return False
    return True


def count_components_undirected(graph: list[list[int]]):
    n = len(graph)
    visited = [False] * n
    count = 0

    def dfs(v: int):
        visited[v] = True
        for u in graph[v]:
            if not visited[u]:
                dfs(u)

    for start in range(n):
        if not visited(start):
            count += 1
            dfs(count)

    return count


def has_cycle_directed(graph: list[list[int]]):
    n = len(graph)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n

    def dfs(v: int):
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


def bfs_directed_distances(graph: list[list[int]], start: int):
    n = len(graph)
    dist = [-1] * n
    dist[start] = 0
    q: deque[int] = deque([start])

    while q:
        v = q.popleft()
        for u in graph[v]:
            if dist[u] == -1:
                dist[u] = dist[v] + 1
                q.append(u)

    return dist


def sources_and_sinks(graph: list[list[int]]):
    n = len(graph)
    in_deg = [0] * n
    for v in range(n):
        for u in graph[v]:
            in_deg[u] += 1
    sources = [v for v in range(n) if in_deg[v] == 0]
    sinks = [v for v in range(n) if len(graph[v]) == 0]
    return (sources, sinks)
