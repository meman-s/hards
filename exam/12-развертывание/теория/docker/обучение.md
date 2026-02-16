# Docker и Docker Compose: краткое обучение под тестовые задания

Этот файл даёт именно то понимание, которое нужно для собеседований и тестов:

- как устроен multi-stage Dockerfile
- как работают build secrets и ssh mount в BuildKit
- как в docker-compose настроить services, healthcheck, networks, volumes

Два других файла в этой папке:

- `docker_practice.md` — примеры тестовых заданий по Dockerfile (multi-stage, secrets, ssh mount) с решениями
- `docker_compose_practice.md` — примеры тестовых заданий по Docker Compose (healthcheck, services, networks, volumes) с решениями

## 1. Multi-stage builds (многоэтапная сборка)

Идея: собирать приложение в одном тяжёлом образе, а запускать в другом, лёгком, копируя только результат сборки.

Типичный пример для Node.js:

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine AS runtime

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./
RUN npm ci --only=production

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

Ключевые моменты:

- первый этап `builder` устанавливает все зависимости и собирает код
- второй этап `runtime` копирует только сборку и минимальный набор файлов
- финальный образ меньше и собирается быстрее при повторных билдах

Частые изменения в тестах:

- добавить новый этап (например, `test`)
- выделить общий базовый этап и наследоваться от него через `FROM base AS build`
- перенести тяжёлые команды в ранние слои, чтобы лучше работал кэш

## 2. Build secrets (секреты при сборке)

Для работы secrets нужен BuildKit. В большинстве окружений он уже включён, но на всякий случай:

```bash
export DOCKER_BUILDKIT=1
```

Секреты — это временный файл, доступный только внутри конкретной команды `RUN` во время сборки. После завершения слоя файла в образе нет.

Минимальный пример:

```dockerfile
# syntax=docker/dockerfile:1
FROM node:18-alpine

WORKDIR /app

RUN --mount=type=secret,id=npm_token \
  echo "//registry.npmjs.org/:_authToken=$(cat /run/secrets/npm_token)" > .npmrc && \
  npm ci && \
  rm .npmrc

COPY . .

CMD ["npm", "start"]
```

Сборка:

```bash
echo "my-secret-token" > npm_token.txt

docker build \
  --secret id=npm_token,src=npm_token.txt \
  -t myapp:latest .
```

Важно:

- секреты нельзя использовать в `ENV` и `ARG`, они живут только внутри конкретного `RUN` со `--mount=type=secret`
- секреты удобно использовать для приватных npm/pip/apt репозиториев и токенов

## 3. SSH mount

SSH mount нужен, когда в процессе сборки нужно сходить в приватный репозиторий по SSH.

Простой пример: клонировать приватный репозиторий на этапе сборки и использовать его исходники.

```dockerfile
# syntax=docker/dockerfile:1
FROM alpine/git AS git-stage

WORKDIR /src

RUN --mount=type=ssh \
  git clone git@github.com:org/private-repo.git .

FROM node:18-alpine

WORKDIR /app

COPY --from=git-stage /src ./private-repo
COPY package*.json ./
RUN npm ci

COPY . .

CMD ["npm", "start"]
```

Сборка:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

docker build --ssh default -t myapp:latest .
```

Важно:

- ssh ключ не попадает в финальный образ
- ssh mount, как и secrets, работает только внутри конкретного `RUN` с `--mount=type=ssh`
- ssh mount часто комбинируют с multi-stage: отдельный этап для клонирования зависимостей

## 4. Docker Compose: services

Секция `services` описывает контейнеры. Минимальный пример:

```yaml
version: "3.8"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=production
    depends_on:
      - db

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
```

Основные поля, которые любят спрашивать:

- `image` или `build` — откуда берётся образ
- `ports` — проброс портов на хост
- `environment` и `env_file` — переменные окружения
- `depends_on` — порядок старта и зависимости
- `restart` — политика перезапуска

## 5. Docker Compose: healthcheck

Healthcheck позволяет следить за состоянием контейнера и строить зависимости вида `condition: service_healthy`.

Пример для PostgreSQL и API:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mydb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
```

Ключевые поля healthcheck:

- `test` — команда проверки
- `interval` — как часто проверять
- `timeout` — таймаут одной проверки
- `retries` — сколько раз подряд можно упасть
- `start_period` — время на прогрев перед тем, как считать падения ошибкой

## 6. Docker Compose: networks

Networks позволяют разделять сервисы на публичные и внутренние.

Пример: фронтенд в одной сети, база в другой, API в обеих:

```yaml
version: "3.8"

services:
  db:
    image: postgres:15-alpine
    networks:
      - backend

  api:
    build: .
    ports:
      - "8000:8000"
    networks:
      - frontend
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    networks:
      - frontend

networks:
  frontend:
  backend:
    internal: true
```

Идея:

- `frontend` — сеть, где живут публичные сервисы
- `backend` — внутренняя сеть, недоступная снаружи
- у базы нет `ports`, она доступна только из сети `backend`

## 7. Docker Compose: volumes

Volumes отвечают за данные. В тестах обычно просят:

- вынести данные БД в именованный том
- подключить директорию с конфигом или статикой как bind mount

Комбинированный пример:

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
    volumes:
      - ./uploads:/app/uploads

volumes:
  postgres_data:
```

Типы volumes:

- именованный том через секцию `volumes` внизу файла
- bind mount `./local_dir:/container_dir`
- анонимный том `/path/inside/container`

## 8. Как использовать эти файлы для подготовки

- этот файл `docker_training.md` прочитай один раз целиком, чтобы сложилась общая картинка
- затем открой `docker_practice.md` и разбери примерные задания по Dockerfile
- потом `docker_compose_practice.md` с примерами по docker-compose

Когда почувствуешь, что понимаешь примеры, напиши мне, и я сгенерирую для тебя новые задания в том же формате, но уже без решений.

