# API Documentation: OpenAPI/Swagger

## 1. Зачем нужно

Документирование API необходимо для:

- Описания всех endpoints и их параметров
- Автоматической генерации интерактивной документации
- Тестирования API через веб-интерфейс
- Генерации клиентских SDK
- Облегчения интеграции для разработчиков

---

## 2. OpenAPI и Swagger

### 2.1 Что такое OpenAPI

**OpenAPI** (ранее Swagger) — спецификация для описания RESTful API.

**Swagger UI** — интерактивный интерфейс для просмотра и тестирования API.

### 2.2 FastAPI и OpenAPI

FastAPI автоматически генерирует OpenAPI схему на основе кода.

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

### 3.1 Метаданные API

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

### 4.1 Pydantic модели с описаниями

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

### 5.1 Query параметры

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

### 6.1 Множественные статус коды

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

### 7.1 Изменение темы

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

### 8.1 Примеры в моделях

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

### 9.1 Использование openapi-generator

```bash
openapi-generator generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./client
```

### 9.2 Использование swagger-codegen

```bash
swagger-codegen generate \
  -i http://localhost:8000/openapi.json \
  -l python \
  -o ./client
```

---

## 10. Best Practices

### 10.1 Полное описание всех endpoints

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

```python
users_router = APIRouter(tags=["Users"])
posts_router = APIRouter(tags=["Posts"])
admin_router = APIRouter(tags=["Admin"])
```

### 10.3 Валидация и документация вместе

```python
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email адрес")
    age: int = Field(..., ge=0, le=150, description="Возраст")
```

### 10.4 Версионирование документации

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

### 11.1 Документирование аутентификации

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
