# Redis: Задания от простого к сложному

Все задания можно скопировать и запустить. Убедитесь, что Redis запущен:
```bash
docker run --name redis-local -p 6379:6379 -d redis
```

---

## Задание 1: String — базовые операции

**Условие:**
- Сохранить имя пользователя
- Получить имя пользователя
- Установить счетчик просмотров и увеличить его на 5

**Решение:**

```python
from redis import Redis

r = Redis(host='localhost', port=6379, db=0, decode_responses=True)

r.set('user:1:name', 'Ivan')
name = r.get('user:1:name')
print(f'Имя пользователя: {name}')

r.set('counter:views', 0)
r.incrby('counter:views', 5)
views = r.get('counter:views')
print(f'Количество просмотров: {views}')
```

**Разбор:**
- `set(key, value)` — сохраняет строку
- `get(key)` — получает строку
- `incrby(key, amount)` — увеличивает числовое значение на указанное число

---

## Задание 2: Hash — профиль пользователя

**Условие:**
- Сохранить профиль пользователя (id, имя, email, возраст) в Hash
- Получить все данные профиля
- Обновить возраст пользователя
- Получить только имя пользователя

**Решение:**

```python
from redis import Redis

r = Redis(host='localhost', port=6379, db=0, decode_responses=True)

user_id = 1
r.hset(f'user:{user_id}', mapping={
    'name': 'Ivan',
    'email': 'ivan@example.com',
    'age': 25
})

profile = r.hgetall(f'user:{user_id}')
print(f'Полный профиль: {profile}')

r.hset(f'user:{user_id}', 'age', 26)
name = r.hget(f'user:{user_id}', 'name')
age = r.hget(f'user:{user_id}', 'age')
print(f'{name}, возраст: {age}')
```

**Разбор:**
- `hset(key, mapping={...})` — сохраняет несколько полей Hash за раз
- `hgetall(key)` — получает все поля Hash как словарь
- `hget(key, field)` — получает одно поле Hash

---

## Задание 3: List — очередь задач

**Условие:**
- Добавить задачи в очередь (слева и справа)
- Получить первую задачу из очереди
- Получить все задачи
- Узнать длину очереди

**Решение:**

```python
from redis import Redis

r = Redis(host='localhost', port=6379, db=0, decode_responses=True)

r.lpush('tasks', 'task1', 'task2', 'task3')
r.rpush('tasks', 'task4', 'task5')

first_task = r.lpop('tasks')
print(f'Первая задача: {first_task}')

all_tasks = r.lrange('tasks', 0, -1)
print(f'Все задачи: {all_tasks}')

length = r.llen('tasks')
print(f'Количество задач в очереди: {length}')
```

**Разбор:**
- `lpush(key, *values)` — добавляет элементы слева (в начало)
- `rpush(key, *values)` — добавляет элементы справа (в конец)
- `lpop(key)` — удаляет и возвращает элемент слева
- `lrange(key, start, end)` — получает элементы (0, -1 = все)
- `llen(key)` — возвращает длину списка

---

## Задание 4: Set — теги и операции над множествами

**Условие:**
- Сохранить теги для двух статей
- Найти общие теги между статьями
- Найти все уникальные теги обеих статей
- Проверить, есть ли тег "python" в первой статье

**Решение:**

```python
from redis import Redis

r = Redis(host='localhost', port=6379, db=0, decode_responses=True)

r.sadd('tags:article:1', 'python', 'redis', 'database')
r.sadd('tags:article:2', 'python', 'fastapi', 'api')

tags1 = r.smembers('tags:article:1')
tags2 = r.smembers('tags:article:2')
print(f'Теги статьи 1: {tags1}')
print(f'Теги статьи 2: {tags2}')

common_tags = r.sinter('tags:article:1', 'tags:article:2')
print(f'Общие теги: {common_tags}')

all_tags = r.sunion('tags:article:1', 'tags:article:2')
print(f'Все уникальные теги: {all_tags}')

has_python = r.sismember('tags:article:1', 'python')
print(f'Есть ли "python" в статье 1: {has_python}')
```

