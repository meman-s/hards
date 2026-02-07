# Безопасность: CORS, CSRF, XSS, SQL Injection, Rate Limiting

## 1. Зачем нужны

Безопасность веб-приложений требует защиты от различных атак и уязвимостей:

- **CORS** — контроль доступа к ресурсам с других доменов
- **CSRF** — защита от подделки межсайтовых запросов
- **XSS** — защита от выполнения вредоносного JavaScript
- **SQL Injection** — защита от внедрения SQL-кода
- **Rate Limiting** — ограничение частоты запросов

---

## 2. CORS (Cross-Origin Resource Sharing)

### 2.1 Что такое CORS

Механизм, позволяющий браузеру запрашивать ресурсы с другого домена, отличного от домена текущей страницы.

### 2.2 Настройка CORS в FastAPI

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 2.3 Разрешение конкретных доменов

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://example.com",
        "https://www.example.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2.4 Разрешение всех доменов (не рекомендуется для production)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2.5 Динамическая настройка CORS

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = ["https://example.com", "https://app.example.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)
```

---

## 3. CSRF (Cross-Site Request Forgery)

### 3.1 Что такое CSRF

Атака, при которой злоумышленник заставляет пользователя выполнить нежелательные действия на сайте, где он аутентифицирован.

### 3.2 Защита через CSRF токены

```python
from fastapi import FastAPI, Request, Form, Depends
from fastapi.security import CSRFProtect
import secrets

app = FastAPI()
csrf = CSRFProtect()

@app.on_event("startup")
async def startup():
    csrf.init_app(app)

@app.get("/form")
async def get_form(request: Request):
    csrf_token = csrf.get_csrf_token(request)
    return {"csrf_token": csrf_token}

@app.post("/submit")
async def submit_form(
    request: Request,
    data: str = Form(...),
    _csrf_token: str = Form(...)
):
    csrf.validate_csrf(request, _csrf_token)
    return {"message": "Form submitted"}
```

### 3.3 Защита через SameSite cookies

```python
from fastapi import FastAPI, Response

@app.post("/login")
def login(response: Response, username: str, password: str):
    if verify_credentials(username, password):
        response.set_cookie(
            key="session_id",
            value=create_session(username),
            httponly=True,
            secure=True,
            samesite="strict"
        )
        return {"message": "Logged in"}
```

### 3.4 Проверка Referer/Origin

```python
from fastapi import FastAPI, Request, HTTPException

ALLOWED_ORIGINS = ["https://example.com"]

@app.middleware("http")
async def check_referer(request: Request, call_next):
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        origin = request.headers.get("Origin")
        referer = request.headers.get("Referer")
        
        if origin and origin not in ALLOWED_ORIGINS:
            raise HTTPException(status_code=403, detail="Invalid origin")
        
        if referer and not any(ref in referer for ref in ALLOWED_ORIGINS):
            raise HTTPException(status_code=403, detail="Invalid referer")
    
    response = await call_next(request)
    return response
```

---

## 4. XSS (Cross-Site Scripting)

### 4.1 Что такое XSS

Внедрение вредоносного JavaScript-кода на страницу, который выполняется в браузере жертвы.

### 4.2 Защита через экранирование

```python
from fastapi import FastAPI
from markupsafe import escape

@app.get("/user/{username}")
def get_user(username: str):
    safe_username = escape(username)
    return {"username": safe_username}
```

### 4.3 Валидация входных данных

```python
from pydantic import BaseModel, validator
import re

class UserInput(BaseModel):
    username: str
    comment: str
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Invalid username')
        return v
    
    @validator('comment')
    def validate_comment(cls, v):
        if '<script' in v.lower():
            raise ValueError('Script tags not allowed')
        return escape(v)
```

### 4.4 Content Security Policy (CSP)

```python
from fastapi import FastAPI, Response

@app.middleware("http")
async def add_csp_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:;"
    )
    return response
```

### 4.5 Санитизация HTML

```python
from bleach import clean

@app.post("/comment")
def add_comment(comment: str):
    allowed_tags = ['p', 'br', 'strong', 'em']
    safe_comment = clean(comment, tags=allowed_tags, strip=True)
    return {"comment": safe_comment}
```

---

## 5. SQL Injection

### 5.1 Что такое SQL Injection

Внедрение вредоносного SQL-кода через входные данные для выполнения нежелательных операций с БД.

### 5.2 Защита через параметризованные запросы

```python
from sqlalchemy import text
from sqlalchemy.orm import Session

def get_user_by_email(db: Session, email: str):
    query = text("SELECT * FROM users WHERE email = :email")
    result = db.execute(query, {"email": email})
    return result.fetchone()

