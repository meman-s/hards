# Dataclasses, attrs и Pydantic

## 1. Зачем нужны «классы данных»

Обычный класс в Python требует писать `__init__`, `__repr__`, `__eq__` и т.д. для простых контейнеров данных. Это шаблонный код, в котором легко ошибиться.

**Классы данных** — способ описать структуру (поля и типы) и автоматически получить:
- конструктор по полям;
- читаемое представление (`__repr__`);
- сравнение по значению (`__eq__`);
- при необходимости: валидацию, сериализацию, неизменяемость.

Три основных подхода в Python: **dataclasses** (стандартная библиотека), **attrs**, **Pydantic**. Выбор зависит от задач: только типы и меньше кода — dataclasses/attrs; валидация и работа с JSON/API — Pydantic.

---

## 2. Dataclasses (стандартная библиотека)

Модуль **`dataclasses`** появился в Python 3.7 (PEP 557). Декоратор **`@dataclass`** генерирует `__init__`, `__repr__`, `__eq__` и опционально другие методы по объявленным полям с аннотациями типов.

### 2.1 Базовый синтаксис

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    active: bool = True
```

Автоматически: `User(name="Alice", age=30)`, `repr(user)`, `user1 == user2` по полям. Поля с значением по умолчанию должны идти после полей без значения по умолчанию.

### 2.2 Параметры декоратора

- **`frozen=True`** — объект неизменяемый (как именованный кортеж); добавляется поведение, совместимое с хешированием, если все поля хешируемы.
- **`order=True`** — генерируются `__lt__`, `__le__`, `__gt__`, `__ge__` (сравнение по полям в порядке объявления).
- **`slots=True`** (Python 3.10+) — класс с `__slots__`, меньше памяти, нельзя добавлять атрибуты динамически.
- **`kw_only=True`** (Python 3.10+) — все поля только keyword-only в конструкторе.
- **`repr=True`**, **`eq=True`** — включить/выключить `__repr__` и `__eq__` (по умолчанию True).

### 2.3 field()

Функция **`field()`** настраивает отдельное поле:

- **`default=...`** / **`default_factory=...`** — значение по умолчанию (для изменяемых типов лучше `default_factory=list`, чтобы не шарить один список между экземплярами).
- **`repr=True/False`** — включать ли в `__repr__`.
- **`compare=True/False`** — участвует ли в `__eq__`.
- **`hash=True/False`** — участвует ли в `__hash__` (важно при `frozen=True`).

```python
from dataclasses import dataclass, field

@dataclass
class Config:
    name: str
    tags: list[str] = field(default_factory=list)
    internal_id: int = field(repr=False, compare=False)
```

### 2.4 Ограничения

- Нет встроенной валидации типов в runtime: при `User(name=123, age="thirty")` ошибки не будет при создании (проверка — только в моём или стороннем коде).
- Нет автоматической сериализации в JSON/из JSON; можно использовать `dataclasses.asdict()` и затем `json.dumps`, или писать свой код.

---

## 3. attrs

Библиотека **attrs** — предшественник идей dataclasses, даёт больше возможностей и работает на старых версиях Python. Установка: `pip install attrs`.

### 3.1 Базовый синтаксис

Декоратор **`@define`** (или устаревший `@attr.s`):

```python
from attrs import define

@define
class User:
    name: str
    age: int
    active: bool = True
```

По умолчанию генерируются `__init__`, `__repr__`, `__eq__`. Имена атрибутов можно не повторять: пишется только тип (и опционально значение по умолчанию).

### 3.2 Параметры декоратора

- **`frozen=True`** — неизменяемый экземпляр.
- **`order=True`** — сравнение по полям.
- **`slots=True`** — класс с `__slots__`.
- **`kw_only=True`** — все поля только по ключевому слову.
- **`repr=True/False`**, **`eq=True/False`** и др.

### 3.3 attr.ib() / field()

В attrs настройка полей через **`attr.ib()`** или в новых версиях **`field()`**:

- **`default=...`**, **`factory=...`** — значение по умолчанию (для списков/словарей — `factory=list`).
- **`repr=...`**, **`eq=...`**, **`order=...`**, **`hash=...`**.
- **`validator`** — функция валидации при присваивании (один или список).
- **`converter`** — преобразование значения при присваивании (например, строка в int).

```python
from attrs import define, field

@define
class Product:
    name: str
    price: float = field(converter=float)
    tags: list[str] = field(factory=list)
```

### 3.4 Валидация

attrs поддерживает **валидаторы** на уровне поля или класса:

```python
from attrs import define, field, validators

@define
class Item:
    name: str = field(validator=validators.min_len(1))
    count: int = field(validator=validators.ge(0))
```

Есть встроенные `validators.instance_of()`, `validators.in_()`, можно писать свои функции.

### 3.5 Отличие от dataclasses

- Более богатые опции (конвертеры, валидаторы из коробки).
- Единообразный API для полей и декоратора.
- Работает на Python 3.6+ и раньше; dataclasses — часть стандартной библиотеки с 3.7.

---

## 4. Pydantic

**Pydantic** — библиотека для валидации данных и настроек с опорой на аннотации типов. Установка: `pip install pydantic`. Часто используется для API (FastAPI), конфигов, парсинга JSON/YAML.

### 4.1 Базовый синтаксис

Модель — класс, наследующий **`BaseModel`**. Поля задаются аннотациями; при создании экземпляра **типы проверяются и по необходимости приводятся** в runtime.

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    active: bool = True
```

