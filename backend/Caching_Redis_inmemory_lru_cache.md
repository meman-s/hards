# Кеширование: Redis и In-memory кэши

## 1. Зачем нужно

**Кеширование** — техника хранения часто используемых данных в быстродоступном хранилище для ускорения доступа.

**Проблемы без кеширования:**
- Медленный доступ к данным (БД, внешние API)
- Высокая нагрузка на БД
- Медленная работа приложения
- Дорогие вычисления выполняются повторно

**Кеширование необходимо для:**

- Ускорения доступа к данным
- Снижения нагрузки на БД
- Улучшения производительности приложения
- Хранения сессий и временных данных
- Распределённого кеширования в микросервисах

**Типы данных для кеширования:**
- Результаты запросов к БД
- Результаты вычислений
- Сессии пользователей
- Статические данные
- Ответы внешних API

---

## 2. In-memory кэширование

**In-memory кеш** — хранение данных в оперативной памяти процесса.

**Преимущества:**
- Очень быстрый доступ
- Простота использования
- Не требует внешних зависимостей

**Недостатки:**
- Ограничен размером памяти
- Данные теряются при перезапуске
- Не разделяется между процессами/серверами

### 2.1 @lru_cache (functools)

**LRU (Least Recently Used)** — алгоритм вытеснения наименее используемых элементов.

**Особенности:**
- Автоматическое управление размером
- Вытеснение старых записей
- Кеширование результатов функций

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(n: int) -> int:
    return n * n

result = expensive_function(5)  # Вычисляется
result = expensive_function(5)  # Берётся из кеша
```

**Параметры:**
- `maxsize` — максимальное количество элементов
- `typed` — раздельное кеширование для разных типов

### 2.2 @cache (Python 3.9+)

**@cache** — неограниченный кеш (без maxsize).

**Использование:**
- Для функций с небольшим количеством уникальных аргументов
- Рекурсивные функции (например, Fibonacci)

```python
from functools import cache

@cache
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)
```

### 2.3 Кэширование с TTL

**TTL (Time To Live)** — время жизни записи в кеше.

**Зачем нужно:**
- Автоматическая инвалидация устаревших данных
- Контроль актуальности данных
- Освобождение памяти

```python
from datetime import datetime, timedelta

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
                else:
                    del cache_data[cache_key]
            
            result = func(*args, **kwargs)
            cache_data[cache_key] = result
            cache_timestamps[cache_key] = datetime.now()
            return result
        
        return wrapper
    return decorator
```

### 2.4 cachetools

**Библиотека `cachetools`** — продвинутые алгоритмы кеширования.

**Типы кешей:**
- `TTLCache` — кеш с TTL
- `LRUCache` — LRU алгоритм
- `LFUCache` — Least Frequently Used
- `RRCache` — Random Replacement

```python
from cachetools import TTLCache, LRUCache

ttl_cache = TTLCache(maxsize=100, ttl=300)
lru_cache = LRUCache(maxsize=128)

def get_cached_data(key: str):
    if key in ttl_cache:
        return ttl_cache[key]
    
    data = fetch_from_db(key)
    ttl_cache[key] = data
    return data
```

**Алгоритмы вытеснения:**
- **LRU** — вытесняет наименее недавно использованные
- **LFU** — вытесняет наименее часто используемые
- **RR** — случайное вытеснение

---

## 3. Redis кеширование

**Redis** — in-memory хранилище данных (key-value store).

**Преимущества:**
- Распределённое кеширование
- Персистентность (опционально)
- Богатый набор структур данных
- Высокая производительность
- Поддержка кластеризации

**Использование:**
- Кеширование между серверами
- Сессии пользователей
- Очереди задач
- Pub/Sub

### 3.1 Подключение к Redis

**Библиотека:** `redis` (python-redis)

```python
import redis

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True  # Автоматическая декодировка строк
)
```

**Параметры подключения:**
- `host`, `port` — адрес сервера
- `db` — номер базы данных (0-15)
- `password` — пароль (если требуется)
- `decode_responses` — автоматическое декодирование

### 3.2 Базовые операции

**Основные команды:**
- `set(key, value)` — установка значения
- `get(key)` — получение значения
- `setex(key, ttl, value)` — установка с TTL
- `delete(key)` — удаление
- `exists(key)` — проверка существования
- `expire(key, ttl)` — установка TTL

```python
import json

def get_cached_user(user_id: int):
    cache_key = f"user:{user_id}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    
    user_data = fetch_user_from_db(user_id)
    redis_client.setex(
        cache_key,
        300,  # TTL в секундах
        json.dumps(user_data)
    )
    return user_data
```

### 3.3 Сериализация данных

**Форматы:**
- **JSON** — для простых структур (dict, list)
- **Pickle** — для сложных объектов Python
- **MessagePack** — компактный бинарный формат

**JSON (рекомендуется):**
```python
import json