**Разбор:**
- `sadd(key, *members)` — добавляет элементы в множество
- `smembers(key)` — получает все элементы множества
- `sinter(key1, key2)` — пересечение множеств (общие элементы)
- `sunion(key1, key2)` — объединение множеств (все уникальные)
- `sismember(key, member)` — проверяет наличие элемента

---

## Задание 5: Sorted Set — простой рейтинг

**Условие:**
- Сохранить рейтинг игроков по очкам
- Получить топ 3 игроков по очкам
- Узнать позицию конкретного игрока
- Увеличить очки игрока на 10

**Решение:**

```python
from redis import Redis

r = Redis(host='localhost', port=6379, db=0, decode_responses=True)

r.zadd('leaderboard', {
    'user:1': 120,
    'user:2': 250,
    'user:3': 180,
    'user:4': 300
})

top_3 = r.zrevrange('leaderboard', 0, 2, withscores=True)
print('Топ 3 игроков:')
for user, score in top_3:
    print(f'  {user}: {score} очков')

rank = r.zrevrank('leaderboard', 'user:2')
score = r.zscore('leaderboard', 'user:2')
print(f'user:2 на позиции {rank} с {score} очками')

r.zincrby('leaderboard', 10, 'user:1')
new_score = r.zscore('leaderboard', 'user:1')
print(f'user:1 теперь имеет {new_score} очков')
```

**Разбор:**
- `zadd(key, mapping={member: score})` — добавляет элементы с оценками
- `zrevrange(key, start, end, withscores=True)` — получает элементы по убыванию score
- `zrevrank(key, member)` — позиция элемента (0 = первое место)
- `zscore(key, member)` — оценка элемента
- `zincrby(key, increment, member)` — увеличивает оценку

---

## Задание 6: Hash + Sorted Set — рейтинг с профилями

**Условие:**
- Хранить профили пользователей (id, имя, email) в Hash
- Хранить рейтинг игроков по очкам в Sorted Set
- Получить топ 3 пользователя по очкам с их именами

**Решение:**

```python
from redis import Redis

r = Redis(host='localhost', port=6379, db=0, decode_responses=True)

users = [
    {'id': 1, 'name': 'Ivan', 'email': 'ivan@example.com', 'points': 120},
    {'id': 2, 'name': 'Anna', 'email': 'anna@example.com', 'points': 250},
    {'id': 3, 'name': 'Petr', 'email': 'petr@example.com', 'points': 180},
    {'id': 4, 'name': 'Maria', 'email': 'maria@example.com', 'points': 300}
]

for user in users:
    r.hset(f"user:{user['id']}", mapping={
        'name': user['name'],
        'email': user['email']
    })
    r.zadd('leaderboard:points', {str(user['id']): user['points']})

print('Профили сохранены, рейтинг обновлен\n')

top_3_ids = r.zrevrange('leaderboard:points', 0, 2)

print('Топ 3 пользователя по очкам:')
result = []
for user_id in top_3_ids:
    name = r.hget(f"user:{user_id}", 'name')
    email = r.hget(f"user:{user_id}", 'email')
    score = r.zscore('leaderboard:points', user_id)
    result.append({
        'id': int(user_id),
        'name': name,
        'email': email,
        'points': int(score)
    })

for i, user in enumerate(result, 1):
    print(f"{i}. {user['name']} ({user['email']}) — {user['points']} очков")
```

**Разбор:**
- Профили хранятся в Hash (`user:{id}`) для быстрого доступа к полям
- Рейтинг хранится в Sorted Set (`leaderboard:points`) для автоматической сортировки
- Связующий элемент — `id` пользователя
- Сначала получаем топ 3 id из Sorted Set, затем для каждого id получаем имя из Hash

**Почему такая структура:**
- Hash удобен для хранения связанных полей (профиль)
- Sorted Set идеален для рейтингов (автоматическая сортировка)
- Разделение ответственности: профиль отдельно, рейтинг отдельно

---

## Задание 7: Pub/Sub — подписка и публикация

**Условие:**
- Создать подписчика на канал уведомлений
- Отправить несколько сообщений в канал
- Подписчик должен получить все сообщения

**Решение:**

