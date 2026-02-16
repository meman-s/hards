from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from datetime import datetime, timedelta
from bson import ObjectId
from bson.errors import InvalidId


client = MongoClient('mongodb://localhost:27017/')
db = client['test_db']


def task_1_basic_queries():
    """Задание 1: Базовые запросы"""
    users = db['users']

    users.insert_many([
        {
            "name": "Иван",
            "email": "ivan@example.com",
            "age": 25,
            "status": "active",
            "tags": ["python", "mongodb"],
            "created_at": datetime.now()
        },
        {
            "name": "Анна",
            "email": "anna@example.com",
            "age": 30,
            "status": "active",
            "tags": ["python", "fastapi"],
            "created_at": datetime.now()
        },
        {
            "name": "Петр",
            "email": "petr@example.com",
            "age": 17,
            "status": "inactive",
            "tags": ["javascript"],
            "created_at": datetime.now()
        },
        {
            "name": "Мария",
            "email": "maria@example.com",
            "age": 105,
            "status": "active",
            "tags": ["python", "mongodb", "redis"],
            "created_at": datetime.now()
        }
    ])

    print("=== Задача 1: Найти всех активных пользователей старше 18 лет ===")
    result = users.find({
        "status": "active",
        "age": {"$gt": 18}
    })
    for user in result:
        print(f"  {user['name']} - {user['age']} лет")

    print("\n=== Задача 2: Найти пользователей с тегами 'python' и 'mongodb' ===")
    result = users.find({
        "tags": {"$all": ["python", "mongodb"]}
    })
    for user in result:
        print(f"  {user['name']} - теги: {user['tags']}")

    print("\n=== Задача 3: Обновить статус всех неактивных пользователей ===")
    result = users.update_many(
        {"status": {"$ne": "active"}},
        {"$set": {"status": "inactive"}}
    )
    print(f"  Обновлено документов: {result.modified_count}")

    print("\n=== Задача 4: Удалить пользователей старше 100 лет ===")
    result = users.delete_many({"age": {"$gt": 100}})
    print(f"  Удалено документов: {result.deleted_count}")


