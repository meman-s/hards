# Задания по Dockerfile (Python, multi-stage, secrets, ssh mount) без решений

Эти задачи максимально близки к формату тестового задания:

- дан упрощённый `Dockerfile`
- нужно дописать или переписать его под требуемые условия
- решений и разборов здесь нет, они есть в `docker_practice.md`

Рекомендуемый формат работы:

- попробуй решить каждое задание сам, не подглядывая в `docker_practice.md`
- затем сравни свой вариант с похожими решениями и объяснениями из `docker_practice.md`

---

## Задание 1. Разбить простой Python Dockerfile на multi-stage

Условие:

- есть Python API (FastAPI)
- текущий Dockerfile собирает всё в один образ, где остаются:
  - кэш pip
  - временные файлы
  - инструменты сборки
- нужно переписать Dockerfile на multi-stage:
  - первый этап — установка зависимостей и подготовка окружения
  - второй этап — только рантайм с установленными зависимостями и кодом приложения

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

Требуется:

- переписать Dockerfile, используя multi-stage
- сделать финальный образ максимально лёгким

---

## Задание 2. Добавить BuildKit secret для приватного pip репозитория

Условие:

- есть multi-stage Dockerfile для Python API
- часть зависимостей лежит в приватном pip репозитории (например, в GitHub Packages)
- файл `pip.conf` с токенами нельзя хранить в образе
- нужно добавить использование build secrets так, чтобы:
  - `pip.conf` передавался только на время сборки
  - приватный репозиторий использовался pip при установке зависимостей
  - в финальном образе не было `pip.conf` и токенов

Исходный Dockerfile:

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

Требуется:

- добавить директиву синтаксиса для Dockerfile (если нужна)
- изменить шаг установки зависимостей так, чтобы он использовал `--mount=type=secret`
- предусмотреть, что `pip.conf` не окажется в слоях образа

---

## Задание 3. Добавить ssh mount для клонирования приватной Python-библиотеки

Условие:

- часть кода находится в приватном репозитории `git@github.com:org/private-lib.git`
- при сборке Docker-образа нужно:
  - через ssh клонировать этот репозиторий
  - использовать его как локальную библиотеку в приложении
- ssh-ключи не должны попадать в итоговый образ

Исходный Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --user -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Требуется:

- добавить отдельный этап, в котором будет выполняться `git clone` приватного репозитория
- использовать `--mount=type=ssh` для доступа к приватному репозиторию
- перенести склонированный код в основной этап, не копируя ssh-ключи

---

## Задание 4. Совместить multi-stage, secrets и ssh mount в одном Dockerfile

Условие:

- у тебя есть Python API
- часть кода — в приватном git-репозитории
- часть зависимостей — в приватном pip репозитории
- нужна финальная конфигурация Dockerfile, которая:
  - использует ssh mount для клонирования приватного репозитория
  - использует BuildKit secret для `pip.conf`
  - собирает финальный лёгкий рантайм-образ через multi-stage

Исходный каркас Dockerfile (можешь его переписать полностью, если хочешь):

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --user -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Требуется:

- добавить все необходимые этапы (git-зависимости, сборка, рантайм)
- правильно использовать `--mount=type=ssh` и `--mount=type=secret`
- следить, чтобы секреты и ключи не попадали в финальный образ

После того как решишь эти задачи, открой `docker_practice.md` и сравни свои варианты с примерными решениями и объяснениями.

