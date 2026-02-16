# functools, itertools

## 1. Зачем нужны

**`functools`** — модуль для работы с функциями: мемоизация, частичное применение, обёртки, сравнение и упорядочивание.

**`itertools`** — модуль для работы с итераторами: комбинации, перестановки, группировка, бесконечные последовательности, фильтрация.

Оба модуля предоставляют готовые инструменты для функционального программирования и эффективной работы с данными без написания собственных реализаций.

---

## 2. functools

### 2.1 @lru_cache — мемоизация

**`lru_cache`** (Least Recently Used cache) — декоратор, который кеширует результаты функции.

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

**Параметры:**
- `maxsize` — максимальное количество кешированных результатов (по умолчанию 128). `None` — без ограничений.
- `typed` — если `True`, аргументы разных типов кешируются отдельно (`f(1)` и `f(1.0)` — разные).

**Очистка кеша:**
```python
fibonacci.cache_clear()
fibonacci.cache_info()
```

`cache_info()` возвращает `CacheInfo` с количеством попаданий, промахов, размерами.

### 2.2 @cache — простой кеш

**`cache`** (Python 3.9+) — упрощённая версия `lru_cache` без ограничения размера:

```python
from functools import cache

@cache
def expensive_function(x):
    return x ** 2
```

Эквивалентно `@lru_cache(maxsize=None)`.

### 2.3 partial — частичное применение

**`partial`** — создаёт новую функцию с частично применёнными аргументами:

```python
from functools import partial

def multiply(x, y):
    return x * y

double = partial(multiply, 2)
print(double(5))
```

Выведет: `10`. `double` эквивалентно `lambda y: multiply(2, y)`.

**С именованными аргументами:**
```python
def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)
```

**Полезно для:**
- Создания специализированных функций из общих.
- Передачи функций с предустановленными параметрами в качестве колбэков.

### 2.4 partialmethod — для методов класса

**`partialmethod`** — аналог `partial` для методов класса:

```python
from functools import partialmethod

class Cell:
    def __init__(self):
        self._alive = False
    
    @property
    def alive(self):
        return self._alive
    
    def set_state(self, state):
        self._alive = state
    
    set_alive = partialmethod(set_state, True)
    set_dead = partialmethod(set_state, False)
```

### 2.5 @wraps — сохранение метаданных

**`wraps`** — декоратор для сохранения метаданных исходной функции в обёртке:

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def example():
    """Example function."""
    pass

print(example.__name__)
print(example.__doc__)
```

Без `@wraps` выведет `wrapper` и `None`; с `@wraps` — `example` и `"Example function."`.

### 2.6 reduce — свёртка последовательности

**`reduce`** — применяет функцию к элементам последовательности, сводя её к одному значению:

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]
product = reduce(lambda x, y: x * y, numbers)
print(product)
```

Выведет: `120` (1 * 2 * 3 * 4 * 5).

**С начальным значением:**
```python
sum_with_init = reduce(lambda x, y: x + y, [1, 2, 3], 10)
print(sum_with_init)
```

Выведет: `16` (10 + 1 + 2 + 3).

**Эквивалент:**
```python
result = initial
for item in iterable:
    result = function(result, item)
```

### 2.7 @total_ordering — автоматическое сравнение

**`total_ordering`** — генерирует недостающие методы сравнения на основе `__eq__` и одного из `__lt__`, `__le__`, `__gt__`, `__ge__`:

```python
from functools import total_ordering

@total_ordering
class Student:
    def __init__(self, name, grade):
        self.name = name
        self.grade = grade
    
    def __eq__(self, other):
        return self.grade == other.grade
    
    def __lt__(self, other):
        return self.grade < other.grade

s1 = Student("Alice", 85)
s2 = Student("Bob", 90)
print(s1 < s2)
print(s1 >= s2)
```

Автоматически генерируются `__le__`, `__gt__`, `__ge__`, `__ne__`.

### 2.8 @singledispatch — перегрузка функций

**`singledispatch`** — перегрузка функции по типу первого аргумента:

