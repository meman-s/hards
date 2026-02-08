# Аутентификация и Авторизация: JWT, OAuth2, Session-based

## 1. Зачем нужны

**Аутентификация** — проверка личности пользователя (кто вы?). Подтверждение, что пользователь действительно тот, за кого себя выдаёт.

**Авторизация** — проверка прав доступа (что вы можете делать?). Определение, какие действия разрешены пользователю после аутентификации.

**Разница:**
- Аутентификация отвечает на вопрос "Кто вы?" (логин/пароль, токен).
- Авторизация отвечает на вопрос "Что вам разрешено?" (роли, права доступа).

**Методы аутентификации:**
- **JWT (JSON Web Tokens)** — токены без состояния, содержащие информацию о пользователе
- **OAuth2** — протокол делегирования доступа, позволяющий приложениям получать доступ к ресурсам от имени пользователя
- **Session-based** — сессии на сервере, хранящие состояние аутентификации

**Зачем нужны:**
- Защита данных от несанкционированного доступа
- Контроль доступа к ресурсам
- Аудит действий пользователей
- Соответствие требованиям безопасности

---

## 2. JWT (JSON Web Tokens)

### 2.1 Что такое JWT

**JWT (JSON Web Token)** — открытый стандарт (RFC 7519) для безопасной передачи информации между сторонами в виде JSON объекта.

**Основная идея:**
- Токен содержит информацию о пользователе в закодированном виде
- Токен подписан секретным ключом, что гарантирует его подлинность
- Сервер может проверить токен без обращения к базе данных (stateless)

**Как работает:**
1. Пользователь логинится, сервер создаёт JWT токен
2. Токен отправляется клиенту (обычно в заголовке Authorization)
3. Клиент отправляет токен с каждым запросом
4. Сервер проверяет подпись токена и извлекает информацию о пользователе

### 2.2 Структура JWT

JWT состоит из трёх частей, разделённых точками (`.`):

**1. Header (заголовок):**
- Содержит тип токена (JWT) и алгоритм подписи (HS256, RS256)
- Кодируется в Base64URL

**2. Payload (полезная нагрузка):**
- Содержит claims (утверждения) — данные о пользователе
- Стандартные claims: `sub` (subject), `exp` (expiration), `iat` (issued at)
- Пользовательские claims: любые дополнительные данные
- Кодируется в Base64URL

**3. Signature (подпись):**
- Создаётся путём подписи header и payload секретным ключом
- Гарантирует целостность и подлинность токена
- Формула: `HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret)`

**Пример структуры:**
```
header.payload.signature
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyQGV4YW1wbGUuY29tIn0.signature
```

**Важно:** JWT не шифрует данные, только кодирует их в Base64. Любой может декодировать payload и увидеть содержимое. Подпись защищает от изменения, но не от чтения.

### 2.3 Создание JWT

**Процесс создания:**
1. Формируется header с алгоритмом и типом
2. Формируется payload с данными пользователя и временем истечения
3. Создаётся подпись на основе header, payload и секретного ключа
4. Все три части кодируются в Base64URL и объединяются точками

**Секретный ключ:**
- Должен быть достаточно длинным и случайным
- Хранится только на сервере
- Используется для создания и проверки подписи
- Если ключ скомпрометирован, все токены становятся небезопасными

**Время жизни токена:**
- Обычно короткое (15 минут - 1 час) для access token
- Длинное (7-30 дней) для refresh token
- После истечения токен становится недействительным

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

### 2.4 Верификация JWT

**Процесс верификации:**
1. Извлекается токен из запроса (обычно из заголовка Authorization)
2. Разделяется на три части (header, payload, signature)
3. Декодируется header и payload из Base64URL
4. Проверяется подпись: вычисляется новая подпись и сравнивается с полученной
5. Проверяется время истечения (`exp` claim)
6. Если всё верно, извлекаются данные пользователя из payload

**Ошибки верификации:**
- **ExpiredSignatureError**: токен истёк
- **InvalidSignatureError**: подпись неверна (токен изменён или ключ неверный)
- **DecodeError**: токен не может быть декодирован
- **InvalidTokenError**: токен имеет неверный формат

**Безопасность:**
- Проверка подписи гарантирует, что токен не был изменён
- Проверка времени истечения предотвращает использование старых токенов
- Секретный ключ должен храниться безопасно

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

### 2.5 Интеграция с FastAPI

**Как это работает:**
1. FastAPI автоматически извлекает токен из заголовка `Authorization: Bearer <token>`
2. Используется `OAuth2PasswordBearer` для автоматического парсинга
3. Создаётся dependency функция, которая верифицирует токен
4. Dependency инжектируется в endpoints, требующие аутентификации

