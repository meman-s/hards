# API Versioning

## 1. Зачем нужно

**Версионирование API** — практика управления изменениями в API путём создания отдельных версий.

**Проблема без версионирования:**
- Изменение API ломает существующие клиенты
- Невозможно добавить новые функции без риска
- Клиенты не могут обновиться мгновенно
- Сложно откатить изменения

**Версионирование API позволяет:**

- Вносить изменения без поломки существующих клиентов
- Поддерживать несколько версий одновременно
- Плавно мигрировать клиентов на новые версии
- Документировать изменения между версиями

**Когда нужна новая версия:**
- Удаление или переименование endpoints
- Изменение структуры ответов (удаление полей)
- Изменение обязательных параметров
- Изменение формата данных

**Когда НЕ нужна новая версия:**
- Добавление новых endpoints
- Добавление новых полей в ответы
- Добавление опциональных параметров
- Исправление багов (обратно совместимые)

---

## 2. Стратегии версионирования

### 2.1 URL Versioning

**URL Versioning** — версия указывается в URL пути (`/api/v1/users`, `/api/v2/users`).

**Преимущества:**
- Простота и понятность
- Легко кэшировать разные версии
- Видно версию в URL
- Простая маршрутизация

**Недостатки:**
- Загрязняет URL
- Нарушает принцип REST (ресурс не должен меняться при версионировании)
- Сложнее поддерживать при большом количестве версий

**Когда использовать:**
- Публичные API
- Когда нужна максимальная простота
- Когда версия — часть контракта API

```python
from fastapi import FastAPI, APIRouter

app = FastAPI()

v1_router = APIRouter(prefix="/api/v1", tags=["v1"])
v2_router = APIRouter(prefix="/api/v2", tags=["v2"])

@v1_router.get("/users/{user_id}")
def get_user_v1(user_id: int):
    return {"id": user_id, "name": "John", "version": "v1"}

@v2_router.get("/users/{user_id}")
def get_user_v2(user_id: int):
    return {
        "id": user_id,
        "name": "John",
        "email": "john@example.com",
        "version": "v2"
    }

app.include_router(v1_router)
app.include_router(v2_router)
```

### 2.2 Header Versioning

**Header Versioning** — версия указывается в HTTP заголовке (например, `API-Version: v2`).

**Преимущества:**
- Чистые URL (без версии в пути)
- Соответствует REST принципам
- Гибкость (можно менять версию без изменения URL)

**Недостатки:**
- Менее очевидно для разработчиков
- Сложнее тестировать (нужно указывать заголовок)
- Не все клиенты легко работают с заголовками

**Когда использовать:**
- RESTful API с чистыми URL
- Когда важна эстетика URL
- Внутренние API

```python
from fastapi import FastAPI, Header, HTTPException
from typing import Optional

app = FastAPI()

@app.get("/api/users/{user_id}")
def get_user(
    user_id: int,
    api_version: Optional[str] = Header(None, alias="API-Version")
):
    if api_version == "v1":
        return {"id": user_id, "name": "John", "version": "v1"}
    elif api_version == "v2":
        return {
            "id": user_id,
            "name": "John",
            "email": "john@example.com",
            "version": "v2"
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid API version")
```

### 2.3 Query Parameter Versioning

**Query Parameter Versioning** — версия указывается в query параметре (`/api/users?version=v2`).

**Преимущества:**
- Простота использования
- Легко тестировать в браузере
- Можно сделать опциональным (default версия)

**Недостатки:**
- Загрязняет URL параметрами
- Менее стандартизировано
- Сложнее кэшировать

**Когда использовать:**
- Простые API
- Когда версия опциональна
- Для быстрого прототипирования

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/api/users/{user_id}")
def get_user(
    user_id: int,
    version: str = Query("v1", regex="^v[12]$")
):
    if version == "v1":
        return {"id": user_id, "name": "John", "version": "v1"}
    elif version == "v2":
        return {
            "id": user_id,
            "name": "John",
            "email": "john@example.com",
            "version": "v2"
        }
