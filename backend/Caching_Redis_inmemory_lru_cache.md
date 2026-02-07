# Кеширование: Redis и In-memory кэши

## 1. Зачем нужно

Кеширование необходимо для:

- Ускорения доступа к данным
- Снижения нагрузки на БД
- Улучшения производительности приложения
- Хранения сессий и временных данных
- Распределённого кеширования в микросервисах

---

## 2. In-memory кэширование

### 2.1 @lru_cache (functools)

```python
from functools import lru_cache
from fastapi import FastAPI

app = FastAPI()

@lru_cache(maxsize=128)
def expensive_function(n: int) -> int:
    print(f"Computing for {n}")
    return n * n

@app.get("/compute/{n}")
def compute(n: int):
    result = expensive_function(n)
    return {"result": result}
```

### 2.2 @cache (Python 3.9+)

```python
from functools import cache

@cache
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

### 2.3 Кэширование с TTL

```python
from functools import lru_cache
from datetime import datetime, timedelta
from typing import Optional

cache_data = {}
cache_timestamps = {}

def cached_with_ttl(ttl_seconds: int = 300):
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = str(args) + str(kwargs)
            
            if cache_key in cache_data:
                timestamp = cache_timestamps[cache_key]
                if datetime.now() - timestamp < timedelta(seconds=ttl_seconds):
                    return cache_data[cache_key]
            
            result = func(*args, **kwargs)
            cache_data[cache_key] = result
            cache_timestamps[cache_key] = datetime.now()
            return result
        
        return wrapper
    return decorator

@cached_with_ttl(ttl_seconds=60)
def get_user_data(user_id: int):
    return {"id": user_id, "name": "John"}
```

### 2.4 cachetools

```python
from cachetools import TTLCache, LRUCache
from fastapi import FastAPI

app = FastAPI()

ttl_cache = TTLCache(maxsize=100, ttl=300)
lru_cache = LRUCache(maxsize=128)

def get_cached_data(key: str):
    if key in ttl_cache:
        return ttl_cache[key]
    
    data = fetch_from_db(key)
    ttl_cache[key] = data
    return data

@app.get("/data/{key}")
def get_data(key: str):
    return get_cached_data(key)
```

---

## 3. Redis кеширование

### 3.1 Подключение к Redis

```python
import redis
from fastapi import FastAPI

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

app = FastAPI()
```

### 3.2 Базовое кеширование

```python
import json
from fastapi import FastAPI
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_user(user_id: int):
    cache_key = f"user:{user_id}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    user_data = fetch_user_from_db(user_id)
    redis_client.setex(
        cache_key,
        300,
        json.dumps(user_data)
    )
    return user_data

@app.get("/users/{user_id}")
def get_user(user_id: int):
    return get_cached_user(user_id)
```

### 3.3 Кеширование с сериализацией

```python
import pickle
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_set(key: str, value: any, ttl: int = 300):
    serialized = pickle.dumps(value)
    redis_client.setex(key, ttl, serialized)

def cache_get(key: str):
    cached = redis_client.get(key)
    if cached:
        return pickle.loads(cached)
    return None
```

### 3.4 Кеширование списков

```python
import json
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_list(key: str, items: list, ttl: int = 300):
    redis_client.setex(key, ttl, json.dumps(items))

def get_cached_list(key: str):
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None
```

---

## 4. Паттерны кеширования

### 4.1 Cache-Aside (Lazy Loading)

```python
def get_user(user_id: int):
    cache_key = f"user:{user_id}"
    
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    user = fetch_user_from_db(user_id)
    redis_client.setex(cache_key, 300, json.dumps(user))
    return user
```

### 4.2 Write-Through

```python
def create_user(user_data: dict):
    user = save_user_to_db(user_data)
    
    cache_key = f"user:{user['id']}"
    redis_client.setex(cache_key, 300, json.dumps(user))
    
    return user
```

### 4.3 Write-Back (Write-Behind)

```python
write_queue = []

def update_user(user_id: int, user_data: dict):
    cache_key = f"user:{user_id}"
    
    updated_user = {**get_user(user_id), **user_data}
    redis_client.setex(cache_key, 300, json.dumps(updated_user))
    
    write_queue.append((user_id, user_data))
    
    return updated_user

def flush_cache():
    while write_queue:
        user_id, user_data = write_queue.pop(0)
        save_user_to_db(user_id, user_data)
```

### 4.4 Cache-Aside с обновлением

```python
def update_user(user_id: int, user_data: dict):
    user = update_user_in_db(user_id, user_data)
    
    cache_key = f"user:{user_id}"
    redis_client.setex(cache_key, 300, json.dumps(user))
    
    return user

def delete_user(user_id: int):
    delete_user_from_db(user_id)
    
    cache_key = f"user:{user_id}"
    redis_client.delete(cache_key)
```

---

## 5. Инвалидация кеша

### 5.1 Простая инвалидация

```python
def invalidate_user_cache(user_id: int):
    cache_key = f"user:{user_id}"
    redis_client.delete(cache_key)

