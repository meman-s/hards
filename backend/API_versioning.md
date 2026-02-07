# API Versioning

## 1. Зачем нужно

Версионирование API позволяет:

- Вносить изменения без поломки существующих клиентов
- Поддерживать несколько версий одновременно
- Плавно мигрировать клиентов на новые версии
- Документировать изменения между версиями

---

## 2. Стратегии версионирования

### 2.1 URL Versioning

Версия указывается в URL пути.

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

Версия указывается в HTTP заголовке.

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

Версия указывается в query параметре.

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

Версия указывается в Accept заголовке.

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

### 5.1 Обратная совместимость

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

- **MAJOR** — несовместимые изменения
- **MINOR** — обратно совместимые новые функции
- **PATCH** — обратно совместимые исправления

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

## 8. Пример полной реализации

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
