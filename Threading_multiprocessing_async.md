# Threading vs Multiprocessing vs Async

## 1. Зачем нужны разные подходы

Python предоставляет три основных способа выполнения параллельного/конкурентного кода:

- **Threading** — потоки (threads) для I/O-bound задач.
- **Multiprocessing** — процессы для CPU-bound задач.
- **Async** — асинхронное программирование для конкурентного I/O.

Выбор зависит от типа задачи: CPU-bound (вычисления) или I/O-bound (сеть, файлы, базы данных).

---

## 2. Threading (потоки)

### 2.1 Что такое потоки

**Поток (thread)** — лёгкая единица выполнения внутри одного процесса. Потоки разделяют память процесса, но имеют собственный стек вызовов.

```python
import threading
import time

def worker(name):
    print(f"Thread {name} started")
    time.sleep(2)
    print(f"Thread {name} finished")

t1 = threading.Thread(target=worker, args=("A",))
t2 = threading.Thread(target=worker, args=("B",))

t1.start()
t2.start()

t1.join()
t2.join()
```

Потоки выполняются параллельно (или кажутся параллельными благодаря переключению контекста).

### 2.2 GIL (Global Interpreter Lock)

**GIL** — глобальная блокировка интерпретатора Python. В любой момент времени только один поток может выполнять Python-код.

**Последствия:**
- Потоки **не дают** реального параллелизма для CPU-bound задач.
- Потоки **эффективны** для I/O-bound задач (во время ожидания I/O GIL освобождается).

**Пример CPU-bound (потоки не помогут):**
```python
import threading

def cpu_task():
    total = 0
    for i in range(10000000):
        total += i
    return total

threads = [threading.Thread(target=cpu_task) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

Этот код **не ускорится** из-за GIL — потоки будут выполняться последовательно.

**Пример I/O-bound (потоки помогут):**
```python
import threading
import requests

def fetch_url(url):
    response = requests.get(url)
    return len(response.content)

urls = ["http://example.com"] * 10
threads = [threading.Thread(target=fetch_url, args=(url,)) for url in urls]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

Здесь потоки эффективны: пока один поток ждёт ответа от сети, другой может работать.

### 2.3 Синхронизация потоков

**Lock (блокировка):**
```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100000):
        with lock:
            counter += 1

threads = [threading.Thread(target=increment) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

`Lock` гарантирует, что только один поток может выполнять критическую секцию одновременно.

**Event (событие):**
```python
import threading

event = threading.Event()

def waiter():
    print("Waiting for event...")
    event.wait()
    print("Event occurred!")

def setter():
    time.sleep(2)
    event.set()

threading.Thread(target=waiter).start()
threading.Thread(target=setter).start()
```

**Queue (очередь):**
```python
import threading
from queue import Queue

q = Queue()

def producer():
    for i in range(5):
        q.put(i)
        print(f"Produced {i}")

def consumer():
    while True:
        item = q.get()
        if item is None:
            break
        print(f"Consumed {item}")
        q.task_done()

threading.Thread(target=producer).start()
threading.Thread(target=consumer).start()
q.join()
```

### 2.4 ThreadPoolExecutor

**`ThreadPoolExecutor`** — пул потоков для удобного управления:

```python
from concurrent.futures import ThreadPoolExecutor
import requests

def fetch(url):
    return requests.get(url).status_code

urls = ["http://example.com"] * 10

with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(fetch, urls)
    print(list(results))
```

### 2.5 Когда использовать Threading

| Сценарий | Подходит? |
|----------|-----------|
| I/O-bound задачи (сеть, файлы, БД) | ✅ Да |
| CPU-bound задачи (вычисления) | ❌ Нет (GIL) |
| Простые конкурентные операции | ✅ Да |
| Нужна общая память | ✅ Да (потоки разделяют память) |

---

## 3. Multiprocessing (процессы)

### 3.1 Что такое процессы

**Процесс** — отдельный экземпляр программы с собственной памятью. Процессы не разделяют память (если не использовать специальные механизмы).

```python
import multiprocessing
import time

