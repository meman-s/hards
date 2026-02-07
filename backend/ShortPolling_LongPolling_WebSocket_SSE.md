# ShortPolling, LongPolling, WebSocket, Server-Sent Events

## 1. Зачем нужны

Различные техники для получения обновлений от сервера в реальном времени:

- **Short Polling** — периодические запросы
- **Long Polling** — запросы с задержкой ответа
- **WebSocket** — двустороннее постоянное соединение
- **Server-Sent Events (SSE)** — односторонний поток от сервера

Каждая техника имеет свои преимущества и области применения.

---

## 2. Short Polling

### 2.1 Принцип работы

Клиент периодически отправляет запросы на сервер для проверки обновлений.

### 2.2 Реализация на клиенте

```javascript
setInterval(async () => {
    const response = await fetch('/api/updates');
    const data = await response.json();
    if (data.hasUpdates) {
        updateUI(data);
    }
}, 5000);
```

### 2.3 Реализация на сервере (FastAPI)

```python
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()
last_update = datetime.now()

@app.get("/api/updates")
def check_updates():
    global last_update
    has_updates = (datetime.now() - last_update).seconds < 5
    return {"hasUpdates": has_updates, "timestamp": datetime.now()}
```

### 2.4 Преимущества

- Простота реализации
- Работает через обычный HTTP
- Не требует специальной инфраструктуры

### 2.5 Недостатки

- Высокая нагрузка на сервер
- Задержка получения обновлений
- Неэффективное использование ресурсов

---

## 3. Long Polling

### 3.1 Принцип работы

Клиент отправляет запрос, сервер держит соединение открытым до появления обновлений или таймаута.

### 3.2 Реализация на сервере (FastAPI)

```python
from fastapi import FastAPI
import asyncio
from datetime import datetime, timedelta

app = FastAPI()
events = []

@app.get("/api/long-poll")
async def long_poll():
    timeout = 30
    start_time = datetime.now()
    
    while (datetime.now() - start_time).seconds < timeout:
        if events:
            return {"events": events.pop(0)}
        await asyncio.sleep(0.5)
    
    return {"events": []}

@app.post("/api/trigger")
def trigger_event(data: dict):
    events.append({"data": data, "timestamp": datetime.now()})
    return {"status": "ok"}
```

### 3.3 Реализация на клиенте

```javascript
async function longPoll() {
    try {
        const response = await fetch('/api/long-poll');
        const data = await response.json();
        if (data.events.length > 0) {
            handleEvents(data.events);
        }
    } catch (error) {
        console.error('Polling error:', error);
    }
    longPoll();
}

longPoll();
```

### 3.4 Преимущества

- Меньше запросов, чем short polling
- Быстрее получает обновления
- Работает через HTTP

### 3.5 Недостатки

- Держит соединения открытыми
- Сложнее масштабирование
- Таймауты требуют переподключения

---

## 4. WebSocket

### 4.1 Принцип работы

Постоянное двустороннее соединение между клиентом и сервером для обмена сообщениями в реальном времени.

### 4.2 Реализация на сервере (FastAPI)

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Message: {data}", websocket)
            await manager.broadcast(f"Client {client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### 4.3 Реализация на клиенте

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/123');

ws.onopen = () => {
    console.log('Connected');
    ws.send('Hello Server');
};

ws.onmessage = (event) => {
    console.log('Message:', event.data);
};

ws.onerror = (error) => {
    console.error('Error:', error);
};

ws.onclose = () => {
    console.log('Disconnected');
};
```

### 4.4 Обработка JSON

```python
from fastapi import WebSocket
import json

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            response = {"echo": data, "timestamp": datetime.now().isoformat()}
            await websocket.send_json(response)
    except WebSocketDisconnect:
        pass
```

### 4.5 Преимущества

- Двусторонняя связь
- Низкая задержка
- Эффективное использование ресурсов
- Поддержка бинарных данных

### 4.6 Недостатки

- Сложнее реализация
- Требует специальной инфраструктуры
- Проблемы с прокси и балансировщиками

---

## 5. Server-Sent Events (SSE)

### 5.1 Принцип работы

Односторонний поток данных от сервера к клиенту через HTTP.

### 5.2 Реализация на сервере (FastAPI)

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio
import json
from datetime import datetime

app = FastAPI()

async def event_generator():
    while True:
        data = {
            "timestamp": datetime.now().isoformat(),
            "message": "Update"
        }
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(1)

@app.get("/events")
async def stream_events():
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### 5.3 Реализация на клиенте

```javascript
const eventSource = new EventSource('/events');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Update:', data);
};

