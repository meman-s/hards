# Аутентификация и Авторизация: JWT, OAuth2, Session-based

## 1. Зачем нужны

**Аутентификация** — проверка личности пользователя (кто вы?).

**Авторизация** — проверка прав доступа (что вы можете делать?).

Методы:
- **JWT (JSON Web Tokens)** — токены без состояния
- **OAuth2** — делегирование доступа
- **Session-based** — сессии на сервере

---

## 2. JWT (JSON Web Tokens)

### 2.1 Структура JWT

JWT состоит из трёх частей:
- Header (алгоритм, тип)
- Payload (данные)
- Signature (подпись)

### 2.2 Создание JWT

```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

token = create_access_token(data={"sub": "user@example.com"})
```

### 2.3 Верификация JWT

```python
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 2.4 Интеграция с FastAPI

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

@app.get("/users/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}
```

### 2.5 Refresh tokens

```python
def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=30)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/refresh")
def refresh_token(refresh_token: str):
    payload = verify_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    new_access_token = create_access_token(data={"sub": payload.get("sub")})
    return {"access_token": new_access_token}
```

### 2.6 Преимущества JWT

- Stateless (не требует хранения на сервере)
- Масштабируемость
- Работает с микросервисами
- Поддержка мобильных приложений

### 2.7 Недостатки JWT

- Невозможность отзыва до истечения срока
- Больший размер, чем session ID
- Безопасность зависит от секретного ключа

---

## 3. OAuth2

### 3.1 Потоки OAuth2

- **Authorization Code** — для веб-приложений
- **Client Credentials** — для сервер-к-сервер
- **Implicit** — устаревший
- **Password** — не рекомендуется

### 3.2 Authorization Code Flow

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
import httpx

app = FastAPI()
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://provider.com/authorize",
    tokenUrl="https://provider.com/token"
)

@app.get("/login")
async def login():
    return {
        "authorization_url": "https://provider.com/authorize?client_id=xxx&redirect_uri=yyy"
    }

@app.get("/callback")
async def callback(code: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://provider.com/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": "xxx",
                "client_secret": "yyy",
                "redirect_uri": "zzz"
            }
        )
        token_data = response.json()
        return token_data
```

### 3.3 Client Credentials Flow

```python
@app.post("/token")
async def get_token():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://provider.com/token",
            data={
                "grant_type": "client_credentials",
                "client_id": "xxx",
                "client_secret": "yyy"
            }
        )
        return response.json()
```

### 3.4 Реализация OAuth2 провайдера

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def fake_hash_password(password: str):
    return "hashed_" + password

def fake_verify_password(plain_password, hashed_password):
    return fake_hash_password(plain_password) == hashed_password

users_db = {
    "user@example.com": {
        "username": "user@example.com",
        "hashed_password": fake_hash_password("secret")
    }
}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or not fake_verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    username = payload.get("sub")
    return {"username": username}
```

---

## 4. Session-based Authentication

### 4.1 Базовая реализация

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from typing import Dict

app = FastAPI()
security = HTTPBasic()
sessions: Dict[str, str] = {}

def verify_user(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username == "admin" and credentials.password == "secret":
        session_id = secrets.token_urlsafe(32)
        sessions[session_id] = credentials.username
        return session_id
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect credentials"
    )

@app.post("/login")
def login(session_id: str = Depends(verify_user)):
    return {"session_id": session_id}

def get_current_user(session_id: str = Header(None)):
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Invalid session")
    return sessions[session_id]

@app.get("/users/me")
def read_users_me(username: str = Depends(get_current_user)):
    return {"username": username}
```

### 4.2 Сессии с cookies

```python
from fastapi import FastAPI, Response, Request
import secrets

sessions: Dict[str, str] = {}

