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

Построчный разбор Dockerfile:

- `# syntax=docker/dockerfile:1`  
  Включает расширенный синтаксис Dockerfile (BuildKit), чтобы можно было использовать `RUN --mount=type=ssh` и `--mount=type=secret`.

- `FROM python:3.11-slim AS git_deps`  
  Первый этап multi-stage, основанный на `python:3.11-slim`. Имя этапа `git_deps` нужно, чтобы потом копировать из него файлы.

- `RUN apt-get update && apt-get install -y git openssh-client && rm -rf /var/lib/apt/lists/*`  
  Обновляет список пакетов, устанавливает `git` и ssh-клиент, а затем удаляет кэш apt, чтобы не раздувать слой образа.

- `WORKDIR /deps`  
  Устанавливает рабочую директорию `/deps` для всех следующих команд в этом этапе.

- `RUN --mount=type=ssh \` и `git clone git@github.com:org/private-lib.git .`  
  Через `--mount=type=ssh` временно подключает ssh-ключи из ssh-агента хоста и клонирует приватный репозиторий в `/deps`. Ключи не сохраняются в образе.

- `FROM python:3.11-slim AS builder`  
  Второй этап multi-stage, где ставятся Python-зависимости и готовится окружение для приложения.

- `WORKDIR /app`  
  Рабочая директория этого этапа — `/app`.

- `ENV PIP_NO_CACHE_DIR=1`  
  Говорит pip не сохранять кэш скачанных пакетов, чтобы уменьшить размер образа.

- `COPY requirements.txt .`  
  Копирует `requirements.txt` из контекста сборки в `/app` внутри контейнера.

- `RUN --mount=type=secret,id=pip_conf \` и три последующие строки  
  Через `--mount=type=secret,id=pip_conf` монтируется временный файл `/run/secrets/pip_conf`.  
  Затем создаётся `/root/.pip`, туда копируется `pip_conf` как `pip.conf`, после чего `pip install --user -r requirements.txt` устанавливает зависимости в `/root/.local`, используя приватный репозиторий из конфига.

- `COPY --from=git_deps /deps ./private-lib`  
  Копирует результат первого этапа (`/deps` из `git_deps`) в `/app/private-lib` текущего этапа, чтобы приватная библиотека была рядом с кодом приложения.

- `COPY . .`  
  Копирует исходный код текущего проекта в `/app`.

- `FROM python:3.11-slim AS runtime`  
  Третий, финальный этап — чистый рантайм-образ, который будет использоваться в проде.

- `WORKDIR /app`  
  Рабочая директория рантайм-образа — `/app`.

- `COPY --from=builder /root/.local /root/.local`  
  Копирует установленный на этапе `builder` набор Python-зависимостей в финальный образ.

- `COPY . .`  
  Копирует исходный код приложения в `/app` финального образа.

- `ENV PATH=/root/.local/bin:$PATH`  
  Добавляет в `PATH` папку с пользовательскими бинарниками, установленными pip, чтобы можно было вызывать их без полного пути.

- `ENV PYTHONUNBUFFERED=1`  
  Отключает буферизацию вывода Python, чтобы логи сразу писались в stdout/stderr.

- `EXPOSE 8000`  
  Документирует, что приложение внутри контейнера слушает порт `8000`.

- `CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]`  
  Команда по умолчанию при запуске контейнера: стартует uvicorn с приложением `app.main:app`, на всех интерфейсах (`0.0.0.0`) и порту `8000`.

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
