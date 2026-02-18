from datetime import datetime
from pprint import pprint
from bson import ObjectId
from pymongo import MongoClient


client = MongoClient("mongodb://localhost:27017/")
db = client["exam_db"]


def seed():
    users = db["users"]
    orders = db["orders"]

    users.drop()
    orders.drop()

    uid1 = ObjectId()
    uid2 = ObjectId()
    uid3 = ObjectId()
    uid4 = ObjectId()

    users.insert_many([
        {
            "_id": uid1,
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30,
            "city": "Moscow",
            "tags": ["developer", "python"]
        },
        {
            "_id": uid2,
            "name": "Maria Ivanova",
            "email": "maria@mail.ru",
            "age": 28,
            "city": "Moscow",
            "tags": ["analyst", "sql"]
        },
        {
            "_id": uid3,
            "name": "Alex Petrov",
            "email": "alex@yandex.ru",
            "age": 35,
            "city": "SPb",
            "tags": ["devops", "linux"]
        },
        {
            "_id": uid4,
            "name": "Olga Sidorova",
            "email": "olga@gmail.com",
            "age": 22,
            "city": "Moscow",
            "tags": ["junior", "python", "django"]
        }
    ])

    orders.insert_many([
        {
            "_id": ObjectId("607f1f77bcf86cd799439021"),
            "user_id": uid1,
            "product": "Laptop",
            "price": 1000,
            "date": datetime(2024, 1, 15)
        },
        {
            "_id": ObjectId("607f1f77bcf86cd799439022"),
            "user_id": uid1,
            "product": "Mouse",
            "price": 50,
            "date": datetime(2024, 2, 20)
        },
        {
            "_id": ObjectId("607f1f77bcf86cd799439023"),
            "user_id": uid2,
            "product": "Monitor",
            "price": 350,
            "date": datetime(2024, 3, 10)
        },
        {
            "_id": ObjectId("607f1f77bcf86cd799439024"),
            "user_id": uid3,
            "product": "Keyboard",
            "price": 120,
            "date": datetime(2024, 4, 5)
        },
        {
            "_id": ObjectId("607f1f77bcf86cd799439025"),
            "user_id": uid4,
            "product": "Headphones",
            "price": 80,
            "date": datetime(2024, 5, 12)
        }
    ])


def task_911():
    seed()
    users = db["users"]
    pprint(list(users.find({"city": "Moscow", "age": {"$gt": 25}})))


def task912():
    seed()
    users = db["users"]
    pipline_total_sum = [
        {"$lookup":
            {"from": "orders", "localField": "_id", "foreignField": "user_id", "as": "orders"}
         },
        {"$unwind": "$orders"},
        {"$group":
            {"_id": "$_id", "total_for_user": {"$sum": "$orders.price"}, "name": {"$first": "$name"}}
         },
        {"$project": {
            "name": 1,
            "total_for_user": 1,
            "_id": 0
        }
        }
    ]
    pprint(list(users.aggregate(pipline_total_sum)))


def task913():
    seed()
    users = db["users"]

    pipline = [
        {"$lookup": {
            "from": "orders",
            "localField": "_id",
            "foreignField": "user_id",
            "as": "order"
        }}
    ]
    pprint(list(users.aggregate(pipline)))


def task914():
    users = db["users"]
    users.create_index([("age", 1), ("city", 1)])
    users.create_index([("age", 1)], partialFilterExpression={"age": {"$gt": 18}})
    users.create_index([("tags", "text")])


