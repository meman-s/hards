# Docker Compose Практика: Healthcheck, Services, Networks, Volumes

## 1. HEALTHCHECK (Проверка здоровья)

Healthcheck позволяет Docker Compose проверять работоспособность контейнеров и автоматически перезапускать неработающие.

### 1.1. Базовый healthcheck в docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    ports:
      - "80:80"
```

### 1.2. Healthcheck для веб-приложения

```yaml
version: '3.8'

services:
  api:
    build: .
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
```

### 1.3. Healthcheck для базы данных (PostgreSQL)

```yaml
version: '3.8'

services:
  postgres:
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
      start_period: 30s
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### 1.4. Healthcheck для Redis

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    volumes:
      - redis_data:/data
```

### 1.5. Healthcheck для MySQL

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: mydb
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-prootpassword"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
    volumes:
      - mysql_data:/var/lib/mysql
```

### 1.6. Healthcheck с кастомным скриптом

```yaml
version: '3.8'

services:
  app:
    build: .
    healthcheck:
      test: ["CMD", "/app/healthcheck.sh"]
      interval: 30s
      timeout: 10s
      retries: 3
    volumes:
      - ./healthcheck.sh:/app/healthcheck.sh
```

healthcheck.sh:
```bash
#!/bin/sh
curl -f http://localhost:8000/health || exit 1
```

### 1.7. Healthcheck с зависимостями

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  worker:
    build: .
    command: celery -A app worker
    depends_on:
      db:
        condition: service_healthy
      api:
        condition: service_healthy
```

## 2. SERVICES (Сервисы)

Services определяют контейнеры, которые будут запущены в составе приложения.

### 2.1. Базовый сервис

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
    environment:
      - NGINX_HOST=localhost
      - NGINX_PORT=80
```

### 2.2. Сервис с build

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        BUILD_VERSION: "1.0.0"
    ports:
      - "8000:8000"
    environment:
      - ENV=production
```

### 2.3. Сервис с несколькими командами

```yaml
version: '3.8'

services:
  app:
    build: .
    command: >
      sh -c "
        python manage.py migrate &&
        python manage.py collectstatic --noinput &&
        gunicorn app.wsgi:application --bind 0.0.0.0:8000
      "
    ports:
      - "8000:8000"
```

### 2.4. Сервис с restart policies

```yaml
version: '3.8'

services:
  app:
    build: .
    restart: always  # always | unless-stopped | on-failure | no
    ports:
      - "8000:8000"
```

### 2.5. Сервис с depends_on

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mydb

  api:
    build: .
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://user:password@db:5432/mydb
```

### 2.6. Сервис с environment файлом

```yaml
version: '3.8'

services:
  app:
    build: .
    env_file:
      - .env
      - .env.production
    environment:
      - DEBUG=false
    ports:
      - "8000:8000"
```

### 2.7. Сервис с labels

```yaml
version: '3.8'

services:
  app:
    build: .
    labels:
      - "com.example.description=My Application"
      - "com.example.version=1.0.0"
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`app.example.com`)"
```

### 2.8. Сервис с deploy (для Docker Swarm)

```yaml
version: '3.8'

services:
  app:
    image: myapp:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        max_attempts: 3
    ports:
      - "8000:8000"
```

### 2.9. Сервис с profiles

```yaml
version: '3.8'

services:
  app:
    build: .
    profiles:
      - production
    ports:
      - "8000:8000"

  dev-tools:
    image: node:18-alpine
    profiles:
      - dev
    volumes:
      - .:/app
    command: npm run dev
```

Использование:
```bash
# Запустить только production сервисы
docker compose --profile production up

# Запустить dev сервисы
docker compose --profile dev up
```

## 3. NETWORKS (Сети)

Networks позволяют изолировать и организовывать коммуникацию между контейнерами.

### 3.1. Базовая сеть

```yaml
version: '3.8'

services:
  web:
    image: nginx:alpine
    networks:
      - frontend

  api:
    build: .
    networks:
      - frontend
      - backend

  db:
    image: postgres:15-alpine
    networks:
      - backend

networks:
  frontend:
  backend:
```

### 3.2. Внешняя сеть

```yaml
version: '3.8'

services:
  app:
    build: .
    networks:
      - existing_network

networks:
  existing_network:
    external: true
    name: my_existing_network
```

### 3.3. Сеть с кастомными настройками

```yaml
version: '3.8'

services:
  app1:
    image: nginx:alpine
    networks:
      custom_net:
        ipv4_address: 172.20.0.10

  app2:
    image: nginx:alpine
    networks:
      custom_net:
        ipv4_address: 172.20.0.11

networks:
  custom_net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### 3.4. Изоляция сервисов через сети

```yaml
version: '3.8'

services:
  # Публичные сервисы
  nginx:
    image: nginx:alpine
    networks:
      - public
    ports:
      - "80:80"

  # Внутренние сервисы
  api:
    build: .
    networks:
      - public
      - internal

  db:
    image: postgres:15-alpine
    networks:
      - internal
    # Нет ports - доступен только внутри сети

networks:
  public:
  internal:
    internal: true  # Изолированная сеть без доступа в интернет
```

### 3.5. Сеть с driver overlay (для Swarm)

```yaml
version: '3.8'

services:
  app:
    image: myapp:latest
    networks:
      - overlay_net

networks:
  overlay_net:
    driver: overlay
    attachable: true
```

### 3.6. Сеть с DNS

```yaml
version: '3.8'

