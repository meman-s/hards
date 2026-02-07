# Generators, iterators, async generators

## 1. Зачем нужны

**Итераторы** и **генераторы** позволяют обрабатывать данные **поэлементно**, не загружая всё в память сразу. Это критично для больших объёмов данных (файлы, потоки, бесконечные последовательности).

**Асинхронные генераторы** — то же самое, но для асинхронного кода: можно приостанавливать выполнение и ждать других операций (I/O, сетевые запросы) без блокировки всего приложения.

Без итераторов пришлось бы загружать всё в список:

```python
def read_all_lines(filename):
    with open(filename) as f:
        return f.readlines()
```

Если файл огромный, это может привести к нехватке памяти. Итераторы позволяют читать по одной строке.

---

## 2. Итераторы (iterators)

### 2.1 Протокол итератора

**Итератор** — объект, который реализует протокол итератора:
- Метод **`__iter__()`** — возвращает сам итератор (или другой итератор).
- Метод **`__next__()`** — возвращает следующий элемент или выбрасывает `StopIteration`, если элементов больше нет.

```python
class CountDown:
    def __init__(self, start):
        self.current = start
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

for num in CountDown(5):
    print(num)
```

Выведет: `5, 4, 3, 2, 1`.

### 2.2 Итерируемые объекты (iterables)

**Итерируемый объект** — объект, у которого есть `__iter__()`, возвращающий итератор. Списки, кортежи, строки, словари — итерируемые.

```python
my_list = [1, 2, 3]
iterator = iter(my_list)
print(next(iterator))
print(next(iterator))
```

`iter()` вызывает `__iter__()`, `next()` вызывает `__next__()`.

### 2.3 Разница между iterable и iterator

- **Iterable** — объект, который можно итерировать (имеет `__iter__()`).
- **Iterator** — объект, который возвращает элементы (имеет `__next__()`).

Итератор обычно сам является итерируемым (возвращает себя в `__iter__()`), но не наоборот: список итерируемый, но не итератор (у него нет `__next__()`).

---

## 3. Генераторы (generators)

### 3.1 Generator functions

**Генераторная функция** — функция, которая использует `yield` вместо `return`. При вызове возвращает **generator object** (итератор), а не значение.

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

gen = countdown(5)
print(next(gen))
print(next(gen))
```

При первом вызове `next()` выполнение начинается с начала функции и идёт до первого `yield`, возвращает значение и **приостанавливается**. При следующем `next()` выполнение продолжается с места после `yield`.

### 3.2 yield vs return

- **`return`** — завершает функцию и возвращает значение.
- **`yield`** — приостанавливает функцию, возвращает значение, но функция остаётся «живой» и может продолжить выполнение при следующем вызове `__next__()`.

```python
def simple_generator():
    yield 1
    yield 2
    yield 3
    return "done"

gen = simple_generator()
for value in gen:
    print(value)
```

Выведет: `1, 2, 3`. Значение после `return` недоступно через итерацию (но можно получить через исключение `StopIteration`).

### 3.3 Generator expressions

**Выражение-генератор** — компактный синтаксис для создания генераторов, похожий на list comprehension:

```python
squares = (x**2 for x in range(10))
print(list(squares))
```

Разница с list comprehension: круглые скобки вместо квадратных, и результат — генератор, а не список (ленивое вычисление).

### 3.4 Отправка значений в генератор (send)

Генератор может **получать** значения через `send()`:

```python
def accumulator():
    total = 0
    while True:
        value = yield total
        if value is None:
            break
        total += value

acc = accumulator()
next(acc)
print(acc.send(10))
print(acc.send(5))
```

`send()` отправляет значение в генератор (оно становится результатом `yield`) и получает следующее значение. Первый вызов должен быть `next()` или `send(None)`, чтобы «запустить» генератор до первого `yield`.

### 3.5 Закрытие генератора (close)

Метод `close()` вызывает `GeneratorExit` внутри генератора, позволяя ему выполнить cleanup:

```python
def resource_generator():
    try:
        yield "resource"
    except GeneratorExit:
        print("Cleaning up")
        raise

gen = resource_generator()
next(gen)
gen.close()
```

---

## 4. yield from (делегирование)

**`yield from`** (Python 3.3+) позволяет генератору **делегировать** выполнение другому итерируемому объекту:

```python
def chain(*iterables):
    for it in iterables:
        yield from it