**Преимущества интеграции:**
- Автоматическое извлечение токена из заголовков
- Удобное использование через Dependency Injection
- Единая точка проверки аутентификации
- Легко переиспользовать в разных endpoints

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

### 2.6 Refresh tokens

**Проблема коротких токенов:**
- Access token имеет короткое время жизни (15-60 минут) для безопасности
- Пользователю пришлось бы логиниться каждые 15 минут
- Это плохой UX

**Решение — Refresh Token:**
- Refresh token имеет длинное время жизни (7-30 дней)
- Хранится безопасно (httpOnly cookie или secure storage)
- Используется для получения нового access token без повторного логина

**Процесс обновления:**
1. Access token истекает
2. Клиент отправляет refresh token на специальный endpoint
3. Сервер проверяет refresh token
4. Сервер выдаёт новый access token (и опционально новый refresh token)
5. Клиент использует новый access token

**Безопасность:**
- Refresh token можно отозвать (добавить в blacklist)
- При компрометации refresh token можно отозвать все сессии пользователя
- Refresh token не должен использоваться для доступа к ресурсам, только для обновления

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

### 2.7 Преимущества JWT

**Stateless (без состояния):**
- Серверу не нужно хранить информацию о сессиях
- Каждый запрос содержит всю необходимую информацию
- Упрощает масштабирование (не нужна общая база сессий)

**Масштабируемость:**
- Легко масштабировать горизонтально (добавлять серверы)
- Не требуется синхронизация состояния между серверами
- Каждый сервер может независимо проверять токены

**Работа с микросервисами:**
- Токен можно передавать между сервисами
- Каждый сервис может проверить токен независимо
- Не требуется централизованная проверка аутентификации

**Поддержка мобильных приложений:**
- Токен можно хранить в secure storage
- Не требуется управление cookies
- Работает с REST API

**Дополнительные преимущества:**
- Можно включить информацию о пользователе прямо в токен
- Меньше запросов к базе данных (не нужно проверять сессию)
- Работает через CDN и прокси

### 2.8 Недостатки JWT

**Невозможность отзыва:**
- После выдачи токена его нельзя отозвать до истечения срока
- Если токен скомпрометирован, он остаётся валидным до истечения
- Решение: использовать короткое время жизни + refresh tokens + blacklist

**Размер токена:**
- JWT больше, чем простой session ID
- Увеличивает размер каждого запроса
- Может быть проблемой при ограниченной пропускной способности

**Безопасность ключа:**
- Если секретный ключ скомпрометирован, все токены становятся небезопасными
- Ключ должен храниться очень безопасно
- Ротация ключа требует перевыдачи всех токенов

**Дополнительные недостатки:**
- Данные в payload видны всем (только Base64, не шифрование)
- Нельзя изменить содержимое токена после выдачи
- Требует правильной настройки алгоритмов подписи

---

## 3. OAuth2

### 3.1 Что такое OAuth2

**OAuth2** — протокол авторизации, позволяющий приложению получать ограниченный доступ к ресурсам пользователя от его имени.

**Основная идея:**
- Пользователь не передаёт свои учётные данные приложению
- Вместо этого приложение получает токен доступа от провайдера
- Токен даёт ограниченные права на определённое время

**Участники OAuth2:**
1. **Resource Owner (Владелец ресурса)** — пользователь, чьи данные защищены
2. **Client (Клиент)** — приложение, запрашивающее доступ
3. **Authorization Server (Сервер авторизации)** — выдает токены доступа
4. **Resource Server (Сервер ресурсов)** — API, защищённый OAuth2

**Типичный сценарий:**
- Пользователь хочет использовать приложение "Войти через Google"
- Приложение перенаправляет на Google для авторизации
- Пользователь логинится в Google и даёт разрешение
- Google выдаёт токен приложению
- Приложение использует токен для доступа к данным пользователя

### 3.2 Потоки OAuth2 (Grant Types)

**Authorization Code Flow:**
- Для веб-приложений с серверной частью
- Безопасный, так как токен не передаётся через браузер
- Используется в большинстве случаев

**Client Credentials Flow:**
- Для сервер-к-сервер взаимодействия
- Приложение аутентифицируется само, без пользователя
- Используется для API-интеграций

**Implicit Flow:**
- Устаревший, не рекомендуется
- Токен передаётся через URL (небезопасно)
- Заменён на Authorization Code Flow с PKCE

**Password Grant (Resource Owner Password Credentials):**
- Не рекомендуется для публичных приложений
- Пользователь передаёт логин/пароль напрямую приложению
- Используется только в доверенных приложениях