def worker(name):
    print(f"Process {name} started")
    time.sleep(2)
    print(f"Process {name} finished")

if __name__ == "__main__":
    p1 = multiprocessing.Process(target=worker, args=("A",))
    p2 = multiprocessing.Process(target=worker, args=("B",))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
```

Процессы выполняются **реально параллельно** (на разных ядрах CPU), каждый имеет свой интерпретатор Python и свой GIL.

### 3.2 Преимущества процессов

- **Реальный параллелизм** — нет GIL, можно использовать все ядра CPU.
- **Изоляция** — сбой одного процесса не влияет на другие.
- **Подходит для CPU-bound задач** — вычисления ускоряются пропорционально количеству ядер.

**Пример CPU-bound (процессы помогут):**
```python
import multiprocessing

def cpu_task(n):
    total = 0
    for i in range(n):
        total += i
    return total

if __name__ == "__main__":
    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(cpu_task, [10000000] * 4)
```

Этот код **ускорится** на многоядерном CPU.

### 3.3 Обмен данными между процессами

**Queue:**
```python
import multiprocessing

def producer(q):
    for i in range(5):
        q.put(i)

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print(f"Got {item}")

if __name__ == "__main__":
    q = multiprocessing.Queue()
    p1 = multiprocessing.Process(target=producer, args=(q,))
    p2 = multiprocessing.Process(target=consumer, args=(q,))
    
    p1.start()
    p2.start()
    p1.join()
    q.put(None)
    p2.join()
```

**Pipe:**
```python
import multiprocessing

def sender(conn):
    conn.send("Hello from process")
    conn.close()

def receiver(conn):
    msg = conn.recv()
    print(msg)
    conn.close()

if __name__ == "__main__":
    parent_conn, child_conn = multiprocessing.Pipe()
    p1 = multiprocessing.Process(target=sender, args=(child_conn,))
    p2 = multiprocessing.Process(target=receiver, args=(parent_conn,))
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()
```

**Shared memory:**
```python
import multiprocessing

def worker(shared_value):
    shared_value.value += 1

if __name__ == "__main__":
    shared_value = multiprocessing.Value('i', 0)
    processes = [multiprocessing.Process(target=worker, args=(shared_value,)) for _ in range(4)]
    
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    
    print(shared_value.value)
```

### 3.4 ProcessPoolExecutor

**`ProcessPoolExecutor`** — пул процессов:

```python
from concurrent.futures import ProcessPoolExecutor

def cpu_task(n):
    return sum(range(n))

if __name__ == "__main__":
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = executor.map(cpu_task, [1000000] * 8)
        print(list(results))
```

### 3.5 Недостатки процессов

- **Больше памяти** — каждый процесс имеет свою копию интерпретатора и данных.
- **Медленнее создание** — процессы тяжелее потоков.
- **Сложнее обмен данными** — нужны специальные механизмы (Queue, Pipe, shared memory).
- **Не подходит для I/O-bound** — избыточно, лучше async или threads.

### 3.6 Когда использовать Multiprocessing

| Сценарий | Подходит? |
|----------|-----------|
| CPU-bound задачи (вычисления) | ✅ Да |
| Нужен реальный параллелизм | ✅ Да |
| I/O-bound задачи | ⚠️ Работает, но избыточно |
| Нужна изоляция процессов | ✅ Да |
| Ограниченная память | ❌ Нет (процессы тяжёлые) |

---

## 4. Async (асинхронное программирование)

### 4.1 Что такое async/await

**Асинхронное программирование** — однопоточная модель конкурентности. Пока одна операция ждёт I/O, выполняется другая.

```python
import asyncio

async def fetch_data(url):
    await asyncio.sleep(1)
    return f"Data from {url}"

async def main():
    tasks = [fetch_data(f"url_{i}") for i in range(5)]
    results = await asyncio.gather(*tasks)
    print(results)

