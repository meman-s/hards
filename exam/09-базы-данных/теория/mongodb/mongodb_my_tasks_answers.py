from __future__ import annotations

from datetime import datetime, timedelta
import os
import sys

from bson import ObjectId
from pymongo import MongoClient


client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client[os.getenv("MONGO_DB", "test_db")]


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

    orders.insert_many(
        [
            {
                "user_id": user1_id,
                "items": [
                    {"product_id": product1_id, "quantity": 1, "price": 50000},
                    {"product_id": product2_id, "quantity": 1, "price": 30000},
                ],
                "status": "completed",
                "created_at": datetime.now() - timedelta(days=1),
                "total": 80000,
            },
            {
                "user_id": user2_id,
                "items": [{"product_id": product3_id, "quantity": 2, "price": 5000}],
                "status": "completed",
                "created_at": datetime.now() - timedelta(days=3),
                "total": 10000,
            },
            {
                "user_id": user3_id,
                "items": [{"product_id": product1_id, "quantity": 1, "price": 50000}],
                "status": "pending",
                "created_at": datetime.now(),
                "total": 50000,
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
    users.find({"status": "active", "age": {"$gt": 18}})
    users.find({"tags": {"$all": ["python", "mongodb"]}})
    users.update_many({"status": {"$ne": "active"}}, {"$set": {"status": "inactive"}})
    users.delete_many({"age": {"$gt": 100}})


def task_2_aggregations() -> None:
    orders = db["orders"]

    pipeline_total = [
        {"$match": {"status": "completed"}},
        {"$group": {"_id": None, "total_revenue": {"$sum": "$total"}}},
    ]
    list(orders.aggregate(pipeline_total))

    pipeline_avg = [
        {"$group": {"_id": "$status", "avg_total": {"$avg": "$total"}, "count": {"$sum": 1}}},
        {"$sort": {"avg_total": -1}},
    ]
    list(orders.aggregate(pipeline_avg))

    pipeline_top = [
        {"$match": {"status": "completed"}},
        {"$group": {"_id": "$user_id", "total_spent": {"$sum": "$total"}, "order_count": {"$sum": 1}}},
        {"$sort": {"total_spent": -1}},
        {"$limit": 5},
    ]
    list(orders.aggregate(pipeline_top))

    pipeline_months = [
        {
            "$group": {
                "_id": {"year": {"$year": "$created_at"}, "month": {"$month": "$created_at"}},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    list(orders.aggregate(pipeline_months))


def task_3_lookup() -> None:
    orders = db["orders"]
    users = db["users"]

    pipeline_orders_with_user = [
        {"$lookup": {"from": "users", "localField": "user_id", "foreignField": "_id", "as": "user"}},
        {"$unwind": "$user"},
        {
            "$project": {
                "user_id": 1,
                "status": 1,
                "total": 1,
                "created_at": 1,
                "user_name": "$user.name",
                "user_email": "$user.email",
            }
        },
    ]
    list(orders.aggregate(pipeline_orders_with_user))

    pipeline_orders_with_items = [
        {"$unwind": "$items"},
        {
            "$lookup": {
                "from": "products",
                "localField": "items.product_id",
                "foreignField": "_id",
                "as": "product",
            }
        },
        {"$unwind": "$product"},
        {
            "$group": {
                "_id": "$_id",
                "user_id": {"$first": "$user_id"},
                "status": {"$first": "$status"},
                "created_at": {"$first": "$created_at"},
                "total": {"$first": "$total"},
                "items": {
                    "$push": {
                        "product_id": "$items.product_id",
                        "quantity": "$items.quantity",
                        "price": "$items.price",
                        "product_name": "$product.name",
                        "category": "$product.category",
                    }
                },
            }
        },
    ]
    list(orders.aggregate(pipeline_orders_with_items))

    pipeline_users_with_stats = [
        {"$lookup": {"from": "orders", "localField": "_id", "foreignField": "user_id", "as": "orders"}},
        {
            "$project": {
                "name": 1,
                "email": 1,
                "order_count": {"$size": "$orders"},
                "total_spent": {"$sum": "$orders.total"},
            }
        },
    ]
    list(users.aggregate(pipeline_users_with_stats))

    pipeline_products_stats = [
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$items.product_id",
                "times_ordered": {"$sum": 1},
                "total_quantity": {"$sum": "$items.quantity"},
            }
        },
    ]
    list(orders.aggregate(pipeline_products_stats))


def task_4_indexes() -> None:
    products = db["products"]

    products.create_index([("category", 1), ("status", 1), ("price", -1)])
    products.create_index([("name", 1)], partialFilterExpression={"status": "active"})
    products.create_index([("name", "text"), ("description", "text")])

    query = {"category": "Электроника", "status": "active"}
    products.find(query).sort("price", -1).explain()


def task_5_complex() -> None:
    orders = db["orders"]

    pipeline_top_categories = [
        {"$match": {"status": "completed"}},
        {"$unwind": "$items"},
        {"$lookup": {"from": "products", "localField": "items.product_id", "foreignField": "_id", "as": "product"}},
        {"$unwind": "$product"},
        {"$group": {"_id": "$product.category", "revenue": {
            "$sum": {"$multiply": ["$items.quantity", "$product.price"]}}}},
        {"$sort": {"revenue": -1}},
        {"$limit": 5},
    ]
    list(orders.aggregate(pipeline_top_categories))

    pipeline_avg_check_by_city = [
        {"$match": {"status": "completed"}},
        {
            "$lookup": {
                "from": "users",
                "localField": "user_id",
                "foreignField": "_id",
                "as": "user",
            }
        },
        {"$unwind": "$user"},
        {
            "$group": {
                "_id": "$user.city",
                "avg_total": {"$avg": "$total"},
                "order_count": {"$sum": 1},
            }
        },
    ]
    list(orders.aggregate(pipeline_avg_check_by_city))

    pipeline_users_over_limit = [
        {"$match": {"status": "completed"}},
        {
            "$group": {
                "_id": "$user_id",
                "total_spent": {"$sum": "$total"},
            }
        },
        {"$match": {"total_spent": {"$gt": 10000}}},
    ]
    list(orders.aggregate(pipeline_users_over_limit))

    db["orders"].create_index([("user_id", 1), ("status", 1), ("created_at", -1)])


def main() -> None:
    if len(sys.argv) < 2:
        print("Команды")
        print("seed")
        print("1")
        print("task_1_basic_queries")
        print("2")
        print("task_2_aggregations")
        print("3")
        print("task_3_lookup")
        print("4")
        print("task_4_indexes")
        print("5")
        print("task_5_complex")
        raise SystemExit(2)

    name = sys.argv[1]
    if name == "seed":
        seed()
        return
    if name.isdigit():
        i = int(name)
        mapping = {
            1: "task_1_basic_queries",
            2: "task_2_aggregations",
            3: "task_3_lookup",
            4: "task_4_indexes",
            5: "task_5_complex",
        }
        if i in mapping:
            name = mapping[i]

    fn = globals().get(name)
    if not callable(fn):
        print("Неизвестная команда")
        raise SystemExit(2)

    seed()
    fn()


if __name__ == "__main__":
    main()