def update_user(user_id: int, user_data: dict):
    user = update_user_in_db(user_id, user_data)
    invalidate_user_cache(user_id)
    return user
```

### 5.2 Инвалидация по паттерну

```python
def invalidate_cache_pattern(pattern: str):
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)

def update_user(user_id: int, user_data: dict):
    user = update_user_in_db(user_id, user_data)
    invalidate_cache_pattern(f"user:{user_id}*")
    return user
```

### 5.3 TTL-based инвалидация

```python
def cache_with_auto_invalidate(key: str, value: any, ttl: int = 300):
    redis_client.setex(key, ttl, json.dumps(value))
```

---

## 6. Распределённое кеширование

### 6.1 Redis Cluster

```python
from redis.cluster import RedisCluster

redis_cluster = RedisCluster(
    startup_nodes=[
        {"host": "127.0.0.1", "port": "7000"},
        {"host": "127.0.0.1", "port": "7001"},
        {"host": "127.0.0.1", "port": "7002"},
    ],
    decode_responses=True
)
```

### 6.2 Кеширование сессий

```python
import secrets
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def create_session(user_id: int) -> str:
    session_id = secrets.token_urlsafe(32)
    session_data = {"user_id": user_id, "created_at": datetime.now().isoformat()}
    redis_client.setex(f"session:{session_id}", 3600, json.dumps(session_data))
    return session_id

def get_session(session_id: str):
    cached = redis_client.get(f"session:{session_id}")
    if cached:
        return json.loads(cached)
    return None
```

---

## 7. Интеграция с FastAPI

### 7.1 Dependency для кеша

```python
from fastapi import FastAPI, Depends
import redis

def get_redis():
    return redis.Redis(host='localhost', port=6379, db=0)

@app.get("/users/{user_id}")
def get_user(user_id: int, cache: redis.Redis = Depends(get_redis)):
    cache_key = f"user:{user_id}"
    cached = cache.get(cache_key)
    
    if cached:
        return json.loads(cached)
    
    user = fetch_user_from_db(user_id)
    cache.setex(cache_key, 300, json.dumps(user))
    return user
```

### 7.2 Middleware для кеширования

```python
from fastapi import FastAPI, Request
import hashlib
import json

@app.middleware("http")
async def cache_middleware(request: Request, call_next):
    if request.method != "GET":
        response = await call_next(request)
        return response
    
    cache_key = hashlib.md5(
        f"{request.url.path}{str(request.query_params)}".encode()
    ).hexdigest()
    
    cached = redis_client.get(cache_key)
    if cached:
        from fastapi.responses import Response
        return Response(
            content=cached,
            media_type="application/json"
        )
    
    response = await call_next(request)
    
    if response.status_code == 200:
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        redis_client.setex(cache_key, 60, body)
        return Response(content=body, media_type="application/json")
    
    return response
```

---

## 8. Best Practices

### 8.1 Выбор стратегии кеширования

- **Часто читаемые, редко изменяемые данные** — Cache-Aside
- **Критичные данные** — Write-Through
- **Высокая нагрузка на запись** — Write-Back

### 8.2 Размер кеша

```python
MAX_CACHE_SIZE = 1000

def manage_cache_size():
    if redis_client.dbsize() > MAX_CACHE_SIZE:
        redis_client.flushdb()
```

### 8.3 Мониторинг кеша

```python
def get_cache_stats():
    info = redis_client.info()
    return {
        "used_memory": info.get("used_memory_human"),
        "keyspace_hits": info.get("keyspace_hits"),
        "keyspace_misses": info.get("keyspace_misses"),
        "hit_rate": info.get("keyspace_hits") / (info.get("keyspace_hits") + info.get("keyspace_misses"))
    }
```

### 8.4 Обработка ошибок

```python
from fastapi import FastAPI, HTTPException
import redis

def safe_cache_get(key: str):
    try:
        return redis_client.get(key)
    except redis.ConnectionError:
        return None
    except Exception as e:
        logger.error(f"Cache error: {e}")
        return None
```

---

## 9. Продвинутые техники

### 9.1 Кеширование с версионированием

```python
CACHE_VERSION = "v1"

def get_versioned_key(key: str) -> str:
    return f"{CACHE_VERSION}:{key}"

def invalidate_version():
    global CACHE_VERSION
    CACHE_VERSION = f"v{int(CACHE_VERSION[1:]) + 1}"
```

### 9.2 Кеширование с компрессией

```python
import gzip
import json

def cache_set_compressed(key: str, value: any, ttl: int = 300):
    serialized = json.dumps(value).encode()
    compressed = gzip.compress(serialized)
    redis_client.setex(key, ttl, compressed)

def cache_get_compressed(key: str):
    cached = redis_client.get(key)
    if cached:
        decompressed = gzip.decompress(cached)
        return json.loads(decompressed)
    return None
```

### 9.3 Кеширование с приоритетами

```python
def cache_set_priority(key: str, value: any, priority: int = 5, ttl: int = 300):
    cache_data = {
        "value": value,
        "priority": priority,
        "timestamp": datetime.now().isoformat()
    }
    redis_client.setex(key, ttl, json.dumps(cache_data))
```
