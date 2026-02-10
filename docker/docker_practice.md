# Docker: multi-stage builds, secrets, ssh mount — примеры тестовых заданий

В этом файле собраны примеры того, как выглядят тестовые задания на тему:

- multi-stage Dockerfile
- build secrets
- ssh mount

Формат заданий такой же, как на тестах:

- дан упрощённый `Dockerfile`
- нужно что‑то добавить или переписать
- ниже — возможное решение и подробное объяснение

## Задание 1. Оптимизировать Dockerfile с помощью multi-stage

Условие:

- дан Dockerfile для Node.js приложения
- образ получился тяжёлый, в нём остаются dev-зависимости и исходники
- нужно переписать Dockerfile на multi-stage, чтобы финальный образ содержал только production-зависимости и сборку

Исходный Dockerfile:

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN npm run build

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

Возможное решение:

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

Пояснение:

- первый этап `builder` ставит все зависимости и собирает проект
- второй этап `runtime` копирует только результат сборки и минимальный набор файлов
- dev-зависимости и исходники не попадают в финальный образ
- финальный образ меньше по размеру и безопаснее

## Задание 2. Добавить secret для приватного npm репозитория

Условие:

- дан multi-stage Dockerfile
- часть зависимостей лежит в приватном npm репозитории
- токен для доступа к репозиторию нельзя класть в образ в виде `ENV`
- нужно использовать build secret и BuildKit

Исходный Dockerfile (упрощённый):

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./
RUN npm ci --only=production

CMD ["node", "dist/index.js"]
```

Возможное решение с секретом:

```dockerfile
# syntax=docker/dockerfile:1
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN --mount=type=secret,id=npm_token \
  echo "//registry.npmjs.org/:_authToken=$(cat /run/secrets/npm_token)" > .npmrc && \
  npm ci && \
  rm .npmrc

COPY . .
RUN npm run build

FROM node:18-alpine AS runtime

WORKDIR /app

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./
RUN npm ci --only=production

CMD ["node", "dist/index.js"]
```

Как собирать:

```bash
echo "my-secret-token" > npm_token.txt

export DOCKER_BUILDKIT=1

docker build \
  --secret id=npm_token,src=npm_token.txt \
  -t myapp:latest .
```

Пояснение:

- директива `# syntax=docker/dockerfile:1` включает расширенный синтаксис Dockerfile для BuildKit
- `--mount=type=secret,id=npm_token` монтирует файл `/run/secrets/npm_token` только внутри этого `RUN`
- токен используется для генерации `.npmrc`, после установки зависимостей файл удаляется
- секрет не попадает в слои образа и не виден в финальном контейнере

## Задание 3. Добавить ssh mount для клонирования приватного репозитория

Условие:

- часть кода лежит в приватном git-репозитории на GitHub
- нужно при сборке образа клонировать этот репозиторий
- ssh ключ не должен попадать в образ
- нужно использовать ssh mount и, желательно, multi-stage

Исходный Dockerfile (упрощённый):

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

CMD ["npm", "start"]
```

Возможное решение:

```dockerfile
# syntax=docker/dockerfile:1
FROM alpine/git AS git-stage

WORKDIR /src

RUN --mount=type=ssh \
  git clone git@github.com:org/private-repo.git .

FROM node:18-alpine AS runtime

WORKDIR /app

COPY --from=git-stage /src ./private-repo

COPY package*.json ./
RUN npm ci

COPY . .

CMD ["npm", "start"]
```

Как собирать:

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

export DOCKER_BUILDKIT=1

docker build \
  --ssh default \
  -t myapp:latest .
```

Пояснение:

- первый этап `git-stage` использует образ `alpine/git` для работы с git
- `--mount=type=ssh` даёт доступ к ssh-ключам агента только внутри этого `RUN`
- приватный репозиторий клонируется в `/src`
- второй этап `runtime` копирует уже скачанный код и собирает приложение
- ssh ключи не попадают в финальный образ

## Задание 4. Комбинация: multi-stage + secrets + ssh mount

Условие:

- нужно показать, что ты умеешь комбинировать все три фичи
- приложение на Node.js
- зависимости частично лежат в приватном npm репозитории (токен через secret)
- часть кода в приватном git репозитории (доступ по ssh)
- финальный образ должен быть небольшим (multi-stage)

Возможное решение:

```dockerfile
# syntax=docker/dockerfile:1
FROM alpine/git AS git-stage

WORKDIR /deps

RUN --mount=type=ssh \
  git clone git@github.com:org/private-lib.git .

FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN --mount=type=secret,id=npm_token \
  echo "//registry.npmjs.org/:_authToken=$(cat /run/secrets/npm_token)" > .npmrc && \
  npm ci && \
  rm .npmrc

COPY --from=git-stage /deps ./private-lib
COPY . .

RUN npm run build

FROM node:18-alpine AS runtime

WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./
RUN npm ci --only=production

EXPOSE 3000

CMD ["node", "dist/index.js"]
```

Как собирать:

```bash
echo "my-secret-token" > npm_token.txt

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

export DOCKER_BUILDKIT=1

docker build \
  --ssh default \
  --secret id=npm_token,src=npm_token.txt \
  -t myapp:latest .
```

Что здесь важно для собеседования:

- умеешь разбивать Dockerfile на логичные этапы
- понимаешь, что и secrets, и ssh mount работают только во время сборки и не попадают в финальный образ
- умеешь комбинировать эти механизмы в одном Dockerfile

Когда разберёшься с этими примерами, напиши, и я подготовлю для тебя отдельный файл с заданиями без решений, чтобы ты мог потренироваться самостоятельно.

