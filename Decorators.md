# Decorators (декораторы)

## 1. Зачем нужны

Декоратор — функция, которая принимает другую функцию и возвращает новую функцию, обычно расширяя или изменяя поведение исходной. Это паттерн для **переиспользования кода** без дублирования: логирование, кеширование, проверка прав доступа, замер времени, валидация аргументов.

Без декораторов пришлось бы оборачивать каждую функцию вручную:

```python
def slow_function():
    start = time.time()
    result = compute()
    print(f"Took {time.time() - start}s")
    return result
```

С декоратором логика выносится в одно место и применяется к любой функции одной строкой.

---

## 2. Синтаксис декоратора

### 2.1 Базовый синтаксис

```python
@decorator
def my_function():
    pass
```

Эквивалентно:

```python
def my_function():
    pass
my_function = decorator(my_function)
```

Декоратор вызывается **сразу при определении функции** (не при вызове), принимает функцию как аргумент и возвращает новую функцию (или ту же, но модифицированную).

### 2.2 Простой пример

```python
def uppercase(func):
    def wrapper():
        result = func()
        return result.upper()
    return wrapper

@uppercase
def greet():
    return "hello"

print(greet())
```

Выведет `"HELLO"`. `wrapper` — внутренняя функция, которая вызывает исходную `func` и модифицирует результат.

---

## 3. Декоратор как функция

### 3.1 Структура декоратора

Декоратор — это **callable** (функция или класс с `__call__`), который:
1. Принимает функцию (или callable) как аргумент.
2. Возвращает новую функцию (или callable), которая обычно вызывает исходную.

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Finished {func.__name__}")
        return result
    return wrapper
```

`*args, **kwargs` нужны, чтобы декоратор работал с функциями с любым количеством аргументов.

### 3.2 Сохранение метаданных

После декорирования `wrapper` заменяет исходную функцию, и метаданные (имя, документация) теряются:

```python
@my_decorator
def add(a, b):
    """Adds two numbers."""
    return a + b