@app.post("/login")
def login(response: Response, username: str, password: str):
    if username == "admin" and password == "secret":
        session_id = secrets.token_urlsafe(32)
        sessions[session_id] = username
        response.set_cookie(key="session_id", value=session_id, httponly=True)
        return {"message": "Logged in"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Invalid session")
    return sessions[session_id]

@app.get("/users/me")
def read_users_me(username: str = Depends(get_current_user)):
    return {"username": username}
```

### 4.3 Сессии с Redis

```python
import redis
from fastapi import FastAPI, Depends, HTTPException
import secrets

redis_client = redis.Redis(host='localhost', port=6379, db=0)

@app.post("/login")
def login(username: str, password: str):
    if username == "admin" and password == "secret":
        session_id = secrets.token_urlsafe(32)
        redis_client.setex(f"session:{session_id}", 3600, username)
        return {"session_id": session_id}
    raise HTTPException(status_code=401, detail="Invalid credentials")

def get_current_user(session_id: str = Header(None)):
    if not session_id:
        raise HTTPException(status_code=401, detail="No session")
    
    username = redis_client.get(f"session:{session_id}")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    return username.decode()

@app.get("/users/me")
def read_users_me(username: str = Depends(get_current_user)):
    return {"username": username}
```

### 4.4 Преимущества Session-based

- Простота реализации
- Возможность отзыва сессий
- Безопасность (сессии на сервере)
- Контроль над активными сессиями

### 4.5 Недостатки Session-based

- Требует хранения на сервере
- Проблемы с масштабированием
- Не подходит для микросервисов без shared storage

---

## 5. Авторизация (RBAC)

### 5.1 Роли и права

```python
from enum import Enum
from fastapi import FastAPI, Depends, HTTPException

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"

role_permissions = {
    Role.ADMIN: [Permission.READ, Permission.WRITE, Permission.DELETE],
    Role.USER: [Permission.READ, Permission.WRITE],
    Role.GUEST: [Permission.READ]
}

def get_user_role(username: str) -> Role:
    user_roles = {
        "admin": Role.ADMIN,
        "user": Role.USER
    }
    return user_roles.get(username, Role.GUEST)

def require_permission(permission: Permission):
    def permission_checker(username: str = Depends(get_current_user)):
        role = get_user_role(username)
        if permission not in role_permissions.get(role, []):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return username
    return permission_checker

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    username: str = Depends(require_permission(Permission.DELETE))
):
    return {"message": f"User {user_id} deleted"}
```

### 5.2 Декоратор для проверки прав

```python
from functools import wraps

def require_role(role: Role):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            username = kwargs.get("username")
            user_role = get_user_role(username)
            if user_role != role and role != Role.ADMIN:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## 6. Best Practices

### 6.1 Безопасное хранение паролей

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 6.2 Защита от brute force

```python
from collections import defaultdict
from datetime import datetime, timedelta

failed_attempts = defaultdict(list)

def check_rate_limit(username: str):
    now = datetime.now()
    attempts = failed_attempts[username]
    attempts[:] = [t for t in attempts if (now - t).seconds < 300]
    
    if len(attempts) >= 5:
        raise HTTPException(status_code=429, detail="Too many attempts")
    
    attempts.append(now)
```

### 6.3 HTTPS только

```python
from fastapi import FastAPI, Request
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()
app.add_middleware(HTTPSRedirectMiddleware)
```

### 6.4 CORS для аутентификации

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 7. Сравнение методов

| Критерий | JWT | OAuth2 | Session |
|----------|-----|--------|---------|
| Stateless | Да | Да | Нет |
| Масштабируемость | Высокая | Высокая | Средняя |
| Отзыв токенов | Сложно | Да | Да |
| Безопасность | Зависит от ключа | Высокая | Высокая |
| Сложность | Средняя | Высокая | Низкая |
| Использование | API, микросервисы | Публичные API | Веб-приложения |

---

## 8. Выбор метода

### 8.1 JWT

- REST API
- Микросервисы
- Мобильные приложения
- Stateless архитектура

### 8.2 OAuth2

- Публичные API
- Интеграция с третьими сторонами
- Делегирование доступа
- Enterprise приложения

### 8.3 Session-based

- Традиционные веб-приложения
- Когда нужен контроль сессий
- Простые требования
- Монолитные приложения
