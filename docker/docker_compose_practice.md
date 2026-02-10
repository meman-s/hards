# Docker Compose: healthcheck, services, networks, volumes — примеры тестовых заданий

В этом файле собраны примеры тестовых заданий по Docker Compose:

- добавление и настройка `healthcheck`
- работа с `services` и `depends_on`
- проектирование `networks` (frontend/backend, internal)
- настройка `volumes` (данные БД, статика, uploads)

Формат:

- дан упрощённый `docker-compose.yml`
- нужно что‑то добавить/изменить
- ниже — возможное решение и объяснение

## Задание 1. Добавить healthcheck и зависимость service_healthy

Условие:

- есть API сервис и база PostgreSQL
- сейчас `api` стартует сразу после `db`, иногда падает, потому что база ещё не успела подняться
- нужно:
  - добавить healthcheck к `db`
  - сделать так, чтобы `api` стартовал только после того, как `db` станет здоровым

Исходный docker-compose.yml:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
    depends_on:
      - db
```

Возможное решение:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
    depends_on:
      db:
        condition: service_healthy
```

Пояснение:

- `pg_isready` проверяет, что база принимает подключения
- `retries` и `interval` задают окно времени, за которое `db` должна подняться
- `depends_on.db.condition: service_healthy` даёт гарантию, что `api` стартует только после состояния `healthy` у `db`

## Задание 2. Разделить сеть на frontend и backend

Условие:

- есть `nginx`, `api` и `db`
- сейчас все сервисы в одной сети и `db` случайно проброшена наружу
- нужно:
  - разделить сеть на `frontend` и `backend`
  - `db` должна быть доступна только из `backend` сети и не иметь проброса портов наружу
  - `nginx` должен ходить к `api`, но не к `db`

Исходный docker-compose.yml:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
```

Возможное решение:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    networks:
      - backend

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
    networks:
      - frontend
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - frontend

networks:
  frontend:
  backend:
    internal: true
```

Пояснение:

- у `db` больше нет `ports`, она не торчит наружу
- `backend` помечена как `internal`, её нельзя напрямую пробросить наружу
- `api` находится и во `frontend`, и в `backend`: снаружи до него можно достучаться по порту, а внутри он видит `db`
- `nginx` находится только во `frontend` и не имеет прямого доступа к `db`

## Задание 3. Настроить volumes для данных БД и статических файлов

Условие:

- есть API и PostgreSQL
- к API подключается директория `uploads` с загружаемыми файлами
- у базы пока нет постоянного хранения, данные пропадают при `docker compose down`
- нужно:
  - добавить именованный том для данных БД
  - вынести `uploads` в отдельную директорию на хосте

Исходный docker-compose.yml:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
    volumes:
      - .:/app
```

Возможное решение:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
    volumes:
      - .:/app
      - ./uploads:/app/uploads

volumes:
  postgres_data:
```

Пояснение:

- `postgres_data` — именованный том, который хранит данные даже после `docker compose down`
- `./uploads:/app/uploads` — bind mount: файлы сохраняются в локальной папке `uploads` на хосте

## Задание 4. Добавить полный healthcheck стеку (db, redis, api)

Условие:

- стек: PostgreSQL, Redis и API
- нужно:
  - добавить healthcheck ко всем трём сервисам
  - сделать так, чтобы `api` стартовал только после того, как `db` и `redis` станут здоровыми

Исходный docker-compose.yml:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password

  redis:
    image: redis:7-alpine

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
```

Возможное решение:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

Пояснение:

- `db` и `redis` получают свои простые команды проверки (`pg_isready` и `redis-cli ping`)
- `api` ждёт их статуса `healthy` через `condition: service_healthy`
- `api` тоже имеет свой healthcheck, который проверяет HTTP эндпоинт `/health`

## Задание 5. Production-ready конфигурация (services + networks + volumes + healthcheck)

Условие:

- нужно собрать воедино все ключевые фичи:
  - отдельные сети `frontend` и `backend`
  - volume для БД
  - healthcheck для `db` и `app`
  - минимальный набор портов наружу

Возможное решение:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    restart: always
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - NODE_ENV=production
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"
    networks:
      - backend
      - frontend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      app:
        condition: service_healthy
    networks:
      - frontend

volumes:
  postgres_data:

networks:
  frontend:
  backend:
    internal: true
```

Что здесь важно для собеседования:

- правильно разведены сети (публичные и внутренние сервисы)
- у БД есть volume для данных, а наружу торчат только нужные порты
- healthcheck настроен на уровне БД и приложения, а зависимости построены через `condition: service_healthy`

Когда разберёшься с этими примерами, напиши, и я подготовлю отдельный набор заданий без решений, чтобы ты мог потренироваться в условиях, максимально похожих на реальный тест.

