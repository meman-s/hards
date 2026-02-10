# Задания по Docker Compose (healthcheck, services, networks, volumes) без решений

Эти задачи продолжают темы из `docker_compose_practice.md`, но без готовых решений:

- healthcheck и depends_on с `service_healthy`
- разделение сервисов по сетям
- настройка volumes для данных и статики

Совет по работе:

- сначала решай задачи в этом файле
- потом сверяйся с похожими примерами и решениями в `docker_compose_practice.md`

---

## Задание 1. Добавить healthcheck к PostgreSQL и API

Условие:

- есть стек: `db` (PostgreSQL) и `api`
- сейчас `api` стартует сразу после `db`, без проверки готовности базы
- нужно:
  - добавить healthcheck к `db`
  - добавить healthcheck к `api`
  - сделать так, чтобы `api` стартовал только после того, как `db` станет `healthy`

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

Требуется:

- дописать секцию `healthcheck` для `db`
- дописать секцию `healthcheck` для `api`
- переписать `depends_on` так, чтобы использовать `condition: service_healthy`

---

## Задание 2. Разделить сеть на frontend и backend

Условие:

- есть три сервиса: `nginx`, `api`, `db`
- сейчас все сервисы в одной сети и у `db` открыт порт наружу
- нужно:
  - сделать две сети: `frontend` и `backend`
  - `db` должна быть только в `backend`, без проброса портов наружу
  - `api` должен видеть и фронт, и базу
  - `nginx` должен видеть только `api`, но не `db`

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

Требуется:

- убрать прямой проброс порта `5432` наружу
- описать сети `frontend` и `backend` в секции `networks`
- привязать каждый сервис только к нужным сетям

---

## Задание 3. Настроить volumes для данных БД и загружаемых файлов

Условие:

- есть `db` (PostgreSQL) и `api`
- сейчас данные БД и загруженные файлы пропадают после `docker compose down -v`
- нужно:
  - вынести данные БД в именованный том
  - вынести директорию `uploads` в отдельную директорию на хосте

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
```

Требуется:

- добавить именованный том для данных БД
- подключить этот том к `db` в нужную директорию
- добавить bind mount `./uploads` к директории внутри контейнера `api`

---

## Задание 4. Полный стек: healthcheck + networks + volumes

Условие:

- нужно собрать “полупродовый” стек из трёх сервисов:
  - `db` — PostgreSQL
  - `api` — бэкенд-приложение
  - `nginx` — фронтовой прокси
- требуется:
  - добавить healthcheck для `db` и `api`
  - развести сервисы по сетям `frontend` и `backend`
  - хранить данные БД в именованном томе
  - пробросить наружу только HTTP-порт `nginx`

Исходный каркас docker-compose.yml:

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
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
    ports:
      - "8000:8000"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
```

Требуется:

- добавить healthcheck к `db` и `api`
- развести сервисы по сетям `frontend` и `backend`
- добавить volume для данных `db` и подключить его
- при необходимости убрать лишние `ports`, оставив снаружи только нужные

После того как решишь эти задачи, открой `docker_compose_practice.md` и найди похожие примеры с решениями и пояснениями для самопроверки.

