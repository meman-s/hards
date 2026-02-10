# MongoDB: Теория и Практика

Материалы по изучению MongoDB: запросы, агрегации, Join ($lookup), индексы.

## Структура

- `MongoDB_теория.md` - теоретический материал
- `MongoDB_тестовое_задание_запрос_с_разбором.md` - задания с описанием решений
- `mongodb_example.py` - практические примеры и решения на Python

## Установка

1. Установите MongoDB:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install mongodb
   
   # Или используйте Docker
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

2. Установите зависимости:
   ```bash
   pip install pymongo
   ```

3. Запустите MongoDB сервер:
   ```bash
   mongod
   ```

## Использование

1. Откройте файл `mongodb_example.py`
2. Раскомментируйте нужную функцию `task_X_...()`
3. Запустите скрипт:
   ```bash
   python mongodb_example.py
   ```

## Содержание заданий

1. **Базовые запросы** - find, update, delete с различными операторами
2. **Агрегации** - статистика по заказам, группировки, вычисления
3. **$lookup** - объединение коллекций (JOIN)
4. **Индексы** - compound, partial, text, TTL индексы
5. **Сложная аналитика** - комплексные агрегации с несколькими коллекциями
6. **Оптимизация запросов** - covered queries, explain(), стратегии индексов
7. **Массивы и вложенные документы** - работа с массивами, $elemMatch, $push
8. **Транзакции** - атомарные операции, переводы между счетами
9. **Геопространственные запросы** - 2dsphere индексы, поиск по радиусу
10. **Полнотекстовый поиск** - text индексы, поиск по релевантности

## Примеры использования

### Базовый запрос
```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['test_db']
collection = db['users']

# Найти всех активных пользователей
result = collection.find({"status": "active"})
for user in result:
    print(user)
```

### Агрегация
```python
pipeline = [
    {"$match": {"status": "active"}},
    {"$group": {
        "_id": "$category",
        "total": {"$sum": "$price"}
    }},
    {"$sort": {"total": -1}}
]
result = collection.aggregate(pipeline)
```

### $lookup (JOIN)
```python
pipeline = [
    {
        "$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user"
        }
    }
]
result = collection.aggregate(pipeline)
```

### Создание индекса
```python
# Compound индекс
collection.create_index([("status", 1), ("created_at", -1)])

# Partial индекс
collection.create_index(
    [("email", 1)],
    partialFilterExpression={"status": "active"}
)

# Text индекс
collection.create_index([("title", "text"), ("content", "text")])
```

## Полезные ссылки

- [Официальная документация MongoDB](https://www.mongodb.com/docs/)
- [PyMongo документация](https://pymongo.readthedocs.io/)
- [MongoDB University](https://university.mongodb.com/)