```

### 2.4 Accept Header Versioning

**Accept Header Versioning** — версия указывается в Accept заголовке через media type (`Accept: application/vnd.api.v2+json`).

**Преимущества:**
- Соответствует HTTP стандартам (Content Negotiation)
- Можно указывать версию и формат одновременно
- Чистые URL

**Недостатки:**
- Сложнее для разработчиков
- Менее распространено
- Требует знания HTTP спецификации

**Когда использовать:**
- Enterprise API
- Когда важна стандартизация
- Когда нужна поддержка разных форматов (JSON, XML)

```python
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.get("/api/users/{user_id}")
def get_user(user_id: int, request: Request):
    accept = request.headers.get("Accept", "")
    
    if "application/vnd.api.v1+json" in accept:
        return {"id": user_id, "name": "John", "version": "v1"}
    elif "application/vnd.api.v2+json" in accept:
        return {
            "id": user_id,
            "name": "John",
            "email": "john@example.com",
            "version": "v2"
        }
    else:
        return {"id": user_id, "name": "John", "version": "v1"}
```

---

## 3. Структура проекта для версионирования

**Организация кода:**
- Каждая версия в отдельной папке
- Общий код выносится в shared модули
- Endpoints разделены по версиям
- Модели версионируются отдельно

**Преимущества:**
- Чёткое разделение версий
- Легко найти код конкретной версии
- Можно удалить старую версию целиком
- Упрощает тестирование

### 3.1 Организация по версиям

```
project/
  app/
    api/
      v1/
        __init__.py
        endpoints/
          users.py
          posts.py
      v2/
        __init__.py
        endpoints/
          users.py
          posts.py
    main.py
```

### 3.2 Реализация

```python
from fastapi import APIRouter
from app.api.v1.endpoints import users as users_v1
from app.api.v2.endpoints import users as users_v2

api_router = APIRouter()

api_router.include_router(
    users_v1.router,
    prefix="/api/v1",
    tags=["users-v1"]
)

api_router.include_router(
    users_v2.router,
    prefix="/api/v2",
    tags=["users-v2"]
)
```

### 3.3 Общие зависимости

```python
from fastapi import APIRouter, Depends
from app.core.dependencies import get_db

v1_router = APIRouter(prefix="/api/v1", dependencies=[Depends(get_db)])
v2_router = APIRouter(prefix="/api/v2", dependencies=[Depends(get_db)])
```

---

## 4. Управление версиями

**Управление версиями:**
- Автоматическое определение версии из запроса
- Fallback на версию по умолчанию
- Валидация поддерживаемых версий
- Централизованная логика выбора версии

### 4.1 Автоматическое определение версии

```python
from fastapi import FastAPI, Request
from typing import Optional

app = FastAPI()

def get_api_version(request: Request) -> str:
    version = request.headers.get("API-Version", "v1")
    if version not in ["v1", "v2"]:
        version = "v1"
    return version

@app.get("/api/users/{user_id}")
def get_user(user_id: int, request: Request):
    version = get_api_version(request)
    
    if version == "v1":
        return get_user_v1(user_id)
    else:
        return get_user_v2(user_id)
```

### 4.2 Версионирование через dependency

```python
from fastapi import FastAPI, Depends, Header, HTTPException
from typing import Optional

app = FastAPI()

def get_api_version(
    api_version: Optional[str] = Header(None, alias="API-Version")
) -> str:
    if api_version and api_version in ["v1", "v2"]:
        return api_version
    return "v1"

@app.get("/api/users/{user_id}")
def get_user(user_id: int, version: str = Depends(get_api_version)):
    if version == "v1":
        return {"id": user_id, "name": "John"}
    else:
        return {"id": user_id, "name": "John", "email": "john@example.com"}
