# Docker Практика: Multi-stage Builds, Secrets, SSH Mount

## 1. MULTI-STAGE BUILDS (Многоэтапная сборка)

Multi-stage builds позволяют использовать несколько образов в одном Dockerfile для оптимизации размера финального образа.

### 1.1. Базовый пример multi-stage build

```dockerfile
# Этап 1: Сборка приложения
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Этап 2: Финальный образ (только runtime)
FROM node:18-alpine AS runtime

WORKDIR /app

# Копируем только необходимые файлы из builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

### 1.2. Multi-stage для Python приложения

```dockerfile
# Этап 1: Сборка зависимостей
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Этап 2: Финальный образ
FROM python:3.11-slim

WORKDIR /app

# Копируем только установленные пакеты
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 1.3. Multi-stage с компиляцией (Go, Rust, C++)

```dockerfile
# Этап 1: Компиляция
FROM golang:1.21-alpine AS builder

WORKDIR /build

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

# Этап 2: Минимальный runtime образ
FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /build/app .

EXPOSE 8080

CMD ["./app"]
```

### 1.4. Multi-stage с несколькими этапами

```dockerfile
# Этап 1: Установка зависимостей
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

# Этап 2: Сборка приложения
FROM node:18-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Этап 3: Тестирование
FROM build AS test
RUN npm run test

# Этап 4: Финальный образ
FROM node:18-alpine AS production
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/package.json ./
RUN npm ci --only=production
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### 1.5. Использование именованных этапов

```dockerfile
FROM node:18-alpine AS base
WORKDIR /app

FROM base AS dependencies
COPY package*.json ./
RUN npm ci

FROM base AS build
COPY --from=dependencies /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS production
COPY --from=build /app/dist ./dist
COPY --from=build /app/package.json ./
RUN npm ci --only=production
CMD ["node", "dist/index.js"]
```

### 1.6. Сборка конкретного этапа

```bash
# Собрать только этап builder
docker build --target builder -t myapp:builder .

# Собрать только этап test
docker build --target test -t myapp:test .

# Собрать финальный образ
docker build --target production -t myapp:latest .
```

## 2. SECRETS (Секреты)

Секреты позволяют безопасно передавать чувствительные данные в образы без их сохранения в истории слоев.

### 2.1. BuildKit secrets (рекомендуемый способ)

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Монтируем секрет во время сборки
RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) && \
    echo "API_KEY=$API_KEY" >> .env

COPY . .
CMD ["python", "app.py"]
```

Использование:
```bash
# Создать файл с секретом
echo "my-secret-api-key" > api_key.txt

# Собрать с секретом
docker build --secret id=api_key,src=api_key.txt -t myapp:latest .
```

### 2.2. Несколько секретов

```dockerfile
# syntax=docker/dockerfile:1
FROM node:18-alpine

WORKDIR /app

RUN --mount=type=secret,id=npm_token \
    --mount=type=secret,id=db_password \
    NPM_TOKEN=$(cat /run/secrets/npm_token) && \
    DB_PASSWORD=$(cat /run/secrets/db_password) && \
    echo "//registry.npmjs.org/:_authToken=$NPM_TOKEN" > .npmrc && \
    npm install && \
    echo "DB_PASSWORD=$DB_PASSWORD" >> .env

COPY . .
CMD ["node", "index.js"]
```

Использование:
```bash
docker build \
  --secret id=npm_token,src=npm_token.txt \
  --secret id=db_password,src=db_password.txt \
  -t myapp:latest .
```

### 2.3. Секреты из переменных окружения

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

RUN --mount=type=secret,id=github_token,env=GITHUB_TOKEN \
    pip install --extra-index-url https://$(cat /run/secrets/github_token)@github.com/org/packages.git/simple/ package-name

COPY . .
CMD ["python", "app.py"]
```

Использование:
```bash
export GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
docker build --secret id=github_token,env=GITHUB_TOKEN -t myapp:latest .
```

### 2.4. Секреты для приватных репозиториев

```dockerfile
# syntax=docker/dockerfile:1
FROM node:18-alpine

WORKDIR /app

RUN --mount=type=secret,id=npmrc \
    cp /run/secrets/npmrc ~/.npmrc && \
    npm install && \
    rm ~/.npmrc

