from pymongo import MongoClient
from bson import ObjectId
from collections import deque


def shortest_path_bfs(graph: list[list[int]], start: int, target: int):
    n = len(graph)
    visited = [False] * n
    parent = [-1] * n
    q = deque([start])
    visited[start] = True

    while q:
        v = q.popleft()
        if v == target:
            break
        for u in graph[v]:
            if not visited[u]:
                visited[u] = True
                parent[u] = v
                q.append(u)

    if not visited[target]:
        return []

    path = []
    current = target
    while current != -1:
        path.append(current)
        current = parent[current]

    return reversed(path)


def topological_sort_tasks(graph: list[list[int]]):
    n = len(graph)
    WHITE, GRAY, BLACK = 0, 1, 2
    result = []
    color = WHITE * n

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


def find_duplicates(items):
    from collections import Counter

    count = dict(Counter(items))
    dups = [i for i in count if count[i] >= 2]
    return dups


client = MongoClient('mongodb://localhost:27017/')
db = client["exam_db"]


def seed():
    ...


products = db["products"]
pipline = [
    {"$lookup": {
        "from": "orders",
        "localField": "_id",
        "foreignField": "product_id",
        "as": "orders"
    }},
    {"$unwind": "$orders"},
    {"$group": {
        "_id": "$category",
        "total_quantity": {"$sum": "orders.quantity"}
    }},
    {"$sort": {
        "total_quantity": -1
    }},
    {"$project": {
        "category": "$_id",
        "total_quantity": 1
    }}
]

products = db["products"]

