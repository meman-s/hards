from __future__ import annotations

from datetime import datetime, timedelta
import os
import sys
from pprint import pprint
from typing import Callable

from bson import ObjectId
from pymongo import MongoClient


client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client["test_db"]


TASKS: dict[str, str] = {
    "task_1_basic_queries": (
        "Задание 1: Базовые запросы (коллекция users)\n"
        "Данные создаются командой: seed\n"
        "\n"
        "Нужно написать 4 запроса/операции:\n"
        "1) Найти всех пользователей, у которых status='active' и age > 18\n"
        "2) Найти пользователей, у которых tags содержит одновременно 'python' и 'mongodb'\n"
        "3) Обновить всех пользователей, у кого status != 'active': поставить status='inactive'\n"
        "4) Удалить пользователей, у которых age > 100\n"
        "\n"
        "Подсказка: find, $gt, $all, update_many, delete_many\n"
    ),
    "task_2_aggregations": (
        "Задание 2: Агрегации (коллекция orders)\n"
        "Данные создаются командой: seed\n"
        "\n"
        "Нужно собрать 4 pipeline:\n"
        "1) Общая сумма total по заказам со status='completed'\n"
        "2) Средний чек total по статусам (group by status): avg_total и count\n"
        "3) Топ-5 user_id по сумме total только по completed\n"
        "4) Количество заказов по месяцам (year, month из created_at)\n"
        "\n"
        "Подсказка: $match, $group, $sum, $avg, $sort, $limit, $year, $month\n"
    ),
    "task_3_lookup": (
        "Задание 3: Join через $lookup (users + orders + products)\n"
        "Данные создаются командой: seed\n"
        "\n"
        "Нужно собрать pipeline:\n"
        "1) Для каждого заказа подтянуть пользователя (users) по user_id, вывести имя и email\n"
        "2) Для каждого заказа развернуть items, подтянуть product, собрать обратно список items\n"
        "3) Для каждого пользователя посчитать order_count и total_spent по его orders\n"
        "4) Для каждого товара посчитать:\n"
        "   - сколько раз товар встречался в заказах (times_ordered)\n"
        "   - суммарное количество (total_quantity)\n"
        "\n"
        "Подсказка: $lookup, $unwind, $group, $push, $size, $sum\n"
    ),
    "task_4_indexes": (
        "Задание 4: Индексы (коллекция products)\n"
        "Данные создаются командой: seed\n"
        "\n"
        "Нужно:\n"
        "1) Создать compound индекс под запрос:\n"
        "   найти товары category='Электроника' и status='active', отсортировать по price DESC\n"
        "2) Создать partial индекс по name только для status='active'\n"
        "3) Создать text индекс по name и description\n"
        "4) Сделать explain() для запроса из пункта 1 и посмотреть стадию выполнения\n"
        "\n"
        "Подсказка: create_index, partialFilterExpression, $text, explain\n"
    ),
    "task_5_complex": (
        "Задание 5: Комплекс (orders + users + products)\n"
        "Данные создаются командой: seed\n"
        "\n"
        "Нужно:\n"
        "1) Топ-5 категорий по выручке среди completed:\n"
        "   revenue = sum(items.quantity * product.price)\n"
        "2) Средний чек по городам пользователей среди completed (lookup orders -> users)\n"
        "3) Пользователи, у которых total_spent по completed > 10000\n"
        "4) Создать compound индекс под запрос:\n"
        "   найти заказы пользователя со status='completed', отсортировать по created_at DESC\n"
        "\n"
        "Подсказка: $lookup, $unwind, $group, $multiply, create_index\n"
    ),
}


TASK_TITLES: dict[str, str] = {
    "task_1_basic_queries": "Базовые запросы",
    "task_2_aggregations": "Агрегации",
    "task_3_lookup": "$lookup (Join)",
    "task_4_indexes": "Индексы",
    "task_5_complex": "Комплекс",
}

TASK_ORDER: list[str] = [
    "task_1_basic_queries",
    "task_2_aggregations",
    "task_3_lookup",
    "task_4_indexes",
    "task_5_complex",
]