COPY . .
CMD ["node", "index.js"]
```

Создать `.npmrc`:
```
//registry.npmjs.org/:_authToken=${NPM_TOKEN}
@myorg:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

### 2.5. Секреты в multi-stage build

```dockerfile
# syntax=docker/dockerfile:1
FROM node:18-alpine AS builder

WORKDIR /app

RUN --mount=type=secret,id=npm_token \
    echo "//registry.npmjs.org/:_authToken=$(cat /run/secrets/npm_token)" > .npmrc && \
    npm install && \
    npm run build && \
    rm .npmrc

FROM node:18-alpine AS production

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./
RUN npm ci --only=production

CMD ["node", "dist/index.js"]
```

### 2.6. Проверка, что секреты не попали в образ

```bash
# Проверить историю образа
docker history myapp:latest

# Проверить файловую систему
docker run --rm myapp:latest ls -la /run/secrets
# Должно быть пусто или файл не должен существовать
```

## 3. SSH MOUNT (SSH монтирование)

SSH mount позволяет использовать SSH ключи для доступа к приватным репозиториям во время сборки.

### 3.1. Базовое использование SSH mount

```dockerfile
# syntax=docker/dockerfile:1
FROM alpine/git AS clone

WORKDIR /tmp

RUN --mount=type=ssh \
    git clone git@github.com:username/private-repo.git

FROM node:18-alpine

WORKDIR /app

COPY --from=clone /tmp/private-repo ./private-repo
COPY . .
RUN npm install

CMD ["node", "index.js"]
```

Использование:
```bash
# Включить SSH агент и добавить ключ
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa

# Собрать с SSH
docker build --ssh default -t myapp:latest .
```

### 3.2. SSH mount с указанием конкретного ключа

```dockerfile
# syntax=docker/dockerfile:1
FROM alpine/git

WORKDIR /tmp

RUN --mount=type=ssh,id=github_key \
    git clone git@github.com:username/private-repo.git
```

Использование:
```bash
docker build --ssh github_key=$SSH_AUTH_SOCK -t myapp:latest .
```

### 3.3. SSH mount для npm приватных пакетов

```dockerfile
# syntax=docker/dockerfile:1
FROM node:18-alpine

WORKDIR /app

RUN --mount=type=ssh \
    apk add --no-cache openssh-client && \
    mkdir -p ~/.ssh && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts && \
    git config --global url."git@github.com:".insteadOf "https://github.com/" && \
    npm install

COPY . .
CMD ["node", "index.js"]
```

### 3.4. SSH mount в multi-stage build

```dockerfile
# syntax=docker/dockerfile:1
FROM alpine/git AS deps

WORKDIR /deps

RUN --mount=type=ssh \
    git clone git@github.com:org/private-dependency.git dependency1 && \
    git clone git@github.com:org/another-dependency.git dependency2

FROM python:3.11-slim

WORKDIR /app

COPY --from=deps /deps ./deps
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "app.py"]
```

### 3.5. SSH mount для клонирования нескольких репозиториев

```dockerfile
# syntax=docker/dockerfile:1
FROM alpine/git AS git-clone

WORKDIR /repos

RUN --mount=type=ssh \
    apk add --no-cache openssh-client && \
    mkdir -p ~/.ssh && \
    ssh-keyscan github.com gitlab.com >> ~/.ssh/known_hosts && \
    git clone git@github.com:org/repo1.git && \
    git clone git@gitlab.com:org/repo2.git

FROM node:18-alpine

WORKDIR /app

COPY --from=git-clone /repos ./repos
COPY package.json .
RUN npm install

COPY . .
CMD ["node", "index.js"]
```

### 3.6. Комбинирование SSH mount и secrets

```dockerfile
# syntax=docker/dockerfile:1
FROM node:18-alpine

WORKDIR /app

RUN --mount=type=ssh \
    --mount=type=secret,id=github_token \
    apk add --no-cache openssh-client && \
    GITHUB_TOKEN=$(cat /run/secrets/github_token) && \
    echo "//npm.pkg.github.com/:_authToken=$GITHUB_TOKEN" > .npmrc && \
    git clone git@github.com:org/private-repo.git && \
    npm install && \
    rm .npmrc

COPY . .
CMD ["node", "index.js"]
```

