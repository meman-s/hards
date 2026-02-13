# Спецификация БД: что создать для интеграции с API

Приложение отдаёт и принимает данные в формате ниже. Твоя задача — реализовать хранилища (PostgreSQL, MongoDB, Redis) и подставить их в бэкенд вместо in-memory хранилища.

---

## Контракт API (уже реализован во фронте и бэкенде)

- **GET /api/items** — возвращает `{"items": [ {"id": int, "title": str, "description": str}, ... ]}`.
- **POST /api/items** — тело `{"title": str, "description": str | null}`; ответ `{"id": int, "title": str, "description": str}`.
- **GET /api/health** — без БД, можно оставить как есть.

Рекомендуемая логика: список items читать из Postgres; ответ GET /api/items кэшировать в Redis; события (список запрошен, элемент создан) писать в Mongo.

---

## 1. PostgreSQL

### Таблица `items`

| Колонка      | Тип         | Ограничения   |
|-------------|-------------|----------------|
| `id`       | SERIAL / INT | PRIMARY KEY   |
| `title`    | VARCHAR(255) | NOT NULL      |
| `description` | TEXT       | NULL разрешён |

Пример создания:

```sql
CREATE TABLE items (
    id   SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT
);
```

### Индексы

- Поиск по id уже по первичному ключу.
- При необходимости поиска по названию: `CREATE INDEX idx_items_title ON items (title);`

### Триггеры (по желанию)

- **После вставки в `items`** — записать в таблицу аудита (например `items_audit`: `item_id`, `action = 'insert'`, `created_at`). Либо вместо своей таблицы аудита вызывать запись в Mongo (это уже в коде бэкенда при добавлении логики).
- **После обновления/удаления** — аналогично `action = 'update'` / `'delete'` в аудит.

Пример таблицы аудита и триггера (вставка):

```sql
CREATE TABLE items_audit (
    id         SERIAL PRIMARY KEY,
    item_id    INT NOT NULL,
    action     VARCHAR(10) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION items_audit_trigger_fn()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO items_audit (item_id, action) VALUES (NEW.id, 'insert');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER items_after_insert
    AFTER INSERT ON items
    FOR EACH ROW EXECUTE PROCEDURE items_audit_trigger_fn();
```

(В PostgreSQL 11+ допустимо `EXECUTE FUNCTION` вместо `EXECUTE PROCEDURE`.)

---

## 2. MongoDB

### Коллекция `events`

Назначение: лог событий (кто что запросил/создал). Схема документа — произвольная, ниже минимальный вариант.

Рекомендуемые поля:

| Поле     | Тип    | Описание                    |
|----------|--------|-----------------------------|
| `type`   | string | Тип события, например `items_listed`, `item_created` |
| `payload`| object | Данные: `{ "count": N }` или `{ "id": 1, "title": "..." }` |
| `at`     | string | ISO 8601 дата/время (UTC), например `2025-02-13T12:00:00Z` |

Индексы:

- `db.events.createIndex({ "at": 1 })` — выборка по времени.
- `db.events.createIndex({ "type": 1 })` — фильтр по типу события.

TTL (по желанию): удалять старые события через N дней:

```javascript
db.events.createIndex({ "at": 1 }, { expireAfterSeconds: 90 * 24 * 3600 });
```

(в данном примере — через 90 дней; поле должно быть типа Date или парситься как дата.)

---

## 3. Redis

### Кэш списка items

- **Ключ:** `api:items:list`
- **Значение:** JSON строка, например `{"items": [{"id": 1, "title": "...", "description": "..."}]}` — тот же формат, что возвращает GET /api/items.
- **TTL:** 60 секунд (или вынести в настройки).

При **GET /api/items**: если ключ есть — вернуть из Redis; иначе прочитать из Postgres, положить в Redis с TTL 60, вернуть ответ.

При **POST /api/items**: после вставки в Postgres удалить ключ `api:items:list` (инвалидация кэша), чтобы следующий GET подтянул свежие данные из БД.

Дополнительно (по желанию): счётчик запросов, например ключ `api:items:requests` с `INCR` и TTL.

---

## Краткий чек-лист

- [ ] **PostgreSQL:** таблица `items` (id, title, description); при желании — `items_audit` и триггеры AFTER INSERT/UPDATE/DELETE.
- [ ] **MongoDB:** коллекция `events` с полями type, payload, at; индексы по `at` и `type`; при желании TTL.
- [ ] **Redis:** ключ `api:items:list` (JSON, TTL 60); при создании item — удалять этот ключ.
- [ ] **Бэкенд:** заменить in-memory хранилище на вызовы к Postgres (чтение/запись items), Redis (get/set/delete кэша), Mongo (insert в events).

После этого фронт и FastAPI продолжат обмениваться данными в том же формате; источником правды станут твои БД.