```python
from functools import singledispatch

@singledispatch
def process(value):
    return f"Unknown: {value}"

@process.register
def _(value: int):
    return f"Integer: {value}"

@process.register
def _(value: str):
    return f"String: {value}"

@process.register
def _(value: list):
    return f"List with {len(value)} items"
```

При вызове `process(42)` выберется версия для `int`.

**Для методов класса:**
```python
from functools import singledispatchmethod

class Formatter:
    @singledispatchmethod
    def format(self, value):
        return str(value)
    
    @format.register
    def _(self, value: int):
        return f"Integer: {value}"
```

### 2.9 @cached_property — кешируемое свойство

**`cached_property`** (Python 3.8+) — вычисляет значение один раз и кеширует его:

```python
from functools import cached_property

class DataSet:
    def __init__(self, data):
        self._data = data
    
    @cached_property
    def expensive_computation(self):
        print("Computing...")
        return sum(self._data) * 2

ds = DataSet([1, 2, 3])
print(ds.expensive_computation)
print(ds.expensive_computation)
```

"Computing..." выведется только один раз.

---

## 3. itertools — комбинаторика

### 3.1 product — декартово произведение

**`product`** — все комбинации элементов из нескольких итерируемых объектов:

```python
from itertools import product

result = list(product([1, 2], ['a', 'b']))
print(result)
```

Выведет: `[(1, 'a'), (1, 'b'), (2, 'a'), (2, 'b')]`.

**С повторением:**
```python
result = list(product([0, 1], repeat=3))
print(result)
```

Выведет все комбинации из 0 и 1 длиной 3: `[(0, 0, 0), (0, 0, 1), ...]`.

**Применение:** генерация всех возможных пар, перебор всех комбинаций параметров.

### 3.2 permutations — перестановки

**`permutations`** — все перестановки элементов:

```python
from itertools import permutations

result = list(permutations([1, 2, 3]))
print(result)
```

Выведет: `[(1, 2, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), (3, 2, 1)]`.

**С ограничением длины:**
```python
result = list(permutations([1, 2, 3], 2))
```

Выведет перестановки длиной 2: `[(1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2)]`.

### 3.3 combinations — комбинации

**`combinations`** — все комбинации элементов без повторений:

```python
from itertools import combinations

result = list(combinations([1, 2, 3, 4], 2))
print(result)
```

Выведет: `[(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]`.

**С повторениями:**
```python
from itertools import combinations_with_replacement

result = list(combinations_with_replacement([1, 2, 3], 2))
```

Выведет: `[(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)]`.

---

## 4. itertools — бесконечные итераторы

### 4.1 count — счётчик

**`count`** — бесконечный счётчик:

```python
from itertools import count

for i in count(start=10, step=2):
    if i > 20:
        break
    print(i)
```

Выведет: `10, 12, 14, 16, 18, 20`.

**Параметры:**
- `start` — начальное значение (по умолчанию 0).
- `step` — шаг (по умолчанию 1).

### 4.2 cycle — циклическое повторение

**`cycle`** — бесконечно повторяет элементы:

```python
from itertools import cycle

colors = cycle(['red', 'green', 'blue'])
for i, color in enumerate(colors):
    if i >= 5:
        break
    print(color)
```

Выведет: `red, green, blue, red, green`.

### 4.3 repeat — повторение значения

**`repeat`** — повторяет значение заданное количество раз (или бесконечно):

```python
from itertools import repeat

result = list(repeat('A', 5))
print(result)
```

Выведет: `['A', 'A', 'A', 'A', 'A']`.

**Бесконечное повторение:**
```python
for value in repeat('hello'):
    break
```

---

## 5. itertools — фильтрация и группировка

### 5.1 takewhile — пока условие истинно

**`takewhile`** — берёт элементы, пока условие истинно:

```python
from itertools import takewhile

numbers = [1, 4, 6, 4, 1]
result = list(takewhile(lambda x: x < 5, numbers))
print(result)
```

Выведет: `[1, 4]` (остановится на 6).

### 5.2 dropwhile — пропустить пока условие истинно

**`dropwhile`** — пропускает элементы, пока условие истинно:

