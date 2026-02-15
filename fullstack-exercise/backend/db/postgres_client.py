from typing import Generator
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel


class Item(BaseModel):
    id: int
    title: str
    description: str | None = None


class PostgresDependencies:
    conn: psycopg2.extensions.connection

    @classmethod
    def init(cls, url: str) -> None:
        cls.conn = psycopg2.connect(url)

    @classmethod
    def close(cls):
        if cls.conn:
            cls.conn.close()
            cls.conn = None


def get_postgres_conn() -> Generator[psycopg2.extensions.connection, None, None]:
    yield PostgresDependencies.conn


def get_items(
    conn: psycopg2.extensions.connection
) -> list[Item]:
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM items ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    return [Item(**dict(row)) for row in rows]


def create_item(
    title: str,
    conn: psycopg2.extensions.connection,
    description: str | None = ""
) -> Item:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO items (title, description) VALUES (%s, %s) RETURNING id, title, description",
        (title, description)
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    return Item(id=row[0], title=row[1], description=row[2] or None)
