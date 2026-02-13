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
    global client
    if client:
        client.close()
        client = None
    global events_coll
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
  if mongo.events_coll: mongo.insert_event("item_created", {"id": item["id"], "title": item["title"], "description": item["description"]})
  return item
"""