def seed() -> dict[str, ObjectId]:
    users = db["users"]
    orders = db["orders"]
    products = db["products"]

    users.drop()
    orders.drop()
    products.drop()

    user1_id = ObjectId()
    user2_id = ObjectId()
    user3_id = ObjectId()

    users.insert_many(
        [
            {
                "_id": user1_id,
                "name": "Иван",
                "email": "ivan@example.com",
                "age": 25,
                "status": "active",
                "tags": ["python", "mongodb"],
                "city": "Москва",
                "created_at": datetime.now() - timedelta(days=10),
            },
            {
                "_id": user2_id,
                "name": "Анна",
                "email": "anna@example.com",
                "age": 30,
                "status": "active",
                "tags": ["python", "fastapi"],
                "city": "СПб",
                "created_at": datetime.now() - timedelta(days=20),
            },
            {
                "_id": user3_id,
                "name": "Петр",
                "email": "petr@example.com",
                "age": 17,
                "status": "inactive",
                "tags": ["javascript"],
                "city": "Москва",
                "created_at": datetime.now() - timedelta(days=5),
            },
            {
                "name": "Мария",
                "email": "maria@example.com",
                "age": 105,
                "status": "active",
                "tags": ["python", "mongodb", "redis"],
                "city": "Казань",
                "created_at": datetime.now() - timedelta(days=2),
            },
        ]
    )

    product1_id = ObjectId()
    product2_id = ObjectId()
    product3_id = ObjectId()

    products.insert_many(
        [
            {
                "_id": product1_id,
                "name": "Ноутбук",
                "category": "Электроника",
                "price": 50000,
                "status": "active",
                "description": "Игровой ноутбук",
                "created_at": datetime.now() - timedelta(days=100),
            },
            {
                "_id": product2_id,
                "name": "Телефон",
                "category": "Электроника",
                "price": 30000,
                "status": "active",
                "description": "Смартфон с хорошей камерой",
                "created_at": datetime.now() - timedelta(days=50),
            },
            {
                "_id": product3_id,
                "name": "Куртка",
                "category": "Одежда",
                "price": 5000,
                "status": "inactive",
                "description": "Теплая зимняя куртка",
                "created_at": datetime.now() - timedelta(days=30),
            },
        ]
    )

    now = datetime.now()
    orders.insert_many(
        [
            {
                "user_id": user1_id,
                "items": [
                    {"product_id": product1_id, "quantity": 1, "price": 50000},
                    {"product_id": product2_id, "quantity": 1, "price": 30000},
                ],
                "status": "completed",
                "created_at": now - timedelta(days=1),
                "total": 80000,
            },
            {
                "user_id": user2_id,
                "items": [{"product_id": product3_id, "quantity": 2, "price": 5000}],
                "status": "completed",
                "created_at": now - timedelta(days=3),
                "total": 10000,
            },
            {
                "user_id": user3_id,
                "items": [{"product_id": product1_id, "quantity": 1, "price": 50000}],
                "status": "pending",
                "created_at": now,
                "total": 50000,
            },
            {
                "user_id": user1_id,
                "items": [{"product_id": product2_id, "quantity": 1, "price": 30000}],
                "status": "completed",
                "created_at": datetime(now.year - 1, 12, 15),
                "total": 30000,
            },
            {
                "user_id": user2_id,
                "items": [{"product_id": product1_id, "quantity": 1, "price": 50000}],
                "status": "completed",
                "created_at": datetime(now.year - 1, 11, 20),
                "total": 50000,
            },
            {
                "user_id": user1_id,
                "items": [{"product_id": product3_id, "quantity": 3, "price": 5000}],
                "status": "completed",
                "created_at": datetime(now.year, 1, 10),
                "total": 15000,
            },
            {
                "user_id": user2_id,
                "items": [
                    {"product_id": product1_id, "quantity": 1, "price": 50000},
                    {"product_id": product2_id, "quantity": 1, "price": 30000},
                ],
                "status": "completed",
                "created_at": datetime(now.year, 2, 5),
                "total": 80000,
            },
            {
                "user_id": user3_id,
                "items": [{"product_id": product2_id, "quantity": 2, "price": 30000}],
                "status": "completed",
                "created_at": datetime(now.year, 3, 25),
                "total": 60000,
            },
            {
                "user_id": user1_id,
                "items": [{"product_id": product1_id, "quantity": 1, "price": 50000}],
                "status": "pending",
                "created_at": datetime(now.year - 1, 10, 8),
                "total": 50000,
            },
            {
                "user_id": user2_id,
                "items": [{"product_id": product3_id, "quantity": 1, "price": 5000}],
                "status": "completed",
                "created_at": datetime(now.year - 1, 9, 15),
                "total": 5000,
            },
        ]
    )

    return {
        "user1_id": user1_id,
        "user2_id": user2_id,
        "user3_id": user3_id,
        "product1_id": product1_id,
        "product2_id": product2_id,
        "product3_id": product3_id,
    }