```

---

## 5. Миграция между версиями

**Миграция клиентов:**
- Старые версии поддерживаются определённое время
- Новые версии объявляются deprecated заранее
- Предоставляется информация о сроках отключения
- Помощь в миграции (документация, примеры)

### 5.1 Обратная совместимость

**Обратная совместимость:**
- Старая версия продолжает работать
- Новая версия добавляет функциональность
- Клиенты могут мигрировать постепенно
- Используются разные модели для разных версий

```python
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel

app = FastAPI()

class UserV1(BaseModel):
    id: int
    name: str

class UserV2(BaseModel):
    id: int
    name: str
    email: str

v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")

@v1_router.get("/users/{user_id}", response_model=UserV1)
def get_user_v1(user_id: int):
    user = get_user_from_db(user_id)
    return UserV1(id=user.id, name=user.name)

@v2_router.get("/users/{user_id}", response_model=UserV2)
def get_user_v2(user_id: int):
    user = get_user_from_db(user_id)
    return UserV2(id=user.id, name=user.name, email=user.email)
```

### 5.2 Deprecation warnings

**Deprecation (устаревание):**
- Уведомление клиентов о скором удалении версии
- Заголовки `Deprecation: true` и `Sunset: <дата>`
- Указывается следующая версия через `Link` заголовок
- Даёт время клиентам на миграцию

```python
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse

@app.get("/api/v1/users/{user_id}")
def get_user_v1(user_id: int, response: Response):
    response.headers["Deprecation"] = "true"
    response.headers["Sunset"] = "Sat, 31 Dec 2024 23:59:59 GMT"
    response.headers["Link"] = '</api/v2/users/{user_id}>; rel="successor-version"'
    return {"id": user_id, "name": "John", "deprecated": True}
```

### 5.3 Автоматический редирект

```python
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

@app.get("/api/v1/users/{user_id}")
def get_user_v1(user_id: int, request: Request):
    redirect_to_v2 = request.headers.get("Upgrade-Insecure-Requests")
    if redirect_to_v2:
        return RedirectResponse(
            url=f"/api/v2/users/{user_id}",
            status_code=301
        )
    return {"id": user_id, "name": "John"}
```

---

## 6. Документирование версий

**Документирование:**
- Каждая версия должна быть задокументирована
- Указываются различия между версиями
- Changelog для отслеживания изменений
- Примеры использования для каждой версии

### 6.1 Раздельная документация

```python
from fastapi import FastAPI, APIRouter

app = FastAPI(
    title="My API",
    description="API with versioning",
    version="2.0.0"
)

v1_router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
    responses={404: {"description": "Not found"}}
)

v2_router = APIRouter(
    prefix="/api/v2",
    tags=["v2"],
    responses={404: {"description": "Not found"}}
)

app.include_router(v1_router)
app.include_router(v2_router)
```

### 6.2 Changelog endpoint

```python
@app.get("/api/changelog")
def get_changelog():
    return {
        "versions": [
            {
                "version": "v2",
                "release_date": "2024-01-01",
                "changes": [
                    "Added email field to user response",
                    "Deprecated v1 endpoints"
                ]
            },
            {
                "version": "v1",
                "release_date": "2023-01-01",
                "status": "deprecated"
            }
        ]
    }
```

---

## 7. Best Practices

### 7.1 Семантическое версионирование

**Semantic Versioning (SemVer):** формат `MAJOR.MINOR.PATCH`

- **MAJOR** — несовместимые изменения (новая версия API)
- **MINOR** — обратно совместимые новые функции (добавление endpoints)
- **PATCH** — обратно совместимые исправления (багфиксы)

**Примеры:**
- `1.0.0 → 2.0.0` — удалили endpoint (MAJOR)
- `2.0.0 → 2.1.0` — добавили новый endpoint (MINOR)
- `2.1.0 → 2.1.1` — исправили баг (PATCH)

```python
API_VERSION = "2.1.0"

