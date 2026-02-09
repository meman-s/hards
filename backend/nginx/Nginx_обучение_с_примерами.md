# Nginx: Reverse Proxy и Load Balancing - Обучение с примерами

## Что такое Nginx и зачем он нужен?

**Nginx** (произносится "энджин-икс") — это веб-сервер, который может работать как:
1. **Обычный веб-сервер** — отдавать статические файлы (HTML, CSS, JS, изображения)
2. **Reverse Proxy** — принимать запросы от клиентов и перенаправлять их на другие серверы
3. **Load Balancer** — распределять нагрузку между несколькими серверами

### Зачем нужен Reverse Proxy?

Представь ситуацию:
- У тебя есть FastAPI приложение, которое работает на порту 8000
- Пользователи должны обращаться к нему через порт 80 (стандартный HTTP порт)
- Ты хочешь добавить SSL (HTTPS)
- Ты хочешь отдавать статические файлы быстрее

**Решение:** Nginx принимает запросы на порту 80/443, а сам FastAPI работает на 8000. Nginx перенаправляет запросы к FastAPI.

### Зачем нужен Load Balancing?

Когда у тебя несколько серверов с одним приложением:
- Распределение нагрузки (не перегружать один сервер)
- Отказоустойчивость (если один сервер упал, другие работают)
- Масштабируемость (легко добавить новый сервер)

---

## Часть 1: Reverse Proxy (Обратный прокси)

### Концепция

```
Клиент → Nginx (порт 80) → FastAPI (порт 8000)
```

Клиент не знает, что на самом деле приложение работает на порту 8000. Он обращается к Nginx, а Nginx "проксирует" запрос к приложению.

### Пример 1: Базовый Reverse Proxy

**Сценарий:** У тебя есть FastAPI приложение на `localhost:8000`, и ты хочешь, чтобы оно было доступно через `http://localhost` (порт 80).

**Конфигурация:**

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Объяснение каждой строки:**

- `listen 80;` — Nginx слушает порт 80 (стандартный HTTP)
- `server_name localhost;` — это конфигурация для домена localhost
- `location /` — все запросы, которые начинаются с `/`
- `proxy_pass http://127.0.0.1:8000;` — перенаправлять запросы на локальный сервер на порту 8000
- `proxy_set_header Host $host;` — передать оригинальный Host заголовок (чтобы приложение знало, к какому домену обращались)
- `proxy_set_header X-Real-IP $remote_addr;` — передать реальный IP клиента (иначе приложение увидит IP Nginx)
- `proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;` — цепочка IP-адресов прокси
- `proxy_set_header X-Forwarded-Proto $scheme;` — протокол (http/https), чтобы приложение знало, был ли запрос через HTTPS

**Как использовать:**

1. Сохрани конфигурацию в файл `/etc/nginx/sites-available/myapp`
2. Создай символическую ссылку: `sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/`
3. Проверь конфигурацию: `sudo nginx -t`
4. Перезагрузи Nginx: `sudo systemctl reload nginx`

### Пример 2: Reverse Proxy с обработкой статических файлов

**Сценарий:** Статические файлы (CSS, JS, изображения) отдавать напрямую из Nginx (быстрее), а API запросы проксировать к приложению.

**Конфигурация:**

