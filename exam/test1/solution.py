import pytest
from pymongo import MongoClient
import time
from functools import wraps
from collections import deque
import queue


def bfs_undirected(graph: list[list[int]], start: int):
    n = len(graph)
    visited = [False] * n
    order = []
    q = deque([start])
    visited[start] = True

    while q:
        v = q.popleft()
        order.append(v)
        for u in graph[v]:
            if not visited[u]:
                visited[u] = True
                q.append(u)

    return order


def dfs_undirected(graph: list[list[int]], start: int):
    n = len(graph)
    visited = [False] * n
    order = []

    def dfs(v: int):
        visited[v] = True
        order.append(v)
        for u in graph[v]:
            if not visited[u]:
                dfs(u)
    dfs(start)
    return order


def bfs_directed(graph: list[list[int]], start: int):
    visited = set()
    visited.add(start)
    q = deque([start])

    while q:
        v = q.popleft()
        for u in graph[v]:
            visited.add(u)
            q.append(u)

    return visited


def dfs_directed(graph: list[list[int]], start: int):
    n = len(graph)
    visited = [False] * n

    def dfs(v: int):
        visited[v] = True
        for u in graph[v]:
            if not visited[u]:
                if dfs(u):
                    return True
        return False

    return dfs(start)


def topological_sort(graph: list[list[int]]):
    n = len(graph)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n
    result = []

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


def count_components(graph: list[list[int]]):
    n = len(graph)
    visited = [False] * n
    count = 0

    def dfs(v: int):
        visited[v] = True
        for u in graph[v]:
            if not visited[u]:
                dfs(u)

    for start in range(n):
        if not visited[start]:
            count += 1
            dfs(start)

    return count


def join_strings(strings):
    return ''.join(strings)


def contains_value(items, target):
    for item in items:
        if item == target:
            return True
    return False


def time_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} taked {elapsed}")
        return result

    return wrapper


def find_common_items(list1, list2):
    set2 = set(list2)
    common = []
    for item in list1:
        if item in set2:
            common.append(item)
    return common


client = MongoClient()
db = client["exam_db"]


def mongo_exersice():
    orders = db["orders"]

    pipeline = [
        {"$lookup": {
            "from": "customers",
            "localField": "customer_id",
            "foreignField": "_id",
            "as": "customer"
        }},
        {"$unwind": "$customer"},
        {"$group": {
            "_id": "$customer_id",
            "total_sum": {"$sum": "$total"},
            "name": {"$first": "$customer.name"}
        }},
        {"$sort": {"total_sum": -1}},
        {"$project": {
            "_id": 0,
            "name": 1,
            "total_sum": 1
        }}
    ]

    return list(orders.aggregate(pipeline))


class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Division by zero")
        return a / b


@pytest.fixture
def calculator():
    return Calculator()


class TestCalculator:
    @pytest.mark.parametrize("a, b, result", [
        (3, 5, 8),
        (0, 0, 0),
        (-1, 1, 0),
        (10, -5, 5),
        (100, 200, 300)
    ])
    def test_add(self, a, b, result, calculator):
        assert calculator.add(a, b) == result

    def test_divide_by_zero(self, calculator):
        with pytest.raises(ValueError, match="Division by zero"):
            calculator.divide(3, 0)

    def test_divide_normal(self, calculator):
        assert calculator.divide(10, 2) == 5
        assert calculator.divide(9, 3) == 3
