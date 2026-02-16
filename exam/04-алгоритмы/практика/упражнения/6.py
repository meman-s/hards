"""
Задание: Слияние двух отсортированных списков

Что дано:
  Две головы (head1 и head2) двух односвязных списков. Оба списка уже отсортированы по возрастанию.
  Пример: список A = 1 → 3 → 5 → None, список B = 2 → 4 → 6 → None.

Что нужно:
  Получить один отсортированный список из всех элементов обоих: 1 → 2 → 3 → 4 → 5 → 6 → None.
  Вернуть голову этого нового списка.

Важно:
  «Создавай новый список, не меняя исходные узлы» — не менять .val и .next у переданных узлов;
  собирать результат в новые узлы (копируя значения) либо, если в условии разрешено, просто перелинковать
  существующие узлы (брать меньший из двух голов, прицеплять к хвосту результата). Если не указано — обычно
  разрешают перелинковку без копирования.

На вход функции: два аргумента — head1, head2 (узлы или None для пустого списка).
На выход: голова объединённого отсортированного списка.

Совет: dummy-узел в начале, хвост который двигаешь; сравнивай значения в головах двух списков,
меньший прицепляй к хвосту. В конце прицепи оставшийся кусок.
Библиотеки: если на входе два обычных отсортированных списка (не связные), слияние в один отсортированный — heapq.merge(list1, list2); возвращает итератор.
"""

from dataclasses import dataclass
import heapq


@dataclass
class Node:
    val: int = 0
    next: 'Node | None' = None

    def __lt__(self, other: 'Node') -> bool:
        return self.val < other.val


def unite_lists(head1: Node | None, head2: Node | None) -> Node | None:
    if not head1:
        return head2
    if not head2:
        return head1
    dummy = Node()
    tail = dummy
    a, b = head1, head2
    while a and b:
        if a.val <= b.val:
            tail.next = a
            a = a.next
        else:
            tail.next = b
            b = b.next
        tail = tail.next
    tail.next = a if a else b
    return dummy.next


def unite_lists_heapq(list1: list[int], list2: list[int]) -> list[int]:
    return list(heapq.merge(list1, list2))
