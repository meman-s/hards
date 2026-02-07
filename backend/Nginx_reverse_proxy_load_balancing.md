# Nginx: Reverse Proxy и Load Balancing

## 1. Зачем нужен

**Nginx** — веб-сервер и reverse proxy, используемый для:

- Обработки статических файлов
- Reverse proxy для приложений
- Load balancing между серверами
- SSL/TLS терминация
- Кэширование
- Сжатие ответов

---

## 2. Reverse Proxy

### 2.1 Базовая конфигурация

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2.2 Проксирование FastAPI приложения

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
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
}
```

### 2.3 Проксирование WebSocket

```nginx
server {
    listen 80;
    server_name ws.example.com;

    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        proxy_read_timeout 86400;
    }
}
```

### 2.4 Проксирование статических файлов

```nginx
server {
    listen 80;
    server_name example.com;

    location /static/ {
        alias /var/www/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

---

## 3. Load Balancing

### 3.1 Базовая конфигурация

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
    }
}
```

### 3.2 Методы балансировки

#### Round Robin (по умолчанию)

```nginx
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

#### Least Connections

```nginx
upstream backend {
    least_conn;
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

#### IP Hash

```nginx
upstream backend {
    ip_hash;
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

#### Weighted

```nginx
upstream backend {
    server 127.0.0.1:8000 weight=3;
    server 127.0.0.1:8001 weight=2;
    server 127.0.0.1:8002 weight=1;
}
```

### 3.3 Health checks

```nginx
upstream backend {
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8002 backup;
}
```

### 3.4 Резервные серверы

```nginx
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002 backup;
    server 127.0.0.1:8003 down;
}
```

---

## 4. SSL/TLS

### 4.1 Базовая SSL конфигурация

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/ssl/certs/example.com.crt;
    ssl_certificate_key /etc/ssl/private/example.com.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}

server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

### 4.2 Let's Encrypt с Certbot

```bash
sudo certbot --nginx -d example.com
```

Автоматически обновляет конфигурацию Nginx.

### 4.3 SSL оптимизация

```nginx
server {
    listen 443 ssl http2;
    
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;
}
```

---

## 5. Кэширование

### 5.1 Кэширование ответов

```nginx
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

server {
    listen 80;
    
    location / {
        proxy_cache my_cache;
        proxy_cache_valid 200 60m;
        proxy_cache_valid 404 1m;
        proxy_cache_key "$scheme$request_method$host$request_uri";
        
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### 5.2 Условное кэширование

```nginx
location /api/ {
    proxy_cache my_cache;
    proxy_cache_bypass $http_cache_control;
    proxy_no_cache $http_cache_control;
    
    proxy_pass http://127.0.0.1:8000;
}
```

---

## 6. Сжатие

### 6.1 Gzip сжатие

```nginx
gzip on;
gzip_vary on;
gzip_min_length 1000;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

server {
    listen 80;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### 6.2 Brotli сжатие

```nginx
brotli on;
brotli_comp_level 6;
brotli_types text/plain text/css application/json application/javascript text/xml application/xml;
```

---

## 7. Rate Limiting

### 7.1 Ограничение запросов

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    listen 80;
    
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### 7.2 Ограничение соединений

```nginx
limit_conn_zone $binary_remote_addr zone=conn_limit:10m;

server {
    listen 80;
    
    location / {
        limit_conn conn_limit 10;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

---

## 8. Логирование

### 8.1 Кастомные логи

```nginx
log_format detailed '$remote_addr - $remote_user [$time_local] '
                   '"$request" $status $body_bytes_sent '
                   '"$http_referer" "$http_user_agent" '
                   '$request_time $upstream_response_time';

server {
    listen 80;
    access_log /var/log/nginx/access.log detailed;
    error_log /var/log/nginx/error.log;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

---

## 9. Безопасность

### 9.1 Скрытие версии Nginx

```nginx
server_tokens off;
```

### 9.2 Защита от DDoS

```nginx
limit_req_zone $binary_remote_addr zone=ddos:10m rate=1r/s;

server {
    listen 80;
    
    location / {
        limit_req zone=ddos burst=5;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### 9.3 Ограничение размера запроса

```nginx
client_max_body_size 10M;
```

### 9.4 Блокировка по IP

```nginx
location /admin/ {
    deny 192.168.1.100;
    allow 192.168.1.0/24;
    deny all;
    
    proxy_pass http://127.0.0.1:8000;
}
```

---

## 10. Пример полной конфигурации

```nginx
upstream backend {
    least_conn;
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:8002 backup;
}

limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g;

server {
    listen 80;
    server_name api.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.example.com;

    ssl_certificate /etc/ssl/certs/api.example.com.crt;
    ssl_certificate_key /etc/ssl/private/api.example.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    access_log /var/log/nginx/api.access.log;
    error_log /var/log/nginx/api.error.log;

    client_max_body_size 10M;

    location /static/ {
        alias /var/www/static/;
        expires 30d;
    }

    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_cache my_cache;
        proxy_cache_valid 200 60m;
        
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

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 11. Best Practices

### 11.1 Разделение конфигураций

```nginx
include /etc/nginx/conf.d/*.conf;
include /etc/nginx/sites-enabled/*;
```

### 11.2 Мониторинг

```nginx
location /nginx_status {
    stub_status on;
    access_log off;
    allow 127.0.0.1;
    deny all;
}
```

### 11.3 Оптимизация производительности

```nginx
worker_processes auto;
worker_connections 1024;

sendfile on;
tcp_nopush on;
tcp_nodelay on;
keepalive_timeout 65;
```

### 11.4 Тестирование конфигурации

```bash
sudo nginx -t
sudo systemctl reload nginx
```
