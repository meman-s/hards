# FastAPI: Dependency Injection, Middleware, Background Tasks

## 1. Зачем нужны

**Dependency Injection (DI)** — паттерн для управления зависимостями, упрощающий тестирование и переиспользование кода.

**Middleware** — промежуточное ПО для обработки запросов/ответов (логирование, аутентификация, CORS).

**Background Tasks** — выполнение задач после отправки ответа клиенту (отправка email, обработка файлов).

---

## 2. Dependency Injection

### 2.1 Что такое Dependency Injection

**Dependency Injection (DI)** — паттерн проектирования, при котором зависимости передаются объекту извне, а не создаются внутри него.

**Принципы:**
- **Инверсия зависимостей**: объект не создаёт свои зависимости, а получает их готовыми.
- **Разделение ответственности**: создание зависимостей отделено от их использования.
- **Тестируемость**: легко подменить зависимости на моки в тестах.

**Как работает в FastAPI:**
1. FastAPI анализирует сигнатуру функции endpoint.
2. Находит параметры с `Depends()`.
3. Вызывает функции-зависимости и передаёт их результаты в endpoint.
4. Если зависимость использует `yield`, код после `yield` выполняется после завершения endpoint (cleanup).

**Преимущества:**
- Переиспользование кода (одна функция-зависимость для многих endpoints).
- Автоматическое управление жизненным циклом (особенно с `yield`).
- Упрощение тестирования (легко подменить зависимости).
- Централизованная логика (например, аутентификация в одном месте).

### 2.2 Базовое использование

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

**Генераторы с yield:**
- Код до `yield` выполняется **до** вызова endpoint (setup).
- Код после `yield` выполняется **после** завершения endpoint (cleanup).
- Полезно для ресурсов, требующих закрытия (БД, файлы, соединения).

### 2.3 Зависимости с параметрами

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

**Зависимости могут принимать параметры:**
- Query параметры, Path параметры, Headers автоматически извлекаются FastAPI.
- Валидация происходит через Pydantic.
- Результат возвращается как зависимость для endpoint.

### 2.4 Вложенные зависимости

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

**Вложенные зависимости:**
- Зависимость может зависеть от другой зависимости.
- FastAPI автоматически разрешает цепочку зависимостей.
- Порядок выполнения: от самых глубоких к поверхностным.
- Полезно для многоуровневой аутентификации (токен → пользователь → права).

### 2.5 Классы как зависимости

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

**Классы как зависимости:**
- Позволяют инкапсулировать логику в классы.
- Фабричная функция создаёт экземпляр класса.
- Полезно для сервисного слоя (UserService, OrderService).

### 2.6 Кэширование зависимостей

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

**Кэширование:**
- `@lru_cache()` кэширует результат функции-зависимости.
- Полезно для дорогих операций (чтение конфигурации, подключение к внешним сервисам).
- Кэш очищается при перезапуске приложения.

### 2.7 Зависимости с исключениями

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

**Исключения в зависимостях:**
- Зависимость может вызвать `HTTPException` для остановки выполнения.
- Исключение возвращается клиенту как HTTP ответ.
- Полезно для валидации и аутентификации.

---

## 3. Middleware

### 3.1 Что такое Middleware

**Middleware** — промежуточный слой между запросом и обработчиком, а также между обработчиком и ответом.

**Как работает:**
1. Запрос приходит на middleware.
2. Middleware может изменить запрос или выполнить действия до обработки.
3. Вызывается `call_next(request)` для передачи запроса дальше.
4. Получается ответ от endpoint.
5. Middleware может изменить ответ или выполнить действия после обработки.
6. Возвращается ответ клиенту.

**Порядок выполнения:**
- Middleware выполняются в **обратном порядке** добавления (LIFO — Last In, First Out).
- Если добавили: A, B, C, то выполнится: C → B → A → endpoint → A → B → C.