```python
from itertools import dropwhile

numbers = [1, 4, 6, 4, 1]
result = list(dropwhile(lambda x: x < 5, numbers))
print(result)
```

Выведет: `[6, 4, 1]` (пропустит 1 и 4, начнёт с 6).

### 5.3 filterfalse — фильтр с инверсией

**`filterfalse`** — возвращает элементы, для которых предикат ложен:

```python
from itertools import filterfalse

numbers = [1, 2, 3, 4, 5, 6]
result = list(filterfalse(lambda x: x % 2 == 0, numbers))
print(result)
```

Выведет: `[1, 3, 5]` (нечётные числа).

### 5.4 groupby — группировка

**`groupby`** — группирует последовательные одинаковые элементы:

```python
from itertools import groupby

data = [1, 1, 2, 2, 2, 3, 3]
for key, group in groupby(data):
    print(key, list(group))
```

Выведет:
```
1 [1, 1]
2 [2, 2, 2]
3 [3, 3]
```

**Важно:** группирует только **последовательные** одинаковые элементы. Для группировки всех одинаковых нужно сначала отсортировать.

**С ключом:**
```python
words = ['apple', 'apricot', 'banana', 'berry']
for key, group in groupby(words, key=lambda x: x[0]):
    print(key, list(group))
```

Выведет:
```
a ['apple', 'apricot']
b ['banana', 'berry']
```

### 5.5 compress — фильтр по маске

**`compress`** — фильтрует элементы по булевой маске:

```python
from itertools import compress

data = ['A', 'B', 'C', 'D']
mask = [True, False, True, False]
result = list(compress(data, mask))
print(result)
```

Выведет: `['A', 'C']`.

---

## 6. itertools — комбинирование итераторов

### 6.1 chain — объединение итераторов

**`chain`** — объединяет несколько итераторов в один:

```python
from itertools import chain

list1 = [1, 2, 3]
list2 = [4, 5, 6]
result = list(chain(list1, list2))
print(result)
```

Выведет: `[1, 2, 3, 4, 5, 6]`.

**`chain.from_iterable`** — принимает итерируемый объект с итераторами:

```python
lists = [[1, 2], [3, 4], [5, 6]]
result = list(chain.from_iterable(lists))
print(result)
```

Выведет: `[1, 2, 3, 4, 5, 6]`.

### 6.2 zip_longest — zip с заполнением

**`zip_longest`** — как `zip`, но заполняет недостающие значения:

```python
from itertools import zip_longest

list1 = [1, 2, 3]
list2 = ['a', 'b']
result = list(zip_longest(list1, list2, fillvalue='X'))
print(result)
```

Выведет: `[(1, 'a'), (2, 'b'), (3, 'X')]`.

### 6.3 islice — срез для итератора

**`islice`** — срез для итератора (аналог `list[start:stop:step]`):

```python
from itertools import islice

numbers = range(10)
result = list(islice(numbers, 2, 8, 2))
print(result)
```

Выведет: `[2, 4, 6]` (с 2-го по 8-й с шагом 2).

**Параметры:**
- `iterable` — итерируемый объект.
- `stop` — до какого индекса (или `start, stop` или `start, stop, step`).

### 6.4 tee — дублирование итератора

**`tee`** — создаёт несколько независимых итераторов из одного:

```python
from itertools import tee

numbers = iter([1, 2, 3, 4])
it1, it2 = tee(numbers, 2)
print(list(it1))
print(list(it2))
```

Выведет: `[1, 2, 3, 4]` дважды.

**Важно:** исходный итератор не должен использоваться после `tee`, иначе данные могут быть потеряны.

---

## 7. itertools — накопление и аккумуляция

### 7.1 accumulate — накопление

**`accumulate`** — накапливает результаты применения функции:

```python
from itertools import accumulate

numbers = [1, 2, 3, 4, 5]
result = list(accumulate(numbers))
print(result)
```

Выведет: `[1, 3, 6, 10, 15]` (суммы: 1, 1+2, 1+2+3, ...).

**С функцией:**
```python
result = list(accumulate([1, 2, 3, 4], func=lambda x, y: x * y))
print(result)
```

Выведет: `[1, 2, 6, 24]` (произведения).