asyncio.run(main())
```

**Ключевые понятия:**
- **`async def`** — асинхронная функция (корутина).
- **`await`** — приостанавливает выполнение, пока операция не завершится.
- **Event loop** — управляет выполнением корутин.

### 4.2 Как работает async

1. Корутина приостанавливается на `await`.
2. Event loop переключается на другую корутину.
3. Когда I/O завершается, корутина возобновляется.

**Важно:** async **не создаёт потоки или процессы** — это кооперативная многозадачность в одном потоке.

### 4.3 Асинхронные операции

**Сеть (aiohttp):**
```python
import aiohttp
import asyncio

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, "http://example.com") for _ in range(10)]
        results = await asyncio.gather(*tasks)
        return results

asyncio.run(main())
```

**Файлы (aiofiles):**
```python
import aiofiles
import asyncio

async def read_file(filename):
    async with aiofiles.open(filename, 'r') as f:
        content = await f.read()
    return content

async def main():
    content = await read_file("data.txt")
    print(content)

asyncio.run(main())
```

**Базы данных (asyncpg, aiomysql):**
```python
import asyncpg
import asyncio

async def fetch_users():
    conn = await asyncpg.connect("postgresql://...")
    users = await conn.fetch("SELECT * FROM users")
    await conn.close()
    return users

asyncio.run(fetch_users())
```

### 4.4 asyncio.gather vs asyncio.create_task

**`asyncio.gather`** — ждёт завершения всех корутин:
```python
results = await asyncio.gather(coro1(), coro2(), coro3())
```

**`asyncio.create_task`** — запускает корутину, не дожидаясь:
```python
task1 = asyncio.create_task(coro1())
task2 = asyncio.create_task(coro2())
result1 = await task1
result2 = await task2
```

### 4.5 Синхронизация в async

**Lock:**
```python
import asyncio

lock = asyncio.Lock()

async def worker(name):
    async with lock:
        print(f"{name} acquired lock")
        await asyncio.sleep(1)
        print(f"{name} released lock")
```

**Event:**
```python
event = asyncio.Event()

async def waiter():
    await event.wait()
    print("Event occurred!")

async def setter():
    await asyncio.sleep(2)
    event.set()
```

**Queue:**
```python
queue = asyncio.Queue()

async def producer():
    for i in range(5):
        await queue.put(i)
        print(f"Produced {i}")

async def consumer():
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Consumed {item}")
        queue.task_done()
```

### 4.6 Когда использовать Async

| Сценарий | Подходит? |
|----------|-----------|
| I/O-bound задачи (сеть, файлы, БД) | ✅ Да (лучший выбор) |
| Много конкурентных соединений | ✅ Да (тысячи корутин) |
| CPU-bound задачи | ❌ Нет (блокирует event loop) |
| Простые конкурентные операции | ✅ Да |
| Нужна низкая задержка | ✅ Да |

---

## 5. Сравнение подходов

### 5.1 Таблица сравнения

| Характеристика | Threading | Multiprocessing | Async |
|----------------|-----------|-----------------|-------|
| **Параллелизм** | Псевдопараллелизм (GIL) | Реальный параллелизм | Конкурентность (кооперативная) |
| **Память** | Разделяемая | Изолированная | Разделяемая (один поток) |
| **CPU-bound** | ❌ Неэффективно | ✅ Эффективно | ❌ Неэффективно |
| **I/O-bound** | ✅ Эффективно | ⚠️ Работает, но избыточно | ✅ Очень эффективно |
| **Сложность** | Средняя | Высокая | Средняя |
| **Масштабируемость** | Ограничена (GIL) | Хорошая (ядра CPU) | Отличная (тысячи корутин) |
| **Накладные расходы** | Низкие | Высокие | Очень низкие |
| **Отладка** | Сложная (race conditions) | Сложная | Проще (однопоточность) |

### 5.2 Когда что использовать

**Threading:**
- Простые I/O-bound задачи.
- Нужна общая память.
- Работа с библиотеками, которые не поддерживают async.

**Multiprocessing:**
- CPU-bound задачи (вычисления, обработка данных).
- Нужен реальный параллелизм.
- Изоляция процессов важна.

**Async:**
- I/O-bound задачи с высокой конкурентностью.
- Веб-серверы, API клиенты.
- Много одновременных соединений.
- Низкая задержка важна.

### 5.3 Комбинирование подходов

**Async + Threading (для блокирующего кода):**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def blocking_operation():
    time.sleep(2)
    return "result"

async def main():
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, blocking_operation)
    print(result)

asyncio.run(main())
```