@app.get("/api/version")
def get_version():
    return {
        "version": API_VERSION,
        "major": 2,
        "minor": 1,
        "patch": 0
    }
```

### 7.2 Минимальная поддержка версий

**Политика поддержки:**
- Определяется минимальная поддерживаемая версия
- Старые версии постепенно отключаются
- Клиентам даётся время на миграцию
- Чёткие сроки отключения (Sunset dates)

```python
SUPPORTED_VERSIONS = ["v1", "v2"]
MIN_SUPPORTED_VERSION = "v1"

@app.middleware("http")
async def check_version(request: Request, call_next):
    version = request.headers.get("API-Version", "v1")
    
    if version not in SUPPORTED_VERSIONS:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Unsupported API version",
                "supported_versions": SUPPORTED_VERSIONS
            }
        )
    
    response = await call_next(request)
    return response
```

### 7.3 Версионирование моделей

**Версионирование моделей:**
- Базовые модели для общих полей
- Версионные модели наследуются от базовых
- Каждая версия имеет свою модель ответа
- Упрощает поддержку и миграцию

```python
from pydantic import BaseModel

class UserBase(BaseModel):
    id: int
    name: str

class UserV1(UserBase):
    pass

class UserV2(UserBase):
    email: str
    phone: str = None
```

### 7.4 Тестирование версий

**Тестирование:**
- Каждая версия должна тестироваться отдельно
- Проверка обратной совместимости
- Тесты на корректность ответов для каждой версии
- Интеграционные тесты для миграции между версиями

```python
def test_user_v1(client):
    response = client.get("/api/v1/users/1")
    assert response.status_code == 200
    assert "email" not in response.json()

def test_user_v2(client):
    response = client.get("/api/v2/users/1")
    assert response.status_code == 200
    assert "email" in response.json()
```

---

## 8. Рекомендации по выбору стратегии

### 8.1 Сравнение стратегий

| Стратегия | Простота | RESTful | Кэширование | Использование |
|-----------|----------|---------|------------|---------------|
| URL | Высокая | Низкая | Отличное | Публичные API |
| Header | Средняя | Высокая | Хорошее | RESTful API |
| Query | Высокая | Средняя | Среднее | Простые API |
| Accept | Низкая | Высокая | Хорошее | Enterprise API |

### 8.2 Выбор стратегии

**URL Versioning:**
- Публичные API
- Когда нужна максимальная простота
- Когда версия — часть контракта

**Header Versioning:**
- RESTful API
- Когда важны чистые URL
- Внутренние API

**Query Parameter:**
- Простые API
- Быстрое прототипирование
- Когда версия опциональна

**Accept Header:**
- Enterprise API
- Когда важна стандартизация
- Поддержка разных форматов

---

## 9. Пример полной реализации

```python
from fastapi import FastAPI, APIRouter, Depends, Header, HTTPException
from typing import Optional
from pydantic import BaseModel

app = FastAPI(title="Versioned API")

class UserV1(BaseModel):
    id: int
    name: str

class UserV2(BaseModel):
    id: int
    name: str
    email: str

def get_api_version(
    api_version: Optional[str] = Header("v1", alias="API-Version")
) -> str:
    if api_version not in ["v1", "v2"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported version. Use v1 or v2"
        )
    return api_version

v1_router = APIRouter(prefix="/api/v1", tags=["v1"])
v2_router = APIRouter(prefix="/api/v2", tags=["v2"])

@v1_router.get("/users/{user_id}", response_model=UserV1)
def get_user_v1(user_id: int):
    return UserV1(id=user_id, name="John")

@v2_router.get("/users/{user_id}", response_model=UserV2)
def get_user_v2(user_id: int):
    return UserV2(id=user_id, name="John", email="john@example.com")

app.include_router(v1_router)
app.include_router(v2_router)
```
