"""
Задание: Валидные скобки
Строка содержит только (), [], {}. Проверь, что скобки расставлены правильно:
каждая открывающая имеет закрывающую того же типа, вложенность допустима.
Закрывающая скобка должна соответствовать последней открытой (LIFO).
Примеры: "()[]{}" → True, "[()]" → True, "({[]})" → True, "([)]" → False.

Совет: стек. Открывающую — клади в стек, закрывающую — сверяй с вершиной стека и снимай.
В конце стек должен быть пуст.
"""
string = input()

stack = []

pairs = {
    "]": "[",
    "}": "{",
    ")": "("
}

for letter in string:
    if letter in "[{(":
        stack.append(letter)
    elif letter in "]})":
        if not stack:
            print(False)
            break
        if stack[-1] == pairs[letter]:
            stack.pop()
        else:
            print(False)
            break
else:
    print(not stack)
