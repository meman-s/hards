# Nginx: Практические упражнения

## Подготовка окружения

### Установка Nginx

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# Проверить статус
sudo systemctl status nginx

# Запустить
sudo systemctl start nginx

# Включить автозапуск
sudo systemctl enable nginx
```

### Создание тестового приложения

Создай простое FastAPI приложение для тестирования:

```python
# test_app.py
from fastapi import FastAPI
import socket

app = FastAPI()

@app.get("/")
def read_root():
    hostname = socket.gethostname()
    return {
        "message": "Hello from FastAPI",
        "server": hostname,
        "port": "8000"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Запусти несколько экземпляров:

```bash
# Терминал 1
python test_app.py

# Терминал 2 (измени порт в коде на 8001)
python test_app.py  # на порту 8001

# Терминал 3 (измени порт в коде на 8002)
python test_app.py  # на порту 8002
```

---

## Упражнение 1: Базовый Reverse Proxy

### Задача
Настрой Nginx так, чтобы запросы к `http://localhost` проксировались на `http://localhost:8000`.

### Шаги

1. Создай файл конфигурации:
```bash
sudo nano /etc/nginx/sites-available/test-proxy
```

2. Добавь конфигурацию:
```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. Активируй конфигурацию:
```bash
sudo ln -s /etc/nginx/sites-available/test-proxy /etc/nginx/sites-enabled/
```

4. Удали дефолтную конфигурацию (если нужно):
```bash
sudo rm /etc/nginx/sites-enabled/default
```

5. Проверь и перезагрузи:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

6. Проверь работу:
```bash
curl http://localhost
```

### Ожидаемый результат
Должен вернуться JSON от FastAPI приложения.

### Проверка
- Открой браузер: `http://localhost`
- Должен увидеть ответ от приложения на порту 8000

---

## Упражнение 2: Reverse Proxy с статическими файлами

### Задача
Настрой Nginx так, чтобы:
- Запросы к `/static/` отдавались из папки `/var/www/static/`
- Все остальные запросы проксировались к приложению

### Шаги

1. Создай папку для статики:
```bash
sudo mkdir -p /var/www/static
sudo chown $USER:$USER /var/www/static
```

2. Создай тестовый файл:
```bash
echo "<h1>Static File Test</h1>" > /var/www/static/test.html
```

3. Обнови конфигурацию:
```nginx
server {
    listen 80;
    server_name localhost;

    location /static/ {
        alias /var/www/static/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

4. Перезагрузи Nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

5. Проверь:
```bash
curl http://localhost/static/test.html
curl http://localhost/
```

### Ожидаемый результат
- `/static/test.html` → содержимое файла
- `/` → ответ от FastAPI

---

## Упражнение 3: Базовый Load Balancing

### Задача
Настрой балансировку между тремя серверами (8000, 8001, 8002) методом Round Robin.

### Шаги

1. Убедись, что запущены 3 экземпляра приложения на разных портах.

2. Создай конфигурацию:
```nginx
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. Перезагрузи Nginx:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

4. Сделай несколько запросов:
```bash
for i in {1..10}; do
    curl http://localhost
    echo ""
done
```

### Ожидаемый результат
Запросы должны распределяться между тремя серверами по очереди.

### Проверка
В ответах должно быть видно разные порты (8000, 8001, 8002).

---

## Упражнение 4: Load Balancing с весами

### Задача
Настрой балансировку так, чтобы сервер на порту 8000 получал в 2 раза больше запросов.

### Шаги

1. Обнови конфигурацию:
```nginx
upstream backend {
    server 127.0.0.1:8000 weight=2;
    server 127.0.0.1:8001 weight=1;
    server 127.0.0.1:8002 weight=1;
}

server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. Перезагрузи Nginx.

3. Сделай 10 запросов и посчитай распределение:
```bash
for i in {1..10}; do
    curl -s http://localhost | grep -o '"port":"[^"]*"'
done
```

### Ожидаемый результат
Примерно 5 запросов на порт 8000, по 2-3 на 8001 и 8002.

---

## Упражнение 5: Least Connections

### Задача
Настрой балансировку методом "наименьшее количество соединений".

### Шаги

1. Обнови конфигурацию:
```nginx
upstream backend {
    least_conn;
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. Перезагрузи Nginx.

3. Сделай несколько параллельных запросов:
```bash
for i in {1..5}; do
    curl http://localhost &
done
wait
```

### Ожидаемый результат
Запросы должны распределяться более равномерно, учитывая текущую нагрузку.

---

## Упражнение 6: Health Checks

### Задача
Настрой автоматическое исключение упавших серверов.

### Шаги

1. Обнови конфигурацию:
```nginx
upstream backend {
    server 127.0.0.1:8000 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:8001 max_fails=2 fail_timeout=10s;
    server 127.0.0.1:8002 max_fails=2 fail_timeout=10s;
}

server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        proxy_connect_timeout 2s;
        proxy_next_upstream error timeout;
    }
}
```

2. Перезагрузи Nginx.

3. Останови один из серверов:
```bash
# Найди процесс и останови его
pkill -f "port=8001"
```

4. Сделай несколько запросов:
```bash
for i in {1..5}; do
    curl http://localhost
    echo ""
done
```

### Ожидаемый результат
После остановки сервера, Nginx должен перестать отправлять на него запросы и использовать только работающие серверы.

5. Запусти сервер снова и подожди 10 секунд - он должен вернуться в балансировку.

---

## Упражнение 7: Backup сервер

### Задача
Настрой резервный сервер, который используется только если все основные недоступны.

### Шаги

1. Обнови конфигурацию:
```nginx
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002 backup;
}

server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. Перезагрузи Nginx.

3. Останови основные серверы (8000 и 8001):
```bash
pkill -f "port=8000"
pkill -f "port=8001"
```

4. Сделай запрос:
```bash
curl http://localhost
```

### Ожидаемый результат
Запрос должен обрабатываться backup сервером (8002).

5. Запусти основные серверы снова - backup перестанет использоваться.

---

## Упражнение 8: Комбинированная конфигурация

### Задача
Создай полную конфигурацию с:
- Load balancing между 3 серверами
- Health checks
- Статическими файлами
- Логированием

### Шаги

1. Создай конфигурацию:
```nginx
upstream backend {
    least_conn;
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8002 max_fails=3 fail_timeout=30s;
}

log_format detailed '$remote_addr - $remote_user [$time_local] '
                   '"$request" $status $body_bytes_sent '
                   '"$http_referer" "$http_user_agent" '
                   'upstream: $upstream_addr';

server {
    listen 80;
    server_name localhost;

    access_log /var/log/nginx/test.access.log detailed;
    error_log /var/log/nginx/test.error.log;

    location /static/ {
        alias /var/www/static/;
        expires 30d;
    }

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        add_header X-Backend-Server $upstream_addr;
    }
}
```

2. Перезагрузи Nginx.

3. Проверь логи:
```bash
sudo tail -f /var/log/nginx/test.access.log
```

4. Сделай несколько запросов и посмотри, как они распределяются.

### Ожидаемый результат
- Статические файлы отдаются напрямую
- API запросы балансируются между серверами
- В логах видно, на какой сервер пошёл запрос
- В заголовках ответа видно `X-Backend-Server`

---

## Упражнение 9: Отладка и мониторинг

### Задача
Научись отлаживать конфигурацию и мониторить работу Nginx.

### Шаги

1. Добавь endpoint для статуса Nginx:
```nginx
location /nginx_status {
    stub_status on;
    access_log off;
    allow 127.0.0.1;
    deny all;
}
```

2. Проверь статус:
```bash
curl http://localhost/nginx_status
```

3. Проверь логи в реальном времени:
```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

4. Проверь активные соединения:
```bash
sudo netstat -tulpn | grep nginx
```

5. Проверь процессы Nginx:
```bash
ps aux | grep nginx
```

---

## Чеклист для самопроверки

После выполнения упражнений проверь:

- [ ] Могу настроить базовый reverse proxy
- [ ] Понимаю, как работает load balancing
- [ ] Знаю разницу между Round Robin, Least Connections, IP Hash
- [ ] Могу настроить health checks
- [ ] Понимаю, как работают backup серверы
- [ ] Умею отлаживать конфигурацию через логи
- [ ] Знаю, как проверить синтаксис конфигурации
- [ ] Понимаю основные директивы Nginx

---

## Дополнительные задания для практики

### Задание 1: Rate Limiting
Настрой ограничение: максимум 10 запросов в секунду с одного IP.

**Подсказка:** Используй `limit_req_zone` и `limit_req`.

### Задание 2: Разные пути на разные серверы
Настрой так, чтобы:
- `/api/v1/` → сервер 8000
- `/api/v2/` → сервер 8001
- `/api/v3/` → сервер 8002

**Подсказка:** Используй разные `location` блоки.

### Задание 3: Кэширование
Настрой кэширование ответов от API на 5 минут.

**Подсказка:** Используй `proxy_cache_path` и `proxy_cache`.

---

## Полезные команды

```bash
# Проверка конфигурации
sudo nginx -t

# Перезагрузка (без простоя)
sudo systemctl reload nginx

# Полный перезапуск
sudo systemctl restart nginx

# Просмотр статуса
sudo systemctl status nginx

# Просмотр логов
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Проверка портов
sudo netstat -tulpn | grep nginx
sudo ss -tulpn | grep nginx

# Тестирование запросов
curl -v http://localhost
curl -H "Host: example.com" http://localhost
```

---

## Решение проблем

### Проблема: "nginx: [emerg] bind() to 0.0.0.0:80 failed"
**Решение:** Порт 80 уже занят. Проверь: `sudo lsof -i :80`

### Проблема: "502 Bad Gateway"
**Решение:** 
1. Проверь, что backend сервер запущен: `curl http://127.0.0.1:8000`
2. Проверь firewall: `sudo ufw status`
3. Проверь логи: `sudo tail -f /var/log/nginx/error.log`

### Проблема: Изменения не применяются
**Решение:**
1. Проверь синтаксис: `sudo nginx -t`
2. Перезагрузи: `sudo systemctl reload nginx`
3. Проверь, что правильный файл активен: `ls -la /etc/nginx/sites-enabled/`

### Проблема: Permission denied
**Решение:**
- Для статических файлов: `sudo chown -R www-data:www-data /var/www/`
- Для логов: проверь права на `/var/log/nginx/`
