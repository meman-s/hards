# API Documentation: OpenAPI/Swagger

## 1. Зачем нужно

**Проблема без документации:**
- Разработчики не знают, как использовать API
- Нужно изучать исходный код для понимания
- Высокий порог входа для новых разработчиков
- Ошибки из-за непонимания контракта API
- Долгая интеграция сторонних сервисов

**Документирование API необходимо для:**

- Описания всех endpoints и их параметров
- Автоматической генерации интерактивной документации
- Тестирования API через веб-интерфейс
- Генерации клиентских SDK
- Облегчения интеграции для разработчиков

**Преимущества хорошей документации:**
- Снижает время на интеграцию
- Уменьшает количество вопросов от разработчиков
- Служит контрактом между клиентом и сервером
- Автоматически синхронизируется с кодом
- Позволяет тестировать API без написания кода

---

## 2. OpenAPI и Swagger

### 2.1 Что такое OpenAPI

**OpenAPI** (ранее Swagger) — открытая спецификация для описания RESTful API в формате YAML или JSON.

**История:**
- Изначально называлась Swagger (разработана компанией SmartBear)
- В 2015 году передана в OpenAPI Initiative под управлением Linux Foundation
- С 2016 года называется OpenAPI Specification (OAS)
- Текущая версия — OpenAPI 3.x

**Что описывает OpenAPI:**
- Endpoints (пути, методы HTTP)
- Параметры запросов (query, path, header, body)
- Структуру ответов (модели данных, статус коды)
- Аутентификацию и авторизацию
- Примеры запросов и ответов
- Метаданные API (версия, контакты, лицензия)

**Swagger UI** — интерактивный веб-интерфейс для просмотра и тестирования API на основе OpenAPI схемы.

**ReDoc** — альтернативный интерфейс документации, более читаемый и структурированный.

### 2.2 FastAPI и OpenAPI

**Автоматическая генерация:**
- FastAPI автоматически генерирует OpenAPI схему на основе кода
- Использует типы Python и Pydantic модели
- Не нужно писать схему вручную
- Схема всегда актуальна (синхронизирована с кодом)

**Как это работает:**
- FastAPI анализирует декораторы, типы параметров, модели Pydantic
- Генерирует JSON схему в формате OpenAPI 3.0
- Предоставляет интерактивную документацию через Swagger UI и ReDoc
- Схему можно экспортировать для генерации клиентов

**Преимущества:**
- Single Source of Truth (код = документация)
- Невозможно забыть обновить документацию
- Типобезопасность через Pydantic
- Валидация и документация из одного источника

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="My API",
    description="API для управления пользователями",
    version="1.0.0"
)

class User(BaseModel):
    id: int
    name: str
    email: str

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    return User(id=user_id, name="John", email="john@example.com")
```

Документация доступна по адресам:
- `/docs` — Swagger UI
- `/redoc` — ReDoc
- `/openapi.json` — JSON схема

---

## 3. Базовая конфигурация

**Метаданные API:**
- Информация о самом API (название, версия, описание)
- Контактная информация для поддержки
- Лицензия и условия использования
- Отображается в начале документации

**Организация endpoints:**
- Группировка по функциональности (теги)
- Описание каждого endpoint
- Структурированная навигация

### 3.1 Метаданные API

**Метаданные включают:**
- `title` — название API
- `description` — подробное описание (поддерживает Markdown)
- `version` — версия API
- `terms_of_service` — ссылка на условия использования
- `contact` — контактная информация разработчиков
- `license_info` — информация о лицензии

**Зачем нужны:**
- Помогают разработчикам понять назначение API
- Указывают, куда обращаться за поддержкой
- Показывают юридические аспекты использования

```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="""
    ## Описание API
    
    Это API для управления пользователями и постами.
    
    * Создавайте пользователей
    * Управляйте постами
    * Получайте статистику
    """,
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "API Support",
        "url": "http://example.com/contact/",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)
```

### 3.2 Теги для группировки

**Теги (Tags):**
- Группируют endpoints по функциональности
- Создают разделы в документации
- Упрощают навигацию в большом API
- Можно добавить описание для каждого тега

**Примеры тегов:**
- `users` — операции с пользователями
- `posts` — операции с постами
- `auth` — аутентификация и авторизация
- `admin` — административные функции

**Преимущества:**
- Логическая организация endpoints
- Легче найти нужный endpoint
- Можно скрыть/показать группы
- Улучшает читаемость документации

```python
from fastapi import FastAPI, APIRouter

app = FastAPI()

users_router = APIRouter(tags=["users"])
posts_router = APIRouter(tags=["posts"])

@users_router.get("/users/")
def get_users():
    return []