### 3.3 Authorization Code Flow

**Как работает Authorization Code Flow:**

1. **Запрос авторизации:**
   - Клиент перенаправляет пользователя на сервер авторизации
   - Передаются: client_id, redirect_uri, scope, state (для защиты от CSRF)

2. **Авторизация пользователя:**
   - Пользователь логинится на сервере авторизации
   - Пользователь даёт разрешение приложению

3. **Получение authorization code:**
   - Сервер авторизации перенаправляет на redirect_uri с authorization code
   - Code одноразовый и имеет короткое время жизни (обычно 10 минут)

4. **Обмен code на токен:**
   - Клиент отправляет code + client_secret на сервер авторизации
   - Сервер проверяет code и выдаёт access token и refresh token

5. **Использование токена:**
   - Клиент использует access token для доступа к ресурсам
   - Токен отправляется в заголовке Authorization: Bearer <token>

**Безопасность:**
- client_secret никогда не передаётся через браузер
- Authorization code одноразовый
- State параметр защищает от CSRF атак
- Токен передаётся только между сервером клиента и сервером ресурсов

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

### 3.4 Client Credentials Flow

**Когда используется:**
- Сервер-к-сервер взаимодействие
- Нет пользователя (машинная аутентификация)
- API-интеграции между сервисами

**Как работает:**
1. Клиент отправляет client_id и client_secret на сервер авторизации
2. Сервер проверяет учётные данные
3. Сервер выдаёт access token
4. Клиент использует токен для доступа к API

**Особенности:**
- Нет refresh token (токен выдаётся на длительный срок)
- Нет пользователя, только приложение
- Используется для сервисных аккаунтов
- Токен даёт доступ к ресурсам приложения, а не пользователя

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

### 3.5 Реализация OAuth2 провайдера

**OAuth2 провайдер** — сервер, который выдаёт токены доступа.

**Компоненты провайдера:**
1. **Authorization endpoint** — где пользователь авторизуется
2. **Token endpoint** — где обменивается code на токен
3. **User info endpoint** — где получается информация о пользователе
4. **Token validation** — проверка валидности токенов

**Процесс:**
- Провайдер управляет пользователями и их учётными данными
- Провайдер выдаёт токены после успешной аутентификации
- Провайдер проверяет токены при запросах к защищённым ресурсам

**Безопасность:**
- Хранение паролей в хешированном виде
- Использование HTTPS для всех запросов
- Валидация redirect_uri для предотвращения атак
- Ограничение времени жизни токенов

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

### 4.1 Что такое Session-based Authentication

**Session-based аутентификация** — метод, при котором сервер хранит информацию о сессии пользователя.

**Как работает:**
1. Пользователь логинится с учётными данными
2. Сервер создаёт уникальный session ID
3. Сервер сохраняет session ID и данные пользователя (в памяти, БД или Redis)
4. Session ID отправляется клиенту (обычно в cookie)
5. Клиент отправляет session ID с каждым запросом
6. Сервер проверяет session ID и извлекает данные пользователя

**Отличие от JWT:**
- JWT: информация хранится в токене (stateless)
- Session: информация хранится на сервере (stateful)
- Session ID — это просто идентификатор, данные на сервере

**Преимущества подхода:**
- Можно отозвать сессию в любой момент
- Данные пользователя не передаются в каждом запросе
- Больше контроля над активными сессиями
- Можно хранить больше данных, чем в JWT

### 4.2 Базовая реализация

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

**Простая реализация:**
- Session ID генерируется случайным образом (secrets.token_urlsafe)
- Session ID хранится в словаре на сервере
- При каждом запросе проверяется наличие session ID в словаре
- При logout session ID удаляется из словаря

**Ограничения простой реализации:**
- Не работает при перезапуске сервера (данные в памяти теряются)
- Не масштабируется на несколько серверов (нет общей памяти)
- Утечка памяти при росте количества сессий

### 4.3 Сессии с cookies

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

**Cookies для хранения session ID:**
- Session ID автоматически отправляется браузером с каждым запросом
- HttpOnly флаг защищает от XSS атак (JavaScript не может прочитать cookie)
- Secure флаг требует HTTPS для передачи cookie
- SameSite флаг защищает от CSRF атак

**Преимущества cookies:**
- Автоматическая отправка с каждым запросом
- Защита от XSS через HttpOnly
- Защита от CSRF через SameSite
- Управление временем жизни через expires

**Недостатки cookies:**
- Ограничение размера (4KB)
- Проблемы с CORS в некоторых случаях
- Не работают в некоторых мобильных приложениях

### 4.4 Сессии с Redis

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