def get_user_by_id(db: Session, user_id: int):
    query = text("SELECT * FROM users WHERE id = :user_id")
    result = db.execute(query, {"user_id": user_id})
    return result.fetchone()
```

### 5.3 Использование ORM (SQLAlchemy)

```python
from sqlalchemy.orm import Session

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def search_users(db: Session, search_term: str):
    return db.query(User).filter(
        User.name.like(f"%{search_term}%")
    ).all()
```

### 5.4 Валидация входных данных

```python
from pydantic import BaseModel, validator
import re

class UserSearch(BaseModel):
    search_term: str
    
    @validator('search_term')
    def validate_search_term(cls, v):
        if not re.match(r'^[a-zA-Z0-9\s]+$', v):
            raise ValueError('Invalid search term')
        if len(v) > 100:
            raise ValueError('Search term too long')
        return v
```

### 5.5 Ограничение прав доступа к БД

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://readonly_user:password@localhost/dbname",
    connect_args={"options": "-c default_transaction_read_only=on"}
)
```

---

## 6. Rate Limiting

### 6.1 Что такое Rate Limiting

Ограничение количества запросов от одного клиента за определённый период времени.

### 6.2 Простая реализация

```python
from fastapi import FastAPI, Request, HTTPException
from collections import defaultdict
import time

request_counts = defaultdict(list)

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    request_counts[client_ip] = [
        req_time for req_time in request_counts[client_ip]
        if current_time - req_time < 60
    ]
    
    if len(request_counts[client_ip]) >= 100:
        raise HTTPException(
            status_code=429,
            detail="Too many requests",
            headers={"Retry-After": "60"}
        )
    
    request_counts[client_ip].append(current_time)
    response = await call_next(request)
    return response
```

### 6.3 Rate limiting с Redis

```python
import redis
from fastapi import FastAPI, Request, HTTPException
import time

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.middleware("http")
async def rate_limit_redis(request: Request, call_next):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"
    
    current = redis_client.incr(key)
    if current == 1:
        redis_client.expire(key, 60)
    
    if current > 100:
        raise HTTPException(
            status_code=429,
            detail="Too many requests"
        )
    
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(100 - current)
    return response
```

### 6.4 Rate limiting по пользователю

```python
from fastapi import FastAPI, Depends, HTTPException
from functools import wraps

def rate_limit_by_user(max_requests: int = 10, window: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401)
            
            key = f"user_rate_limit:{user_id}"
            current = redis_client.incr(key)
            if current == 1:
                redis_client.expire(key, window)
            
            if current > max_requests:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded: {max_requests} requests per {window} seconds"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@app.get("/api/data")
@rate_limit_by_user(max_requests=10, window=60)
async def get_data(user_id: int):
    return {"data": "some data"}
```

### 6.5 Использование slowapi

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/data")
@limiter.limit("10/minute")
async def get_data(request: Request):
    return {"data": "some data"}
```

---

## 7. Дополнительные меры безопасности

### 7.1 HTTPS принудительно

```python
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()
app.add_middleware(HTTPSRedirectMiddleware)
```

### 7.2 Безопасные заголовки

```python
from fastapi import FastAPI, Request

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### 7.3 Валидация размера запроса

```python
from fastapi import FastAPI, Request, HTTPException

MAX_REQUEST_SIZE = 10 * 1024 * 1024

@app.middleware("http")
async def check_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_REQUEST_SIZE:
        raise HTTPException(status_code=413, detail="Request too large")
    
    response = await call_next(request)
    return response
```

### 7.4 Логирование подозрительной активности

```python
import logging
from fastapi import FastAPI, Request

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_suspicious_activity(request: Request, call_next):
    user_agent = request.headers.get("user-agent", "")
    if "bot" in user_agent.lower() or "crawler" in user_agent.lower():
        logger.warning(f"Suspicious user agent: {user_agent} from {request.client.host}")
    
    response = await call_next(request)
    
    if response.status_code == 401 or response.status_code == 403:
        logger.warning(f"Unauthorized/Forbidden: {request.method} {request.url} from {request.client.host}")
    
    return response
```

---

## 8. Best Practices

### 8.1 Принцип наименьших привилегий

```python
from sqlalchemy import create_engine

readonly_engine = create_engine(
    "postgresql://readonly_user:password@localhost/dbname"
)

write_engine = create_engine(
    "postgresql://write_user:password@localhost/dbname"
)
```

### 8.2 Регулярное обновление зависимостей

```bash
pip list --outdated
pip install --upgrade package_name
```

### 8.3 Сканирование уязвимостей

```bash
pip install safety
safety check
```

### 8.4 Хранение секретов

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    database_url: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 8.5 Аудит безопасности

- Регулярное тестирование на проникновение
- Анализ логов на подозрительную активность
- Мониторинг необычных паттернов запросов
- Обновление политик безопасности
