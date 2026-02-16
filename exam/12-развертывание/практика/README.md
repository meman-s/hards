# Комплексное упражнение: БД, бэкенд, фронт, Redis, Nginx, Docker

## Роли

- **Ты (и AI):** бэкенд (FastAPI), фронтенд, docker-compose для локальной разработки, примеры env.
- **Ты (вручную):** конфиг Nginx, production Dockerfile и сборка образа приложения.

---

## Архитектура

```
[Браузер] → [Nginx] → [Frontend (статика)]  или  [Nginx] → [Backend API]
                ↓
           [Backend :8000]
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
[PostgreSQL] [MongoDB]  [Redis]
  основное     логи/     кэш,
  хранилище   события   сессии
```

- **PostgreSQL** — основные данные: пользователи, сущности приложения (таблицы, связи).
- **MongoDB** — документы/события: лог действий, аудит, гибкая схема.
- **Redis** — кэш ответов API, сессии, счётчики (TTL).

Бэкенд поднимается на порту 8000, фронт можно раздавать через Nginx или с бэкенда в dev.

---

## Что уже сделано (в репозитории)

1. **Backend** (`fullstack-exercise/backend/`)
   - FastAPI с in-memory хранилищем: GET/POST `/api/items`, GET `/api/health`. Готов обмениваться данными с фронтом.
   - Подключение Postgres, Mongo, Redis **не реализовано** — что создать в БД и как с ними работать, описано в **DB_SPEC.md**.

2. **Frontend** (`fullstack-exercise/frontend/`)
   - Одна страница: список элементов, форма добавления; запросы к `/api/items`.

3. **DB_SPEC.md** (в `fullstack-exercise/`)
   - Спецификация для **твоей** реализации: таблицы Postgres (в т.ч. триггеры), коллекция Mongo, ключи Redis, контракт API.

4. **docker-compose.yml**
   - Опционально: сервисы `postgres`, `mongo`, `redis` для локальной разработки. Бэкенд запускаешь сам (`uvicorn main:app --reload --port 8000`).

---

## Твои задачи

### 1. Nginx

- Создать конфиг (например `fullstack-exercise/nginx/nginx.conf` или в своей папке `nginx/`).
- Варианты:
  - **A:** Nginx раздаёт статику фронта и проксирует `/api` на `http://backend:8000`.
  - **B:** Nginx только reverse proxy на бэкенд; фронт отдаёт сам бэкенд (StaticFiles).
- Требования: проксирование на бэкенд, при необходимости раздача статики, заголовки `Host`/`X-Forwarded-*`.

### 2. Docker-образ приложения

- Написать **Dockerfile** для production:
  - Сборка/копирование бэкенда (и при желании фронта).
  - Запуск одного процесса (например `uvicorn` для FastAPI).
  - Пользователь не root, порт 8000 (или как в проекте).
- Опционально: multi-stage, если нужна сборка фронта (npm build) и копирование в образ.

### 3. Запуск полного стека

- Вариант с твоим Nginx и твоим образом:
  - В `docker-compose` добавить сервисы `frontend` (если статика отдельно) и `nginx`, образ бэкенда — твой.
  - Либо отдельный `docker-compose.prod.yml` с nginx и твоим образом backend.
- Проверить: браузер → Nginx → API → ответ; кэш в Redis, данные в Postgres и Mongo.

---

## Порядок выполнения

1. Запустить бэкенд и фронт: убедиться, что они обмениваются данными (in-memory). Бэкенд: `cd backend && uvicorn main:app --reload --port 8000`; фронт: открыть `frontend/index.html`, API укажет на localhost:8000.
2. По **DB_SPEC.md** создать в Postgres таблицу `items` (и при желании аудит + триггеры), в Mongo коллекцию `events`, в Redis — кэш по ключу `api:items:list`.
3. Поднять Postgres, Mongo, Redis (например `docker compose up -d postgres mongo redis`).
4. В бэкенде заменить in-memory хранилище на вызовы к твоим БД (по контракту из DB_SPEC.md).
5. Написать конфиг Nginx, Dockerfile, при необходимости дописать compose и проверить полный стек.

---

## Полезные команды

```bash
cd fullstack-exercise
docker compose up -d postgres mongo redis
cd backend && uvicorn main:app --reload --port 8000
# Фронт: открыть frontend/index.html в браузере (API = http://localhost:8000)
```

Для продакшена: свой **Dockerfile** (не Dockerfile.dev) и образ backend; в compose добавить сервис **nginx** с твоим конфигом.

---

## Чек-лист

- [ ] Бэкенд и фронт обмениваются данными (in-memory).
- [ ] По DB_SPEC.md созданы: таблица items (и триггеры) в Postgres, коллекция events в Mongo, кэш в Redis.
- [ ] Postgres, Mongo, Redis подняты; бэкенд переведён на них.
- [ ] Написан конфиг Nginx, Dockerfile; полный стек запускается.

Подсказки по текущему состоянию compose, nginx и Dockerfile: см. **NEXT_STEPS.md**.