def task_2_aggregations():
    """Задание 2: Агрегации - Статистика по заказам"""
    orders = db['orders']

    orders.insert_many([
        {
            "user_id": ObjectId(),
            "items": [
                {"product_id": ObjectId(), "quantity": 2, "price": 100},
                {"product_id": ObjectId(), "quantity": 1, "price": 50}
            ],
            "status": "completed",
            "created_at": datetime.now() - timedelta(days=1),
            "total": 250
        },
        {
            "user_id": ObjectId(),
            "items": [
                {"product_id": ObjectId(), "quantity": 3, "price": 200}
            ],
            "status": "completed",
            "created_at": datetime.now() - timedelta(days=2),
            "total": 600
        },
        {
            "user_id": ObjectId(),
            "items": [
                {"product_id": ObjectId(), "quantity": 1, "price": 150}
            ],
            "status": "pending",
            "created_at": datetime.now(),
            "total": 150
        }
    ])

    print("=== Задача 1: Общая сумма всех завершенных заказов ===")
    pipeline = [
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": None,
            "total_revenue": {"$sum": "$total"}
        }}
    ]
    result = list(orders.aggregate(pipeline))
    if result:
        print(f"  Общая сумма: {result[0]['total_revenue']}")

    print("\n=== Задача 2: Средний чек по статусам заказов ===")
    pipeline = [
        {"$group": {
            "_id": "$status",
            "avg_total": {"$avg": "$total"},
            "count": {"$sum": 1}
        }},
        {"$sort": {"avg_total": -1}}
    ]
    result = list(orders.aggregate(pipeline))
    for item in result:
        print(
            f"  {item['_id']}: средний чек = {item['avg_total']:.2f}, количество = {item['count']}")

    print("\n=== Задача 3: Топ-5 пользователей по сумме заказов ===")
    pipeline = [
        {"$match": {"status": "completed"}},
        {"$group": {
            "_id": "$user_id",
            "total_spent": {"$sum": "$total"},
            "order_count": {"$sum": 1}
        }},
        {"$sort": {"total_spent": -1}},
        {"$limit": 5}
    ]
    result = list(orders.aggregate(pipeline))
    for item in result:
        print(
            f"  User ID: {item['_id']}, потрачено: {item['total_spent']}, заказов: {item['order_count']}")

    print("\n=== Задача 4: Количество заказов по месяцам ===")
    pipeline = [
        {"$group": {
            "_id": {
                "year": {"$year": "$created_at"},
                "month": {"$month": "$created_at"}
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    result = list(orders.aggregate(pipeline))
    for item in result:
        print(
            f"  {item['_id']['year']}-{item['_id']['month']:02d}: {item['count']} заказов")


def task_3_lookup():
    """Задание 3: $lookup - Объединение коллекций"""
    users = db['users_lookup']
    orders = db['orders_lookup']
    products = db['products_lookup']

    user1_id = ObjectId()
    user2_id = ObjectId()
    product1_id = ObjectId()
    product2_id = ObjectId()

    users.insert_many([
        {"_id": user1_id, "name": "Иван", "email": "ivan@example.com"},
        {"_id": user2_id, "name": "Анна", "email": "anna@example.com"}
    ])

    products.insert_many([
        {"_id": product1_id, "name": "Товар 1", "price": 100},
        {"_id": product2_id, "name": "Товар 2", "price": 200}
    ])

    orders.insert_many([
        {
            "user_id": user1_id,
            "items": [
                {"product_id": product1_id, "quantity": 2},
                {"product_id": product2_id, "quantity": 1}
            ],
            "total": 400,
            "status": "completed"
        },
        {
            "user_id": user2_id,
            "items": [
                {"product_id": product1_id, "quantity": 1}
            ],
            "total": 100,
            "status": "completed"
        }
    ])

    print("=== Задача 1: Найти все заказы с информацией о пользователе ===")
    pipeline = [
        {
            "$lookup": {
                "from": "users_lookup",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": "$user"}
    ]
    result = list(orders.aggregate(pipeline))
    for order in result:
        print(
            f"  Заказ на сумму {order['total']} от пользователя {order['user']['name']}")

    print("\n=== Задача 2: Найти заказы с информацией о пользователе и товарах ===")
    pipeline = [
        {
            "$lookup": {
                "from": "users_lookup",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {"$unwind": "$items"},
        {
            "$lookup": {
                "from": "products_lookup",
                "localField": "items.product_id",
                "foreignField": "_id",
                "as": "product"
            }
        },
        {"$unwind": "$product"},
        {
            "$group": {
                "_id": "$_id",
                "user_name": {"$first": "$user.name"},
                "total": {"$first": "$total"},
                "items": {"$push": {
                    "product_name": "$product.name",
                    "quantity": "$items.quantity",
                    "price": "$product.price"
                }}
            }
        }
    ]
    result = list(orders.aggregate(pipeline))
    for order in result:
        print(f"  Заказ от {order['user_name']}, сумма: {order['total']}")
        for item in order['items']:
            print(
                f"    - {item['product_name']}: {item['quantity']} шт. по {item['price']}")

    print("\n=== Задача 3: Найти пользователей с количеством их заказов ===")
    pipeline = [
        {
            "$lookup": {
                "from": "orders_lookup",
                "localField": "_id",
                "foreignField": "user_id",
                "as": "orders"
            }
        },
        {
            "$project": {
                "name": 1,
                "email": 1,
                "order_count": {"$size": "$orders"},
                "total_spent": {"$sum": "$orders.total"}
            }
        }
    ]
    result = list(users.aggregate(pipeline))
    for user in result:
        print(
            f"  {user['name']}: {user['order_count']} заказов, потрачено: {user['total_spent']}")

    print("\n=== Задача 4: Найти товары с количеством раз, когда они были заказаны ===")
    pipeline = [
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$items.product_id",
                "times_ordered": {"$sum": 1},
                "total_quantity": {"$sum": "$items.quantity"}
            }
        },
        {
            "$lookup": {
                "from": "products_lookup",
                "localField": "_id",
                "foreignField": "_id",
                "as": "product"
            }
        },
        {"$unwind": "$product"},
        {
            "$project": {
                "product_name": "$product.name",
                "times_ordered": 1,
                "total_quantity": 1
            }
        }
    ]
    result = list(orders.aggregate(pipeline))
    for item in result:
        print(
            f"  {item['product_name']}: заказан {item['times_ordered']} раз, всего {item['total_quantity']} шт.")


def task_4_indexes():
    """Задание 4: Индексы"""
    products = db['products_indexes']

    products.insert_many([
        {
            "name": "Товар 1",
            "category": "Электроника",
            "price": 1000,
            "status": "active",
            "created_at": datetime.now(),
            "description": "Описание товара 1"
        },
        {
            "name": "Товар 2",
            "category": "Одежда",
            "price": 500,
            "status": "active",
            "created_at": datetime.now(),
            "description": "Описание товара 2"
        }
    ])

    print("=== Задача 1: Compound индекс для запросов по категории и статусу с сортировкой по цене ===")
    try:
        products.create_index([
            ("category", 1),
            ("status", 1),
            ("price", 1)
        ])
        print("  Индекс создан: (category, status, price)")
    except Exception as e:
        print(f"  Ошибка: {e}")

    print("\n=== Задача 2: Partial индекс для активных товаров на поле name ===")
    try:
        products.create_index(
            [("name", 1)],
            partialFilterExpression={"status": "active"}
        )
        print("  Partial индекс создан: name (только для status='active')")
    except Exception as e:
        print(f"  Ошибка: {e}")

    print("\n=== Задача 3: Text индекс для поиска по name и description ===")
    try:
        products.create_index([
            ("name", "text"),
            ("description", "text")
        ])
        print("  Text индекс создан на поля: name, description")
    except Exception as e:
        print(f"  Ошибка: {e}")

    print("\n=== Задача 4: TTL индекс для автоматического удаления неактивных товаров через 30 дней ===")
    try:
        products.create_index(
            [("created_at", 1)],
            expireAfterSeconds=30 * 24 * 60 * 60
        )
        print("  TTL индекс создан: автоматическое удаление через 30 дней")
    except Exception as e:
        print(f"  Ошибка: {e}")

    print("\n=== Список всех индексов ===")
    indexes = list(products.list_indexes())
    for index in indexes:
        print(f"  {index['name']}: {index.get('key', {})}")


def task_5_complex_analytics():
    """Задание 5: Сложная агрегация - Аналитика продаж"""
    users = db['users_analytics']
    orders = db['orders_analytics']
    products = db['products_analytics']

    user1_id = ObjectId()
    user2_id = ObjectId()
    user3_id = ObjectId()

    users.insert_many([
        {"_id": user1_id, "name": "Иван",
            "email": "ivan@example.com", "city": "Москва"},
        {"_id": user2_id, "name": "Анна", "email": "anna@example.com", "city": "СПб"},
        {"_id": user3_id, "name": "Петр",
            "email": "petr@example.com", "city": "Москва"}
    ])

    product1_id = ObjectId()
    product2_id = ObjectId()
    product3_id = ObjectId()

    products.insert_many([
        {"_id": product1_id, "name": "Ноутбук",
            "category": "Электроника", "price": 50000},
        {"_id": product2_id, "name": "Телефон",
            "category": "Электроника", "price": 30000},
        {"_id": product3_id, "name": "Куртка", "category": "Одежда", "price": 5000}
    ])

    orders.insert_many([
        {
            "user_id": user1_id,
            "items": [
                {"product_id": product1_id, "quantity": 1},
                {"product_id": product2_id, "quantity": 1}
            ],
            "status": "completed",
            "total": 80000,
            "created_at": datetime.now() - timedelta(days=5)
        },
        {
            "user_id": user2_id,
            "items": [
                {"product_id": product3_id, "quantity": 2}
            ],
            "status": "completed",
            "total": 10000,
            "created_at": datetime.now() - timedelta(days=3)
        },
        {
            "user_id": user3_id,
            "items": [
                {"product_id": product1_id, "quantity": 1}
            ],
            "status": "completed",
            "total": 50000,
            "created_at": datetime.now() - timedelta(days=1)
        }
    ])

    print("=== Задача 1: Топ-10 категорий товаров по выручке ===")
    pipeline = [
        {"$match": {"status": "completed"}},
        {"$unwind": "$items"},
        {
            "$lookup": {
                "from": "products_analytics",
                "localField": "items.product_id",
                "foreignField": "_id",
                "as": "product"
            }
        },
        {"$unwind": "$product"},
        {
            "$group": {
                "_id": "$product.category",
                "revenue": {"$sum": {"$multiply": ["$items.quantity", "$product.price"]}},
                "order_count": {"$sum": 1}
            }
        },
        {"$sort": {"revenue": -1}},
        {"$limit": 10}
    ]
    result = list(orders.aggregate(pipeline))
    for item in result:
        print(
            f"  {item['_id']}: выручка = {item['revenue']}, заказов = {item['order_count']}")

    print("\n=== Задача 2: Средний чек по городам пользователей ===")
    pipeline = [
        {"$match": {"status": "completed"}},
        {
            "$lookup": {
                "from": "users_analytics",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {
            "$group": {
                "_id": "$user.city",
                "avg_total": {"$avg": "$total"},
                "order_count": {"$sum": 1}
            }
        },
        {"$sort": {"avg_total": -1}}
    ]
    result = list(orders.aggregate(pipeline))
    for item in result:
        print(
            f"  {item['_id']}: средний чек = {item['avg_total']:.2f}, заказов = {item['order_count']}")

    print("\n=== Задача 3: Пользователи с заказами на сумму больше 10000 ===")
    pipeline = [
        {"$match": {"status": "completed"}},
        {
            "$lookup": {
                "from": "users_analytics",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {"$unwind": "$user"},
        {
            "$group": {
                "_id": "$user_id",
                "user_name": {"$first": "$user.name"},
                "total_spent": {"$sum": "$total"}
            }
        },
        {"$match": {"total_spent": {"$gt": 10000}}},
        {"$sort": {"total_spent": -1}}
    ]
    result = list(orders.aggregate(pipeline))
    for item in result:
        print(f"  {item['user_name']}: потрачено {item['total_spent']}")

    print("\n=== Задача 4: Динамика продаж по дням за последний месяц ===")
    pipeline = [
        {"$match": {
            "status": "completed",
            "created_at": {"$gte": datetime.now() - timedelta(days=30)}
        }},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"},
                    "day": {"$dayOfMonth": "$created_at"}
                },
                "total_revenue": {"$sum": "$total"},
                "order_count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    result = list(orders.aggregate(pipeline))
    for item in result:
        date = f"{item['_id']['year']}-{item['_id']['month']:02d}-{item['_id']['day']:02d}"
        print(
            f"  {date}: выручка = {item['total_revenue']}, заказов = {item['order_count']}")


def task_6_query_optimization():
    """Задание 6: Оптимизация запросов"""
    articles = db['articles']

    articles.insert_many([
        {
            "title": "Статья о MongoDB",
            "content": "Содержимое статьи...",
            "author_id": ObjectId(),
            "tags": ["mongodb", "database"],
            "views": 100,
            "created_at": datetime.now(),
            "status": "published"
        },
        {
            "title": "Статья о Python",
            "content": "Содержимое статьи...",
            "author_id": ObjectId(),
            "tags": ["python", "programming"],
            "views": 200,
            "created_at": datetime.now(),
            "status": "published"
        }
    ])

    print("=== Задача 1: Compound индекс для запроса по автору и статусу с сортировкой по дате ===")
    try:
        articles.create_index([
            ("author_id", 1),
            ("status", 1),
            ("created_at", -1)
        ])
        print("  Индекс создан: (author_id, status, created_at)")
    except Exception as e:
        print(f"  Ошибка: {e}")

    author_id = list(articles.find().limit(1))[0]['author_id']
    query = {
        "author_id": author_id,
        "status": "published"
    }
    result = articles.find(query).sort("created_at", -1)
    explain_result = result.explain()
    print(
        f"  Стадия выполнения: {explain_result['executionStats']['executionStages']['stage']}")

    print("\n=== Задача 2: Compound индекс для запроса по тегам с сортировкой по просмотрам ===")
    try:
        articles.create_index([
            ("tags", 1),
            ("views", -1)
        ])
        print("  Индекс создан: (tags, views)")
    except Exception as e:
        print(f"  Ошибка: {e}")

    print("\n=== Задача 3: Covered query для получения только заголовков и дат ===")
    try:
        articles.create_index([
            ("status", 1),
            ("title", 1),
            ("created_at", 1)
        ])
        print("  Индекс создан для covered query: (status, title, created_at)")

        query = {"status": "published"}
        projection = {"title": 1, "created_at": 1, "_id": 0}
        result = articles.find(query, projection)
        explain_result = result.explain()
        stage = explain_result['executionStats']['executionStages']['stage']
        print(f"  Стадия выполнения: {stage}")
        if stage == "IXSCAN":
            print("  ✓ Covered query - все данные из индекса!")
    except Exception as e:
        print(f"  Ошибка: {e}")

    print("\n=== Задача 4: Проверка использования индексов через explain() ===")
    query = {"status": "published", "tags": "mongodb"}
    result = articles.find(query).sort("views", -1)
    explain_result = result.explain()
    execution_stats = explain_result['executionStats']
    print(f"  Стадия: {execution_stats['executionStages']['stage']}")
    print(f"  Документов проверено: {execution_stats['totalDocsExamined']}")
    print(f"  Документов возвращено: {execution_stats['nReturned']}")


def task_7_arrays_nested():
    """Задание 7: Работа с массивами и вложенными документами"""
    posts = db['posts']

    user1_id = ObjectId()
    user2_id = ObjectId()

    posts.insert_many([
        {
            "title": "Пост 1",
            "comments": [
                {
                    "user_id": user1_id,
                    "text": "Отличный пост!",
                    "likes": 15,
                    "created_at": datetime.now()
                },
                {
                    "user_id": user2_id,
                    "text": "Согласен",
                    "likes": 5,
                    "created_at": datetime.now()
                }
            ],
            "tags": ["python", "mongodb"],
            "author_id": ObjectId()
        },
        {
            "title": "Пост 2",
            "comments": [
                {
                    "user_id": user1_id,
                    "text": "Интересно",
                    "likes": 3,
                    "created_at": datetime.now()
                }
            ],
            "tags": ["javascript"],
            "author_id": ObjectId()
        }
    ])

    print("=== Задача 1: Найти посты с комментариями, у которых больше 10 лайков ===")
    result = posts.find({
        "comments": {
            "$elemMatch": {"likes": {"$gt": 10}}
        }
    })
    for post in result:
        print(f"  {post['title']}")

    print("\n=== Задача 2: Найти посты с комментариями конкретного пользователя ===")
    result = posts.find({
        "comments.user_id": user1_id
    })
    for post in result:
        print(f"  {post['title']}")

    print("\n=== Задача 3: Обновить количество лайков в комментарии ===")
    result = posts.update_one(
        {
            "title": "Пост 1",
            "comments.user_id": user1_id
        },
        {
            "$inc": {"comments.$.likes": 5}
        }
    )
    print(f"  Обновлено документов: {result.modified_count}")

    print("\n=== Задача 4: Добавить новый комментарий к посту ===")
    new_comment = {
        "user_id": ObjectId(),
        "text": "Новый комментарий",
        "likes": 0,
        "created_at": datetime.now()
    }
    result = posts.update_one(
        {"title": "Пост 1"},
        {"$push": {"comments": new_comment}}
    )
    print(
        f"  Добавлен комментарий, обновлено документов: {result.modified_count}")


def task_8_transactions():
    """Задание 8: Транзакции и атомарные операции"""
    accounts = db['accounts']
    transactions = db['transactions']

    account1_id = ObjectId()
    account2_id = ObjectId()

    accounts.insert_many([
        {"_id": account1_id, "balance": 1000},
        {"_id": account2_id, "balance": 500}
    ])

    print("=== Задача 1: Перевод средств между счетами (транзакция) ===")
    session = client.start_session()
    try:
        with session.start_transaction():
            amount = 200
            accounts.update_one(
                {"_id": account1_id},
                {"$inc": {"balance": -amount}},
                session=session
            )
            accounts.update_one(
                {"_id": account2_id},
                {"$inc": {"balance": amount}},
                session=session
            )
            transactions.insert_one({
                "from_account": account1_id,
                "to_account": account2_id,
                "amount": amount,
                "created_at": datetime.now()
            }, session=session)
        print(
            f"  Перевод выполнен успешно: {amount} со счета {account1_id} на {account2_id}")
    except Exception as e:
        print(f"  Ошибка транзакции: {e}")
    finally:
        session.end_session()

    print("\n=== Задача 2: Атомарное увеличение баланса ===")
    result = accounts.update_one(
        {"_id": account1_id},
        {"$inc": {"balance": 100}}
    )
    print(f"  Баланс увеличен, обновлено документов: {result.modified_count}")

    print("\n=== Задача 3: Проверка и обновление баланса атомарно ===")
    min_balance = 100
    withdraw_amount = 50
    result = accounts.update_one(
        {
            "_id": account1_id,
            "balance": {"$gte": min_balance + withdraw_amount}
        },
        {"$inc": {"balance": -withdraw_amount}}
    )
    if result.modified_count > 0:
        print(f"  Снятие выполнено: {withdraw_amount}")
    else:
        print("  Недостаточно средств")


def task_9_geospatial():
    """Задание 9: Геопространственные запросы"""
    locations = db['locations']

    locations.insert_many([
        {
            "name": "Ресторан 1",
            "location": {
                "type": "Point",
                "coordinates": [37.6173, 55.7558]
            }
        },
        {
            "name": "Ресторан 2",
            "location": {
                "type": "Point",
                "coordinates": [30.3159, 59.9343]
            }
        },
        {
            "name": "Ресторан 3",
            "location": {
                "type": "Point",
                "coordinates": [37.6175, 55.7560]
            }
        }
    ])

    print("=== Задача 1: Создать геопространственный индекс ===")
    try:
        locations.create_index([("location", "2dsphere")])
        print("  Геопространственный индекс создан")
    except Exception as e:
        print(f"  Ошибка: {e}")

    print("\n=== Задача 2: Найти все локации в радиусе 5 км от точки ===")
    center_point = [37.6173, 55.7558]
    radius_km = 5
    radius_radians = radius_km / 6371

    result = locations.find({
        "location": {
            "$geoWithin": {
                "$centerSphere": [center_point, radius_radians]
            }
        }
    })
    for loc in result:
        print(f"  {loc['name']}: {loc['location']['coordinates']}")

    print("\n=== Задача 3: Найти ближайшие 10 локаций к заданной точке ===")
    query_point = {"type": "Point", "coordinates": [37.6173, 55.7558]}
    pipeline = [
        {
            "$geoNear": {
                "near": query_point,
                "distanceField": "distance",
                "spherical": True,
                "limit": 10
            }
        }
    ]
    result = list(locations.aggregate(pipeline))
    for loc in result:
        distance_km = loc.get('distance', 0) / 1000
        print(f"  {loc['name']}: расстояние {distance_km:.2f} км")


def task_10_text_search():
    """Задание 10: Полнотекстовый поиск"""
    articles = db['articles_text']

    articles.insert_many([
        {
            "title": "MongoDB для начинающих",
            "content": "MongoDB - это NoSQL база данных. Python часто используется с MongoDB.",
            "description": "Введение в MongoDB"
        },
        {
            "title": "Python и базы данных",
            "content": "Python поддерживает работу с различными базами данных, включая MongoDB и Redis.",
            "description": "Работа с базами данных в Python"
        },
        {
            "title": "Redis кэширование",
            "content": "Redis используется для кэширования данных.",
            "description": "Кэширование с Redis"
        }
    ])

    print("=== Задача 1: Создать text индекс на поля title, content, description ===")
    try:
        articles.create_index([
            ("title", "text"),
            ("content", "text"),
            ("description", "text")
        ])
        print("  Text индекс создан")
    except Exception as e:
        print(f"  Ошибка: {e}")

    print("\n=== Задача 2: Найти статьи, содержащие слова 'mongodb' и 'python' ===")
    result = articles.find({
        "$text": {"$search": "mongodb python"}
    })
    for article in result:
        print(f"  {article['title']}")

    print("\n=== Задача 3: Найти статьи, содержащие 'mongodb', но не содержащие 'redis' ===")
    result = articles.find({
        "$text": {"$search": "mongodb -redis"}
    })
    for article in result:
        print(f"  {article['title']}")

    print("\n=== Задача 4: Text search с сортировкой по релевантности ===")
    pipeline = [
        {
            "$match": {
                "$text": {"$search": "mongodb python"}
            }
        },
        {
            "$addFields": {
                "score": {"$meta": "textScore"}
            }
        },
        {
            "$sort": {"score": {"$meta": "textScore"}}
        }
    ]
    result = list(articles.aggregate(pipeline))
    for article in result:
        score = article.get('score', 0)
        print(f"  {article['title']}: релевантность = {score:.2f}")


if __name__ == "__main__":
    print("MongoDB Примеры и Тестовые задания\n")
    print("Раскомментируйте нужную функцию для запуска:\n")

    # task_1_basic_queries()
    # task_2_aggregations()
    # task_3_lookup()
    # task_4_indexes()
    # task_5_complex_analytics()
    # task_6_query_optimization()
    # task_7_arrays_nested()
    # task_8_transactions()
    # task_9_geospatial()
    # task_10_text_search()

    print("\nДля запуска примеров:")
    print("1. Убедитесь, что MongoDB запущен (mongod)")
    print("2. Раскомментируйте нужную функцию task_X_...()")
    print("3. Запустите скрипт: python mongodb_example.py")