**Async + Multiprocessing (для CPU-bound в async):**
```python
import asyncio
from concurrent.futures import ProcessPoolExecutor

def cpu_task(n):
    return sum(range(n))

async def main():
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, cpu_task, 1000000)
    print(result)

asyncio.run(main())
```

---

## 6. Практические примеры

### 6.1 Веб-скрапинг

**Threading:**
```python
from concurrent.futures import ThreadPoolExecutor
import requests

def fetch(url):
    return requests.get(url).text

urls = ["http://example.com"] * 10
with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(fetch, urls)
```

**Async (лучше):**
```python
import aiohttp
import asyncio

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

asyncio.run(main())
```

### 6.2 Обработка изображений (CPU-bound)

**Multiprocessing:**
```python
from concurrent.futures import ProcessPoolExecutor
from PIL import Image

def process_image(filename):
    img = Image.open(filename)
    img = img.resize((800, 600))
    img.save(f"processed_{filename}")
    return filename

filenames = ["img1.jpg", "img2.jpg", "img3.jpg"]
with ProcessPoolExecutor(max_workers=4) as executor:
    results = executor.map(process_image, filenames)
```

### 6.3 Веб-сервер

**Async (FastAPI, aiohttp):**
```python
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/")
async def read_root():
    await asyncio.sleep(0.1)
    return {"message": "Hello"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    data = await fetch_from_db(item_id)
    return data
```

---

## 7. Краткая сводка для экзамена

| Концепция | Кратко |
|-----------|--------|
| **Threading** | Потоки, разделяют память, GIL ограничивает CPU-bound, эффективен для I/O |
| **GIL** | Глобальная блокировка интерпретатора, только один поток выполняет Python-код |
| **Multiprocessing** | Процессы, изолированная память, реальный параллелизм, эффективен для CPU-bound |
| **Async** | Асинхронное программирование, корутины, event loop, эффективен для I/O-bound |
| **async def** | Асинхронная функция (корутина) |
| **await** | Приостанавливает корутину до завершения операции |
| **Event loop** | Управляет выполнением корутин в async |
| **CPU-bound** | Задачи, ограниченные процессором (вычисления) → Multiprocessing |
| **I/O-bound** | Задачи, ограниченные вводом/выводом (сеть, файлы) → Async или Threading |
| **ThreadPoolExecutor** | Пул потоков для удобного управления |
| **ProcessPoolExecutor** | Пул процессов для CPU-bound задач |
| **asyncio.gather** | Запускает несколько корутин и ждёт все результаты |
| **asyncio.create_task** | Запускает корутину, не дожидаясь её завершения |

### Когда использовать

- **Threading:** простые I/O-bound задачи, общая память нужна.
- **Multiprocessing:** CPU-bound задачи, нужен реальный параллелизм.
- **Async:** I/O-bound задачи с высокой конкурентностью, веб-серверы, API.

---

## 8. Полезные ссылки

- [docs.python.org — threading — Thread-based parallelism](https://docs.python.org/3/library/threading.html)
- [docs.python.org — multiprocessing — Process-based parallelism](https://docs.python.org/3/library/multiprocessing.html)
- [docs.python.org — asyncio — Asynchronous I/O](https://docs.python.org/3/library/asyncio.html)
- [Real Python — Python Threading](https://realpython.com/intro-to-python-threading/)
- [Real Python — Python Multiprocessing](https://realpython.com/python-multiprocessing/)
- [Real Python — Async IO in Python](https://realpython.com/async-io-python/)
- [Python GIL Explained](https://wiki.python.org/moin/GlobalInterpreterLock)