services:
  app1:
    image: nginx:alpine
    networks:
      - app_network
    hostname: app1

  app2:
    image: nginx:alpine
    networks:
      - app_network
    hostname: app2
    # Может обращаться к app1 по имени: app1

networks:
  app_network:
    driver: bridge
```

## 4. VOLUMES (Тома)

Volumes обеспечивают постоянное хранение данных и обмен файлами между контейнерами и хостом.

### 4.1. Именованный том

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: mydb

volumes:
  postgres_data:
```

### 4.2. Bind mount (монтирование директории)

```yaml
version: '3.8'

services:
  app:
    build: .
    volumes:
      - ./src:/app/src
      - ./config:/app/config:ro  # read-only
    ports:
      - "8000:8000"
```

### 4.3. Анонимный том

```yaml
version: '3.8'

services:
  app:
    image: node:18-alpine
    volumes:
      - /app/node_modules  # Анонимный том
      - .:/app
    command: npm start
```

### 4.4. Том с драйвером

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /path/to/host/directory
```

### 4.5. Внешний том

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    volumes:
      - existing_volume:/var/lib/postgresql/data

volumes:
  existing_volume:
    external: true
    name: my_existing_volume
```

### 4.6. Общий том между сервисами

```yaml
version: '3.8'

services:
  app1:
    image: nginx:alpine
    volumes:
      - shared_data:/shared

  app2:
    image: nginx:alpine
    volumes:
      - shared_data:/shared

volumes:
  shared_data:
```

### 4.7. Том с правами доступа

```yaml
version: '3.8'

services:
  app:
    build: .
    user: "1000:1000"
    volumes:
      - app_data:/app/data
    command: python app.py

volumes:
  app_data:
```

### 4.8. Том для временных файлов (tmpfs)

```yaml
version: '3.8'

services:
  app:
    image: nginx:alpine
    tmpfs:
      - /tmp
      - /var/cache/nginx:size=100m
```

## 5. ПОЛНЫЕ ПРАКТИЧЕСКИЕ ПРИМЕРЫ

### 5.1. Веб-приложение с базой данных

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d myapp"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - backend

  api:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - frontend
      - backend
    volumes:
      - ./uploads:/app/uploads

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./static:/usr/share/nginx/html/static:ro
    depends_on:
      api:
        condition: service_healthy
    networks:
      - frontend

volumes:
  postgres_data:
  redis_data:

networks:
  frontend:
  backend:
    internal: true
```

### 5.2. Микросервисная архитектура

```yaml
version: '3.8'

services:
  # База данных
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - db_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Кэш
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    networks:
      - cache_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s

  # API Gateway
  gateway:
    build: ./gateway
    ports:
      - "8000:8000"
    depends_on:
      - auth_service
      - user_service
      - order_service
    networks:
      - api_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s

  # Сервис аутентификации
  auth_service:
    build: ./services/auth
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - api_network
      - db_network
      - cache_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s

  # Сервис пользователей
  user_service:
    build: ./services/user
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/myapp
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - api_network
      - db_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s

  # Сервис заказов
  order_service:
    build: ./services/order
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - api_network
      - db_network
      - cache_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s

volumes:
  postgres_data:
  redis_data:

networks:
  api_network:
  db_network:
    internal: true
  cache_network:
    internal: true
```

### 5.3. Разработка с hot-reload

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: myapp
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - dev_network

  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    volumes:
      - .:/app
      - /app/node_modules  # Исключить node_modules из синхронизации
    ports:
      - "3000:3000"
      - "9229:9229"  # Node.js debug port
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/myapp
    depends_on:
      - db
    networks:
      - dev_network
    command: npm run dev

volumes:
  postgres_data:

networks:
  dev_network:
```

### 5.4. Production-ready конфигурация

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - backend
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  app:
    build:
      context: .
      dockerfile: Dockerfile.prod
    restart: always
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}
      - NODE_ENV=production
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    networks:
      - backend
      - frontend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_files:/usr/share/nginx/html/static:ro
    depends_on:
      app:
        condition: service_healthy
    networks:
      - frontend
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

volumes:
  postgres_data:
  static_files:

networks:
  frontend:
  backend:
    internal: true
```

## 6. КОМАНДЫ ДЛЯ РАБОТЫ

### 6.1. Базовые команды

```bash
# Запустить все сервисы
docker compose up

# Запустить в фоне
docker compose up -d

# Остановить все сервисы
docker compose down

# Остановить и удалить volumes
docker compose down -v

# Пересобрать и запустить
docker compose up --build

# Показать логи
docker compose logs

# Логи конкретного сервиса
docker compose logs -f api

# Выполнить команду в контейнере
docker compose exec api python manage.py migrate

# Показать статус
docker compose ps

# Показать использование ресурсов
docker compose top
```

### 6.2. Работа с healthcheck

```bash
# Проверить статус healthcheck
docker compose ps

# Показать детали healthcheck
docker inspect <container_id> | grep -A 10 Health
```

### 6.3. Работа с volumes

```bash
# Создать volume
docker volume create my_volume

# Показать все volumes
docker volume ls

# Показать детали volume
docker volume inspect my_volume

# Удалить volume
docker volume rm my_volume

# Удалить неиспользуемые volumes
docker volume prune
```

### 6.4. Работа с networks

```bash
# Показать все сети
docker network ls

# Показать детали сети
docker network inspect <network_name>

# Создать внешнюю сеть
docker network create my_network

# Удалить сеть
docker network rm my_network
```
