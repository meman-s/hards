# Docker: multi-stage builds, secrets, ssh mount для Python — примеры тестовых заданий

В этом файле собраны примеры того, как выглядят тестовые задания на тему:

- multi-stage Dockerfile для Python-приложений
- build secrets для приватных pip репозиториев
- ssh mount для доступа к приватным git репозиториям

Формат заданий:

- дан упрощённый `Dockerfile` для Python сервиса
- нужно что‑то добавить или переписать
- ниже — возможное решение и подробное объяснение

## Задание 1. Оптимизировать Python Dockerfile с помощью multi-stage

Условие:

- дан Dockerfile для Python API (например, FastAPI)
- образ получился тяжёлый, в нём остаются инструменты сборки и кэш pip
- нужно переписать Dockerfile на multi-stage, чтобы финальный образ содержал только установленные зависимости и код приложения

Исходный Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Возможное решение:

```dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install --user -r requirements.txt

COPY . .

FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Пояснение:

- первый этап `builder` устанавливает зависимости в пользовательскую директорию
- второй этап `runtime` копирует только установленные пакеты и исходный код
- в финальном образе нет кэша pip и временных файлов, образ меньше по размеру

## Задание 2. Добавить secret для приватного pip репозитория

Условие:

- дан multi-stage Dockerfile для Python
- часть зависимостей лежит в приватном pip репозитории (например, в GitHub Packages)
- конфиг `pip.conf` с токенами нельзя класть в образ напрямую
- нужно использовать build secret и BuildKit

Исходный Dockerfile (упрощённый):

```dockerfile
FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user -r requirements.txt

COPY . .

FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Возможное решение с секретом:

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN --mount=type=secret,id=pip_conf \
  mkdir -p /root/.pip && \
  cp /run/secrets/pip_conf /root/.pip/pip.conf && \
  pip install --user -r requirements.txt

COPY . .

FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Как собирать:

```bash
export DOCKER_BUILDKIT=1

cp pip.conf pip_conf.txt

docker build \
  --secret id=pip_conf,src=pip_conf.txt \
  -t myapp:latest .
```

Пояснение:

- директива `# syntax=docker/dockerfile:1` включает расширенный синтаксис Dockerfile для BuildKit
- `--mount=type=secret,id=pip_conf` монтирует временный файл `/run/secrets/pip_conf` только внутри этого `RUN`
- `pip.conf` используется для настройки приватного репозитория и не попадает в слои образа

## Задание 3. Добавить ssh mount для клонирования приватного Python репозитория

Условие:

- часть кода или зависимостей лежит в приватном git-репозитории на GitHub
- нужно при сборке образа клонировать этот репозиторий
- ssh ключ не должен попадать в образ
- нужно использовать ssh mount и multi-stage

Исходный Dockerfile (упрощённый):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --user -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Возможное решение:

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.11-slim AS deps

RUN apt-get update && apt-get install -y git openssh-client && rm -rf /var/lib/apt/lists/*

WORKDIR /deps

RUN --mount=type=ssh \
  git clone git@github.com:org/private-repo.git .

FROM python:3.11-slim AS runtime

WORKDIR /app

COPY requirements.txt .
RUN pip install --user -r requirements.txt

COPY --from=deps /deps ./private-repo
COPY . .

ENV PATH=/root/.local/bin:$PATH

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Как собирать:

```bash
export DOCKER_BUILDKIT=1

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

docker build \
  --ssh default \
  -t myapp:latest .
```

Пояснение:

- первый этап `deps` устанавливает git и через ssh mount клонирует приватный репозиторий
- второй этап `runtime` копирует результат клонирования и устанавливает зависимости приложения
- ssh ключи доступны только во время шага `RUN --mount=type=ssh` и не попадают в финальный образ

## Задание 4. Комбинация: multi-stage + secrets + ssh mount для Python

Условие:

- нужно показать, что ты умеешь комбинировать все три фичи
- Python API (FastAPI или Django)
- часть кода лежит в приватном git репозитории
- часть зависимостей доступна только через приватный pip репозиторий
- финальный образ должен быть компактным

Возможное решение:

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.11-slim AS git_deps

RUN apt-get update && apt-get install -y git openssh-client && rm -rf /var/lib/apt/lists/*

WORKDIR /deps

RUN --mount=type=ssh \
  git clone git@github.com:org/private-lib.git .

FROM python:3.11-slim AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN --mount=type=secret,id=pip_conf \
  mkdir -p /root/.pip && \
  cp /run/secrets/pip_conf /root/.pip/pip.conf && \
  pip install --user -r requirements.txt

COPY --from=git_deps /deps ./private-lib
COPY . .

FROM python:3.11-slim AS runtime

WORKDIR /app

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Как собирать:

```bash
export DOCKER_BUILDKIT=1

cp pip.conf pip_conf.txt

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

docker build \
  --ssh default \
  --secret id=pip_conf,src=pip_conf.txt \
  -t myapp:latest .
```

Что здесь важно для собеседования:

- умеешь разбивать Dockerfile на этапы: отдельный этап для git зависимостей, отдельный для установки пакетов, отдельный для рантайма
- понимаешь, что secrets и ssh mount работают только внутри конкретных команд `RUN` и не попадают в финальный образ
- умеешь адаптировать эти приёмы под Python стек, а не только под Node.js

Когда разберёшься с этими примерами, напиши, и я подготовлю для тебя отдельный файл с Python-заданиями без решений, чтобы ты мог потренироваться самостоятельно.