redis_client.setex(key, ttl, json.dumps(data))
data = json.loads(redis_client.get(key))
```

**Pickle:**
```python
import pickle

redis_client.setex(key, ttl, pickle.dumps(obj))
obj = pickle.loads(redis_client.get(key))
```

### 3.4 Структуры данных Redis

**Типы данных:**
- **String** — строки и числа
- **List** — списки
- **Set** — множества
- **Hash** — словари
- **Sorted Set** — отсортированные множества

**Примеры:**
```python
# Список
redis_client.lpush('queue', 'item1')
redis_client.rpop('queue')

# Множество
redis_client.sadd('tags', 'python', 'redis')
redis_client.smembers('tags')

# Hash
redis_client.hset('user:1', 'name', 'John')
redis_client.hgetall('user:1')
```

---

## 4. Паттерны кеширования

### 4.1 Cache-Aside (Lazy Loading)

**Принцип:** Приложение само управляет кешем.

**Алгоритм:**
1. Проверить кеш
2. Если нет — загрузить из БД
3. Сохранить в кеш
4. Вернуть данные

**Преимущества:**
- Простота реализации
- Гибкость
- Кеш не блокирует БД при сбое

**Недостатки:**
- Cache miss требует двух операций
- Возможна race condition

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

**Принцип:** Запись идёт одновременно в кеш и БД.

**Алгоритм:**
1. Записать в БД
2. Записать в кеш
3. Вернуть результат

**Преимущества:**
- Консистентность данных
- Всегда актуальные данные в кеше

**Недостатки:**
- Медленнее (две записи)
- Лишние записи в кеш при редком чтении

```python
def create_user(user_data: dict):
    user = save_user_to_db(user_data)
    
    cache_key = f"user:{user['id']}"
    redis_client.setex(cache_key, 300, json.dumps(user))
    
    return user
```

### 4.3 Write-Back (Write-Behind)

**Принцип:** Сначала запись в кеш, затем асинхронно в БД.

**Алгоритм:**
1. Записать в кеш
2. Добавить в очередь на запись в БД
3. Асинхронно записать в БД

**Преимущества:**
- Быстрая запись
- Снижение нагрузки на БД
- Batch записи

**Недостатки:**
- Риск потери данных при сбое
- Сложность реализации
- Возможна несогласованность

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

### 4.4 Refresh-Ahead

**Принцип:** Предзагрузка данных до истечения TTL.

**Алгоритм:**
1. Проверить время до истечения TTL
2. Если близко — обновить в фоне
3. Вернуть текущие данные

**Преимущества:**
- Всегда актуальные данные
- Нет задержек на обновление

---

## 5. Инвалидация кеша

**Инвалидация** — удаление устаревших данных из кеша.

### 5.1 Простая инвалидация

**Методы:**
- Удаление по ключу
- Удаление при обновлении данных
- Ручная инвалидация

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

**Использование:**
- Удаление группы связанных ключей
- Инвалидация по префиксу
- Очистка категорий данных

```python
def invalidate_cache_pattern(pattern: str):
    keys = redis_client.keys(pattern)  # Медленно на больших БД!
    if keys:
        redis_client.delete(*keys)

# Лучше использовать SCAN для больших БД
def invalidate_pattern_safe(pattern: str):
    cursor = 0
    while True:
        cursor, keys = redis_client.scan(cursor, match=pattern, count=100)
        if keys:
            redis_client.delete(*keys)
        if cursor == 0:
            break
```

### 5.3 TTL-based инвалидация

**Автоматическая инвалидация:**
- Установка TTL при записи
- Автоматическое удаление при истечении
- Не требует ручного управления

```python
def cache_with_auto_invalidate(key: str, value: any, ttl: int = 300):
    redis_client.setex(key, ttl, json.dumps(value))
```

### 5.4 Версионирование ключей

**Принцип:** Изменение версии инвалидирует все старые ключи.

```python
CACHE_VERSION = "v1"

def get_versioned_key(key: str) -> str:
    return f"{CACHE_VERSION}:{key}"

def invalidate_all():
    global CACHE_VERSION
    CACHE_VERSION = f"v{int(CACHE_VERSION[1:]) + 1}"
```

---

## 6. Распределённое кеширование

**Распределённый кеш** — кеш, разделяемый между несколькими серверами.

### 6.1 Redis Cluster

**Кластеризация Redis:**
- Шардирование данных
- Высокая доступность
- Масштабируемость

```python
from redis.cluster import RedisCluster

