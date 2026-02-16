from datetime import datetime, timezone
import pymongo
from fastapi import Depends
from typing import Generator


DB_NAME = "practicedb"


class MongoDependencies:
    client: pymongo.MongoClient
    events_coll: pymongo.collection.Collection

    @classmethod
    def init(cls, url: str) -> None:
        client = pymongo.MongoClient(url)
        cls.client = client
        cls.events_coll = client[DB_NAME]["events"]
        cls.events_coll.create_index("at")
        cls.events_coll.create_index("type")

    @classmethod
    def close(cls) -> None:
        if cls.client:
            cls.client.close()
            cls.client = None
            cls.events_coll = None


def get_events_collection() -> Generator[pymongo.collection.Collection, None, None]:
    yield MongoDependencies.events_coll


def insert_event(
    event_type: str,
    payload: dict,
    events_coll: pymongo.collection.Collection = Depends(get_events_collection)
) -> None:
    doc = {
        "type": event_type,
        "payload": payload,
        "at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }
    events_coll.insert_one(doc)
