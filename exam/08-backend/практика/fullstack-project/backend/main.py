import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from db.mongo_client import MongoDependencies, insert_event, get_events_collection
from db.postgres_client import PostgresDependencies, create_item, get_items, get_postgres_conn
from db.redis_client import (
    RedisDependencies,
    get_cached_items,
    invalidate_cached_items,
    set_cached_items,
    get_redis_client
)


class RequestItem(BaseModel):
    title: str
    description: str | None


@asynccontextmanager
async def lifespan(_fastapi_app: FastAPI):
    postgres_url = os.environ.get("POSTGRES_URL")
    mongo_url = os.environ.get("MONGO_URL")
    redis_url = os.environ.get("REDIS_URL")

    PostgresDependencies.init(postgres_url)
    MongoDependencies.init(mongo_url)
    RedisDependencies.init(redis_url)

    yield

    PostgresDependencies.close()
    MongoDependencies.close()
    RedisDependencies.close()


app = FastAPI(lifespan=lifespan)


@app.get("/api/health")
def healt():
    return ("healthy")


@app.get("/api/items")
def read_items(
    conn=Depends(get_postgres_conn),
    events_coll=Depends(get_events_collection),
    redis_client=Depends(get_redis_client)
):
    cached = get_cached_items(redis_client)
    if cached is not None:
        return cached

    items = get_items(conn)
    res = {"items": [item.model_dump() for item in items]}
    set_cached_items(res, redis_client)
    insert_event("items_listed", {"count": len(items)}, events_coll)

    return res


@app.post("/api/items")
def create_items(
    body: RequestItem,
    conn=Depends(get_postgres_conn),
    events_coll=Depends(get_events_collection),
    redis_client=Depends(get_redis_client)
):
    item = create_item(body.title, conn, body.description)
    invalidate_cached_items(redis_client)

    insert_event(
        "item_created",
        item.model_dump(),
        events_coll
    )

    return item