Использование:
```bash
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa

docker build \
  --ssh default \
  --secret id=github_token,src=github_token.txt \
  -t myapp:latest .
```

## 4. ПРАКТИЧЕСКИЕ ПРИМЕРЫ КОМБИНАЦИЙ

### 4.1. Полный пример: Multi-stage + Secrets + SSH

```dockerfile
# syntax=docker/dockerfile:1

# Этап 1: Клонирование приватных репозиториев
FROM alpine/git AS git-deps

WORKDIR /deps

RUN --mount=type=ssh \
    apk add --no-cache openssh-client && \
    mkdir -p ~/.ssh && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts && \
    git clone git@github.com:org/private-lib.git

# Этап 2: Установка зависимостей
FROM node:18-alpine AS dependencies

WORKDIR /app

RUN --mount=type=secret,id=npm_token \
    echo "//registry.npmjs.org/:_authToken=$(cat /run/secrets/npm_token)" > .npmrc && \
    npm ci && \
    rm .npmrc

# Этап 3: Сборка
FROM node:18-alpine AS build

WORKDIR /app

COPY --from=dependencies /app/node_modules ./node_modules
COPY --from=git-deps /deps/private-lib ./private-lib
COPY . .

RUN npm run build

# Этап 4: Тестирование
FROM build AS test

RUN npm run test

# Этап 5: Финальный образ
FROM node:18-alpine AS production

WORKDIR /app

ENV NODE_ENV=production

COPY --from=build /app/dist ./dist
COPY --from=build /app/package.json ./
RUN npm ci --only=production

EXPOSE 3000

USER node

CMD ["node", "dist/index.js"]
```

Сборка:
```bash
eval $(ssh-agent -s)
ssh-add ~/.ssh/id_rsa

docker build \
  --target production \
  --ssh default \
  --secret id=npm_token,src=npm_token.txt \
  -t myapp:latest .
```

### 4.2. Python приложение с приватными зависимостями

```dockerfile
# syntax=docker/dockerfile:1

FROM python:3.11-slim AS builder

WORKDIR /app

RUN --mount=type=ssh \
    --mount=type=secret,id=pip_conf \
    apt-get update && \
    apt-get install -y git openssh-client && \
    mkdir -p ~/.ssh && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts && \
    cp /run/secrets/pip_conf ~/.pip/pip.conf && \
    pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.3. Go приложение с приватными модулями

```dockerfile
# syntax=docker/dockerfile:1

FROM golang:1.21-alpine AS builder

WORKDIR /build

RUN apk add --no-cache git openssh-client

RUN --mount=type=ssh \
    mkdir -p ~/.ssh && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts && \
    git config --global url."git@github.com:".insteadOf "https://github.com/"

COPY go.mod go.sum ./
RUN --mount=type=ssh go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o app .

FROM alpine:latest

RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /build/app .

EXPOSE 8080

CMD ["./app"]
```

## 5. ОПТИМИЗАЦИЯ И ЛУЧШИЕ ПРАКТИКИ

### 5.1. Кэширование слоев

```dockerfile
# Плохо: кэш сломается при любом изменении кода
COPY . .
RUN npm install
RUN npm run build

# Хорошо: зависимости кэшируются отдельно
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
```

### 5.2. Минимизация размера образа

```dockerfile
# Используйте alpine образы
FROM node:18-alpine  # вместо node:18

# Удаляйте кэш и временные файлы в одной команде
RUN npm install && \
    npm cache clean --force && \
    rm -rf /tmp/*

# Используйте .dockerignore
# .dockerignore:
# node_modules
# .git
# *.log
# .env
```

### 5.3. Безопасность

```dockerfile
# Создайте непривилегированного пользователя
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

USER appuser

# Не используйте секреты в финальном образе
# Секреты доступны только во время сборки
```

### 5.4. Проверка безопасности

```bash
# Проверить уязвимости в образе
docker scan myapp:latest

# Проверить размер образа
docker images myapp:latest

# Проверить историю
docker history myapp:latest
```
