"""
Задание: BFS по графу
Дан граф как список смежности и стартовая вершина. Верни порядок обхода вершин
в BFS (начиная со стартовой).

Совет: очередь (deque), множество посещённых. Пока очередь не пуста: достать вершину,
добавить в результат, всех непосещённых соседей в очередь и в посещённые.
Библиотеки: collections.deque — очередь с append() и popleft() за O(1); list.pop(0) был бы O(n).
"""

from dataclasses import dataclass
from collections import deque


@datadclass
class Node():
    val: int
    chlds: list["Node | None"]


def bfs(root: Node | None):