- `User(name="Alice", age=30)` — ок.
- `User(name="Bob", age="25")` — Pydantic приведёт `"25"` к `int`.
- `User(name="x", age="not a number")` — **ValidationError** при создании.

### 4.2 Валидация и приведение типов

Pydantic в runtime:
- проверяет, что значение подходит под тип (или может быть приведено);
- приводит типы, где это возможно (str → int, int → float и т.д.);
- выдаёт понятные ошибки с путём к полю и причиной.

Поддерживаются сложные типы: `list[int]`, `dict[str, int]`, вложенные модели, `Optional`, `Union`, типы из `typing`.

### 4.3 Дополнительные возможности полей

Через **`Field()`** задают ограничения и метаданные:

- **`default=...`**, **`default_factory=...`**.
- **`min_length`**, **`max_length`** для строк и коллекций.
- **`ge`**, **`gt`**, **`le`**, **`lt`** для чисел.
- **`regex`** для строк.
- **`description`** — для схем и документации API.
- **`alias`** — имя при сериализации/десериализации (например, для snake_case ↔ camel_case).

```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(ge=0)
    tags: list[str] = Field(default_factory=list, max_length=10)
```

### 4.4 Валидаторы

- **`@field_validator("field_name")`** (Pydantic v2) — валидатор для одного поля.
- **`@model_validator(mode="after")`** — проверка всей модели (например, зависимость между полями).

В Pydantic v1 использовались `@validator` и `@root_validator`.

### 4.5 Сериализация

- **`model.model_dump()`** (v2) / **`model.dict()`** (v1) — модель в словарь (по умолчанию по именам полей).
- **`model.model_dump_json()`** (v2) / **`model.json()`** (v1) — в JSON-строку.
- **`Model.model_validate(data)`** (v2) / **`Model.parse_obj(data)`** (v1) — словарь или объект в модель с валидацией.
- **`Model.model_validate_json(s)`** (v2) — парсинг из JSON-строки.

Это делает Pydantic удобным для REST API, конфигов, чтения из файлов.

### 4.6 Настройки модели

Через **`model_config`** (v2) или **`Config`** внутри класса (v1):

- **`frozen=True`** — модель неизменяемая.
- **`extra="forbid"`** — запретить лишние поля при парсинге.
- **`populate_by_name=True`** — разрешить и alias, и имя поля.
- **`str_strip_whitespace=True`** — срезать пробелы у строк.

### 4.7 Версии Pydantic

- **Pydantic v2** — актуальная, быстрая, на Rust-ядре (optional). API: `model_dump`, `model_validate`, `field_validator`, `model_validator`.
- **Pydantic v1** — старый API: `dict()`, `parse_obj()`, `validator`, `root_validator`. Важно не путать при чтении документации и кода.

---

## 5. Сравнение

| Критерий | dataclasses | attrs | Pydantic |
|----------|-------------|-------|----------|
| Стандартная библиотека | Да (3.7+) | Нет | Нет |
| Генерация __init__, __repr__, __eq__ | Да | Да | Да (плюс валидация) |
| Валидация в runtime | Нет | Есть (validators) | Да, основа подхода |
| Приведение типов (str→int и т.д.) | Нет | Через converter | Да, из коробки |
| Сериализация в/из JSON | Вручную (asdict) | Вручную | Встроенная |
| frozen, order, slots | Да | Да | frozen, настройки конфига |
| Сложность | Минимальная | Средняя | Выше, много опций |
| Типичный сценарий | Внутренние DTO, структуры | Классы с валидацией без API | API, конфиги, парсинг данных |

---

## 6. Когда что использовать

- **dataclasses** — простые контейнеры данных внутри приложения, нужны только типы и меньше кода, без валидации и JSON. Не требует зависимостей.
- **attrs** — когда нужны валидаторы и конвертеры, но не нужна тяжёлая сериализация/парсинг как в Pydantic; или нужна поддержка старых версий Python.
- **Pydantic** — входные данные извне (API, формы, конфиги, JSON/YAML): валидация и приведение типов обязательны, удобна сериализация и интеграция с FastAPI/документацией.

---

## 7. Краткая сводка для экзамена

| Термин | Кратко |
|--------|--------|
| @dataclass | Декоратор из stdlib: генерирует __init__, __repr__, __eq__ по полям с аннотациями |
| field() (dataclasses) | Настройка поля: default_factory, repr, compare, hash |
| frozen | Неизменяемый экземпляр (dataclasses/attrs/Pydantic) |
| attrs @define | Аналог dataclass с валидаторами и конвертерами |
| attr.ib() / field() (attrs) | Настройка поля в attrs: factory, validator, converter |
| Pydantic BaseModel | Модель с валидацией и приведением типов в runtime |
| Field() (Pydantic) | Ограничения и метаданные: min_length, ge, alias и т.д. |
| model_dump / model_validate | Сериализация в dict и парсинг из dict/JSON в Pydantic v2 |
| ValidationError | Ошибка Pydantic при невалидных данных |

---

## 8. Полезные ссылки

- [PEP 557 — Data Classes](https://peps.python.org/pep-0557/)
- [docs.python.org — dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [attrs — документация](https://www.attrs.org/)
- [Pydantic — документация](https://docs.pydantic.dev/) (v2)
