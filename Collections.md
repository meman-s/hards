# Collections (deque, Counter, defaultdict, OrderedDict)

## 1. Зачем нужны

Модуль **`collections`** предоставляет специализированные структуры данных, которые решают конкретные задачи эффективнее, чем встроенные типы (`list`, `dict`, `tuple`).

- **`deque`** — двусторонняя очередь: быстрые операции добавления/удаления с обоих концов (O(1) vs O(n) у списка).
- **`Counter`** — счётчик элементов: удобный подсчёт частоты встречаемости.
- **`defaultdict`** — словарь с значениями по умолчанию: не нужно проверять наличие ключа перед добавлением.
- **`OrderedDict`** — упорядоченный словарь: сохраняет порядок вставки элементов (в Python 3.7+ обычный `dict` тоже упорядочен, но `OrderedDict` имеет дополнительные методы).

---

## 2. deque (double-ended queue)

### 2.1 Основные операции

**`deque`** — двусторонняя очередь, оптимизированная для добавления и удаления элементов с обоих концов.

```python
from collections import deque

d = deque([1, 2, 3])
d.append(4)
d.appendleft(0)
d.pop()
d.popleft()
```

Операции:
- **`append(x)`** — добавить справа (O(1)).
- **`appendleft(x)`** — добавить слева (O(1)).
- **`pop()`** — удалить справа (O(1)).
- **`popleft()`** — удалить слева (O(1)).

У списка `list.insert(0, x)` и `list.pop(0)` имеют сложность O(n), так как требуют сдвига всех элементов.

### 2.2 Ограничение размера (maxlen)

`deque` может иметь максимальный размер. При добавлении элемента сверх лимита элемент с противоположного конца удаляется:

```python
d = deque([1, 2, 3], maxlen=3)
d.append(4)
print(d)
```

Выведет: `deque([2, 3, 4], maxlen=3)`. Элемент `1` был автоматически удалён.

Полезно для скользящего окна, истории команд, кеша последних N элементов.

### 2.3 Ротация

**`rotate(n)`** — циклически сдвигает элементы:

```python
d = deque([1, 2, 3, 4, 5])
d.rotate(2)
print(d)
```

Выведет: `deque([4, 5, 1, 2, 3])`. Положительный `n` сдвигает вправо, отрицательный — влево.

### 2.4 Когда использовать deque

| Сценарий | Почему deque |
|----------|--------------|
| Очередь (FIFO) | `append()` + `popleft()` — O(1) |
| Стек (LIFO) | `append()` + `pop()` — O(1) |
| Скользящее окно | `maxlen` + автоматическое удаление |
| История команд | `maxlen` ограничивает размер |
| BFS в графах | Быстрая очередь для обхода |

### 2.5 Индексация и срезы

`deque` поддерживает индексацию (`d[0]`, `d[-1]`), но **не поддерживает срезы** (`d[1:3]` — ошибка). Доступ к элементам по индексу — O(1), но вставка/удаление в середину — O(n) (не рекомендуется).

---

## 3. Counter

### 3.1 Базовое использование

**`Counter`** — подкласс `dict`, предназначенный для подсчёта хешируемых объектов.

```python
from collections import Counter

c = Counter(['a', 'b', 'a', 'c', 'b', 'a'])
print(c)
```

Выведет: `Counter({'a': 3, 'b': 2, 'c': 1})`.

Можно создать из любой итерируемой последовательности, словаря или строки:

```python
Counter("hello")
Counter({'a': 2, 'b': 1})
Counter(a=3, b=2)
```

### 3.2 Операции с Counter

**Обновление счётчика:**

```python
c = Counter(['a', 'b'])
c.update(['a', 'c'])
print(c)
```

Выведет: `Counter({'a': 2, 'b': 1, 'c': 1})`.

**Уменьшение счётчика:**

```python
c = Counter(['a', 'a', 'b'])
c.subtract(['a', 'b'])
print(c)
```

Выведет: `Counter({'a': 1, 'b': 0})`. Отрицательные значения разрешены.

**Доступ к элементам:**

```python
c = Counter(['a', 'a', 'b'])
print(c['a'])
print(c['c'])
```

`c['a']` вернёт `2`, `c['c']` вернёт `0` (не `KeyError`, как в обычном словаре).

### 3.3 Полезные методы

**`most_common(n)`** — возвращает n самых частых элементов:

```python
c = Counter('abracadabra')
print(c.most_common(3))
```

Выведет: `[('a', 5), ('b', 2), ('r', 2)]`.

**`elements()`** — возвращает итератор по всем элементам (каждый элемент повторяется столько раз, сколько его счётчик):

```python
c = Counter(a=3, b=2)
list(c.elements())
```

Выведет: `['a', 'a', 'a', 'b', 'b']`.

**Арифметические операции:**

```python
c1 = Counter(a=3, b=1)
c2 = Counter(a=1, b=2)
print(c1 + c2)
print(c1 - c2)
print(c1 & c2)
print(c1 | c2)
```

- `+` — суммирует счётчики.
- `-` — вычитает (только положительные результаты).
- `&` — пересечение (минимум по каждому ключу).
- `|` — объединение (максимум по каждому ключу).

### 3.4 Типичные сценарии

**Подсчёт частоты символов:**

```python
text = "hello world"
counter = Counter(text)
print(counter.most_common(3))
```

**Подсчёт слов:**

```python
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
counter = Counter(words)
```

**Проверка анаграмм:**

```python
def is_anagram(word1, word2):
    return Counter(word1) == Counter(word2)
```

---

## 4. defaultdict

### 4.1 Проблема обычного dict

При работе с обычным словарём нужно проверять наличие ключа:

```python
d = {}
for key in ['a', 'b', 'a']:
    if key not in d:
        d[key] = []
    d[key].append(1)
```

**`defaultdict`** автоматически создаёт значение по умолчанию при обращении к несуществующему ключу.

### 4.2 Базовое использование

```python
from collections import defaultdict

d = defaultdict(list)
d['a'].append(1)
d['b'].append(2)
```

При обращении к `d['a']`, если ключа нет, вызывается `list()` (фабричная функция), создаётся пустой список и он возвращается.

**Фабричные функции:**

```python
dd_int = defaultdict(int)
dd_list = defaultdict(list)
dd_set = defaultdict(set)
dd_str = defaultdict(str)
dd_lambda = defaultdict(lambda: "default")
```

- `int()` → `0`
- `list()` → `[]`
- `set()` → `set()`
- `str()` → `''`
- `lambda` — любая функция без аргументов

### 4.3 Примеры использования

**Группировка элементов:**

```python
data = [('a', 1), ('b', 2), ('a', 3), ('b', 4)]
grouped = defaultdict(list)
for key, value in data:
    grouped[key].append(value)
```

Результат: `{'a': [1, 3], 'b': [2, 4]}`.

**Подсчёт с defaultdict(int):**

```python
words = ['apple', 'banana', 'apple']
count = defaultdict(int)
for word in words:
    count[word] += 1
```

Эквивалентно `Counter`, но можно использовать любую логику инкремента.

**Граф (список смежности):**

```python
graph = defaultdict(list)
edges = [(1, 2), (1, 3), (2, 3)]
for u, v in edges:
    graph[u].append(v)
    graph[v].append(u)
```

### 4.4 default_factory

Можно получить и изменить фабричную функцию:

```python
d = defaultdict(list)
print(d.default_factory)
d.default_factory = lambda: "empty"
print(d['new_key'])
```

Выведет: `<class 'list'>` и `'empty'`.

Если установить `default_factory = None`, поведение становится как у обычного словаря (будет `KeyError`).

---

## 5. OrderedDict

### 5.1 Зачем нужен (исторически)

В Python 3.7+ обычный `dict` сохраняет порядок вставки, но **`OrderedDict`** имеет дополнительные методы и гарантирует порядок во всех версиях Python.

### 5.2 Основные операции

```python
from collections import OrderedDict

od = OrderedDict()
od['a'] = 1
od['b'] = 2
od['c'] = 3
print(list(od.keys()))
```

Выведет: `['a', 'b', 'c']` — порядок вставки сохранён.

### 5.3 Уникальные методы OrderedDict

**`move_to_end(key, last=True)`** — перемещает элемент в конец (или начало, если `last=False`):

```python
od = OrderedDict([('a', 1), ('b', 2), ('c', 3)])
od.move_to_end('a')
print(list(od.keys()))
```

Выведет: `['b', 'c', 'a']`.

**`popitem(last=True)`** — удаляет и возвращает последний элемент (или первый, если `last=False`):

