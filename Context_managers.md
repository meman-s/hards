# Context managers (менеджеры контекста)

## 1. Зачем нужны

Часто нужно выполнить **подготовку** (открыть файл, захватить блокировку, начать транзакцию), потом **действия**, и в конце **обязательно освободить ресурс** (закрыть файл, отпустить блокировку, закоммитить или откатить транзакцию). Если в середине произойдёт исключение, освобождение всё равно должно выполниться.

Ручной код легко ломается:

```python
f = open("data.txt")
process(f)
f.close()
```

Если `process(f)` выбросит исключение, `f.close()` не вызовется — утечка дескриптора. Правильно — оборачивать в try/finally, но это шаблонно.

**Context manager** — объект, который определяет «вход» и «выход» из блока кода. Синтаксис **`with`** гарантирует вызов «выхода» даже при исключении. Типичные примеры: `with open(...) as f`, работа с блокировками, транзакциями, таймерами.

---

## 2. Синтаксис with

```python
with EXPRESSION as VAR:
    BLOCK
```

1. Вычисляется `EXPRESSION` и у результата вызывается метод **`__enter__`**.
2. Возвращаемое значение `__enter__` присваивается в `VAR` (если есть `as VAR`).
3. Выполняется `BLOCK`.
4. В конце блока (нормальном или при исключении) вызывается **`__exit__`** того же объекта.

Если в `BLOCK` было исключение, оно передаётся в `__exit__(self, exc_type, exc_val, exc_tb)`. Если `__exit__` возвращает истинное значение, исключение «проглатывается»; иначе — пробрасывается дальше.

Несколько менеджеров в одном `with`:

```python
with open("a.txt") as a, open("b.txt") as b:
    ...
```

Эквивалентно вложенным `with`: сначала вход в первый, потом во второй; выход — в обратном порядке.

---

## 3. Протокол: __enter__ и __exit__

Context manager — объект, у которого есть методы **`__enter__`** и **`__exit__`** (протокол контекстного менеджера).

- **`__enter__(self)`** — вызывается при входе в `with`. Возвращаемое значение попадает в переменную после `as`. Часто возвращается сам объект (`return self`) или открытый ресурс.
- **`__exit__(self, exc_type, exc_val, exc_tb)`** — вызывается при выходе из блока. Аргументы: тип исключения, экземпляр, traceback; если выхода по исключению не было — все три `None`. Возврат `True` подавляет исключение, `False` или `None` — исключение пробрасывается.

Пример: менеджер, который замеряет время и при выходе печатает длительность.

```python
import time

class Timer:
    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type: type | None, exc_val: BaseException | None, exc_tb: object) -> bool:
        elapsed = time.perf_counter() - self.start
        print(f"Elapsed: {elapsed:.2f}s")
        return False

with Timer() as t:
    time.sleep(0.1)
```

Здесь `__exit__` возвращает `False`, чтобы не скрывать исключения. Ресурс (таймер) не требует особой очистки, только логирование.

Пример с ресурсом: блокировка (упрощённо).

```python
class SimpleLock:
    def __init__(self) -> None:
        self.locked = False

    def __enter__(self) -> "SimpleLock":
        if self.locked:
            raise RuntimeError("already locked")
        self.locked = True
        return self

    def __exit__(self, exc_type: type | None, exc_val: BaseException | None, exc_tb: object) -> bool:
        self.locked = False
        return False
```

При любом выходе из `with` (в том числе по исключению) `locked` снова станет `False`.

---

## 4. contextlib.contextmanager — через генератор

Писать класс с `__enter__`/`__exit__` каждый раз неудобно. Модуль **`contextlib`** даёт декоратор **`@contextmanager`**, превращающий генератор в context manager.

Правило:
- до **`yield`** — код «входа» (аналог `__enter__`);
- значение в **`yield`** — то, что попадёт в переменную после `as`;
- после **`yield`** — код «выхода» (аналог `__exit__`); он выполняется при выходе из блока (включая исключение).

Пример: таймер через contextmanager.

```python
import time
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"Elapsed: {time.perf_counter() - start:.2f}s")

with timer():
    time.sleep(0.1)
```

`try/finally` нужен, чтобы блок после `yield` выполнился и при исключении. Если в `yield` передать значение, оно попадёт в переменную: `yield start` → `with timer() as t: ...` получит `t = start`.

Пример с ресурсом: временная смена текущей директории.

```python
import os
from contextlib import contextmanager

@contextmanager
def chdir(path: str):
    old = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(old)
```

---

## 5. Готовые утилиты в contextlib

- **`contextlib.closing(thing)`** — вызывает `thing.close()` при выходе из `with`. Для объектов с методом `close()`, но без `__enter__`/`__exit__`.

- **`contextlib.suppress(*exceptions)`** — подавляет указанные исключения внутри блока (при выходе исключение не пробрасывается).

- **`contextlib.nullcontext(enter_result=None)`** — «пустой» менеджер: ничего не делает при входе/выходе, при `as x` в `x` попадёт `enter_result`. Удобно, когда контекст опционален (например, иногда передаётся реальный менеджер, иногда заглушка).

- **`contextlib.ExitStack`** — динамически собирает несколько контекстов (например, переменное число файлов) и при выходе закрывает их в обратном порядке.

Примеры:

```python
from contextlib import closing, suppress, nullcontext

with suppress(FileNotFoundError):
    os.remove("maybe_missing.txt")

with nullcontext():
    pass

with closing(some_legacy_connection()) as conn:
    conn.send(data)
```

---

## 6. Типичные сценарии

| Сценарий | Пример |
|----------|--------|
| Файлы | `with open("file.txt") as f: ...` — файл закроется при выходе |
| Блокировки | `with lock: ...` — захват при входе, освобождение при выходе |
| Транзакции БД | вход — begin, выход — commit или при исключении rollback |
| Временные ресурсы | создание/удаление временного каталога, смена директории |
| Замер времени | вход — запомнить время, выход — вывести разницу |
| Подавление исключений | `with suppress(SomeError): ...` |

---

## 7. Краткая сводка для экзамена

| Термин | Кратко |
|--------|--------|
| Context manager | Объект с `__enter__` и `__exit__`, используется в `with` |
| with EXPR as var | Вызов EXPR.__enter__(), выполнение блока, затем EXPR.__exit__() при любом выходе |
| __enter__ | Вызывается при входе; возвращаемое значение — в переменную после `as` |
| __exit__(exc_type, exc_val, exc_tb) | Вызывается при выходе; return True — подавить исключение |
| @contextmanager | Декоратор из contextlib: генератор (до yield — вход, после — выход) превращается в менеджер |
| closing(thing) | Вызывает thing.close() при выходе |
| suppress(*exceptions) | В блоке подавляет указанные исключения |
| nullcontext() | Пустой менеджер, ничего не делает |

---

## 8. Полезные ссылки

- [PEP 343 — The "with" Statement](https://peps.python.org/pep-0343/)
- [docs.python.org — with statement](https://docs.python.org/3/reference/compound_stmts.html#the-with-statement)
- [contextlib — документация](https://docs.python.org/3/library/contextlib.html)