**Redis для хранения сессий:**
- Сессии хранятся в Redis (внешнее хранилище)
- Работает при перезапуске сервера (данные персистентны)
- Масштабируется на несколько серверов (общее хранилище)
- Автоматическое истечение сессий через TTL

**Преимущества Redis:**
- Быстрый доступ (in-memory хранилище)
- Автоматическое удаление истёкших сессий
- Работает в распределённых системах
- Поддержка кластеризации

**Настройка:**
- Устанавливается время жизни сессии (TTL)
- При каждом запросе TTL обновляется (sliding expiration)
- При logout сессия удаляется из Redis

### 4.5 Преимущества Session-based

**Простота реализации:**
- Понятная модель работы
- Легко отлаживать
- Не требует сложной криптографии

**Возможность отзыва:**
- Можно немедленно отозвать сессию
- Полезно при компрометации или logout
- Можно отозвать все сессии пользователя

**Безопасность:**
- Данные пользователя не передаются в каждом запросе
- Session ID — просто идентификатор, не содержит данных
- Можно хранить чувствительные данные на сервере

**Контроль:**
- Видно все активные сессии пользователя
- Можно ограничить количество одновременных сессий
- Можно видеть историю активности

### 4.6 Недостатки Session-based

**Требует хранения:**
- Нужно хранить сессии на сервере или в БД/Redis
- Увеличивает использование памяти/диска
- Требует управления жизненным циклом сессий

**Проблемы с масштабированием:**
- При нескольких серверах нужна общая база сессий
- Sticky sessions (привязка к серверу) ограничивает балансировку
- Shared storage (Redis/БД) становится узким местом

**Не подходит для микросервисов:**
- Каждый сервис должен иметь доступ к хранилищу сессий
- Усложняет архитектуру
- JWT лучше подходит для распределённых систем

---

## 5. Авторизация (RBAC)

### 5.1 Что такое авторизация

**Авторизация** — процесс определения, какие действия разрешены пользователю после аутентификации.

**Разница с аутентификацией:**
- Аутентификация: "Кто вы?" → проверка личности
- Авторизация: "Что вам разрешено?" → проверка прав

**Модели авторизации:**

**RBAC (Role-Based Access Control) — Ролевая модель:**
- Пользователям назначаются роли (admin, user, guest)
- Ролям назначаются права (read, write, delete)
- Проверка: имеет ли роль пользователя нужное право

**ABAC (Attribute-Based Access Control) — Атрибутивная модель:**
- Права определяются атрибутами (отдел, проект, уровень доступа)
- Более гибкая, но сложнее в реализации

**ACL (Access Control List) — Списки доступа:**
- Для каждого ресурса список пользователей с правами
- Точный контроль, но сложно управлять

### 5.2 Роли и права (RBAC)

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

**Роли (Roles):**
- Группируют пользователей по функциям
- Примеры: ADMIN, USER, MODERATOR, GUEST
- Пользователь может иметь несколько ролей

**Права (Permissions):**
- Конкретные действия, которые можно выполнять
- Примеры: READ, WRITE, DELETE, MANAGE_USERS
- Права назначаются ролям, а не пользователям напрямую

**Матрица ролей и прав:**
- Определяет, какие права есть у каждой роли
- Администратор обычно имеет все права
- Обычный пользователь имеет ограниченные права

**Проверка прав:**
- При запросе определяется роль пользователя
- Проверяется, есть ли у роли нужное право
- Если права нет, запрос отклоняется (403 Forbidden)

### 5.3 Декоратор для проверки прав

**Декораторы для авторизации:**
- Обёртывают endpoint функции
- Проверяют права до выполнения функции
- Возвращают ошибку, если прав нет

**Преимущества:**
- Декларативный подход (видно права прямо в коде)
- Переиспользование логики проверки
- Легко комбинировать с dependency injection

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

**Почему нельзя хранить пароли в открытом виде:**
- При компрометации БД все пароли становятся известны
- Пользователи часто используют одинаковые пароли на разных сайтах
- Нарушение может привести к компрометации других аккаунтов

**Хеширование паролей:**
- Пароль никогда не хранится в открытом виде
- Используется односторонняя функция хеширования (bcrypt, argon2)
- Добавляется "соль" (salt) для защиты от rainbow tables

**Как работает:**
1. При регистрации пароль хешируется с солью
2. Хеш и соль сохраняются в БД
3. При логине пароль хешируется с той же солью
4. Сравниваются хеши (не пароли)

**Алгоритмы:**
- **bcrypt**: медленный, защищён от brute force
- **argon2**: современный, победитель Password Hashing Competition
- **scrypt**: защищён от атак с использованием специализированного оборудования