@posts_router.get("/posts/")
def get_posts():
    return []

app.include_router(users_router)
app.include_router(posts_router)
```

### 3.3 Описание endpoints

**Описание endpoint включает:**
- `summary` — краткое описание (отображается в списке)
- `description` — подробное описание функциональности
- `response_description` — описание ответа
- `tags` — к какой группе относится endpoint

**Зачем нужно:**
- Понимание назначения endpoint без изучения кода
- Описание бизнес-логики и ограничений
- Примеры использования
- Информация о возможных ошибках

```python
from fastapi import FastAPI, Query, Path

app = FastAPI()

@app.get(
    "/users/{user_id}",
    summary="Получить пользователя",
    description="Возвращает информацию о пользователе по его ID",
    response_description="Информация о пользователе",
    tags=["users"]
)
def get_user(
    user_id: int = Path(..., description="ID пользователя", example=1)
):
    return {"id": user_id, "name": "John"}
```

---

## 4. Документирование моделей

**Модели данных:**
- Описывают структуру запросов и ответов
- Автоматически валидируются Pydantic
- Генерируют схему в OpenAPI
- Служат документацией структуры данных

**Поля модели:**
- Тип данных
- Обязательность (required/optional)
- Ограничения (min/max, regex, format)
- Описание и примеры значений

### 4.1 Pydantic модели с описаниями

**Field() для документирования:**
- `description` — описание поля
- `example` — пример значения
- `ge/le` — ограничения на числовые значения
- `min_length/max_length` — ограничения на строки

**Config.schema_extra:**
- Дополнительные примеры для всей модели
- Можно указать несколько примеров
- Используется в Swagger UI для демонстрации

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int = Field(..., description="Уникальный идентификатор пользователя", example=1)
    name: str = Field(..., description="Имя пользователя", example="John Doe")
    email: str = Field(..., description="Email адрес", example="john@example.com")
    age: int = Field(None, description="Возраст пользователя", ge=0, le=150, example=30)
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30
            }
        }
```

### 4.2 Вложенные модели

**Вложенные модели:**
- Модели могут содержать другие модели
- Создают иерархическую структуру данных
- Автоматически документируются в OpenAPI
- Поддерживают списки и опциональные вложения

**Использование:**
- Сложные структуры данных (адреса, профили)
- Списки связанных объектов
- Опциональные вложенные объекты
- Рефакторинг общих частей моделей

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    street: str = Field(..., description="Улица")
    city: str = Field(..., description="Город")
    zip_code: str = Field(..., description="Почтовый индекс")

class User(BaseModel):
    id: int
    name: str
    addresses: List[Address] = Field(..., description="Список адресов пользователя")
```

---

## 5. Документирование параметров

**Типы параметров:**
- **Query** — параметры в URL (`?param=value`)
- **Path** — параметры в пути URL (`/users/{id}`)
- **Header** — HTTP заголовки
- **Body** — тело запроса (для POST/PUT)

**Документирование параметров:**
- Описание назначения параметра
- Тип и ограничения
- Обязательность
- Примеры значений
- Значения по умолчанию

### 5.1 Query параметры

**Query параметры:**
- Используются для фильтрации, пагинации, поиска
- Видны в URL
- Можно сделать опциональными
- Поддерживают валидацию (min/max, regex)

**Типичные случаи:**
- Пагинация (`skip`, `limit`)
- Фильтрация (`status`, `category`)
- Поиск (`search`, `q`)
- Сортировка (`sort_by`, `order`)

```python
from fastapi import FastAPI, Query
from typing import Optional

app = FastAPI()

@app.get("/users/")
def get_users(
    skip: int = Query(0, description="Количество пропускаемых записей", ge=0),
    limit: int = Query(10, description="Максимальное количество записей", ge=1, le=100),
    search: Optional[str] = Query(None, description="Поисковый запрос", min_length=1)
):
    return {"skip": skip, "limit": limit, "search": search}
```

### 5.2 Path параметры

**Path параметры:**
- Часть URL пути (`/users/{user_id}`)
- Всегда обязательны
- Идентифицируют ресурс
- Типизируются (int, str, UUID)

**Использование:**
- ID ресурса (`/users/123`)
- Слаг (`/posts/my-post`)
- UUID (`/orders/{order_id}`)
- Вложенные ресурсы (`/users/{user_id}/posts/{post_id}`)

```python
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(
    user_id: int = Path(..., description="ID пользователя", example=1, gt=0)
):
    return {"id": user_id}