**С начальным значением (Python 3.8+):**
```python
result = list(accumulate([1, 2, 3], initial=10))
print(result)
```

Выведет: `[10, 11, 13, 16]`.

---

## 8. Практические примеры

### 8.1 Генерация всех пар

```python
from itertools import product

def generate_pairs(items):
    return list(product(items, repeat=2))
```

### 8.2 Поиск подпоследовательностей

```python
from itertools import combinations

def find_subsets(items, size):
    return list(combinations(items, size))
```

### 8.3 Группировка по ключу

```python
from itertools import groupby

def group_by_key(data, key_func):
    sorted_data = sorted(data, key=key_func)
    return {k: list(g) for k, g in groupby(sorted_data, key=key_func)}
```

### 8.4 Скользящее окно

```python
from itertools import islice, tee

def sliding_window(iterable, n):
    iters = tee(iterable, n)
    for i, it in enumerate(iters):
        for _ in range(i):
            next(it, None)
    return zip(*iters)

result = list(sliding_window([1, 2, 3, 4, 5], 3))
print(result)
```

Выведет: `[(1, 2, 3), (2, 3, 4), (3, 4, 5)]`.

### 8.5 Мемоизация рекурсивных функций

```python
from functools import lru_cache

@lru_cache(maxsize=None)
def edit_distance(s1, s2):
    if not s1:
        return len(s2)
    if not s2:
        return len(s1)
    if s1[0] == s2[0]:
        return edit_distance(s1[1:], s2[1:])
    return 1 + min(
        edit_distance(s1[1:], s2),
        edit_distance(s1, s2[1:]),
        edit_distance(s1[1:], s2[1:])
    )
```

---

## 9. Краткая сводка для экзамена

### functools

| Функция/Декоратор | Назначение |
|-------------------|------------|
| `@lru_cache` | Кеширование результатов функции (LRU) |
| `@cache` | Простой кеш без ограничения размера |
| `partial` | Частичное применение аргументов |
| `partialmethod` | Частичное применение для методов класса |
| `@wraps` | Сохранение метаданных функции в обёртке |
| `reduce` | Свёртка последовательности к одному значению |
| `@total_ordering` | Автоматическая генерация методов сравнения |
| `@singledispatch` | Перегрузка функции по типу первого аргумента |
| `@cached_property` | Кешируемое свойство класса |

### itertools — комбинаторика

| Функция | Назначение |
|---------|------------|
| `product` | Декартово произведение (все комбинации) |
| `permutations` | Перестановки элементов |
| `combinations` | Комбинации без повторений |
| `combinations_with_replacement` | Комбинации с повторениями |

### itertools — бесконечные итераторы

| Функция | Назначение |
|---------|------------|
| `count` | Бесконечный счётчик |
| `cycle` | Циклическое повторение элементов |
| `repeat` | Повторение значения |

### itertools — фильтрация

| Функция | Назначение |
|---------|------------|
| `takewhile` | Элементы, пока условие истинно |
| `dropwhile` | Пропустить элементы, пока условие истинно |
| `filterfalse` | Элементы, для которых предикат ложен |
| `compress` | Фильтр по булевой маске |

### itertools — группировка и комбинирование

| Функция | Назначение |
|---------|------------|
| `groupby` | Группировка последовательных одинаковых элементов |
| `chain` | Объединение нескольких итераторов |
| `chain.from_iterable` | Объединение итераторов из итерируемого объекта |
| `zip_longest` | zip с заполнением недостающих значений |
| `islice` | Срез для итератора |
| `tee` | Дублирование итератора |

### itertools — накопление

| Функция | Назначение |
|---------|------------|
| `accumulate` | Накопление результатов применения функции |

---

## 10. Полезные ссылки

- [docs.python.org — functools — Higher-order functions and operations on callable objects](https://docs.python.org/3/library/functools.html)
- [docs.python.org — itertools — Functions creating iterators for efficient looping](https://docs.python.org/3/library/itertools.html)
- [Real Python — Python's functools Module](https://realpython.com/python-functools-module/)
- [Real Python — Python Itertools](https://realpython.com/python-itertools/)