def task_1_basic_queries() -> None:
    users = db["users"]

    pprint(list(users.find({"status": "active", "age": {"$gt": 18}}, {"name": 1, "age": 1, "status": 1})))
    print('-'*30)
    pprint(list(users.find({"tags": {"$all": ["python", "mongodb"]}}, {"tags": 1})))
    print('-'*30)

    update_result = users.update_many(
        {"status": {"$ne": "active"}},
        {"$set": {"status": "inactive"}},
    )
    print(update_result.matched_count, update_result.modified_count)
    print('-'*30)

    delete_result = users.delete_many({"age": {"$gt": 100}})
    print(delete_result.deleted_count)
    print('-'*30)

    pprint(list(users.find({})))


def task_2_aggregations() -> None:
    orders = db["orders"]

    pipline_total = [
        {"$match": {"status": "completed"}},
        {"$group": {"_id": None, "total_revenue": {"$sum": "$total"}}}
    ]
    pprint(list(orders.aggregate(pipline_total)))

    print("-"*30, end="\n")

    pipline_avg = [
        {"$group": {"_id": "$status", "avg_total": {"$avg": "$total"}, "count": {"$sum": 1}}},
        {"$sort": {"avg_total": -1}}
    ]
    pprint(list(orders.aggregate(pipline_avg)))
    print("-"*30, end="\n")

    pipline_top = [
        {"$match": {"status": "completed"}},
        {"$group": {"_id": "$user_id", "total_spend": {"$sum": "$total"}, "order_count": {"$sum": 1}}},
        {"$sort": {"total_spend": -1}},
        {"$limit": 5}
    ]
    pprint(list(orders.aggregate(pipline_top)))
    print("-"*30, end="\n")

    pipline_month = [
        {"$group": {
            "_id": {"year": {"$year": "$created_at"}, "month": {"$month": "$created_at"}},
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    pprint(list(orders.aggregate(pipline_month)))
    print("-"*30, end="\n")


def task_3_lookup() -> None:
    orders = db["orders"]
    users = db["users"]

    pipline_users = [
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "_id", "as": "user"}},
        {"$unwind": "$user"},
        {"$project": {"user_id": 1, "status": 1, "total": 1, "created_at": 1, "user_name": "$user.name"}},
    ]
    pprint(list(orders.aggregate(pipline_users)))
    print("-"*30, end="\n")

    pipline_items = [
        {"$unwind": "$items"},
        {"$lookup": {
            "from": "products",
            "localField": "items.product_id",
            "foreignField": "_id",
            "as": "product"
        }},
        {"$unwind": "$product"},
        {"$group": {
            "_id": "$_id",
            "user_id": {"$first": "$user_id"},
            "status": {"$first": "$status"},
            "created_at": {"$first": "$created_at"},
            "total": {"$first": "$total"},
            "items": {
                "$push": {
                    "name": "$product.name",
                    "price": "$items.price",
                    "category": "$product.category",
                    "quantity": "$items.quantity"
                }
            }
        }}
    ]
    pprint(list(orders.aggregate(pipline_items)))
    print("-"*30, end="\n")

    pipline_users_order_count = [
        {"$lookup": {"from": "orders", "localField": "_id", "foreignField": "user_id", "as": "orders"}},
        {"$project":
            {
                "name": 1,
                "email": 1,
                "total_spent": {"$sum": "$orders.total"},
                "order_count": {"$size": "$orders"}
            }
         }
    ]
    pprint(list(users.aggregate(pipline_users_order_count)))
    print("-"*30, end="\n")

    pipline_product = [
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.product_id",
            "times_ordered": {"$sum": 1},
            "total_quantity": {"$sum": "$items.quantity"}
        }},
        {"$lookup": {
            "from": "products",
            "localField": "_id",
            "foreignField": "_id",
            "as": "product"
        }},
        {"$unwind": "$product"},
        {"$project": {
            "name": "$product.name",
            "times_ordered": 1,
            "total_quantity": 1
        }}
    ]
    pprint(list(orders.aggregate(pipline_product)))
    print("-"*30, end="\n")


