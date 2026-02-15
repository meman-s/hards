"""
Эталонная реализация для справки. Не импортируется в приложение.
Подглядывай сюда, когда будешь заполнять postgres.py, mongo.py, redis_cache.py, __init__.py и main.py.
"""


# =============================================================================
# postgres.py — скопируй в db/postgres.py
# =============================================================================
POSTGRES_PY = """
import psycopg2
from psycopg2.extras import RealDictCursor

conn = None


def init_postgres(url: str) -> None:
    global conn
    conn = psycopg2.connect(url)


def close_postgres() -> None:
    global conn
    if conn:
        conn.close()
        conn = None


def get_items() -> list[dict]:
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, title, description FROM items ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    return [
        {"id": r["id"], "title": r["title"], "description": r["description"] or ""}
        for r in rows
    ]


def create_item(title: str, description: str | None) -> dict:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO items (title, description) VALUES (%s, %s) RETURNING id, title, description",
        (title, description or ""),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    return {"id": row[0], "title": row[1], "description": row[2] or ""}
"""


# =============================================================================
# mongo.py — скопируй в db/mongo.py
# ВАЖНО: используй простые функции, НЕ классы и НЕ dataclass!
# =============================================================================
MONGO_PY = """
from datetime import datetime, timezone
import pymongo

client = None
events_coll = None
DB_NAME = "practicedb"


def init_mongo(url: str) -> None:
    global client, events_coll
    client = pymongo.MongoClient(url)
    events_coll = client[DB_NAME]["events"]
    events_coll.create_index("at")
    events_coll.create_index("type")


def close_mongo() -> None:
    global client, events_coll
    if client:
        client.close()
        client = None
    events_coll = None


def insert_event(event_type: str, payload: dict) -> None:
    doc = {
        "type": event_type,
        "payload": payload,
        "at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    events_coll.insert_one(doc)
"""


# =============================================================================
# redis_cache.py — скопируй в db/redis_cache.py
# =============================================================================
REDIS_CACHE_PY = """
import json
import redis

redis_client = None
CACHE_KEY = "api:items:list"
CACHE_TTL = 60


def init_redis(url: str) -> None:
    global redis_client
    redis_client = redis.Redis.from_url(url, decode_responses=True)


def close_redis() -> None:
    global redis_client
    if redis_client:
        redis_client.close()
        redis_client = None


def get_cached_items() -> dict | None:
    if redis_client is None:
        return None
    data = redis_client.get(CACHE_KEY)
    if data is None:
        return None
    return json.loads(data)


def set_cached_items(data: dict, ttl: int = CACHE_TTL) -> None:
    if redis_client is None:
        return
    redis_client.set(CACHE_KEY, json.dumps(data), ex=ttl)


def invalidate_items_cache() -> None:
    if redis_client is None:
        return
    redis_client.delete(CACHE_KEY)
"""


# =============================================================================
# __init__.py — скопируй в db/__init__.py
# =============================================================================
INIT_PY = """
import os

from . import postgres
from . import mongo
from . import redis_cache


def init_db() -> None:
    postgres_url = os.environ.get("POSTGRES_URL")
    mongo_url = os.environ.get("MONGO_URL")
    redis_url = os.environ.get("REDIS_URL")
    if postgres_url:
        postgres.init_postgres(postgres_url)
    if mongo_url:
        mongo.init_mongo(mongo_url)
    if redis_url:
        redis_cache.init_redis(redis_url)


def close_db() -> None:
    postgres.close_postgres()
    mongo.close_mongo()
    redis_cache.close_redis()
"""


# =============================================================================
# main.py — только lifespan и эндпоинты items (остальное оставь как есть)
# =============================================================================
MAIN_PY_SNIPPETS = """
lifespan:
  init_db()
  yield
  close_db()

GET /api/items:
  cached = redis_cache.get_cached_items()
  if cached is not None: return cached
  items = postgres.get_items()
  result = {"items": items}
  redis_cache.set_cached_items(result)
  if mongo.events_coll: mongo.insert_event("items_listed", {"count": len(items)})
  return result

POST /api/items:
  item = postgres.create_item(body.title, body.description)
  redis_cache.invalidate_items_cache()
  if mongo.events_coll:
    mongo.insert_event("item_created", {"id": item["id"], "title": item["title"], "description": item["description"]})
  return item
"""


# =============================================================================
# АЛЬТЕРНАТИВНЫЙ ПОДХОД: Dependency Injection через FastAPI
# Используй этот подход, если хочешь более "правильную" архитектуру
# =============================================================================
MONGO_PY_DI = """
from datetime import datetime, timezone
from typing import Generator
import pymongo
from fastapi import Depends

DB_NAME = "practicedb"


class MongoDependencies:
    client: pymongo.MongoClient | None = None
    events_coll: pymongo.collection.Collection | None = None

    @classmethod
    def init(cls, url: str) -> None:
        cls.client = pymongo.MongoClient(url)
        cls.events_coll = cls.client[DB_NAME]["events"]
        cls.events_coll.create_index("at")
        cls.events_coll.create_index("type")

    @classmethod
    def close(cls) -> None:
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.events_coll = None


def get_events_collection() -> Generator[pymongo.collection.Collection | None, None, None]:
    yield MongoDependencies.events_coll


def insert_event(
    event_type: str,
    payload: dict,
    events_coll: pymongo.collection.Collection | None = Depends(get_events_collection)
) -> None:
    if events_coll is None:
        return
    doc = {
        "type": event_type,
        "payload": payload,
        "at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    events_coll.insert_one(doc)
"""


