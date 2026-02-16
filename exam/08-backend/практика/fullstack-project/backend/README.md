# Backend (FastAPI)

Пока работает на in-memory хранилище: GET/POST /api/items, GET /api/health. Фронт с ним уже обменивается данными.

Чтобы подключить свои БД (PostgreSQL, MongoDB, Redis), см. **DB_SPEC.md** в корне `fullstack-exercise/`: что создать в каждой БД, какие триггеры и ключи Redis использовать. После этого замени в этом проекте хранение на вызовы к твоим БД.

## Запуск

```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Документация API: http://localhost:8000/docs