def task_4_indexes() -> None:
    products = db["products"]

    products.create_index([("category", 1), ("status", 1), ("price", 1)])
    products.create_index([("name", 1)], partialFilterExpression={"status": "active"})
    products.create_index([("name", "text"), ("description", "text")])

    query = {"category": "Электроника", "status": "active"}
    pprint(products.find(query).sort("price", -1).explain())


def task_5_complex() -> None:
    orders = db["orders"]

    pipline_top = [
        {"$match": {"status": "completed"}},
        {"$unwind": "$items"},
        {"$lookup":
            {
                "from": "products",
                "localField": "items.product_id",
                "foreignField": "_id",
                "as": "product"
            }
         },
        {"$unwind": "$product"},
        {"$group":
            {
                "_id": "$product.category",
                "revenue": {"$sum": {"$multiply": ["$items.quantity", "$items.price"]}}
            }
         },
        {"$sort": {"revenue": -1}}
    ]
    pprint(list(orders.aggregate(pipline_top)))
    print("-"*30, end="\n")

    pipline_cities = [
        {"$match": {"status": "completed"}},
        {"$lookup":
            {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user"
            }
         },
        {"$unwind": "$user"},
        {"$group":
            {
                "_id": "$user.city",
                "city": {"$first": "$user.city"},
                "avg": {"$avg": "$total"},
                "order_count": {"$sum": 1}
            }
         },
        {"$project":
         {
             "_id": 0,
             "city": 1,
             "avg": 1,
             "order_count": 1
         }}
    ]
    pprint(list(orders.aggregate(pipline_cities)))
    print("-"*30, end="\n")

    pipline_rich = [
        {"$match": {"status": "completed"}},
        {"$lookup":
         {
             "from": "users",
             "localField": "user_id",
             "foreignField": "_id",
             "as": "user"
         }},
        {"$unwind": "$user"},
        {"$group":
         {
             "_id": "$user_id",
             "name": {"$first": "$user.name"},
             "total_spent": {"$sum": "$total"}
         }},
        {"$match": {"total_spent": {"$gt": 10000}}},
        {"$project":
         {
             "name": 1,
             "total_spent": 1,
             "_id": 0
         }}
    ]
    pprint(list(orders.aggregate(pipline_rich)))
    print("-"*30, end="\n")

    orders.create_index([("status", 1), ("created_at", -1), ("user_id", 1)])
    print("-"*30, end="\n")


def _tasks() -> dict[str, Callable[[], None]]:
    return {
        "task_1_basic_queries": task_1_basic_queries,
        "task_2_aggregations": task_2_aggregations,
        "task_3_lookup": task_3_lookup,
        "task_4_indexes": task_4_indexes,
        "task_5_complex": task_5_complex,
    }


def main() -> None:
    tasks = _tasks()
    if len(sys.argv) < 2:
        print("Команды")
        print("seed")
        print("list")
        print("show")
        for i, task_name in enumerate(TASK_ORDER, start=1):
            print(str(i))
        for name in sorted(tasks.keys()):
            print(name)
        raise SystemExit(2)

    name = sys.argv[1]
    if name.isdigit():
        i = int(name)
        if 1 <= i <= len(TASK_ORDER):
            name = TASK_ORDER[i - 1]

    if name == "seed":
        seed()
        return
    if name == "list":
        for i, task_name in enumerate(TASK_ORDER, start=1):
            print(str(i))
            print(task_name)
            print(TASK_TITLES.get(task_name, ""))
        return
    if name == "show":
        if len(sys.argv) < 3:
            print("Укажи имя задания")
            for i, task_name in enumerate(TASK_ORDER, start=1):
                print(str(i))
                print(task_name)
            raise SystemExit(2)
        task_name = sys.argv[2]
        if task_name.isdigit():
            i = int(task_name)
            if 1 <= i <= len(TASK_ORDER):
                task_name = TASK_ORDER[i - 1]
        if task_name not in tasks:
            print("Неизвестное задание")
            raise SystemExit(2)
        print(TASKS.get(task_name, ""))
        return
    if name not in tasks:
        print("Неизвестная команда")
        print("seed")
        print("list")
        print("show")
        for i, task_name in enumerate(TASK_ORDER, start=1):
            print(str(i))
        for available in sorted(tasks.keys()):
            print(available)
        raise SystemExit(2)

    print("-"*30, end="\n")
    seed()
    tasks[name]()
    print("-"*30, end="\n")


if __name__ == "__main__":
    main()
