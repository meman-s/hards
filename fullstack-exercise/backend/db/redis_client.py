import json
import redis
from typing import Generator


CACHE_KEY = "api:items:list"
CACHE_TTL = 60


class RedisDependencies:
    redis_client: redis.Redis

    @classmethod
    def init(cls, url: str) -> None:
        cls.redis_client = redis.Redis.from_url(url, decode_responses=True)

    @classmethod
    def close(cls) -> None:
        if cls.redis_client:
            cls.redis_client.close()
            cls.redis_client = None


def get_redis_client() -> Generator[redis.Redis, None, None]:
    yield RedisDependencies.redis_client


def get_cached_items(redis_client: redis.Redis) -> dict | None:
    data = redis_client.get(CACHE_KEY)
    if data is None:
        return None
    return json.loads(data)


def set_cached_items(
    data: dict,
    redis_client: redis.Redis,
    ttl: int = CACHE_TTL
) -> None:
    redis_client.set(CACHE_KEY, json.dumps(data), ex=ttl)


def invalidate_cached_items(redis_client: redis.Redis) -> None:
    redis_client.delete(CACHE_KEY)