def seed92():
    products = db["products"]
    reviews = db["reviews"]
    users = db["users"]

    products.drop()
    reviews.drop()
    users.drop()

    pr1 = ObjectId()
    pr2 = ObjectId()
    pr3 = ObjectId()

    uid1 = ObjectId()
    uid2 = ObjectId()
    uid3 = ObjectId()
    uid4 = ObjectId()
    uid5 = ObjectId()
    uid6 = ObjectId()

    users.insert_many([
        {
            "_id": uid1,
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30,
            "city": "Moscow",
            "tags": ["developer", "python"]
        },
        {
            "_id": uid2,
            "name": "Maria Ivanova",
            "email": "maria@mail.ru",
            "age": 28,
            "city": "Moscow",
            "tags": ["analyst", "sql"]
        },
        {
            "_id": uid3,
            "name": "Alex Petrov",
            "email": "alex@yandex.ru",
            "age": 35,
            "city": "SPb",
            "tags": ["devops", "linux"]
        },
        {
            "_id": uid4,
            "name": "Olga Sidorova",
            "email": "olga@gmail.com",
            "age": 22,
            "city": "Moscow",
            "tags": ["junior", "python", "django"]
        },
        {
            "_id": uid5,
            "name": "Dmitry Kozlov",
            "email": "dmitry@mail.ru",
            "age": 40,
            "city": "Kazan",
            "tags": ["lead", "architecture"]
        },
        {
            "_id": uid6,
            "name": "Anna Volkova",
            "email": "anna@gmail.com",
            "age": 26,
            "city": "Moscow",
            "tags": ["qa", "automation"]
        }
    ])

    products.insert_many(
        [
            {
                "_id": pr1,
                "name": "Smartphone",
                "category": "Electronics",
                "price": 500,
                "stock": 100,
                "description": "Latest smartphone with advanced features",
            },
            {
                "_id": pr2,
                "name": "Laptop",
                "category": "Electronics",
                "price": 1200,
                "stock": 50,
                "description": "Lightweight laptop for everyday work",
            },
            {
                "_id": pr3,
                "name": "Headphones",
                "category": "Audio",
                "price": 150,
                "stock": 200,
                "description": "Wireless headphones with noise cancellation",
            },
        ]
    )

    reviews.insert_many(
        [
            {
                "_id": ObjectId(),
                "product_id": pr1,
                "user_id": uid1,
                "rating": 5,
                "comment": "Great smartphone with excellent camera",
            },
            {
                "_id": ObjectId(),
                "product_id": pr1,
                "user_id": uid2,
                "rating": 4,
                "comment": "Good value for money",
            },
            {
                "_id": ObjectId(),
                "product_id": pr2,
                "user_id": uid1,
                "rating": 5,
                "comment": "Perfect for programming and study",
            },
            {
                "_id": ObjectId(),
                "product_id": pr2,
                "user_id": uid3,
                "rating": 3,
                "comment": "Battery could be better",
            },
            {
                "_id": ObjectId(),
                "product_id": pr3,
                "user_id": uid4,
                "rating": 4,
                "comment": "Comfortable and good sound",
            },
            {
                "_id": ObjectId(),
                "product_id": pr1,
                "user_id": uid5,
                "rating": 5,
                "comment": "Best phone I ever had",
            },
            {
                "_id": ObjectId(),
                "product_id": pr3,
                "user_id": uid6,
                "rating": 5,
                "comment": "Great for calls and music",
            },
        ]
    )


def task192():
    seed92()
    products = db["products"]

    pprint(list(products.find({"category": "Electronics", "price": {"$lt": 1000}})))


def task292():
    seed92()
    reviews = db["reviews"]

    pipline_avg = [
        {"$group":
            {
                "_id": "$product_id",
                "score": {"$avg": "$rating"},
            }},
        {"$lookup":
            {
                "from": "products",
                "localField": "_id",
                "foreignField": "_id",
                "as": "product"
            }},
        {"$unwind": "$product"},
        {"$project": {
            "_id": 0,
            "product": "$product.name",
            "score": 1
        }}
    ]
    pprint(list(reviews.aggregate(pipline_avg)))


def task392():
    seed92()
    reviews = db["reviews"]

    pipline_lookup = [
        {"$match": {"rating": {"$gte": 4}}},
        {"$lookup": {
            "from": "products",
            "localField": "product_id",
            "foreignField": "_id",
            "as": "product"
        }}
    ]
    pprint(list(reviews.aggregate(pipline_lookup)))


def task492():
    products = db["products"]
    seed92()

    products.create_index([()])


task392()