```nginx
server {
    listen 80;
    server_name example.com;

    # Статические файлы отдаём напрямую
    location /static/ {
        alias /var/www/myapp/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Все остальное проксируем к приложению
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Объяснение:**

- `location /static/` — запросы, начинающиеся с `/static/`
- `alias /var/www/myapp/static/;` — физический путь к файлам на диске
- `expires 30d;` — кэшировать файлы на 30 дней
- `add_header Cache-Control "public, immutable";` — браузер будет кэшировать файлы

**Почему это быстрее?**
- Nginx очень быстрый в отдаче статических файлов
- Не нужно загружать Python приложение для каждого CSS/JS файла
- Меньше нагрузка на приложение

### Пример 3: Reverse Proxy для WebSocket

**Сценарий:** У тебя есть WebSocket соединение (например, для чата или real-time обновлений).

**Конфигурация:**

```nginx
server {
    listen 80;
    server_name example.com;

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        proxy_read_timeout 86400;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Объяснение:**

- `proxy_http_version 1.1;` — использовать HTTP/1.1 (нужно для WebSocket)
- `proxy_set_header Upgrade $http_upgrade;` — передать заголовок Upgrade (нужен для перехода на WebSocket)
- `proxy_set_header Connection "upgrade";` — установить Connection: upgrade
- `proxy_read_timeout 86400;` — таймаут 24 часа (WebSocket соединения долгие)

**Важно:** WebSocket требует специальных заголовков для "апгрейда" HTTP соединения до WebSocket.

---

## Часть 2: Load Balancing (Балансировка нагрузки)

### Концепция

```
Клиент → Nginx → [Сервер 1, Сервер 2, Сервер 3]
```

Nginx распределяет запросы между несколькими серверами. Это называется "upstream" (верхний поток).

### Пример 1: Базовый Load Balancing (Round Robin)

**Сценарий:** У тебя 3 экземпляра приложения на портах 8000, 8001, 8002. Nginx должен распределять запросы между ними по очереди.

**Конфигурация:**

```nginx
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

**Объяснение:**

- `upstream backend` — определяет группу серверов с именем "backend"
- `server 127.0.0.1:8000;` — первый сервер
- `server 127.0.0.1:8001;` — второй сервер
- `server 127.0.0.1:8002;` — третий сервер
- `proxy_pass http://backend;` — проксировать к группе "backend" (не к конкретному серверу!)

**Как работает Round Robin:**
1. Первый запрос → сервер 8000
2. Второй запрос → сервер 8001
3. Третий запрос → сервер 8002
4. Четвертый запрос → сервер 8000 (цикл повторяется)

### Пример 2: Load Balancing с весами (Weighted)

**Сценарий:** У тебя есть мощный сервер (8000) и два менее мощных (8001, 8002). Хочешь отправлять больше запросов на мощный.

**Конфигурация:**

```nginx
upstream backend {
    server 127.0.0.1:8000 weight=3;
    server 127.0.0.1:8001 weight=2;
    server 127.0.0.1:8002 weight=1;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Объяснение:**

- `weight=3` — сервер получает в 3 раза больше запросов
- `weight=2` — сервер получает в 2 раза больше запросов
- `weight=1` — сервер получает базовое количество запросов

**Распределение:**
- Из 6 запросов: 3 пойдут на 8000, 2 на 8001, 1 на 8002

### Пример 3: Least Connections (Наименьшее количество соединений)

**Сценарий:** Хочешь отправлять запросы на сервер с наименьшим количеством активных соединений (более равномерная нагрузка).

**Конфигурация:**

```nginx
upstream backend {
    least_conn;
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Объяснение:**

- `least_conn;` — использовать метод "наименьшее количество соединений"
- Nginx отслеживает, сколько активных соединений у каждого сервера
- Новый запрос отправляется на сервер с наименьшим количеством соединений

**Когда использовать:**
- Когда запросы обрабатываются разное время
- Когда некоторые серверы могут быть перегружены

### Пример 4: IP Hash (Привязка к IP)

**Сценарий:** Хочешь, чтобы один и тот же клиент всегда попадал на один и тот же сервер (например, для сессий).

**Конфигурация:**

```nginx
upstream backend {
    ip_hash;
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Объяснение:**

- `ip_hash;` — использовать хэш IP-адреса для выбора сервера
- Один и тот же IP всегда попадает на один и тот же сервер
- Полезно, когда сессии хранятся на сервере (не в Redis/БД)

**Ограничение:** Если сервер упал, клиенты с его IP будут получать ошибки (пока сервер не вернётся).

### Пример 5: Health Checks и резервные серверы

**Сценарий:** Хочешь автоматически исключать упавшие серверы и использовать резервный сервер.

**Конфигурация:**

```nginx
upstream backend {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8002 backup;
}

server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Объяснение:**

- `max_fails=3` — после 3 неудачных попыток считать сервер недоступным
- `fail_timeout=30s` — через 30 секунд попробовать снова использовать сервер
- `backup` — использовать этот сервер только если все основные недоступны

**Как работает:**
1. Если сервер 8000 не отвечает 3 раза подряд → временно исключается
2. Через 30 секунд Nginx попробует снова использовать его
3. Если все основные серверы (8000, 8001) недоступны → используется backup (8002)

### Пример 6: Временно отключенный сервер

**Конфигурация:**

```nginx
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002 down;
}
```

**Объяснение:**

- `down` — сервер полностью исключён из балансировки
- Полезно для планового обслуживания
- Чтобы вернуть сервер, убери `down` и перезагрузи Nginx

---

## Часть 3: Комбинированный пример (Reverse Proxy + Load Balancing)

**Сценарий:** Полноценная конфигурация с несколькими серверами, SSL, статическими файлами и кэшированием.

**Конфигурация:**

```nginx
# Определяем группу серверов
upstream backend {
    least_conn;
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8002 backup;
}

# Редирект с HTTP на HTTPS
server {
    listen 80;
    server_name api.example.com;
    return 301 https://$server_name$request_uri;
}

# Основной сервер с SSL
server {
    listen 443 ssl http2;
    server_name api.example.com;

    # SSL сертификаты
    ssl_certificate /etc/ssl/certs/api.example.com.crt;
    ssl_certificate_key /etc/ssl/private/api.example.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Логирование
    access_log /var/log/nginx/api.access.log;
    error_log /var/log/nginx/api.error.log;

    # Ограничение размера загружаемых файлов
    client_max_body_size 10M;

    # Статические файлы
    location /static/ {
        alias /var/www/api/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API endpoints с балансировкой
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Все остальное
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Что делает эта конфигурация:**

1. **Load Balancing:** Распределяет запросы между 3 серверами методом least_conn
2. **Health Checks:** Автоматически исключает упавшие серверы
3. **Backup сервер:** Используется если основные недоступны
4. **SSL:** Все запросы перенаправляются на HTTPS
5. **Статические файлы:** Отдаются напрямую из Nginx
6. **Логирование:** Все запросы логируются

---

## Часть 4: Практические советы

### Как проверить конфигурацию

```bash
# Проверить синтаксис
sudo nginx -t

# Если всё ОК, перезагрузить
sudo systemctl reload nginx

# Или перезапустить
sudo systemctl restart nginx
```

### Где находятся файлы конфигурации

- **Основной файл:** `/etc/nginx/nginx.conf`
- **Дополнительные конфигурации:** `/etc/nginx/conf.d/*.conf`
- **Сайты (sites):** `/etc/nginx/sites-available/` и `/etc/nginx/sites-enabled/`

**Рекомендация:** Создавай конфигурации в `sites-available`, а затем создавай символическую ссылку в `sites-enabled`:

```bash
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/myapp
```

### Как посмотреть логи

```bash
# Логи доступа
sudo tail -f /var/log/nginx/access.log

# Логи ошибок
sudo tail -f /var/log/nginx/error.log
```

### Как проверить, что балансировка работает

1. Добавь логирование в приложение (выводи IP и порт сервера)
2. Сделай несколько запросов
3. Проверь, что запросы распределяются между серверами

Или используй заголовок для отладки:

```nginx
location / {
    proxy_pass http://backend;
    add_header X-Backend-Server $upstream_addr;
    # ... остальные заголовки
}
```

Этот заголовок покажет, на какой сервер был отправлен запрос.

---

## Часть 5: Частые ошибки и их решение

### Ошибка 1: "502 Bad Gateway"

**Причина:** Nginx не может подключиться к backend серверу.

**Решение:**
- Проверь, что приложение запущено: `curl http://127.0.0.1:8000`
- Проверь, что порт правильный в конфигурации
- Проверь firewall: `sudo ufw status`

### Ошибка 2: "Connection refused"

**Причина:** Приложение слушает только на `127.0.0.1`, но Nginx пытается подключиться по другому адресу.

**Решение:** Убедись, что в конфигурации Nginx используется правильный адрес:
```nginx
proxy_pass http://127.0.0.1:8000;  # для localhost
# или
proxy_pass http://0.0.0.0:8000;    # если приложение слушает на всех интерфейсах
```

### Ошибка 3: WebSocket не работает

**Причина:** Не хватает заголовков для WebSocket.

**Решение:** Добавь:
```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### Ошибка 4: Приложение видит IP Nginx вместо IP клиента

**Причина:** Не передаются заголовки X-Real-IP или X-Forwarded-For.

**Решение:** Добавь в конфигурацию:
```nginx
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

---

## Резюме

### Reverse Proxy используется для:
- Скрытия внутренней структуры серверов
- Добавления SSL/TLS
- Оптимизации (кэширование, сжатие)
- Обработки статических файлов

### Load Balancing используется для:
- Распределения нагрузки между серверами
- Повышения отказоустойчивости
- Масштабирования приложения

### Основные директивы:
- `upstream` — определяет группу серверов
- `proxy_pass` — проксирует запросы
- `proxy_set_header` — передаёт заголовки
- `location` — определяет правила для разных путей

### Следующие шаги:
1. Попробуй настроить простой reverse proxy для своего приложения
2. Добавь второй экземпляр приложения и настрой load balancing
3. Поэкспериментируй с разными методами балансировки
4. Добавь health checks и backup сервер
