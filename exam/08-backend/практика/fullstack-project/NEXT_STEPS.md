# Volumes для Nginx и что ещё поправить

---

## 1. Как устроены volumes у Nginx

Nginx в контейнере нужно дать две вещи с хоста:

1. **Файл конфига** — твой `nginx.conf` (или конфиг из `conf.d`).
2. **Папку со статикой** — папку `frontend`, чтобы раздавать `index.html` и остальное.

Сейчас у тебя написано:

```yaml
volumes:
  - nginx_data:/.nginx/nginx.conf
```

Так делать нельзя: **именованный том** (`nginx_data`) — это пустое хранилище Docker. Ты монтируешь его в точку `/.nginx/nginx.conf`, т.е. подменяешь один файл содержимым тома (пустым). Нужно не том, а **файл с диска**.

Нужны **bind mount** (привязка к папке/файлу на хосте):

- Источник: путь на твоей машине (относительно папки с `docker-compose.yml`).
- Назначение: путь **внутри контейнера**, куда nginx смотрит по умолчанию.

### Конфиг

- Официальный образ nginx:alpine подхватывает конфиги из **/etc/nginx/conf.d/** (файлы `*.conf`).
- Вариант: смонтировать твой файл как один конфиг в conf.d, например:
  - **Хост:** `./nginx/nginx.conf`
  - **Контейнер:** `/etc/nginx/conf.d/default.conf`
- Тогда твой конфиг будет использоваться. Если в образе уже есть `default.conf`, он будет заменён твоим.

Запись в compose:

```yaml
volumes:
  - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
```

(Без именованного тома — это bind mount.)

### Статика (frontend)

- В конфиге у тебя: `location /static/` и `alias /frontend/;` — значит, внутри контейнера nginx должен видеть каталог **/frontend/** (там лежат index.html и т.д.).
- Нужно смонтировать папку с хоста в этот путь:
  - **Хост:** `./frontend` (папка рядом с docker-compose).
  - **Контейнер:** `/frontend`

В compose:

```yaml
volumes:
  - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
  - ./frontend:/frontend
```

Итого для nginx в `volumes` оставляешь два таких пункта (без `nginx_data`). Именованный том `nginx_data` для такого сценария не нужен — его можно убрать из сервиса nginx и из секции `volumes` внизу файла.

---

## 2. Что поправить в nginx.conf

- **upstream:** сейчас `server 127.0.0.1:8000` — внутри контейнера nginx это сам nginx, а не backend. В одной сети с backend обращаться нужно по имени сервиса: **server backend:8000;** (и в конце точка с запятой).
- **Главная страница:** сейчас раздаётся только `location /static/`. Если открывать сайт по корню `http://localhost/`, nginx не отдаст `index.html`. Нужен либо **location /** с `alias /frontend/;` (или `root /frontend;`), чтобы по `/` отдавался файл из `/frontend/index.html`, либо отдавать фронт только по `/static/` и тогда открывать `http://localhost/static/index.html`. Обычно делают корень `/` для главной.

---

## 3. Остальное в docker-compose

- **postgres** — в volume путь опечатка: **posgresql** → **postgresql** (`/var/lib/postgresql/data`).
- **postgres healthcheck** — в массиве указано `CMD-CHECK` — должно быть **CMD** (через пробел, не дефис). Формат: `test: ["CMD", "pg_isready", "-U", "stepan", "-d", "practicedb"]`.
- **mongo** — образ лучше указать с тегом, например **mongo:6** или **mongo:4**. Имя **mongo4** без тега может не найтись.
- **mongo healthcheck** — команда должна быть в формате списка, и хост для подключения в одной сети — имя сервиса **mongo**, не `db`. Пример: `["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]` или аналог для твоей версии mongo.
- **mongo volumes** — монтировать том в **корень** (`/`) опасно. Для данных mongo обычно: **mongo_data:/data/db**.
- **redis** — том **redis_data** объявлен внизу, но к сервису redis не подключён. Если нужна персистентность — добавь к сервису redis: `volumes: - redis_data:/data` (и при необходимости команду с `--appendonly yes`).
- **backend** — в стадии **runtime** в Dockerfile не копируется код приложения (нет `COPY . .` или `COPY --from=builder /app /app`). В образе есть только зависимости из builder, а `main.py` и др. отсутствуют. В Dockerfile в стадии runtime нужно скопировать приложение из builder, например: `COPY --from=builder /app /app`.
- **backend healthcheck** — поле **healthcheck** есть, но без **test**. Нужно указать команду проверки (например запрос на http://localhost:8000/api/health), **interval**, **timeout**, **retries**.

---

## 4. Краткий чек-лист

| Где | Что сделать |
|-----|-------------|
| docker-compose, nginx | volumes: два bind mount — конфиг и папка frontend; убрать nginx_data из сервиса и из секции volumes. |
| nginx.conf | upstream: backend:8000; при необходимости location / для главной. |
| docker-compose, postgres | Исправить путь тома на postgresql; healthcheck — CMD и корректная команда. |
| docker-compose, mongo | Образ с тегом; volume в /data/db; healthcheck в виде списка и с хостом mongo. |
| docker-compose, redis | При желании подключить redis_data к /data. |
| docker-compose, backend | healthcheck с test (и interval, timeout, retries). |
| backend Dockerfile | В runtime скопировать приложение из builder (COPY --from=builder /app /app). |

После правок: `docker compose up -d`, зайти на http://localhost (или http://localhost/static/index.html, если оставишь только /static/), проверить, что открывается фронт и запросы к /api/ доходят до backend.

---

## 5. Что делать дальше (по шагам)

**Шаг 1. Проверка файлов**

- Убедись, что в `docker-compose.yml`: у nginx есть два тома (конфиг и `./frontend`), в секции `volumes` внизу только именованные тома `postgres_data` и `mongo_data`, путь к фронту — `./frontend` (не fontend).
- В `backend/Dockerfile` в стадии runtime должны копироваться и `/root/.local` (зависимости), и `/app` (код).
- В `nginx/nginx.conf` — upstream `backend:8000`, location `/api/` на proxy_pass, location `/` на alias `/frontend/` с index.

**Шаг 2. Запуск**

- В каталоге `fullstack-exercise` выполни: `docker compose up -d --build`.
- Дождись, пока все сервисы станут healthy: `docker compose ps` (в колонке Status — healthy).

**Шаг 3. Проверка в браузере**

- Открой http://localhost — должна открыться главная страница с формой и списком.
- Добавь элемент через форму — запрос должен уходить на `/api/items` через nginx к backend.
- Если список не загружается или форма не работает — открой DevTools (F12) → Network и проверь, что запросы к `/api/...` идут на порт 80 и возвращают 200.

**Шаг 4. Дальнейшие задачи по упражнению**

- Подключить backend к Postgres, Mongo, Redis по **DB_SPEC.md** (таблица items, коллекция events, кэш).
- Заполнить в `docker-compose` переменные backend: `POSTGRES_URL`, `MONGO_URL`, `REDIS_URL` (значения взять из имён сервисов и кредов из compose).
- После подключения БД — убрать in-memory хранилище в backend и использовать реальные БД.
