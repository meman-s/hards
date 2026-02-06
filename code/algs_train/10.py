"""
Задание: Взбирание по лестнице
Лестница из n ступенек. За шаг можно подняться на 1 или 2 ступеньки.
Сколькими разными способами добраться до вершины? Реализуй за O(n) по времени и O(1) по памяти.

Совет: динамика — ways(i) = ways(i-1) + ways(i-2), база ways(1)=1, ways(2)=2.
Хранить только два последних значения, не весь массив.
"""


def path(net: list[list[int]]) -> int:
    h = len(net)
    w = len(net[0])
    for i in range(1, h):
        net[i][0] += net[i - 1][0]
    for j in range(1, w):
        net[0][j] += net[0][j - 1]
    for i in range(1, h):
        for j in range(1, w):
            net[i][j] += min(net[i - 1][j], net[i][j - 1])
    return net[h - 1][w - 1]
