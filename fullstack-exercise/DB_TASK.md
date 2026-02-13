# Задание: интеграция БД без ORM

Ниже — что добавить, куда и как создавать таблицы/коллекции. Работа только с драйверами (сырой SQL, клиенты Mongo/Redis). Схемы и логика — в **DB_SPEC.md**.

---

## 1. Зависимости backend

В **backend/requirements.txt** добавить:

```
psycopg2-binary>=2.9.0
pymongo>=4.0.0
redis>=5.0.0
```

- **psycopg2-binary** — PostgreSQL, выполнение сырого SQL (cursor.execute, fetchall).
- **pymongo** — MongoDB, вставка документов в коллекцию.
- **redis** — Redis, get/set/delete/expire.

Пересобрать образ: `docker compose build backend`.

---

## 2. Переменные окружения

В **docker-compose.yml** у сервиса `backend` заполнить `environment`:

```yaml
environment:
  - POSTGRES_URL=postgresql://stepan:123123@postgres:5432/practicedb
  - MONGO_URL=mongodb://mongo:27017
  - REDIS_URL=redis://redis:6379/0
```

Хост — имя сервиса из compose (`postgres`, `mongo`, `redis`), порты — стандартные. Пароль и БД — как в сервисе `postgres`.

---

## 3. PostgreSQL: создание таблиц

Без ORM таблицы создаются один раз — сырым SQL.

**Вариант А. Init-скрипт при первом запуске контейнера**

1. В проекте создать файл **backend/init_db.sql** (или **postgres/init.sql** рядом с compose) с содержимым:

```sql
CREATE TABLE IF NOT EXISTS items (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(255) NOT NULL,
    description TEXT
);

CREATE INDEX IF NOT EXISTS idx_items_title ON items (title);
```

2. В **docker-compose.yml** у сервиса `postgres` добавить монтирование и при необходимости переменную для init:

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
  - ./backend/init_db.sql:/docker-entrypoint-initdb.d/01_items.sql
```

Файлы в `/docker-entrypoint-initdb.d/` выполняются при первом создании БД (когда volume пустой). При уже существующей БД они не выполняются.

**Вариант Б. Создание при старте приложения**

В коде backend при запуске FastAPI (lifespan или первый запрос) выполнить тот же SQL через `psycopg2`:

- Подключиться по `POSTGRES_URL`.
- Вызвать `cursor.execute(open("init_db.sql").read())` или вшить строку с `CREATE TABLE IF NOT EXISTS ...`.
- Закрыть cursor и commit.

Выбери один вариант и придерживайся его.

---

## 4. PostgreSQL: работа из backend (без ORM)

- Подключение: `psycopg2.connect(POSTGRES_URL)` (или коннект при старте и переиспользование).
- Для async FastAPI можно оставить sync-драйвер и вынести вызовы в `run_in_executor`, либо позже перейти на `asyncpg` — по заданию достаточно sync.

Примеры:

**Список items (GET /api/items):**

```python
cur = conn.cursor()
cur.execute("SELECT id, title, description FROM items ORDER BY id")
rows = cur.fetchall()
items = [{"id": r[0], "title": r[1], "description": r[2] or ""} for r in rows]
```

**Создание item (POST /api/items):**

```python
cur = conn.cursor()
cur.execute(
    "INSERT INTO items (title, description) VALUES (%s, %s) RETURNING id",
    (body.title, body.description or "")
)
row = cur.fetchone()
item_id = row[0]
conn.commit()
```

После вставки формировать ответ `{"id": item_id, "title": ..., "description": ...}`.

---

## 5. MongoDB: коллекция events

Таблицу в Mongo не создаёшь — коллекция появляется при первой вставке.

- Подключение: `pymongo.MongoClient(MONGO_URL)`, выбрать БД, например `practicedb` или `app`.
- Коллекция: `events`.

Вставка документа (без ORM):

```python
doc = {
    "type": "item_created",
    "payload": {"id": item_id, "title": body.title, "description": body.description or ""},
    "at": datetime.utcnow().isoformat() + "Z"
}
mongo_client["practicedb"]["events"].insert_one(doc)
```

Индексы (по желанию) можно создать при старте приложения:

```python
coll = mongo_client["practicedb"]["events"]
coll.create_index("at")
coll.create_index("type")
```

Либо один раз выполнить в mongosh и не трогать в коде.

---

## 6. Redis: кэш списка items

- Подключение: `redis.Redis.from_url(REDIS_URL)`.
- Ключ списка: `api:items:list`.
- Значение: JSON-строка ответа GET /api/items, например `json.dumps({"items": [...]})`.
- TTL: 60 секунд.

**GET /api/items:**

1. `data = redis_client.get("api:items:list")`.
2. Если `data` не None — вернуть `json.loads(data)`.
3. Иначе — прочитать из Postgres, собрать `{"items": [...]}`, положить `redis_client.set("api:items:list", json.dumps(res), ex=60)`, вернуть ответ.

**POST /api/items:**

После вставки в Postgres: `redis_client.delete("api:items:list")`.

---

## 7. Куда что класть в backend

- **Подключения** — при старте приложения (FastAPI lifespan или глобальные переменные после создания клиентов). Хранить в модуле или передавать в зависимости.
- **Эндпоинты** — в **main.py**: в `list_items` — Redis (get) → при промахе Postgres (SELECT) + Redis (set) + при желании Mongo (insert event `items_listed`). В `create_item` — Postgres (INSERT) + Redis (delete ключа) + Mongo (insert event `item_created`).
- **SQL** — либо в **init_db.sql**, либо строками в коде; отдельный файл **db/postgres.py** с функциями `get_items()`, `create_item(...)` по желанию для порядка.
- **Mongo/Redis** — вынести в **db/mongo.py** и **db/redis.py** с функциями `insert_event(...)`, `get_cached_items()`, `set_cached_items()`, `invalidate_items_cache()` — по желанию.

Структура может быть такой:

```
backend/
  main.py           # FastAPI, эндпоинты, вызовы к БД
  init_db.sql       # CREATE TABLE для Postgres (если вариант А)
  db/
    postgres.py     # connect, get_items, create_item (сырой SQL)
    mongo.py        # insert_event
    redis_cache.py  # get/set/delete кэша items
```

---

## 8. Чек-лист по шагам

| Шаг | Действие |
|-----|----------|
| 1 | Добавить в requirements.txt: psycopg2-binary, pymongo, redis. |
| 2 | В docker-compose заполнить POSTGRES_URL, MONGO_URL, REDIS_URL для backend. |
| 3 | Создать таблицу items: init_db.sql в docker-entrypoint-initdb.d ИЛИ выполнить SQL при старте из кода. |
| 4 | В backend: подключение к Postgres, в list_items — SELECT, в create_item — INSERT ... RETURNING id. |
| 5 | В backend: подключение к Mongo, в create_item и при GET items вставить документ в events. |
| 6 | В backend: подключение к Redis; GET /api/items — сначала get ключа, иначе Postgres + set с TTL 60; POST — delete ключа. |
| 7 | Убрать глобальные items_store и next_id из main.py, заменить на вызовы к БД. |

После этого API продолжит отдавать тот же контракт; источник данных — Postgres, кэш — Redis, лог событий — Mongo. Детали схем (аудит, TTL в Mongo) — в **DB_SPEC.md**.
