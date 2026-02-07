# FastAPI: Dependency Injection, Middleware, Background Tasks

## 1. Зачем нужны

**Dependency Injection (DI)** — паттерн для управления зависимостями, упрощающий тестирование и переиспользование кода.

**Middleware** — промежуточное ПО для обработки запросов/ответов (логирование, аутентификация, CORS).

**Background Tasks** — выполнение задач после отправки ответа клиенту (отправка email, обработка файлов).

---

## 2. Dependency Injection

### 2.1 Базовое использование

```python
from fastapi import FastAPI, Depends

app = FastAPI()

def get_db():
    db = "database_connection"
    try:
        yield db
    finally:
        print("Closing database connection")

@app.get("/items/")
def read_items(db: str = Depends(get_db)):
    return {"db": db, "items": []}
```

### 2.2 Зависимости с параметрами

```python
from fastapi import FastAPI, Depends, Query

def pagination_params(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    return {"skip": skip, "limit": limit}

@app.get("/items/")
def read_items(pagination: dict = Depends(pagination_params)):
    return {"items": [], **pagination}
```

### 2.3 Вложенные зависимости

```python
from fastapi import FastAPI, Depends, Header

def get_user_token(authorization: str = Header(...)):
    return authorization.split(" ")[1] if " " in authorization else authorization

def get_current_user(token: str = Depends(get_user_token)):
    return {"id": 1, "name": "John", "token": token}

@app.get("/users/me")
def read_current_user(user: dict = Depends(get_current_user)):
    return user
```

### 2.4 Классы как зависимости

```python
from fastapi import FastAPI, Depends
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

class UserService:
    def get_user(self, user_id: int) -> User:
        return User(id=user_id, name="John")

def get_user_service() -> UserService:
    return UserService()

@app.get("/users/{user_id}")
def read_user(
    user_id: int,
    service: UserService = Depends(get_user_service)
):
    return service.get_user(user_id)
```

### 2.5 Кэширование зависимостей

```python
from fastapi import FastAPI, Depends
from functools import lru_cache

@lru_cache()
def get_settings():
    return {"api_key": "secret", "debug": True}

@app.get("/settings")
def read_settings(settings: dict = Depends(get_settings)):
    return settings
```

### 2.6 Зависимости с исключениями

```python
from fastapi import FastAPI, Depends, HTTPException, status

def verify_token(token: str = Header(...)):
    if token != "valid_token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return token

@app.get("/protected")
def protected_route(token: str = Depends(verify_token)):
    return {"message": "Access granted"}
```

---

## 3. Middleware

### 3.1 Базовое middleware

```python
from fastapi import FastAPI, Request
import time

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### 3.2 Логирование запросов

```python
import logging
from fastapi import FastAPI, Request

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

### 3.3 CORS middleware

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3.4 Аутентификация в middleware

```python
from fastapi import FastAPI, Request, HTTPException, status

@app.middleware("http")
async def authenticate(request: Request, call_next):
    if request.url.path.startswith("/api/protected"):
        token = request.headers.get("Authorization")
        if not token or token != "Bearer valid_token":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Unauthorized"}
            )
    response = await call_next(request)
    return response
```

### 3.5 Rate limiting middleware

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
        raise HTTPException(status_code=429, detail="Too many requests")
    
    request_counts[client_ip].append(current_time)
    response = await call_next(request)
    return response
```

### 3.6 Обработка ошибок в middleware

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )
```

---

## 4. Background Tasks

### 4.1 Базовое использование

```python
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def write_log(message: str):
    with open("log.txt", "a") as f:
        f.write(f"{message}\n")

@app.post("/send-email/")
def send_email(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(write_log, f"Email sent to {email}")
    return {"message": "Email queued"}
```

### 4.2 Отправка email в фоне

```python
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, BackgroundTasks

def send_email_task(to: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["To"] = to
    msg["From"] = "noreply@example.com"
    
    with smtplib.SMTP("smtp.example.com", 587) as server:
        server.starttls()
        server.login("user", "password")
        server.send_message(msg)

@app.post("/notify/")
def notify_user(
    user_email: str,
    message: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(
        send_email_task,
        to=user_email,
        subject="Notification",
        body=message
    )
    return {"message": "Notification queued"}
```

### 4.3 Обработка файлов в фоне

```python
from fastapi import FastAPI, BackgroundTasks, UploadFile, File
import aiofiles

async def process_file_async(file_path: str):
    async with aiofiles.open(file_path, "r") as f:
        content = await f.read()
    processed = content.upper()
    async with aiofiles.open(f"{file_path}.processed", "w") as f:
        await f.write(processed)

@app.post("/upload/")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    file_path = f"uploads/{file.filename}"
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)
    
    background_tasks.add_task(process_file_async, file_path)
    return {"message": "File uploaded and queued for processing"}
```

### 4.4 Очистка данных в фоне

```python
from fastapi import FastAPI, BackgroundTasks
from datetime import datetime, timedelta

def cleanup_old_files():
    cutoff = datetime.now() - timedelta(days=7)
    import os
    for filename in os.listdir("temp"):
        filepath = os.path.join("temp", filename)
        if os.path.getmtime(filepath) < cutoff.timestamp():
            os.remove(filepath)

@app.post("/cleanup/")
def trigger_cleanup(background_tasks: BackgroundTasks):
    background_tasks.add_task(cleanup_old_files)
    return {"message": "Cleanup queued"}
```

### 4.5 Комбинирование с зависимостями

```python
from fastapi import FastAPI, BackgroundTasks, Depends

def get_background_tasks() -> BackgroundTasks:
    return BackgroundTasks()

@app.post("/process/")
def process_data(
    data: dict,
    background_tasks: BackgroundTasks = Depends(get_background_tasks)
):
    def process_task():
        print(f"Processing: {data}")
    
    background_tasks.add_task(process_task)
    return {"message": "Processing started"}
```

---

## 5. Best Practices

### 5.1 Структура зависимостей

```python
from fastapi import FastAPI, Depends
from typing import Generator

def get_db() -> Generator:
    db = "database"
    try:
        yield db
    finally:
        print("Cleanup")

def get_user_service(db: str = Depends(get_db)):
    return UserService(db)

@app.get("/items/")
def read_items(service = Depends(get_user_service)):
    return service.get_all()
```

### 5.2 Переиспользование middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware

class CustomMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Custom"] = "value"
        return response

app.add_middleware(CustomMiddleware)
```

### 5.3 Обработка ошибок в background tasks

```python
import logging
from fastapi import FastAPI, BackgroundTasks

logger = logging.getLogger(__name__)

def safe_background_task(task_id: str):
    try:
        print(f"Processing task {task_id}")
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")

@app.post("/task/")
def create_task(
    task_id: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(safe_background_task, task_id)
    return {"message": "Task created"}
```

---

## 6. Продвинутые техники

### 6.1 Зависимости с контекстом

```python
from contextvars import ContextVar
from fastapi import FastAPI, Depends

request_id_var: ContextVar[str] = ContextVar("request_id")

def get_request_id() -> str:
    return request_id_var.get()

@app.middleware("http")
async def set_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", "unknown")
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

@app.get("/items/")
def read_items(request_id: str = Depends(get_request_id)):
    return {"request_id": request_id}
```

### 6.2 Условные зависимости

```python
from fastapi import FastAPI, Depends, Header

def get_user_role(is_admin: bool = Header(False)):
    if is_admin:
        return "admin"
    return "user"

@app.get("/admin/")
def admin_route(role: str = Depends(get_user_role)):
    if role != "admin":
        raise HTTPException(status_code=403)
    return {"message": "Admin access"}
```