list(chain([1, 2], [3, 4], [5, 6]))
```

Эквивалентно:

```python
def chain(*iterables):
    for it in iterables:
        for item in it:
            yield item
```

`yield from` также передаёт `send()` и `throw()` во вложенный генератор, что важно для продвинутых сценариев.

---

## 5. Типичные паттерны генераторов

### 5.1 Чтение файлов построчно

```python
def read_large_file(filename):
    with open(filename) as f:
        for line in f:
            yield line.strip()
```

Не загружает весь файл в память.

### 5.2 Бесконечные последовательности

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

fib = fibonacci()
for _ in range(10):
    print(next(fib))
```

### 5.3 Фильтрация и трансформация

```python
def filter_even(numbers):
    for n in numbers:
        if n % 2 == 0:
            yield n * 2
```

### 5.4 Группировка (chunking)

```python
def chunks(iterable, size):
    iterator = iter(iterable)
    while True:
        chunk = []
        try:
            for _ in range(size):
                chunk.append(next(iterator))
            yield chunk
        except StopIteration:
            if chunk:
                yield chunk
            break
```

---

## 6. Асинхронные генераторы (async generators)

### 6.1 async def и yield

**Асинхронный генератор** — функция с `async def` и `yield`:

```python
async def async_countdown(n):
    while n > 0:
        await asyncio.sleep(0.1)
        yield n
        n -= 1
```

При вызове возвращает **async generator object**. Для итерации используется `async for`:

```python
async def main():
    async for value in async_countdown(5):
        print(value)
```

### 6.2 async for

**`async for`** — асинхронный аналог `for`. Работает только внутри `async def`:

```python
async def process_items():
    async for item in async_generator():
        await process(item)
```

Под капотом `async for` вызывает `__aiter__()` и `__anext__()` (асинхронные версии `__iter__()` и `__next__()`).

### 6.3 Протокол async iterator

Асинхронный итератор должен реализовывать:
- **`__aiter__()`** — возвращает сам итератор (async версия `__iter__`).
- **`__anext__()`** — возвращает awaitable, который при await даёт следующий элемент или выбрасывает `StopAsyncIteration`.

```python
class AsyncCountDown:
    def __init__(self, start):
        self.current = start
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.current <= 0:
            raise StopAsyncIteration
        await asyncio.sleep(0.1)
        self.current -= 1
        return self.current + 1
```

### 6.4 yield from в async генераторах

В async генераторах `yield from` заменён на `async for` или можно использовать напрямую делегирование:

```python
async def chain_async(*async_iterables):
    for async_iter in async_iterables:
        async for item in async_iter:
            yield item
```

---

## 7. Практические примеры async генераторов

### 7.1 Асинхронное чтение файла

```python
async def async_read_lines(filename):
    loop = asyncio.get_event_loop()
    with open(filename) as f:
        while True:
            line = await loop.run_in_executor(None, f.readline)
            if not line:
                break
            yield line.strip()
```

### 7.2 Потоковая обработка API

```python
async def fetch_pages(url):
    page = 1
    while True:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{url}?page={page}") as resp:
                data = await resp.json()
                if not data.get("items"):
                    break
                for item in data["items"]:
                    yield item
                page += 1
```

### 7.3 Обработка событий в реальном времени

```python
async def event_stream():
    while True:
        event = await wait_for_event()
        yield event
        if event.type == "close":
            break
```

---

## 8. Взаимодействие синхронного и асинхронного кода

### 8.1 Запуск async генератора из sync кода

Для запуска async генератора из синхронного кода нужен event loop:

```python
async def async_gen():
    for i in range(5):
        yield i

def sync_function():
    loop = asyncio.get_event_loop()
    gen = async_gen()
    try:
        while True:
            value = loop.run_until_complete(gen.__anext__())
            print(value)
    except StopAsyncIteration:
        pass
```

Или проще через `asyncio.run()`:

```python
async def main():
    async for value in async_gen():
        print(value)

asyncio.run(main())
```

### 8.2 Обёртка sync итератора в async

Если нужно использовать синхронный итератор в async коде:

```python
async def async_wrap(iterable):
    for item in iterable:
        yield item
```

Или через executor для блокирующих операций:

```python
async def async_read_file(filename):
    loop = asyncio.get_event_loop()
    with open(filename) as f:
        while True:
            line = await loop.run_in_executor(None, f.readline)
            if not line:
                break
            yield line
```

---

## 9. Продвинутые техники

### 9.1 Корутины vs генераторы

**Корутина** — функция с `async def` (без `yield`). Возвращает coroutine object, который нужно await.

**Async генератор** — функция с `async def` и `yield`. Возвращает async generator object, используется с `async for`.

Не путать: `async def` без `yield` — корутина; `async def` с `yield` — async генератор.

### 9.2 Генераторы и исключения

Исключения можно отправлять в генератор через `throw()`:

```python
def resilient_generator():
    try:
        while True:
            try:
                value = yield
                print(f"Got {value}")
            except ValueError as e:
                print(f"ValueError: {e}")
    except GeneratorExit:
        print("Generator closing")
        raise

gen = resilient_generator()
next(gen)
gen.throw(ValueError, "test error")
```

### 9.3 Состояние генератора

Генератор сохраняет локальные переменные между вызовами:

```python
def stateful_generator():
    count = 0
    while True:
        count += 1
        value = yield count
        if value:
            count = value

gen = stateful_generator()
next(gen)
print(gen.send(10))
print(next(gen))
```

---

## 10. Производительность и память

### 10.1 Ленивое вычисление

Генераторы вычисляют значения **по требованию** (lazy evaluation), а не заранее:

```python
def expensive_computation():
    for i in range(1000000):
        result = complex_calculation(i)
        yield result

for value in expensive_computation():
    if meets_condition(value):
        break
```

Если условие выполнится на 10-м элементе, остальные 999990 не будут вычислены.

### 10.2 Память

Генераторы потребляют **константную память** (O(1)), независимо от размера данных:

```python
def read_huge_file(filename):
    with open(filename) as f:
        for line in f:
            yield process(line)
```

Список потребовал бы O(n) памяти.

### 10.3 Когда не использовать генераторы

- Нужен **случайный доступ** к элементам (индексация).
- Нужно **многократно итерировать** одни и те же данные (генератор одноразовый).
- Нужна **длина** последовательности заранее (генератор может быть бесконечным).

---

## 11. Краткая сводка для экзамена

| Термин | Кратко |
|--------|--------|
| Iterable | Объект с `__iter__()`, можно итерировать (списки, строки, генераторы) |
| Iterator | Объект с `__next__()`, возвращает элементы по одному |
| `iter(obj)` | Вызывает `obj.__iter__()`, возвращает итератор |
| `next(iterator)` | Вызывает `iterator.__next__()`, возвращает следующий элемент или `StopIteration` |
| Generator function | Функция с `yield`, возвращает generator object при вызове |
| `yield` | Приостанавливает функцию, возвращает значение, сохраняет состояние |
| Generator expression | `(x**2 for x in range(10))` — компактный синтаксис генератора |
| `yield from` | Делегирует выполнение другому итерируемому объекту |
| `send(value)` | Отправляет значение в генератор, становится результатом `yield` |
| `close()` | Закрывает генератор, вызывает `GeneratorExit` |
| `throw(exc)` | Отправляет исключение в генератор |
| Async generator | `async def` с `yield`, возвращает async generator object |
| `async for` | Асинхронная итерация, работает только в `async def` |
| `__aiter__()` | Асинхронный `__iter__()`, возвращает async iterator |
| `__anext__()` | Асинхронный `__next__()`, возвращает awaitable |
| `StopAsyncIteration` | Исключение для завершения async итерации |
| Lazy evaluation | Вычисление по требованию, не заранее |
| Одноразовость | Генератор можно итерировать только один раз |

---

## 12. Полезные ссылки

- [PEP 255 — Simple Generators](https://peps.python.org/pep-0255/)
- [PEP 342 — Coroutines via Enhanced Generators](https://peps.python.org/pep-0342/)
- [PEP 380 — Syntax for Delegating to a Subgenerator](https://peps.python.org/pep-0380/)
- [PEP 492 — Coroutines with async and await syntax](https://peps.python.org/pep-0492/)
- [PEP 525 — Asynchronous Generators](https://peps.python.org/pep-0525/)
- [docs.python.org — Iterator Types](https://docs.python.org/3/library/stdtypes.html#iterator-types)
- [docs.python.org — Generator Types](https://docs.python.org/3/c-api/gen.html)