```python
od = OrderedDict([('a', 1), ('b', 2)])
item = od.popitem(last=False)
print(item, list(od.keys()))
```

Выведет: `('a', 1)` и `['b']`.

### 5.4 Сравнение OrderedDict

Два `OrderedDict` равны, если у них одинаковые пары ключ-значение **и в том же порядке**:

```python
od1 = OrderedDict([('a', 1), ('b', 2)])
od2 = OrderedDict([('b', 2), ('a', 1)])
print(od1 == od2)
```

Выведет: `False` (разный порядок).

Обычные словари в Python 3.7+ тоже сравниваются с учётом порядка, но `OrderedDict` делает это явно.

### 5.5 Типичные сценарии

**LRU-кеш (упрощённо):**

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```

**Сохранение порядка при объединении словарей:**

```python
d1 = OrderedDict([('a', 1), ('b', 2)])
d2 = OrderedDict([('c', 3), ('d', 4)])
merged = OrderedDict(list(d1.items()) + list(d2.items()))
```

---

## 6. Сравнение производительности

| Операция | list | deque | dict | defaultdict |
|----------|------|-------|------|--------------|
| Добавление в начало | O(n) | O(1) | — | — |
| Добавление в конец | O(1) | O(1) | — | — |
| Удаление с начала | O(n) | O(1) | — | — |
| Удаление с конца | O(1) | O(1) | — | — |
| Доступ по ключу | — | — | O(1) | O(1) |
| Проверка ключа | — | — | O(1) | O(1) |

**Вывод:** для очередей и стеков используйте `deque`; для словарей с значениями по умолчанию — `defaultdict`.

---

## 7. Другие коллекции из модуля collections

### 7.1 namedtuple

Создаёт подкласс `tuple` с именованными полями:

```python
from collections import namedtuple

Point = namedtuple('Point', ['x', 'y'])
p = Point(1, 2)
print(p.x, p.y)
```

### 7.2 ChainMap

Объединяет несколько словарей в один (поиск идёт по порядку):

```python
from collections import ChainMap

d1 = {'a': 1, 'b': 2}
d2 = {'b': 3, 'c': 4}
chain = ChainMap(d1, d2)
print(chain['a'], chain['b'], chain['c'])
```

Выведет: `1, 2, 4`. `chain['b']` берётся из первого словаря (`d1`).

---

## 8. Краткая сводка для экзамена

| Коллекция | Назначение | Ключевые особенности |
|-----------|-----------|---------------------|
| **deque** | Двусторонняя очередь | `appendleft()`, `popleft()` — O(1); `maxlen` для ограничения размера; `rotate()` для сдвига |
| **Counter** | Подсчёт элементов | Автоматический подсчёт; `most_common(n)`; арифметические операции (`+`, `-`, `&`, `\|`) |
| **defaultdict** | Словарь с значениями по умолчанию | Автоматическое создание значения при обращении к несуществующему ключу; `default_factory` |
| **OrderedDict** | Упорядоченный словарь | Сохраняет порядок вставки; `move_to_end()`, `popitem()`; сравнение с учётом порядка |
| **namedtuple** | Кортеж с именованными полями | Доступ по имени: `point.x` вместо `point[0]` |
| **ChainMap** | Объединение словарей | Поиск по цепочке словарей по порядку |

### Операции deque

- `append(x)`, `appendleft(x)` — добавление
- `pop()`, `popleft()` — удаление
- `rotate(n)` — циклический сдвиг
- `maxlen` — максимальный размер

### Операции Counter

- `update(iterable)` — увеличить счётчики
- `subtract(iterable)` — уменьшить счётчики
- `most_common(n)` — n самых частых
- `elements()` — итератор по элементам
- Арифметика: `+`, `-`, `&`, `|`

### Операции defaultdict

- `default_factory` — функция для создания значений по умолчанию
- Автоматическое создание при `d[key]`, если ключа нет

### Операции OrderedDict

- `move_to_end(key, last=True)` — переместить элемент
- `popitem(last=True)` — удалить и вернуть элемент
- Сравнение с учётом порядка

---

## 9. Полезные ссылки

- [docs.python.org — collections — High-performance container datatypes](https://docs.python.org/3/library/collections.html)
- [PEP 372 — Adding an ordered dictionary to collections](https://peps.python.org/pep-0372/)
- [Real Python — Python's collections: A Buffet of Specialized Data Types](https://realpython.com/python-collections-module/)