**Типы middleware:**
- **HTTP middleware**: обрабатывает все HTTP запросы.
- **ASGI middleware**: более низкоуровневый, работает с ASGI протоколом.

**Использование:**
- Логирование запросов/ответов.
- Добавление заголовков.
- Аутентификация и авторизация.
- Обработка CORS.
- Rate limiting.
- Мониторинг и метрики.

### 3.2 Базовое middleware

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

**Структура middleware:**
- Принимает `request: Request` и `call_next` (следующий middleware/endpoint).
- Выполняет код **до** `call_next` (pre-processing).
- Вызывает `await call_next(request)` для передачи запроса.
- Выполняет код **после** `call_next` (post-processing).
- Возвращает `Response`.

### 3.3 Логирование запросов

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

**Логирование:**
- Захватывает информацию о запросе до обработки.
- Захватывает информацию о ответе после обработки.
- Полезно для отладки и мониторинга.

### 3.4 CORS middleware

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

**CORS (Cross-Origin Resource Sharing):**
- Разрешает запросы с других доменов.
- Добавляет необходимые заголовки в ответ.
- Обрабатывает preflight запросы (OPTIONS).

### 3.5 Аутентификация в middleware

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

**Аутентификация:**
- Проверяет токены/учётные данные до обработки запроса.
- Может вернуть ошибку без вызова endpoint.
- Полезно для защиты целых групп endpoints.

### 3.6 Rate limiting middleware

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

**Rate limiting:**
- Отслеживает количество запросов от клиента.
- Блокирует превысивших лимит.
- Защищает от DDoS и злоупотреблений.

**Ограничения:**
- Простая реализация хранит счётчики в памяти (не подходит для распределённых систем).
- Для production лучше использовать Redis или специализированные библиотеки.

### 3.7 Обработка ошибок в middleware

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

**Обработка ошибок:**
- `@app.exception_handler` перехватывает исключения определённого типа.
- Позволяет кастомизировать формат ошибок.
- Полезно для единообразной обработки ошибок валидации.

---

## 4. Background Tasks

### 4.1 Что такое Background Tasks

**Background Tasks** — задачи, которые выполняются **после** отправки ответа клиенту.

**Как работает:**
1. Endpoint получает запрос.
2. Добавляет задачи в `BackgroundTasks`.
3. Выполняет основную логику endpoint.
4. Возвращает ответ клиенту.
5. **После отправки ответа** выполняются background tasks.

**Преимущества:**
- Клиент не ждёт выполнения долгих операций.
- Улучшает время отклика API.
- Полезно для операций, которые не критичны для ответа.

**Ограничения:**
- Выполняются в **том же процессе**, что и приложение.
- Если приложение завершится, задачи могут не выполниться.
- Не подходят для критичных операций (лучше использовать очереди задач: Celery, RQ).

**Когда использовать:**
- Отправка email (не критично для ответа).
- Логирование событий.
- Обработка файлов.
- Очистка временных данных.
- Обновление кэша.

**Когда НЕ использовать:**
- Критичные операции (сохранение важных данных).
- Долгие операции (лучше использовать очереди).
- Операции, требующие гарантии выполнения.

### 4.2 Базовое использование

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

**Механизм:**
- `BackgroundTasks` автоматически инжектируется FastAPI.
- `add_task()` добавляет задачу в очередь.
- Задачи выполняются последовательно после отправки ответа.

### 4.3 Отправка email в фоне

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

**Email в фоне:**
- Отправка email может занимать секунды.
- Клиенту не нужно ждать завершения отправки.
- Ошибки отправки не влияют на ответ API.

### 4.4 Обработка файлов в фоне

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

**Обработка файлов:**
- Файл сохраняется сразу (быстрый ответ).
- Обработка (конвертация, ресайз) выполняется в фоне.
- Клиент получает подтверждение загрузки без ожидания обработки.

### 4.5 Очистка данных в фоне

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

