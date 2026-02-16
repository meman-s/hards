# MongoDB: Теория и Практика

## Содержание
1. [Основы запросов](#основы-запросов)
2. [Агрегации](#агрегации)
3. [Join ($lookup)](#join-lookup)
4. [Индексы](#индексы)

---

## Основы запросов

### Базовые операции

#### Find - поиск документов
```python
# Найти все документы
collection.find({})

# Найти с условием
collection.find({"status": "active"})

# Найти один документ
collection.find_one({"name": "John"})

# Сортировка и лимит
collection.find({}).sort("created_at", -1).limit(10)
```

#### Операторы сравнения
- `$eq` - равно
- `$ne` - не равно
- `$gt` - больше
- `$gte` - больше или равно
- `$lt` - меньше
- `$lte` - меньше или равно
- `$in` - входит в массив
- `$nin` - не входит в массив

```python
# Примеры
collection.find({"age": {"$gte": 18, "$lte": 65}})
collection.find({"status": {"$in": ["active", "pending"]}})
collection.find({"tags": {"$nin": ["deleted", "archived"]}})
```

#### Логические операторы
- `$and` - логическое И
- `$or` - логическое ИЛИ
- `$not` - логическое НЕ
- `$nor` - ни одно из условий

```python
collection.find({
    "$and": [
        {"age": {"$gte": 18}},
        {"status": "active"}
    ]
})

collection.find({
    "$or": [
        {"role": "admin"},
        {"role": "moderator"}
    ]
})
```

#### Операторы для массивов
- `$all` - все элементы присутствуют
- `$elemMatch` - хотя бы один элемент соответствует условию
- `$size` - размер массива

```python
collection.find({"tags": {"$all": ["python", "mongodb"]}})
collection.find({"scores": {"$elemMatch": {"$gte": 80}}})
collection.find({"items": {"$size": 3}})
```

#### Операторы для строк
- `$regex` - регулярное выражение
- `$text` - текстовый поиск (требует text index)

```python
collection.find({"name": {"$regex": "^J", "$options": "i"}})
```

#### Update операции
```python
# Обновить один документ
collection.update_one(
    {"_id": ObjectId("...")},
    {"$set": {"status": "active"}}
)

# Обновить несколько документов
collection.update_many(
    {"status": "pending"},
    {"$set": {"status": "active"}}
)

# Операторы обновления
# $set - установить значение
# $unset - удалить поле
# $inc - увеличить числовое значение
# $push - добавить в массив
# $pull - удалить из массива
# $addToSet - добавить в массив (без дубликатов)
```

#### Delete операции
```python
# Удалить один документ
collection.delete_one({"_id": ObjectId("...")})

# Удалить несколько документов
collection.delete_many({"status": "deleted"})
```

---

## Агрегации

Агрегация - это мощный инструмент для обработки данных в MongoDB. Pipeline состоит из стадий, которые обрабатывают документы последовательно.

### Основные стадии pipeline

#### $match - фильтрация
```python
pipeline = [
    {"$match": {"status": "active", "age": {"$gte": 18}}}
]
```

#### $project - выбор и преобразование полей
```python
pipeline = [
    {
        "$project": {
            "name": 1,
            "age": 1,
            "full_name": {"$concat": ["$first_name", " ", "$last_name"]},
            "_id": 0
        }
    }
]
```

#### $group - группировка
```python
pipeline = [
    {
        "$group": {
            "_id": "$category",
            "total": {"$sum": "$price"},
            "count": {"$sum": 1},
            "avg_price": {"$avg": "$price"},
            "max_price": {"$max": "$price"},
            "min_price": {"$min": "$price"}
        }
    }
]
```

#### $sort - сортировка
```python
pipeline = [
    {"$sort": {"created_at": -1}}
]
```

#### $limit и $skip - пагинация
```python
pipeline = [
    {"$skip": 10},
    {"$limit": 20}
]
```

#### $unwind - развертывание массива
```python
pipeline = [
    {"$unwind": "$tags"}
]
```

#### $lookup - объединение коллекций (JOIN)
```python
pipeline = [
    {
        "$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user_info"
        }
    }
]
```

#### $addFields / $set - добавление полей
```python
pipeline = [
    {
        "$addFields": {
            "total": {"$add": ["$price", "$tax"]}
        }
    }
]
```

#### $facet - множественные pipeline
```python
pipeline = [
    {
        "$facet": {
            "by_category": [
                {"$group": {"_id": "$category", "count": {"$sum": 1}}}
            ],
            "by_status": [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}}
            ]
        }
    }
]
```

#### $count - подсчет документов
```python
pipeline = [
    {"$match": {"status": "active"}},
    {"$count": "active_count"}
]
```

### Примеры сложных агрегаций

#### Подсчет статистики по категориям
```python
pipeline = [
    {"$match": {"status": "active"}},
    {
        "$group": {
            "_id": "$category",
            "total_revenue": {"$sum": "$price"},
            "order_count": {"$sum": 1},
            "avg_price": {"$avg": "$price"}
        }
    },
    {"$sort": {"total_revenue": -1}},
    {"$limit": 10}
]
```

#### Анализ временных рядов
```python
pipeline = [
    {
        "$group": {
            "_id": {
                "year": {"$year": "$created_at"},
                "month": {"$month": "$created_at"},
                "day": {"$dayOfMonth": "$created_at"}
            },
            "count": {"$sum": 1},
            "total": {"$sum": "$amount"}
        }
    },
    {"$sort": {"_id": 1}}
]
```

---

## Join ($lookup)

`$lookup` позволяет выполнять операции, аналогичные JOIN в реляционных БД.

### Базовый $lookup
```python
pipeline = [
    {
        "$lookup": {
            "from": "users",              # коллекция для объединения
            "localField": "user_id",      # поле в текущей коллекции
            "foreignField": "_id",         # поле в объединяемой коллекции
            "as": "user"                  # имя поля для результата
        }
    }
]
```

### $lookup с условиями ($match)
```python
pipeline = [
    {
        "$lookup": {
            "from": "orders",
            "let": {"user_id": "$_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$user_id", "$$user_id"]}}},
                {"$match": {"status": "completed"}},
                {"$project": {"total": 1, "created_at": 1}}
            ],
            "as": "completed_orders"
        }
    }
]
```

### Множественный $lookup
```python
pipeline = [
    {
        "$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user"
        }
    },
    {
        "$lookup": {
            "from": "products",
            "localField": "product_id",
            "foreignField": "_id",
            "as": "product"
        }
    },
    {
        "$unwind": "$user"
    },
    {
        "$unwind": "$product"
    }
]
```

### $lookup с $unwind для одного документа
```python
pipeline = [
    {
        "$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user"
        }
    },
    {
        "$unwind": {
            "path": "$user",
            "preserveNullAndEmptyArrays": True  # оставить документ даже если нет совпадений
        }
    }
]
```

### Пример: Заказы с информацией о пользователе и товарах
```python
pipeline = [
    {
        "$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "_id",
            "as": "user"
        }
    },
    {
        "$unwind": "$user"
    },
    {
        "$lookup": {
            "from": "products",
            "localField": "items.product_id",
            "foreignField": "_id",
            "as": "product_details"
        }
    },
    {
        "$project": {
            "order_id": 1,
            "user_name": "$user.name",
            "user_email": "$user.email",
            "items": 1,
            "product_details": 1,
            "total": 1
        }
    }
]
```

---

## Индексы

Индексы ускоряют выполнение запросов и улучшают производительность.

### Создание индексов

#### Одиночный индекс
```python
# Создать индекс на одно поле
collection.create_index("email")
collection.create_index("created_at")

# Уникальный индекс
collection.create_index("email", unique=True)

# Индекс с направлением (1 - по возрастанию, -1 - по убыванию)
collection.create_index([("created_at", -1)])
```

#### Compound индекс (составной)
```python
# Индекс на несколько полей
collection.create_index([("user_id", 1), ("created_at", -1)])

# Важно: порядок полей имеет значение!
# Индекс (user_id, created_at) эффективен для запросов:
# - user_id
# - user_id + created_at
# НО НЕ эффективен для запросов только по created_at
```

#### Partial индекс
Частичный индекс создается только для документов, соответствующих условию.

```python
# Индекс только для активных пользователей
collection.create_index(
    [("email", 1)],
    partialFilterExpression={"status": "active"}
)

# Индекс для документов с определенным диапазоном значений
collection.create_index(
    [("score", 1)],
    partialFilterExpression={"score": {"$gte": 0}}
)
```

#### Text индекс (полнотекстовый поиск)
```python
# Создать text индекс на одно поле
collection.create_index([("title", "text")])

# Text индекс на несколько полей
collection.create_index([
    ("title", "text"),
    ("description", "text"),
    ("content", "text")
])

# Использование text поиска
collection.find({"$text": {"$search": "mongodb python"}})
```

#### TTL индекс (Time To Live)
```python
# Автоматическое удаление документов через 3600 секунд
collection.create_index(
    [("created_at", 1)],
    expireAfterSeconds=3600
)
```

#### Sparse индекс
```python
# Индекс только для документов, где поле существует
collection.create_index(
    [("optional_field", 1)],
    sparse=True
)
```

### Управление индексами

#### Просмотр индексов
```python
# Список всех индексов
indexes = collection.list_indexes()
for index in indexes:
    print(index)

# Информация об индексах
collection.index_information()
```

#### Удаление индексов
```python
# Удалить индекс по имени
collection.drop_index("email_1")

# Удалить все индексы (кроме _id)
collection.drop_indexes()
```

### Стратегии использования индексов

#### Правило ESR (Equality, Sort, Range)
При создании compound индекса порядок полей должен быть:
1. **E**quality (равенство) - поля с точным совпадением
2. **S**ort (сортировка) - поля для сортировки
3. **R**ange (диапазон) - поля с операторами сравнения

```python
# Запрос: найти по статусу, отсортировать по дате, фильтр по цене
# Индекс должен быть: (status, created_at, price)
collection.create_index([("status", 1), ("created_at", -1), ("price", 1)])

# Запрос
collection.find({
    "status": "active",
    "price": {"$gte": 100}
}).sort("created_at", -1)
```

#### Анализ использования индексов
```python
# Explain запроса
explain_result = collection.find({"email": "test@example.com"}).explain()
print(explain_result["executionStats"])

# Проверить, используется ли индекс
if explain_result["executionStats"]["executionStages"]["stage"] == "IXSCAN":
    print("Индекс используется!")
```

### Рекомендации по индексам

1. **Не создавайте слишком много индексов** - каждый индекс замедляет запись
2. **Используйте compound индексы** для запросов с несколькими полями
3. **Следуйте правилу ESR** при создании compound индексов
4. **Используйте partial индексы** для экономии места
5. **Мониторьте использование индексов** через explain()
6. **Создавайте индексы на часто используемых полях** в WHERE и ORDER BY

---

## Оптимизация запросов

### Использование проекции
```python
# Выбирать только нужные поля
collection.find({"status": "active"}, {"name": 1, "email": 1, "_id": 0})
```

### Использование limit
```python
# Ограничивать количество результатов
collection.find({}).limit(100)
```

### Избегание $where
```python
# Плохо (медленно)
collection.find({"$where": "this.age > 18"})

# Хорошо (быстро)
collection.find({"age": {"$gt": 18}})
```

### Использование covered queries
Запрос считается "covered", если все поля в результате находятся в индексе.

```python
# Индекс
collection.create_index([("user_id", 1), ("status", 1), ("created_at", 1)])

# Covered query
collection.find(
    {"user_id": 123, "status": "active"},
    {"user_id": 1, "status": 1, "created_at": 1, "_id": 0}
)
```

---

## Заключение

MongoDB предоставляет мощные инструменты для работы с данными:
- Гибкие запросы с множеством операторов
- Мощные агрегационные pipeline для сложной обработки данных
- $lookup для объединения коллекций
- Различные типы индексов для оптимизации производительности

Правильное использование этих инструментов позволяет создавать эффективные и масштабируемые приложения.
