from redis import Redis
import threading
import time


r = Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

# r.set('counter:views', 0)
# r.incrby('counter:views', 6)
# print(r.get('counter:views'))

# user_id = 1
# r.hset(f'user:{user_id}', mapping={
#     'name': 'Ivan',
#     'email': 'example.com',
#     'age': 25
# })
# print(r.hgetall(f'user:{user_id}'))
# print(r.hget(f'user:{user_id}', 'name'))

# r.lpush('tasks', 'task1', 'task2', 'task3')
# r.lpush('tasks', 'task4', 'task5')
# all_tasks = r.lrange('tasks', 0, -1)
# print(all_tasks)
# print(r.llen('tasks'))

# r.sadd('tags:article:1', 'python', 'redis', 'database')
# r.sadd('tags:article:2', 'python', 'fastapi', 'api')
# print(r.smembers('tags:article:1'))
# print(r.smembers('tags:article:2'))
# print(r.sinter('tags:article:1', 'tags:article:2'))
# print(r.sunion('tags:article:1', 'tags:article:2'))
# print(r.sismember('tags:article:1', 'python'))

# r.zadd('leaderboard', {
#     'user:1': 120,
#     'user:2': 121,
#     'user:3': 122,
#     'user:4': 123,
#     'user:5': 124,
# })
# print(r.zrevrange('leaderboard', 0, 2, withscores=True))
# print(r.zrevrank('leaderboard', 'user:2'))
# print(r.zscore('leaderboard', 'user:2'))
# r.zincrby('leaderboard', 10, 'user:1')
# print(r.zscore('leaderboard', 'user:1'))


# users = [
#     {'id': 1, 'name': 'Ivan', 'email': 'ivan@example.com', 'points': 120},
#     {'id': 2, 'name': 'Anna', 'email': 'anna@example.com', 'points': 250},
#     {'id': 3, 'name': 'Petr', 'email': 'petr@example.com', 'points': 180},
#     {'id': 4, 'name': 'Maria', 'email': 'maria@example.com', 'points': 300}
# ]

# for user in users:
#     r.hset(f"user:{user['id']}", mapping={
#         'name': user['name'],
#         'email': user['email']
#     })
#     r.zadd('leaderboard:points', {str(user['id']): user['points']})

# top_3 = r.zrevrange('leaderboard:points', 0, -1, withscores=True)
# print(top_3)
# res = []
# for idx, user in top_3:
#     user_id = user[0]
#     name = r.hget(f"user:{user_id}", 'name')
#     email = r.hget(f"user:{user_id}", 'email')
#     score = user[1]
#     res.append([user_id, name, email, score])
# print(res)
# print(r.zrevrange('leaderboard:points', 0, 2))


pubsub = r.pubsub()


def subscriber():
    pubsub.subscribe('notifications')

    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"recieved {message['data']}")


thread = threading.Thread(target=subscriber, daemon=True)
thread.start()

r.publish('notifications', 'hi')
r.publish('notifications', "i'm Stepan")
time.sleep(1)
r.publish('notifications', 'jls;adjfl;jsadfl;k')
time.sleep(1)
pubsub.unsubscribe()