**Очистка данных:**
- Периодическая очистка не должна блокировать API.
- Выполняется в фоне после ответа клиенту.
- Полезно для maintenance операций.

### 4.6 Комбинирование с зависимостями

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

**С зависимостями:**
- `BackgroundTasks` можно инжектировать через `Depends()`.
- Полезно для переиспользования в нескольких endpoints.
- Позволяет централизовать логику работы с задачами.

---

## 5. Best Practices

### 5.0 Когда что использовать

**Dependency Injection:**
- Управление зависимостями (БД, сервисы).
- Аутентификация и авторизация.
- Валидация параметров.
- Переиспользование кода.

**Middleware:**
- Глобальная обработка всех запросов.
- Логирование и мониторинг.
- CORS, безопасность.
- Rate limiting.

**Background Tasks:**
- Не критичные операции после ответа.
- Отправка уведомлений.
- Обработка файлов.
- Очистка данных.

### 5.1 Структура зависимостей

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

**Организация:**
- Разделять зависимости по доменам (auth, db, services).
- Использовать генераторы для ресурсов с cleanup.
- Создавать фабричные функции для сервисов.

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

**Классы middleware:**
- Позволяют переиспользовать middleware в разных приложениях.
- Инкапсулирует логику middleware.
- Легче тестировать и поддерживать.

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

**Обработка ошибок:**
- Всегда оборачивайте background tasks в try-except.
- Логируйте ошибки для отладки.
- Не позволяйте ошибкам в задачах влиять на основное приложение.

---

## 6. Продвинутые техники

### 6.0 Производительность и ограничения

**Dependency Injection:**
- Зависимости вычисляются для каждого запроса.
- Используйте кэширование для дорогих операций.
- Избегайте тяжёлых вычислений в зависимостях.

**Middleware:**
- Выполняется для **каждого** запроса.
- Держите логику middleware простой и быстрой.
- Избегайте блокирующих операций.

**Background Tasks:**
- Выполняются **после** отправки ответа, но **до** закрытия соединения.
- Если задача долгая, клиент всё равно может ждать.
- Для долгих задач используйте очереди (Celery, RQ).

### 6.1 Зависимости с контекстом

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

**Context Variables:**
- `ContextVar` хранит данные, специфичные для текущего запроса.
- Автоматически изолированы между запросами.
- Полезно для передачи контекста через цепочку зависимостей.
- Работает с async/await корректно.

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

---

## 7. Сравнение подходов

### 7.1 Dependency Injection vs Middleware

| Критерий | Dependency Injection | Middleware |
|----------|---------------------|------------|
| **Область действия** | Отдельные endpoints | Все запросы |
| **Гибкость** | Высокая (можно выбирать endpoints) | Низкая (применяется везде) |
| **Производительность** | Вычисляется только для нужных endpoints | Выполняется для всех запросов |
| **Использование** | Логика, специфичная для endpoints | Глобальная обработка |

### 7.2 Background Tasks vs Очереди задач

| Критерий | Background Tasks | Очереди (Celery/RQ) |
|----------|------------------|---------------------|
| **Гарантия выполнения** | Нет (зависит от процесса) | Да (персистентное хранилище) |
| **Масштабируемость** | Ограничена одним процессом | Неограниченная (множество воркеров) |
| **Сложность** | Простая | Средняя/Высокая |
| **Использование** | Простые задачи | Критичные/долгие задачи |

### 7.3 Рекомендации

**Используйте Dependency Injection для:**
- Аутентификации (только для защищённых endpoints).
- Валидации параметров.
- Управления ресурсами (БД, файлы).

**Используйте Middleware для:**
- Логирования всех запросов.
- CORS.
- Глобальной аутентификации (если все endpoints защищены).

**Используйте Background Tasks для:**
- Простых не критичных операций.
- Быстрых задач (< 1 секунды).

**Используйте Очереди для:**
- Критичных операций.
- Долгих задач (> 1 секунды).
- Задач, требующих гарантии выполнения.