eventSource.onerror = (error) => {
    console.error('SSE Error:', error);
    eventSource.close();
};
```

### 5.4 События с типами

```python
async def event_generator():
    event_id = 0
    while True:
        event_id += 1
        yield f"id: {event_id}\n"
        yield f"event: message\n"
        yield f"data: {json.dumps({'message': 'Hello'})}\n\n"
        await asyncio.sleep(1)
```

```javascript
eventSource.addEventListener('message', (event) => {
    console.log('Message event:', event.data);
});
```

### 5.5 Преимущества

- Простая реализация
- Автоматическое переподключение
- Работает через HTTP
- Низкая задержка

### 5.6 Недостатки

- Только односторонняя связь
- Ограничения браузера (6 соединений)
- Текстовый формат

---

## 6. Сравнение техник

| Критерий | Short Polling | Long Polling | WebSocket | SSE |
|----------|---------------|--------------|-----------|-----|
| Направление | Двустороннее | Двустороннее | Двустороннее | Одностороннее |
| Задержка | Высокая | Средняя | Низкая | Низкая |
| Нагрузка | Высокая | Средняя | Низкая | Низкая |
| Сложность | Низкая | Средняя | Высокая | Низкая |
| Поддержка | Все браузеры | Все браузеры | Все браузеры | Все браузеры |
| Использование | Простые случаи | Умеренные обновления | Интерактивные приложения | Уведомления, ленты |

---

## 7. Выбор техники

### 7.1 Short Polling

- Простые уведомления
- Низкая частота обновлений
- Прототипирование

### 7.2 Long Polling

- Умеренная частота обновлений
- Когда WebSocket избыточен
- Совместимость с HTTP-инфраструктурой

### 7.3 WebSocket

- Интерактивные приложения (чат, игры)
- Высокая частота обновлений
- Двусторонняя связь критична
- Бинарные данные

### 7.4 SSE

- Уведомления в реальном времени
- Ленты новостей
- Мониторинг
- Когда нужна только передача от сервера

---

## 8. Гибридные подходы

### 8.1 WebSocket + HTTP fallback

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except:
        pass

@app.get("/api/poll")
async def http_fallback():
    return {"message": "Use WebSocket for real-time updates"}
```

### 8.2 SSE + HTTP для отправки

```python
@app.get("/events")
async def sse_stream():
    return StreamingResponse(event_generator())

@app.post("/send")
async def send_message(message: dict):
    await broadcast_message(message)
    return {"status": "sent"}
```

---

## 9. Best Practices

### 9.1 Обработка переподключений

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        print(f"Error: {e}")
        await manager.disconnect(websocket)
```

### 9.2 Heartbeat для WebSocket

```python
async def heartbeat(websocket: WebSocket):
    while True:
        await asyncio.sleep(30)
        try:
            await websocket.send_json({"type": "ping"})
        except:
            break

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    asyncio.create_task(heartbeat(websocket))
    # ... остальной код
```

### 9.3 Ограничение соединений

```python
MAX_CONNECTIONS = 100

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        if len(self.active_connections) >= MAX_CONNECTIONS:
            await websocket.close(code=1008, reason="Too many connections")
            return
        await websocket.accept()
        self.active_connections.append(websocket)
```

### 9.4 Аутентификация в WebSocket

```python
from fastapi import WebSocket, WebSocketException, status

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    if not token or not verify_token(token):
        await websocket.close(code=1008, reason="Unauthorized")
        return
    
    await websocket.accept()
    # ... остальной код
```
