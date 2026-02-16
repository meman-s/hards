# RPC vs REST

## 1. Зачем нужны

**RPC (Remote Procedure Call)** — вызов удалённых процедур как локальных функций. Прямой вызов методов на сервере.

**REST (Representational State Transfer)** — архитектурный стиль для веб-сервисов, основанный на ресурсах и HTTP-методах.

Оба подхода используются для создания API, но имеют разные философии и области применения.

---

## 2. REST

### 2.1 Основные принципы

- **Ресурсы** — всё представлено как ресурсы (URL)
- **HTTP-методы** — GET, POST, PUT, DELETE, PATCH
- **Stateless** — каждый запрос содержит всю необходимую информацию
- **Кэшируемость** — ответы могут кэшироваться
- **Единообразный интерфейс** — стандартные HTTP-методы и коды статуса

### 2.2 Пример REST API

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id, "name": "John"}

@app.post("/users")
def create_user(user_data: dict):
    return {"id": 1, **user_data}

@app.put("/users/{user_id}")
def update_user(user_id: int, user_data: dict):
    return {"id": user_id, **user_data}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    return {"message": "User deleted"}
```

### 2.3 Преимущества REST

- Простота и понятность
- Кэширование на уровне HTTP
- Масштабируемость
- Широкая поддержка инструментов
- Идемпотентность операций

### 2.4 Недостатки REST

- Over-fetching и under-fetching данных
- Множественные запросы для сложных операций
- Ограниченный набор операций (CRUD)

---

## 3. RPC

### 3.1 Основные принципы

- **Вызов методов** — как локальные функции
- **Протоколы** — JSON-RPC, gRPC, XML-RPC
- **Гибкость** — любые операции, не только CRUD
- **Типизация** — строгая типизация (особенно в gRPC)

### 3.2 Пример JSON-RPC

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class RPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: dict
    id: int

class RPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: dict = None
    error: dict = None
    id: int

@app.post("/rpc")
def rpc_handler(request: RPCRequest):
    if request.method == "getUser":
        return RPCResponse(
            result={"id": request.params["user_id"], "name": "John"},
            id=request.id
        )
    elif request.method == "calculateSum":
        return RPCResponse(
            result={"sum": sum(request.params["numbers"])},
            id=request.id
        )
    else:
        return RPCResponse(
            error={"code": -32601, "message": "Method not found"},
            id=request.id
        )
```

### 3.3 Пример gRPC

```python
import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc

class UserService(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        return user_pb2.UserResponse(
            id=request.user_id,
            name="John",
            email="john@example.com"
        )
    
    def CalculateSum(self, request, context):
        return user_pb2.SumResponse(
            result=sum(request.numbers)
        )

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
server.add_insecure_port('[::]:50051')
server.start()
```

### 3.4 Преимущества RPC

- Естественный вызов методов
- Гибкость операций
- Строгая типизация (gRPC)
- Эффективность (бинарные протоколы)
- Поддержка стриминга (gRPC)

### 3.5 Недостатки RPC

- Сложнее кэширование
- Меньше стандартизации
- Сложнее отладка
- Привязка к конкретному протоколу

---

## 4. Сравнение

| Критерий | REST | RPC |
|----------|------|-----|
| Философия | Ресурсы и действия | Методы и процедуры |
| Протокол | HTTP | HTTP, gRPC, WebSocket |
| Формат данных | JSON, XML | JSON, Protobuf, XML |
| Кэширование | Встроенное | Требует реализации |
| Типизация | Слабая | Строгая (gRPC) |
| Простота | Высокая | Средняя |
| Производительность | Средняя | Высокая (gRPC) |
| Использование | Веб-API, публичные API | Микросервисы, внутренние API |

---

## 5. Когда использовать REST

- Публичные API
- CRUD-операции
- Простые веб-приложения
- Когда нужна простота и понятность
- Когда важна совместимость с HTTP-инструментами

---

## 6. Когда использовать RPC

- Микросервисная архитектура
- Сложные операции, не укладывающиеся в CRUD
- Высокие требования к производительности
- Внутренние API
- Когда нужна строгая типизация
- Стриминг данных

---

## 7. Гибридный подход

Можно комбинировать оба подхода:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")  # REST
def get_user(user_id: int):
    return {"id": user_id, "name": "John"}

@app.post("/rpc")  # RPC
def rpc_handler(request: dict):
    method = request.get("method")
    if method == "batchGetUsers":
        return {"result": [get_user(uid) for uid in request["params"]["ids"]]}
```

---

## 8. GraphQL как альтернатива

**GraphQL** — запросный язык, объединяющий преимущества REST и RPC:

- Единая точка входа (как RPC)
- Запросы данных (как REST)
- Типизация (как gRPC)
- Гибкость запросов

```python
from strawberry.fastapi import GraphQLRouter
import strawberry

@strawberry.type
class User:
    id: int
    name: str
    email: str

@strawberry.type
class Query:
    @strawberry.field
    def user(self, user_id: int) -> User:
        return User(id=user_id, name="John", email="john@example.com")

schema = strawberry.Schema(Query)
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
```