```python
from redis import Redis
import threading
import time

r = Redis(host='localhost', port=6379, db=0, decode_responses=True)
pubsub = r.pubsub()

def subscriber():
    pubsub.subscribe('notifications')
    print('Подписчик запущен, ожидает сообщения...\n')
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"Получено сообщение: {message['data']}")

thread = threading.Thread(target=subscriber, daemon=True)
thread.start()

time.sleep(1)

print('Отправка сообщений...')
r.publish('notifications', 'Привет от издателя!')
time.sleep(0.5)
r.publish('notifications', 'Второе сообщение')
time.sleep(0.5)
r.publish('notifications', 'Третье сообщение')

time.sleep(1)
pubsub.unsubscribe('notifications')
print('\nПодписка отменена')
```

**Разбор:**
- `pubsub()` — создает объект для работы с Pub/Sub
- `subscribe(channel)` — подписывается на канал
- `listen()` — слушает сообщения (блокирующий вызов, поэтому в отдельном потоке)
- `publish(channel, message)` — отправляет сообщение в канал
- `unsubscribe(channel)` — отписывается от канала

**Важно:**
- Подписчик должен работать в отдельном потоке, иначе блокирует выполнение
- `listen()` возвращает словари с полями `type` и `data`
- Тип `message` означает реальное сообщение (не служебные события)

---

## Задание 8: Комплексное — система задач с приоритетами

**Условие:**
- Хранить задачи в List (очередь)
- Хранить приоритеты задач в Sorted Set (score = приоритет)
- Добавить несколько задач с приоритетами
- Получить задачу с наивысшим приоритетом
- Удалить задачу из очереди после выполнения

**Решение:**

```python
from redis import Redis

r = Redis(host='localhost', port=6379, db=0, decode_responses=True)

tasks = [
    {'id': 'task1', 'name': 'Важная задача', 'priority': 10},
    {'id': 'task2', 'name': 'Обычная задача', 'priority': 5},
    {'id': 'task3', 'name': 'Срочная задача', 'priority': 15},
    {'id': 'task4', 'name': 'Неважная задача', 'priority': 1}
]

for task in tasks:
    r.lpush('tasks:queue', task['id'])
    r.zadd('tasks:priorities', {task['id']: task['priority']})
    r.hset(f"task:{task['id']}", mapping={
        'name': task['name'],
        'priority': task['priority']
    })

print('Задачи добавлены\n')

top_priority_task_id = r.zrevrange('tasks:priorities', 0, 0)[0]
task_info = r.hgetall(f"task:{top_priority_task_id}")
print(f'Задача с наивысшим приоритетом: {task_info["name"]} (приоритет: {task_info["priority"]})')

r.lrem('tasks:queue', 1, top_priority_task_id)
r.zrem('tasks:priorities', top_priority_task_id)
r.delete(f"task:{top_priority_task_id}")

print(f'Задача {top_priority_task_id} выполнена и удалена')

remaining_tasks = r.lrange('tasks:queue', 0, -1)
print(f'Оставшиеся задачи в очереди: {remaining_tasks}')
```

**Разбор:**
- List хранит порядок задач в очереди
- Sorted Set хранит приоритеты для быстрого поиска задачи с максимальным приоритетом
- Hash хранит детали задачи
- `lrem(key, count, value)` — удаляет элемент из списка
- `zrem(key, member)` — удаляет элемент из Sorted Set
- `delete(key)` — удаляет ключ полностью

---

## Итоговая сводка по структурам данных

| Структура | Когда использовать | Основные операции |
|-----------|-------------------|-------------------|
| **String** | Простые значения, счетчики | `set`, `get`, `incr`, `incrby` |
| **Hash** | Объекты с несколькими полями | `hset`, `hget`, `hgetall`, `hdel` |
| **List** | Очереди, стеки, хронология | `lpush`, `rpush`, `lpop`, `rpop`, `lrange` |
| **Set** | Уникальные элементы, теги | `sadd`, `smembers`, `sinter`, `sunion` |
| **Sorted Set** | Рейтинги, приоритеты | `zadd`, `zrevrange`, `zscore`, `zrank` |
| **Pub/Sub** | Уведомления, события | `subscribe`, `publish`, `listen` |
