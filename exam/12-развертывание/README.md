# 12. Развертывание

Материалы для изучения развертывания приложений: Docker, CI/CD, RabbitMQ.

## 📁 Структура

```
12-развертывание/
├── README.md          # Этот файл
├── вопросы.md         # Вопросы для самопроверки
├── задания.md         # Практические задания
├── теория/            # Теоретические материалы
│   ├── docker/
│   │   ├── обучение.md
│   │   ├── практика.md
│   │   ├── задания-dockerfile.md
│   │   ├── задания-compose.md
│   │   └── примеры/
│   │       ├── dockerfile.1
│   │       ├── dockerfile.2
│   │       ├── dockerfile.3
│   │       ├── dockerfile.4
│   │       ├── docker-compose.1.yml
│   │       ├── docker-compose.2.yml
│   │       ├── docker-compose.3.yml
│   │       └── docker-compose.4.yml
│   └── compose/
│       └── практика.md
└── практика/          # Практические упражнения
    ├── README.md
    └── примеры/
        └── docker-compose.yml
```

## 📚 Содержание

- Docker (multi-stage builds, secrets, SSH mount)
- Docker Compose (healthcheck, services, networks, volumes)
- RabbitMQ (очереди задач, Pub/Sub)
- Семантическое версионирование (SemVer)
- CI/CD (автоматизация тестов, сборка, развертывание)

## 🔗 Связанные темы

- [11. Тестирование](../11-тестирование/) - предыдущий раздел (тесты в CI/CD)
- [08. Backend](../08-backend/) - развертывание backend приложений
