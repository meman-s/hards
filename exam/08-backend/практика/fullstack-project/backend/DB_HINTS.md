# Подсказки: инициализация БД и код в Python

---

## 1. Когда инициализировать подключения

Инициализировать все клиенты (Postgres, Mongo, Redis) **один раз при старте приложения**, а не в каждом запросе. В FastAPI для этого удобен **lifespan**:

- При **старте** — читаешь из `os.environ` URL, создаёшь подключения, кладёшь их в `app.state` (или в отдельный модуль `db`).
- При **остановке** — закрываешь соединения (conn.close(), mongo_client.close(), redis не обязательно закрывать, но можно).

Пример каркаса в main.py:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: создать conn, mongo_client, redis_client из os.environ
    # сохранить в app.state: app.state.pg = conn, app.state.mongo = ..., app.state.redis = ...
    yield
    # shutdown: conn.close(), mongo_client.close()

app = FastAPI(lifespan=lifespan)
```

Дальше в эндпоинтах брать из `request.app.state.pg` и т.д. Либо завести модуль `db`, в нём при старте записать глобальные переменные `pg_conn`, `mongo_client`, `redis_client`, и в main импортировать `from db import pg_conn` — как тебе удобнее.

---

## 2. Откуда брать URL

Всё из переменных окружения (в Docker они уже заданы в compose):

- `os.environ.get("POSTGRES_URL")` — строка вида `postgresql://user:pass@host:5432/dbname`
- `os.environ.get("MONGO_URL")` — `mongodb://mongo:27017`
- `os.environ.get("REDIS_URL")` — `redis://redis:6379/0`

Если переменной нет (локальный запуск без Docker), можно не поднимать приложение или подставлять дефолт — на твоё усмотрение.

---

## 3. Postgres (psycopg2)

- Подключение: `conn = psycopg2.connect(POSTGRES_URL)`. Один conn на всё приложение, не создавать в каждом запросе.
- Запрос: `cur = conn.cursor()`, потом `cur.execute("SELECT ...", (param,))`, `cur.fetchall()` или `cur.fetchone()`, для INSERT/UPDATE — `conn.commit()`, `cur.close()`.
- Параметры в запросах — только через плейсхолдеры `%s`, не подставлять строки в SQL (защита от инъекций): `cur.execute("SELECT id, title FROM items WHERE id = %s", (id_,))`.
- После INSERT с RETURNING: `cur.execute("INSERT INTO items (title, description) VALUES (%s, %s) RETURNING id", (...)); row = cur.fetchone(); id = row[0]`.

Таблицы уже создаются через init_db в Docker — в коде ничего создавать не нужно, только SELECT/INSERT.

---

## 4. MongoDB (pymongo)

- Подключение: `client = pymongo.MongoClient(MONGO_URL)`. Один клиент на приложение.
- БД и коллекция: `db = client["practicedb"]` (или другое имя), `coll = db["events"]`.
- Вставка: `coll.insert_one({"type": "item_created", "payload": {...}, "at": "2025-02-13T12:00:00Z"})`. Коллекция создаётся при первой вставке.
- Индексы по желанию можно создать при старте: `coll.create_index("at"), coll.create_index("type")`.

---

## 5. Redis (redis)

- Подключение: `r = redis.Redis.from_url(REDIS_URL)`. Один клиент на приложение.
- Кэш списка: ключ `api:items:list`, значение — JSON-строка. Получить: `data = r.get("api:items:list")`; если не None — `json.loads(data)`. Записать: `r.set("api:items:list", json.dumps({"items": [...]}), ex=60)`. Инвалидация: `r.delete("api:items:list")`.
- `r.get()` возвращает bytes — для JSON нужен `.decode()` или в Redis 4+ можно использовать `decode_responses=True` при создании клиента.

---

## 6. Куда класть код

Вариант А — всё в main.py: в lifespan создаёшь подключения и вешаешь на `app.state`; в эндпоинтах берёшь `request.app.state.pg` и делаешь запросы там же.

Вариант Б — вынести в модули:
- `db/__init__.py` — при импорте ничего не делать; либо одна функция `init_db(postgres_url, mongo_url, redis_url)`, которую вызываешь из lifespan и которая заполняет глобальные переменные в db/postgres.py, db/mongo.py, db/redis_cache.py.
- `db/postgres.py` — переменная `conn = None`, функция `get_items()` (SELECT, возвращает list[dict]), `create_item(title, description)` (INSERT, возвращает id или полный item).
- `db/mongo.py` — переменная `client` или `coll`, функция `insert_event(type, payload)`.
- `db/redis_cache.py` — переменная `redis_client`, функции `get_cached_items()`, `set_cached_items(data, ttl=60)`, `invalidate_items_cache()`.

В main в lifespan вызываешь инициализацию (создание соединений и запись в эти модули), в эндпоинтах вызываешь только функции из db (get_items, create_item, insert_event, get_cached_items и т.д.).

---

## 7. Порядок в эндпоинтах

**GET /api/items:**  
Сначала Redis (get). Если есть — вернуть. Если нет — SELECT из Postgres, собрать ответ, set в Redis с TTL 60, вернуть. По желанию — записать в Mongo событие `items_listed`.

**POST /api/items:**  
INSERT в Postgres (получить id), delete ключа в Redis, записать в Mongo событие `item_created`, вернуть `{"id": ..., "title": ..., "description": ...}`.

Так ты инициализируешь все БД при старте и пишешь код без ORM, только драйверы и сырой SQL/документы/ключи.