POSTGRES_PY_DI = """
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Generator
from fastapi import Depends


class PostgresDependencies:
    conn: psycopg2.extensions.connection | None = None

    @classmethod
    def init(cls, url: str) -> None:
        cls.conn = psycopg2.connect(url)

    @classmethod
    def close(cls) -> None:
        if cls.conn:
            cls.conn.close()
            cls.conn = None


def get_postgres_conn() -> Generator[psycopg2.extensions.connection, None, None]:
    if PostgresDependencies.conn is None:
        raise RuntimeError("Postgres connection not initialized")
    yield PostgresDependencies.conn


def get_items(conn: psycopg2.extensions.connection = Depends(get_postgres_conn)) -> list[dict]:
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, title, description FROM items ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    return [
        {"id": r["id"], "title": r["title"], "description": r["description"] or ""}
        for r in rows
    ]


def create_item(
    title: str,
    description: str | None,
    conn: psycopg2.extensions.connection = Depends(get_postgres_conn)
) -> dict:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO items (title, description) VALUES (%s, %s) RETURNING id, title, description",
        (title, description or ""),
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    return {"id": row[0], "title": row[1], "description": row[2] or ""}
"""


REDIS_CACHE_PY_DI = """
import json
import redis
from typing import Generator
from fastapi import Depends

CACHE_KEY = "api:items:list"
CACHE_TTL = 60


class RedisDependencies:
    redis_client: redis.Redis | None = None

    @classmethod
    def init(cls, url: str) -> None:
        cls.redis_client = redis.Redis.from_url(url, decode_responses=True)

    @classmethod
    def close(cls) -> None:
        if cls.redis_client:
            cls.redis_client.close()
            cls.redis_client = None


def get_redis_client() -> Generator[redis.Redis | None, None, None]:
    yield RedisDependencies.redis_client


def get_cached_items(redis_client: redis.Redis | None) -> dict | None:
    if redis_client is None:
        return None
    data = redis_client.get(CACHE_KEY)
    if data is None:
        return None
    return json.loads(data)


def set_cached_items(
    data: dict,
    redis_client: redis.Redis | None,
    ttl: int = CACHE_TTL
) -> None:
    if redis_client is None:
        return
    redis_client.set(CACHE_KEY, json.dumps(data), ex=ttl)


def invalidate_items_cache(redis_client: redis.Redis | None) -> None:
    if redis_client is None:
        return
    redis_client.delete(CACHE_KEY)
"""


MAIN_PY_DI_SNIPPETS = """
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
import redis
from db.postgres_di import PostgresDependencies, get_items, create_item
from db.mongo_di import MongoDependencies, insert_event, get_events_collection
from db.redis_cache_di import (
    RedisDependencies,
    get_redis_client,
    get_cached_items,
    set_cached_items,
    invalidate_items_cache
)
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    postgres_url = os.environ.get("POSTGRES_URL")
    mongo_url = os.environ.get("MONGO_URL")
    redis_url = os.environ.get("REDIS_URL")

    if postgres_url:
        PostgresDependencies.init(postgres_url)
    if mongo_url:
        MongoDependencies.init(mongo_url)
    if redis_url:
        RedisDependencies.init(redis_url)

    yield

    PostgresDependencies.close()
    MongoDependencies.close()
    RedisDependencies.close()


app = FastAPI(lifespan=lifespan)


@app.get("/api/items")
def read_items(
    items_func = Depends(get_items),
    events_coll = Depends(get_events_collection),
    redis_client: redis.Redis | None = Depends(get_redis_client)
):
    cached = get_cached_items(redis_client)
    if cached is not None:
        return cached

    items = items_func()
    result = {"items": items}
    set_cached_items(result, redis_client)

    if events_coll:
        insert_event("items_listed", {"count": len(items)}, events_coll)

    return result


@app.post("/api/items")
def create_item_endpoint(
    body: dict,
    create_func = Depends(create_item),
    events_coll = Depends(get_events_collection),
    redis_client: redis.Redis | None = Depends(get_redis_client)
):
    item = create_func(body["title"], body.get("description"))
    invalidate_items_cache(redis_client)

    if events_coll:
        insert_event("item_created", {
            "id": item["id"],
            "title": item["title"],
            "description": item["description"]
        }, events_coll)

    return item
"""


# =============================================================================
# КОГДА ЧТО ИСПОЛЬЗОВАТЬ:
# =============================================================================
APPROACH_COMPARISON = """
ПОДХОД 1 (глобальные переменные) - текущий пример:
✅ Проще для понимания
✅ Меньше кода
✅ Подходит для учебных проектов
❌ Глобальные переменные сложнее тестировать
❌ Менее явная зависимость в сигнатурах функций

ПОДХОД 2 (dependency injection) - альтернативный:
✅ Более явные зависимости (видно в сигнатуре функции)
✅ Легче тестировать (можно подменить зависимости)
✅ Соответствует best practices FastAPI
✅ Более гибкий для расширения
❌ Больше кода
❌ Сложнее для новичков

ВАЖНО: В обоих подходах подключения создаются ОДИН РАЗ при старте (в lifespan),
а не в каждом запросе! Dependency injection здесь используется только для передачи
уже созданных подключений в функции, а не для создания новых.

НЕ ДЕЛАЙ ТАК (создание подключения в каждом запросе):
def get_db():
    conn = psycopg2.connect(url)  # ❌ Плохо! Новое подключение каждый раз
    yield conn
    conn.close()
"""