print(add.__name__)
```

Выведет `"wrapper"`, а не `"add"`. Решение — использовать **`functools.wraps`**:

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

`@wraps(func)` копирует `__name__`, `__doc__`, `__module__` и другие атрибуты из исходной функции в `wrapper`.

---

## 4. Декораторы с аргументами

### 4.1 Декоратор с параметрами

Если декоратор должен принимать аргументы (например, уровень логирования, количество повторов), нужна **двухуровневая структура**:

```python
def repeat(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(times=3)
def say_hello():
    print("Hello")
```

Структура:
- Внешняя функция (`repeat`) принимает аргументы декоратора и возвращает декоратор.
- Внутренняя функция (`decorator`) принимает функцию и возвращает обёртку.
- `wrapper` — финальная обёртка, которая вызывает исходную функцию.

### 4.2 Опциональные аргументы

Если декоратор может использоваться и с аргументами, и без них, нужна проверка:

```python
def retry(max_attempts=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    print(f"Attempt {attempt + 1} failed: {e}")
        return wrapper
    
    if callable(max_attempts):
        func = max_attempts
        max_attempts = 3
        return decorator(func)
    return decorator
```

Или проще через проверку типа:

```python
def retry(max_attempts=3):
    if callable(max_attempts):
        func = max_attempts
        max_attempts = 3
        return retry(max_attempts)(func)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if attempt == max_attempts - 1:
                        raise
        return wrapper
    return decorator
```

---

## 5. Несколько декораторов

Декораторы применяются **снизу вверх** (от функции к внешнему):

```python
@decorator1
@decorator2
@decorator3
def my_function():
    pass
```

Эквивалентно:

```python
my_function = decorator1(decorator2(decorator3(my_function)))
```

Сначала применяется `decorator3`, затем `decorator2`, затем `decorator1`. При вызове выполнение идёт в обратном порядке: сначала логика `decorator1`, потом `decorator2`, потом `decorator3`, затем сама функция, затем возврат через все обёртки.

---

## 6. Декоратор как класс

Класс с методом `__call__` тоже может быть декоратором:

```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.count = 0
        functools.update_wrapper(self, func)
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"{self.func.__name__} called {self.count} times")
        return self.func(*args, **kwargs)

@CountCalls
def greet(name):
    return f"Hello, {name}"

greet("Alice")
greet("Bob")
```

Преимущество класса — можно хранить состояние между вызовами (счётчик, кеш и т.д.).

### 6.1 Класс-декоратор с аргументами

```python
class Timer:
    def __init__(self, func=None, *, unit="seconds"):
        self.func = func
        self.unit = unit
        if func:
            functools.update_wrapper(self, func)
    
    def __call__(self, *args, **kwargs):
        if self.func is None:
            self.func = args[0]
            functools.update_wrapper(self, self.func)
            return self
        
        start = time.perf_counter()
        result = self.func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{self.func.__name__} took {elapsed:.2f} {self.unit}")
        return result

@Timer(unit="ms")
def slow_function():
    time.sleep(0.1)
```

---

## 7. Встроенные декораторы в Python

### 7.1 @property, @staticmethod, @classmethod

- **`@property`** — превращает метод в атрибут (геттер). Можно добавить `@<name>.setter` и `@<name>.deleter`.

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius must be positive")
        self._radius = value
```

- **`@staticmethod`** — статический метод, не получает `self` или `cls`.

- **`@classmethod`** — метод класса, получает `cls` (класс) первым аргументом.

### 7.2 @functools.lru_cache

Кеширует результаты функции (LRU — least recently used):

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

### 7.3 @functools.singledispatch

Перегрузка функций по типу первого аргумента:

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
```

### 7.4 @dataclass (Python 3.7+)

Автоматически генерирует `__init__`, `__repr__`, `__eq__` и другие методы:

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
```

---

## 8. Типичные сценарии использования

| Сценарий | Пример |
|----------|--------|
| Логирование | Записывать вызовы функции с аргументами и результатами |
| Кеширование | Сохранять результаты вычислений (memoization) |
| Замер времени | Измерять время выполнения функции |
| Повторы (retry) | Повторять вызов при ошибке |
| Валидация | Проверять типы или значения аргументов перед вызовом |
| Авторизация | Проверять права доступа перед выполнением |
| Дебаунс/троттлинг | Ограничивать частоту вызовов функции |
| Транзакции | Начинать/завершать транзакцию БД вокруг функции |

---

## 9. Декораторы для методов класса

Декоратор, применяемый к методу, получает метод как аргумент. Если нужно обращаться к экземпляру класса, используйте `*args` и проверяйте первый аргумент:

```python
def log_method(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        print(f"{self.__class__.__name__}.{func.__name__} called")
        return func(self, *args, **kwargs)
    return wrapper

class MyClass:
    @log_method
    def method(self, x):
        return x * 2
```

Или через дескриптор (продвинутый вариант):

```python
class LoggedMethod:
    def __init__(self, func):
        self.func = func
        functools.update_wrapper(self, func)
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return functools.partial(self.func, obj)
```

---

## 10. Краткая сводка для экзамена

| Термин | Кратко |
|--------|--------|
| Декоратор | Функция, принимающая функцию и возвращающая новую функцию |
| @decorator | Синтаксический сахар: `func = decorator(func)` |
| @functools.wraps | Сохраняет метаданные исходной функции (`__name__`, `__doc__` и т.д.) |
| Декоратор с аргументами | Двухуровневая структура: внешняя функция принимает аргументы, внутренняя — функцию |
| Несколько декораторов | Применяются снизу вверх; выполнение при вызове — сверху вниз |
| Класс-декоратор | Класс с `__call__` может быть декоратором; удобно для хранения состояния |
| @property | Превращает метод в атрибут (геттер/сеттер) |
| @staticmethod | Статический метод (не получает `self`) |
| @classmethod | Метод класса (получает `cls`) |
| @lru_cache | Кеширует результаты функции |
| @dataclass | Автоматически генерирует методы для класса данных |

---

## 11. Полезные ссылки

- [PEP 318 — Decorators for Functions and Methods](https://peps.python.org/pep-0318/)
- [PEP 3129 — Class Decorators](https://peps.python.org/pep-3129/)
- [docs.python.org — Decorators](https://docs.python.org/3/glossary.html#term-decorator)
- [functools — документация](https://docs.python.org/3/library/functools.html)
- [Real Python — Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/)