```

### 5.3 Header параметры

**Header параметры:**
- Передаются в HTTP заголовках
- Используются для метаданных запроса
- Не видны в URL
- Часто используются для аутентификации

**Типичные случаи:**
- Токены аутентификации (`Authorization`, `X-Token`)
- Версия API (`API-Version`)
- Язык (`Accept-Language`)
- Кастомные заголовки (`X-Request-ID`)

```python
from fastapi import FastAPI, Header
from typing import Optional

app = FastAPI()

@app.get("/items/")
def get_items(
    x_token: Optional[str] = Header(None, description="Токен аутентификации")
):
    return {"token": x_token}
```

---

## 6. Документирование ответов

**Документирование ответов:**
- Описание успешных ответов (200, 201)
- Описание ошибок (400, 404, 500)
- Модели для каждого статус кода
- Примеры ответов

**Зачем нужно:**
- Разработчики знают, что ожидать
- Понимают структуру ошибок
- Могут обработать все возможные случаи
- Упрощает отладку

### 6.1 Множественные статус коды

**Разные статус коды:**
- `200 OK` — успешный запрос
- `201 Created` — ресурс создан
- `400 Bad Request` — ошибка валидации
- `404 Not Found` — ресурс не найден
- `500 Internal Server Error` — ошибка сервера

**Документирование:**
- Каждый статус код имеет свою модель
- Описание, когда возвращается этот код
- Примеры ответов для каждого случая
- Помогает клиентам правильно обрабатывать ответы

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str

class ErrorMessage(BaseModel):
    detail: str

@app.get(
    "/users/{user_id}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    responses={
        404: {"model": ErrorMessage, "description": "Пользователь не найден"},
        500: {"model": ErrorMessage, "description": "Внутренняя ошибка сервера"}
    }
)
def get_user(user_id: int):
    if user_id == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return User(id=user_id, name="John")
```

### 6.2 Различные модели ответов

**Union типы для ответов:**
- Один endpoint может возвращать разные модели
- В зависимости от результата операции
- Union[SuccessResponse, ErrorResponse]
- Документируется в OpenAPI как возможные варианты

**Использование:**
- Успешный ответ и ошибка
- Разные форматы ответа
- Условные ответы в зависимости от параметров

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Union

class SuccessResponse(BaseModel):
    status: str = "success"
    data: dict

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str

@app.get(
    "/api/data",
    response_model=Union[SuccessResponse, ErrorResponse]
)
def get_data():
    return SuccessResponse(data={"key": "value"})
```

---

## 7. Кастомизация Swagger UI

**Кастомизация:**
- Изменение внешнего вида документации
- Добавление логотипа и брендинга
- Настройка цветов и стилей
- Расширение OpenAPI схемы

**Зачем нужно:**
- Соответствие корпоративному стилю
- Улучшение пользовательского опыта
- Добавление специфичной информации
- Интеграция с существующими системами

### 7.1 Изменение темы

**Кастомизация Swagger UI:**
- Переопределение HTML страницы `/docs`
- Использование кастомных CSS/JS
- Изменение цветовой схемы
- Добавление логотипа компании

```python
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI()

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )
```

### 7.2 Кастомная OpenAPI схема

**Кастомизация схемы:**
- Переопределение функции `app.openapi`
- Добавление кастомных полей в схему
- Расширение метаданных
- Добавление специфичных для проекта данных

**Расширения OpenAPI:**
- `x-logo` — логотип в документации
- `x-code-samples` — примеры кода
- Кастомные поля с префиксом `x-`
- Интеграция с внешними инструментами

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="Custom API documentation",
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

---

## 8. Примеры запросов и ответов

**Примеры:**
- Показывают реальные данные для запросов/ответов
- Помогают разработчикам понять формат
- Ускоряют интеграцию
- Снижают количество ошибок

**Где указывать примеры:**
- В полях моделей (Field example)
- В Config.schema_extra (примеры для модели)
- В Body() для запросов
- В responses для ответов

### 8.1 Примеры в моделях

**Примеры в Pydantic:**
- `Field(..., example="value")` — пример для поля
- `Config.schema_extra.examples` — несколько примеров
- Отображаются в Swagger UI
- Можно использовать для тестирования

```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    email: str = Field(..., example="john@example.com")
    age: int = Field(None, example=30)
    
    class Config:
        schema_extra = {
            "examples": [
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "age": 30
                },
                {
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "age": 25
                }
            ]
        }
```

### 8.2 Примеры в endpoints

**Примеры в Body:**
- Указываются прямо в параметре Body()
- Показывают структуру запроса
- Используются в Swagger UI для тестирования
- Можно указать несколько примеров

```python
from fastapi import FastAPI, Body

app = FastAPI()

@app.post("/users/")
def create_user(
    user: dict = Body(
        ...,
        example={
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        }
    )
):
    return user