**Никогда не используйте:**
- MD5, SHA1, SHA256 для паролей (слишком быстрые)
- Простое хеширование без соли
- Обратимое шифрование (не хеширование)

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### 6.2 Защита от brute force

**Brute force атака** — попытка подобрать пароль путём перебора возможных комбинаций.

**Защита:**
- Ограничение количества попыток входа
- Блокировка после нескольких неудачных попыток
- Увеличение задержки между попытками (exponential backoff)
- CAPTCHA после нескольких попыток

**Реализация:**
- Отслеживание неудачных попыток по IP или username
- Временное окно для подсчёта попыток (например, 5 минут)
- Блокировка на определённое время или до ручной разблокировки

**Дополнительные меры:**
- Rate limiting на уровне API
- Мониторинг подозрительной активности
- Уведомления о множественных неудачных попытках

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

**Почему HTTPS обязателен:**
- Пароли и токены передаются в открытом виде по HTTP
- Злоумышленник может перехватить данные (man-in-the-middle)
- Cookies с session ID могут быть украдены

**Что защищает HTTPS:**
- Шифрование данных в транзите
- Защита от перехвата паролей и токенов
- Защита от подмены ответов сервера
- Защита cookies от перехвата

**Реализация:**
- Принудительное перенаправление HTTP → HTTPS
- HSTS заголовок для принудительного HTTPS в браузере
- Secure флаг для cookies (передача только по HTTPS)

```python
from fastapi import FastAPI, Request
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()
app.add_middleware(HTTPSRedirectMiddleware)
```

### 6.4 CORS для аутентификации

**CORS (Cross-Origin Resource Sharing):**
- Разрешает запросы с других доменов
- Необходим для SPA (Single Page Applications)
- Требует правильной настройки для работы с credentials

**Настройка для аутентификации:**
- `allow_credentials=True` — разрешает отправку cookies/tokens
- `allow_origins` — список разрешённых доменов (не "*" с credentials)
- Правильные заголовки для preflight запросов

**Безопасность:**
- Не использовать `allow_origins=["*"]` с credentials
- Указывать конкретные домены
- Проверять Origin заголовок на сервере

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

### 7.1 Детальное сравнение

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

### 8.1 Когда использовать JWT

**REST API:**
- Stateless архитектура упрощает масштабирование
- Не требуется управление сессиями
- Легко интегрировать с различными клиентами

**Микросервисы:**
- Каждый сервис может независимо проверять токен
- Не требуется общая база сессий
- Токен можно передавать между сервисами

**Мобильные приложения:**
- Токен можно хранить в secure storage
- Не требуется управление cookies
- Работает офлайн (токен валиден до истечения)

**Stateless архитектура:**
- Когда нужна максимальная масштабируемость
- Когда нет возможности использовать shared storage
- Когда важна простота развёртывания

### 8.2 Когда использовать OAuth2

**Публичные API:**
- Когда нужно предоставить доступ третьим приложениям
- Когда пользователи не хотят создавать новый аккаунт
- Когда нужна стандартизированная авторизация

**Интеграция с третьими сторонами:**
- Вход через социальные сети (Google, Facebook)
- Интеграция с внешними сервисами
- Делегирование доступа к ресурсам

**Делегирование доступа:**
- Когда приложение должно работать от имени пользователя
- Когда нужен ограниченный доступ (scopes)
- Когда нужен контроль пользователя над доступом

**Enterprise приложения:**
- Когда нужна централизованная авторизация
- Когда используются корпоративные identity providers
- Когда нужен аудит доступа

### 8.3 Когда использовать Session-based

**Традиционные веб-приложения:**
- Когда есть серверная часть, управляющая сессиями
- Когда нужен полный контроль над сессиями
- Когда простота важнее масштабируемости

**Когда нужен контроль сессий:**
- Немедленный отзыв доступа
- Просмотр активных сессий
- Ограничение количества одновременных сессий

**Простые требования:**
- Монолитное приложение
- Один сервер или sticky sessions
- Не требуется интеграция с внешними сервисами

**Монолитные приложения:**
- Когда все компоненты на одном сервере
- Когда есть общая база данных для сессий
- Когда простота реализации важна

### 8.4 Гибридные подходы

**JWT + Session:**
- JWT для API, Session для веб-интерфейса
- JWT для внешних клиентов, Session для внутренних

**OAuth2 + JWT:**
- OAuth2 для получения токенов
- JWT для передачи токенов между сервисами

**Выбор зависит от:**
- Архитектуры приложения
- Требований к безопасности
- Необходимости масштабирования
- Типа клиентов (веб, мобильные, API)