redis_cluster = RedisCluster(
    startup_nodes=[
        {"host": "127.0.0.1", "port": "7000"},
        {"host": "127.0.0.1", "port": "7001"},
    ],
    decode_responses=True
)
```

### 6.2 Кеширование сессий

**Использование Redis для сессий:**
- Хранение сессий между серверами
- TTL для автоматического истечения
- Быстрый доступ

```python
import secrets
import json
from datetime import datetime

def create_session(user_id: int) -> str:
    session_id = secrets.token_urlsafe(32)
    session_data = {
        "user_id": user_id,
        "created_at": datetime.now().isoformat()
    }
    redis_client.setex(
        f"session:{session_id}",
        3600,  # 1 час
        json.dumps(session_data)
    )
    return session_id

def get_session(session_id: str):
    cached = redis_client.get(f"session:{session_id}")
    if cached:
        return json.loads(cached)
    return None
```

### 6.3 Репликация

**Master-Slave репликация:**
- Чтение с реплик
- Запись в master
- Повышение доступности

---

## 7. Оптимизация и производительность

### 7.1 Пайплайнинг

**Pipeline** — группировка команд для уменьшения round-trips.

```python
pipe = redis_client.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.get('key1')
results = pipe.execute()
```

### 7.2 Компрессия данных

**Сжатие больших значений:**
- Уменьшение использования памяти
- Медленнее запись/чтение
- Использовать для больших данных

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

### 7.3 Мониторинг кеша

**Метрики:**
- Hit rate (процент попаданий)
- Miss rate (процент промахов)
- Использование памяти
- Количество ключей

```python
def get_cache_stats():
    info = redis_client.info()
    hits = info.get("keyspace_hits", 0)
    misses = info.get("keyspace_misses", 0)
    total = hits + misses
    
    return {
        "used_memory": info.get("used_memory_human"),
        "keyspace_hits": hits,
        "keyspace_misses": misses,
        "hit_rate": hits / total if total > 0 else 0
    }
```

---

## 8. Best Practices

### 8.1 Выбор стратегии кеширования

**Рекомендации:**
- **Часто читаемые, редко изменяемые** — Cache-Aside
- **Критичные данные** — Write-Through
- **Высокая нагрузка на запись** — Write-Back
- **Нужна актуальность** — Refresh-Ahead

### 8.2 Размер кеша

**Управление размером:**
- Ограничение максимального размера
- Использование LRU/LFU для вытеснения
- Мониторинг использования памяти

```python
MAX_CACHE_SIZE = 1000

def manage_cache_size():
    if redis_client.dbsize() > MAX_CACHE_SIZE:
        # Очистка старых ключей или использование LRU
        pass
```

### 8.3 Ключи кеша

**Правила именования:**
- Использовать префиксы (`user:`, `session:`)
- Включать версию при необходимости
- Избегать специальных символов
- Делать ключи читаемыми

**Примеры:**
- `user:123:profile`
- `session:abc123`
- `cache:v1:data:key`

### 8.4 TTL

**Выбор TTL:**
- Короткий TTL для часто изменяемых данных
- Длинный TTL для статических данных
- Адаптивный TTL в зависимости от частоты обновления

### 8.5 Обработка ошибок

**Стратегии:**
- Graceful degradation — при сбое Redis работать без кеша
- Fallback на БД
- Логирование ошибок
- Retry для временных сбоев

```python
def safe_cache_get(key: str):
    try:
        return redis_client.get(key)
    except redis.ConnectionError:
        # Fallback на БД
        return None
    except Exception as e:
        logger.error(f"Cache error: {e}")
        return None
```

### 8.6 Избегание проблем

**Типичные ошибки:**
- Кеширование слишком большого объёма данных
- Отсутствие инвалидации при обновлении
- Использование `KEYS` на больших БД (использовать `SCAN`)
- Кеширование чувствительных данных без шифрования
- Отсутствие мониторинга

---

## 9. Сравнение подходов

### 9.1 In-memory vs Redis

| Критерий | In-memory | Redis |
|---------|-----------|-------|
| Скорость | Очень высокая | Высокая |
| Распределение | Нет | Да |
| Персистентность | Нет | Опционально |
| Сложность | Просто | Средне |
| Масштабируемость | Ограничена | Высокая |

### 9.2 Когда использовать

**In-memory:**
- Односерверное приложение
- Быстрые вычисления
- Небольшой объём данных
- Временные данные

**Redis:**
- Микросервисы
- Несколько серверов
- Большой объём данных
- Сессии пользователей
- Очереди задач

---

## 10. Полезные библиотеки

**Python:**
- `redis` — клиент для Redis
- `cachetools` — продвинутые алгоритмы кеширования
- `functools.lru_cache` — встроенный LRU кеш
- `diskcache` — кеш на диске

**Инструменты:**
- `redis-cli` — командная строка Redis
- `redis-benchmark` — тестирование производительности
- `redis-stat` — мониторинг Redis