```

---

## 9. Генерация клиентских SDK

**Генерация клиентов:**
- OpenAPI схема используется для генерации клиентских библиотек
- Поддерживается множество языков (Python, JavaScript, Java, Go и др.)
- Автоматически создаются типизированные клиенты
- Синхронизируются с API

**Преимущества:**
- Не нужно писать клиент вручную
- Типобезопасность на стороне клиента
- Автоматическое обновление при изменении API
- Снижает количество ошибок интеграции

**Инструменты:**
- `openapi-generator` — современный инструмент (рекомендуется)
- `swagger-codegen` — оригинальный инструмент от Swagger

### 9.1 Использование openapi-generator

**openapi-generator:**
- Поддерживает 50+ языков и фреймворков
- Активно развивается
- Большое сообщество
- Генерирует современный код

**Процесс:**
1. Экспорт OpenAPI схемы (`/openapi.json`)
2. Запуск генератора с указанием языка
3. Получение готового клиента
4. Использование в проекте

```bash
openapi-generator generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./client
```

### 9.2 Использование swagger-codegen

**swagger-codegen:**
- Оригинальный инструмент от Swagger
- Менее активно развивается
- Все ещё используется в некоторых проектах
- Аналогичный процесс генерации

```bash
swagger-codegen generate \
  -i http://localhost:8000/openapi.json \
  -l python \
  -o ./client
```

---

## 10. Best Practices

**Принципы хорошей документации:**
- Полнота — все endpoints документированы
- Ясность — понятные описания
- Примеры — реальные примеры использования
- Актуальность — синхронизация с кодом

### 10.1 Полное описание всех endpoints

**Что должно быть:**
- `summary` — краткое описание
- `description` — подробное описание функциональности
- `response_description` — что возвращает endpoint
- `tags` — к какой группе относится
- `status_code` — код успешного ответа

```python
@app.post(
    "/users/",
    summary="Создать пользователя",
    description="Создаёт нового пользователя в системе",
    response_description="Созданный пользователь",
    status_code=201,
    tags=["users"]
)
def create_user(user: UserCreate):
    return user
```

### 10.2 Использование тегов для организации

**Организация через теги:**
- Группировка по функциональным областям
- Логическая структура API
- Упрощает навигацию
- Можно добавить описание для тега

```python
users_router = APIRouter(tags=["Users"])
posts_router = APIRouter(tags=["Posts"])
admin_router = APIRouter(tags=["Admin"])
```

### 10.3 Валидация и документация вместе

**Единый источник:**
- Pydantic модели служат и для валидации, и для документации
- Ограничения (min/max, regex) автоматически попадают в схему
- Невозможно забыть обновить документацию
- Типобезопасность гарантирует корректность схемы

```python
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email адрес")
    age: int = Field(..., ge=0, le=150, description="Возраст")
```

### 10.4 Версионирование документации

**Версионирование:**
- Разные URL для разных версий документации
- `/api/v1/docs` и `/api/v2/docs`
- Разные OpenAPI схемы для каждой версии
- Позволяет поддерживать несколько версий API одновременно

```python
app = FastAPI(
    title="My API",
    version="2.0.0",
    openapi_url="/api/v2/openapi.json",
    docs_url="/api/v2/docs",
    redoc_url="/api/v2/redoc"
)
```

---

## 11. Расширенная документация

**Расширенные возможности:**
- Документирование схем аутентификации
- Описание всех возможных ошибок
- Примеры сложных сценариев
- Интеграция с внешними сервисами

### 11.1 Документирование аутентификации

**Security Schemes:**
- Описание способов аутентификации в OpenAPI
- Bearer Token (JWT)
- OAuth2
- API Keys
- Basic Auth

**Зачем нужно:**
- Swagger UI показывает кнопку "Authorize"
- Можно протестировать защищённые endpoints
- Разработчики понимают, как аутентифицироваться
- Документируется процесс получения токена

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        routes=app.routes,
    )
    
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/users/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    return {"user": "current"}
```

### 11.2 Документирование ошибок

**Документирование ошибок:**
- Все возможные статус коды ошибок
- Структура ответа при ошибке
- Примеры ошибок
- Описание, когда возникает ошибка

**Важность:**
- Разработчики знают, какие ошибки ожидать
- Могут правильно обработать ошибки
- Понимают структуру ответа об ошибке
- Упрощает отладку интеграции

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class ValidationError(BaseModel):
    field: str
    message: str

class ErrorResponse(BaseModel):
    error: str
    details: list[ValidationError]

@app.post(
    "/users/",
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Ошибка валидации",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Validation failed",
                        "details": [
                            {"field": "email", "message": "Invalid email format"}
                        ]
                    }
                }
            }
        }
    }
)
def create_user(user: dict):
    return user
```
