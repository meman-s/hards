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

#### 2.1.1 Архитектура потоков

**Поток состоит из:**
- **Стек вызовов** — каждый поток имеет свой стек для локальных переменных и вызовов функций.
- **Регистры CPU** — состояние процессора для каждого потока.
- **Программный счётчик** — текущая инструкция, которую выполняет поток.

**Разделяемые ресурсы:**
- **Куча (heap)** — общая память процесса, доступная всем потокам.
- **Глобальные переменные** — общие для всех потоков.
- **Файловые дескрипторы** — открытые файлы доступны всем потокам.

#### 2.1.2 Переключение контекста (Context Switching)

**Переключение контекста** — процесс сохранения состояния одного потока и загрузки состояния другого.

**Что происходит при переключении:**
1. Сохраняются регистры CPU текущего потока.
2. Сохраняется указатель стека.
3. Загружаются регистры и стек следующего потока.
4. Восстанавливается программный счётчик.

**Накладные расходы:**
- Переключение контекста занимает **1-10 микросекунд**.
- При частых переключениях накладные расходы могут превысить выгоду от параллелизма.
- **Кэш процессора** может быть сброшен при переключении, что замедляет выполнение.

#### 2.1.3 Планировщик потоков

Операционная система использует **планировщик** (scheduler) для распределения времени CPU между потоками.

**Алгоритмы планирования:**
- **Round-robin** — каждому потоку даётся квант времени по очереди.
- **Приоритетное планирование** — потоки с высоким приоритетом выполняются чаще.
- **Многоуровневая очередь** — разные очереди для разных типов задач.

**В Python:**
- Планирование потоков контролируется **операционной системой**, а не Python.
- Python может только **запросить** создание потока, но не управляет его выполнением напрямую.

### 2.2 GIL (Global Interpreter Lock)

**GIL** — глобальная блокировка интерпретатора Python. В любой момент времени только один поток может выполнять Python-код.

#### 2.2.1 Почему существует GIL

GIL был введён в Python для упрощения управления памятью и обеспечения потокобезопасности:

1. **Управление памятью**: Python использует reference counting для управления памятью. Без GIL несколько потоков могли бы одновременно изменять счётчик ссылок, что привело бы к утечкам памяти или двойному освобождению.

2. **Потокобезопасность C-расширений**: Многие C-библиотеки, используемые Python, не были написаны с учётом многопоточности. GIL защищает их от race conditions.

3. **Простота реализации**: GIL упростил реализацию CPython, сделав его более стабильным.

#### 2.2.2 Как работает GIL

GIL работает по принципу **tick-based switching**:

- Каждые **100 тиков** (ticks) интерпретатор проверяет, не нужно ли переключиться на другой поток.
- Тик — это одна инструкция байт-кода Python.
- При I/O операциях (чтение файла, сетевой запрос) поток добровольно освобождает GIL, позволяя другим потокам работать.

**Механизм переключения:**
1. Поток A выполняет Python-код (держит GIL).
2. После 100 тиков или при I/O операции поток A освобождает GIL.
3. Поток B захватывает GIL и начинает выполнение.
4. Процесс повторяется.

#### 2.2.3 Последствия GIL

**Для CPU-bound задач:**
- Потоки **не дают** реального параллелизма — только один поток выполняет Python-код одновременно.
- Множественные потоки для вычислений могут быть даже **медленнее** из-за накладных расходов на переключение контекста.
- GIL создаёт **последовательное выполнение** Python-кода, даже на многоядерных CPU.

**Для I/O-bound задач:**
- Потоки **эффективны** — во время ожидания I/O (сеть, файлы, БД) GIL освобождается.
- Пока один поток ждёт ответа от сети, другие потоки могут выполнять Python-код.
- Это даёт **псевдопараллелизм** для I/O операций.

#### 2.2.4 Попытки убрать GIL

Несколько попыток создать Python без GIL (Unladen Swallow, PyPy, Gilectomy) показали:
- **Снижение производительности** однопоточных программ на 20-50%.
- **Сложность реализации** — требуется полная переработка управления памятью.
- **Проблемы совместимости** с существующими C-расширениями.

**Вывод:** GIL остаётся в CPython как компромисс между простотой, стабильностью и производительностью.

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

#### 2.3.1 Проблема race conditions

**Race condition** (состояние гонки) возникает, когда результат выполнения зависит от порядка выполнения потоков.

**Пример проблемы:**
```python
counter = 0

def increment():
    global counter
    for _ in range(100000):
        counter += 1  # Не атомарная операция!
```

Операция `counter += 1` состоит из трёх шагов:
1. Прочитать значение `counter`.
2. Увеличить его на 1.
3. Записать обратно.

Если два потока выполняют это одновременно, оба могут прочитать одно и то же значение, увеличить его и записать — результат будет неправильным.

**Решение:** использовать блокировки (locks) для синхронизации доступа к общим ресурсам.

#### 2.3.2 Lock (блокировка)

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

**Механизм работы Lock:**
- **Захват (acquire)**: поток пытается захватить блокировку. Если она свободна — захватывает и продолжает. Если занята — блокируется и ждёт.
- **Освобождение (release)**: поток освобождает блокировку, позволяя другим потокам её захватить.
- **Deadlock**: если поток пытается захватить блокировку, которую уже держит — возникает взаимная блокировка (deadlock).

**Типы блокировок:**
- **Lock (обычная)**: может быть захвачена только один раз.
- **RLock (реентерабельная)**: может быть захвачена тем же потоком несколько раз (полезно для рекурсивных функций).

#### 2.3.3 Semaphore (семафор)

**Семафор** — обобщение блокировки, позволяющее N потокам одновременно выполнять критическую секцию.

```python
import threading

semaphore = threading.Semaphore(3)  # Максимум 3 потока одновременно

def worker():
    with semaphore:
        print("Working...")
        time.sleep(1)
```

**Использование:**
- Ограничение количества одновременных подключений к ресурсу.
- Управление пулом ресурсов (например, соединения с БД).

#### 2.3.4 Event (событие)

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

**Event** — механизм для координации потоков через сигналы.

**Механизм работы:**
- **wait()**: поток блокируется, пока событие не будет установлено.
- **set()**: устанавливает событие, пробуждая все ожидающие потоки.
- **clear()**: сбрасывает событие.
- **is_set()**: проверяет, установлено ли событие.

**Использование:**
- Координация запуска потоков.
- Сигнализация о завершении операции.
- Управление жизненным циклом потоков.

#### 2.3.5 Condition (условие)

**Condition** — комбинация Lock и Event, позволяющая потокам ждать выполнения условия.

```python
import threading

condition = threading.Condition()
items = []

def producer():
    with condition:
        items.append("item")
        condition.notify()  # Уведомляет ожидающие потоки

def consumer():
    with condition:
        while not items:
            condition.wait()  # Ждёт, пока items не станет непустым
        item = items.pop()
```

**Использование:**
- Producer-Consumer паттерн.
- Ожидание выполнения условий.
- Координация сложных взаимодействий между потоками.

#### 2.3.6 Queue (очередь)

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

**Queue** — потокобезопасная очередь для обмена данными между потоками.

**Особенности:**
- **Потокобезопасность**: операции `put()` и `get()` атомарны.
- **Блокировка**: `get()` блокируется, если очередь пуста; `put()` блокируется, если очередь полна.
- **Размер**: можно ограничить максимальный размер очереди.

**Типы очередей:**
- **Queue**: обычная очередь (FIFO).
- **LifoQueue**: стек (LIFO).
- **PriorityQueue**: очередь с приоритетами.

#### 2.3.7 Deadlock (взаимная блокировка)

**Deadlock** возникает, когда два или более потока блокируют друг друга, ожидая освобождения ресурсов.

**Условия для deadlock (условия Коффмана):**
1. **Взаимное исключение**: ресурсы не могут использоваться одновременно.
2. **Удержание и ожидание**: поток держит один ресурс и ждёт другой.
3. **Неперераспределяемость**: ресурсы нельзя отобрать у потока.
4. **Циклическое ожидание**: потоки образуют цикл ожидания.

**Пример deadlock:**
```python
lock1 = threading.Lock()
lock2 = threading.Lock()

def thread1():
    with lock1:
        time.sleep(0.1)
        with lock2:  # Ждёт lock2
            pass

def thread2():
    with lock2:
        time.sleep(0.1)
        with lock1:  # Ждёт lock1
            pass
```

**Предотвращение:**
- Всегда захватывать блокировки в **одинаковом порядке**.
- Использовать **таймауты** при захвате блокировок.
- Избегать **вложенных блокировок**.

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

#### 3.1.1 Архитектура процессов

**Процесс состоит из:**
- **Адресное пространство** — изолированная память процесса.
- **Код программы** — исполняемые инструкции.
- **Данные** — переменные, структуры данных.
- **Стек** — для локальных переменных и вызовов функций.
- **Куча** — для динамически выделяемой памяти.
- **Файловые дескрипторы** — открытые файлы и сокеты.
- **Регистры CPU** — состояние процессора.

**Изоляция процессов:**
- Процессы **не могут** напрямую обращаться к памяти друг друга.
- Обмен данными требует **межпроцессного взаимодействия** (IPC).
- Сбой одного процесса **не влияет** на другие.

#### 3.1.2 Создание процессов (fork/spawn)

**Fork (Unix/Linux):**
- Создаёт **копию** родительского процесса.
- Дочерний процесс получает **копию всей памяти** родителя.
- Быстрое создание благодаря **copy-on-write** (COW) — память копируется только при изменении.

**Spawn (Windows, macOS по умолчанию):**
- Запускает **новый интерпретатор Python**.
- Импортирует модуль и выполняет целевую функцию.
- Медленнее, но более безопасно и предсказуемо.

**В Python:**
- На Unix используется **fork** по умолчанию.
- На Windows всегда используется **spawn**.
- Можно выбрать метод через `multiprocessing.set_start_method()`.

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

#### 3.1.3 Параллелизм процессов

**Реальный параллелизм:**
- Каждый процесс имеет **свой GIL** — нет ограничений на параллельное выполнение Python-кода.
- Процессы могут выполняться на **разных ядрах CPU** одновременно.
- Операционная система **распределяет** процессы между ядрами.

**Масштабируемость:**
- Производительность **линейно масштабируется** с количеством ядер CPU (до определённого предела).
- На 4-ядерном CPU можно получить **до 4x ускорение** для CPU-bound задач.
- Накладные расходы на создание и синхронизацию процессов ограничивают выгоду.

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

### 3.3 Обмен данными между процессами (IPC)

**Межпроцессное взаимодействие (IPC)** необходимо, так как процессы имеют изолированную память.

**Методы IPC:**
1. **Queue** — очередь сообщений.
2. **Pipe** — двунаправленный канал.
3. **Shared Memory** — разделяемая память.
4. **Manager** — прокси-объекты для сложных структур данных.

#### 3.3.1 Queue (очередь сообщений)

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

**Queue в multiprocessing:**
- Использует **pickle** для сериализации данных.
- Данные **копируются** между процессами (не разделяются напрямую).
- Поддерживает блокирующие операции `get()` и `put()`.
- Потокобезопасна и процессобезопасна.

#### 3.3.2 Pipe (канал)

**Pipe:**
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

**Shared Memory** — общая область памяти, доступная нескольким процессам.

**Типы shared memory:**
- **Value**: одно значение (int, float, etc.).
- **Array**: массив значений.

**Особенности:**
- **Быстрый доступ**: нет сериализации/десериализации.
- **Требует синхронизации**: нужны блокировки для безопасного доступа.
- **Ограниченные типы**: только простые типы C (int, float, char, etc.).

**Синхронизация shared memory:**
```python
import multiprocessing

lock = multiprocessing.Lock()
shared_value = multiprocessing.Value('i', 0)

def worker(value, lock):
    for _ in range(1000):
        with lock:
            value.value += 1
```

#### 3.3.4 Manager (менеджер объектов)

**Manager** создаёт прокси-объекты для сложных структур данных.

```python
import multiprocessing

def worker(d, l):
    d[1] = '1'
    d['2'] = 2
    l.reverse()

if __name__ == '__main__':
    with multiprocessing.Manager() as manager:
        d = manager.dict()
        l = manager.list(range(10))
        
        p = multiprocessing.Process(target=worker, args=(d, l))
        p.start()
        p.join()
        
        print(d)
        print(l)
```

**Особенности:**
- Поддерживает **сложные структуры**: dict, list, Namespace, etc.
- **Медленнее** shared memory из-за сериализации.
- **Удобнее** для сложных данных.

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

#### 4.1.1 Конкурентность vs Параллелизм

**Важное различие:**
- **Параллелизм** — выполнение нескольких задач **одновременно** (на разных ядрах CPU).
- **Конкурентность** — выполнение нескольких задач **попеременно** (переключение между задачами).

**Async обеспечивает конкурентность, но не параллелизм:**
- В один момент времени выполняется **только одна корутина**.
- Переключение происходит **кооперативно** (корутина сама решает, когда уступить управление).
- Это **не параллелизм**, но эффективно для I/O-bound задач.

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

#### 4.1.2 Корутины (Coroutines)

**Корутина** — функция, которая может быть приостановлена и возобновлена.

**Свойства корутин:**
- **Не выполняется сразу** при вызове — возвращает coroutine object.
- **Выполняется** только при `await` или передаче в event loop.
- **Может быть приостановлена** на `await` и **возобновлена** позже.
- **Сохраняет состояние** между приостановками (локальные переменные, стек вызовов).

**Пример:**
```python
async def coroutine():
    print("Start")
    await asyncio.sleep(1)  # Приостанавливается здесь
    print("End")  # Возобновляется здесь

# Вызов корутины не выполняет её:
coro = coroutine()  # Создаёт coroutine object

# Выполнение:
await coro  # или asyncio.run(coro)
```

#### 4.1.3 Futures и Tasks

**Future** — объект, представляющий результат асинхронной операции, который будет доступен в будущем.

**Task** — подкласс Future, обёртка вокруг корутины, которая планируется для выполнения в event loop.

**Разница:**
- **Future**: результат операции, которая может быть выполнена где-то ещё.
- **Task**: корутина, которая уже запланирована для выполнения.

```python
# Future
future = asyncio.Future()
future.set_result("result")

# Task
task = asyncio.create_task(coroutine())
result = await task
```

### 4.2 Как работает async

#### 4.2.1 Event Loop (цикл событий)

**Event Loop** — центральный механизм asyncio, управляющий выполнением корутин и обработкой событий.

**Основные функции:**
1. **Планирование корутин** — решает, какую корутину выполнять следующей.
2. **Обработка I/O** — отслеживает готовность файловых дескрипторов и сокетов.
3. **Управление таймерами** — обрабатывает `asyncio.sleep()` и другие задержки.
4. **Выполнение callbacks** — вызывает функции обратного вызова.

**Алгоритм работы:**
```
1. Event loop получает список готовых корутин.
2. Выбирает одну корутину и выполняет её до следующего await.
3. Если корутина приостанавливается на await, переходит к следующей.
4. Проверяет готовность I/O операций (epoll/kqueue/select).
5. Возобновляет корутины, ожидающие завершённых I/O операций.
6. Повторяет цикл.
```

#### 4.2.2 Кооперативная многозадачность

**Кооперативная многозадачность** означает, что корутина **сама решает**, когда уступить управление.

**Преимущества:**
- **Низкие накладные расходы** — нет переключения контекста между потоками.
- **Предсказуемость** — переключение происходит только на `await`.
- **Эффективность** — можно создать **тысячи корутин** без проблем с памятью.

**Недостатки:**
- **Блокирующий код** блокирует весь event loop.
- Требуется **дисциплина** — нельзя использовать блокирующие операции.

**Важно:** async **не создаёт потоки или процессы** — это кооперативная многозадачность в одном потоке.

#### 4.2.3 Механизм await

**`await`** — ключевое слово, которое:
1. **Приостанавливает** выполнение текущей корутины.
2. **Возвращает управление** event loop.
3. **Ждёт** завершения операции (обычно I/O).
4. **Возобновляет** выполнение корутины, когда операция завершена.

**Что можно await:**
- Другие корутины.
- Tasks (обёртки вокруг корутин).
- Futures (результаты операций).
- Awaitable объекты (объекты с методом `__await__`).

**Пример работы:**
```python
async def fetch_data():
    print("Start fetching")
    await asyncio.sleep(1)  # Приостанавливается здесь
    print("Data fetched")   # Возобновляется здесь
    return "data"

async def main():
    result = await fetch_data()  # Ждёт завершения fetch_data
    print(result)
```

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

#### 4.4.1 asyncio.gather

**`asyncio.gather`** — запускает несколько корутин **одновременно** и ждёт завершения всех.

**Особенности:**
- Запускает все корутины **сразу** (не последовательно).
- Возвращает **список результатов** в том же порядке, что и аргументы.
- Если одна корутина падает с исключением, остальные **продолжают выполняться**.
- Можно использовать `return_exceptions=True` для получения исключений в результатах.

```python
results = await asyncio.gather(coro1(), coro2(), coro3())
# Все три корутины выполняются параллельно
```

**Преимущества:**
- Простой синтаксис для параллельного выполнения.
- Автоматическая обработка результатов и исключений.

#### 4.4.2 asyncio.create_task

**`asyncio.create_task`** — оборачивает корутину в Task и **планирует** её выполнение.

**Особенности:**
- Создаёт **Task** из корутины.
- Корутина **начинает выполняться** сразу (не ждёт await).
- Возвращает **Task объект**, который можно await позже.
- Полезно для **fire-and-forget** операций или когда нужно контролировать выполнение.

```python
task1 = asyncio.create_task(coro1())  # Начинает выполняться сразу
task2 = asyncio.create_task(coro2())  # Начинает выполняться сразу
# Делаем что-то ещё
result1 = await task1  # Ждём завершения
result2 = await task2  # Ждём завершения
```

**Преимущества:**
- Больше контроля над выполнением.
- Можно отменить задачу через `task.cancel()`.
- Можно проверять статус через `task.done()`.

#### 4.4.3 asyncio.wait

**`asyncio.wait`** — ждёт завершения задач с различными условиями.

```python
done, pending = await asyncio.wait(
    [task1, task2, task3],
    return_when=asyncio.FIRST_COMPLETED  # Ждём первую завершённую
)
```

**Условия возврата:**
- `FIRST_COMPLETED` — когда первая задача завершена.
- `FIRST_EXCEPTION` — когда первая задача упала с исключением.
- `ALL_COMPLETED` — когда все задачи завершены (по умолчанию).

### 4.5 Синхронизация в async

**Зачем нужна синхронизация в async?**
Хотя async однопоточен, **race conditions** всё равно возможны, если несколько корутин обращаются к общим данным между `await` операциями.

#### 4.5.1 Lock (блокировка)

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

**Async Queue** — потокобезопасная очередь для обмена данными между корутинами.

**Особенности:**
- `put()` и `get()` — асинхронные операции (используют await).
- Блокируются только корутины, а не весь поток.
- Эффективна для producer-consumer паттернов в async.

#### 4.5.5 Проблемы синхронизации в async

**Deadlock в async:**
- Возможен, если корутины ждут друг друга через блокировки.
- Решается так же, как в threading — правильный порядок захвата блокировок.

**Starvation (голодание):**
- Корутина может долго ждать, если другие корутины постоянно захватывают ресурс.
- Решается через приоритеты или fair locks.

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

#### 5.1.1 Детальное сравнение производительности

**CPU-bound задачи (100% загрузка CPU):**
- **Threading**: ❌ Не ускоряется (GIL), может быть медленнее из-за накладных расходов.
- **Multiprocessing**: ✅ Линейное ускорение до количества ядер (4 ядра ≈ 4x быстрее).
- **Async**: ❌ Не ускоряется, блокирует event loop.

**I/O-bound задачи (ожидание сети/файлов):**
- **Threading**: ✅ Хорошо, но ограничено количеством потоков (обычно 50-100).
- **Multiprocessing**: ⚠️ Работает, но избыточно (тяжёлые процессы для I/O).
- **Async**: ✅✅ Лучший выбор — тысячи корутин с минимальными накладными расходами.

**Смешанные задачи (I/O + немного CPU):**
- **Threading**: ✅ Хорошо для простых случаев.
- **Multiprocessing**: ⚠️ Избыточно, если CPU часть небольшая.
- **Async**: ✅ Хорошо, но CPU часть должна быть быстрой (не блокировать loop).

#### 5.1.2 Использование памяти

**Threading:**
- Каждый поток: ~1-8 MB (стек потока).
- Общая память процесса.
- **Низкое** потребление памяти.

**Multiprocessing:**
- Каждый процесс: полная копия интерпретатора Python (~30-50 MB).
- Изолированная память.
- **Высокое** потребление памяти (N процессов × размер процесса).

**Async:**
- Каждая корутина: ~1-2 KB (состояние корутины).
- Общая память процесса.
- **Очень низкое** потребление памяти (тысячи корутин ≈ несколько MB).

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

## 7. Дополнительные концепции

### 7.1 Приоритеты потоков

**Приоритет потока** определяет, как часто планировщик ОС выделяет ему время CPU.

**В Python:**
- Python не предоставляет прямого управления приоритетами потоков.
- Приоритеты контролируются **операционной системой**.
- Можно использовать системные вызовы для изменения приоритета (платформо-зависимо).

**Типы приоритетов:**
- **Высокий**: системные потоки, критические операции.
- **Нормальный**: большинство пользовательских потоков.
- **Низкий**: фоновые задачи.

### 7.2 Daemon потоки

**Daemon поток** — поток, который завершается при завершении главного потока.

```python
thread = threading.Thread(target=worker, daemon=True)
thread.start()
# Программа завершится, даже если daemon поток ещё работает
```

**Использование:**
- Фоновые задачи (логирование, мониторинг).
- Задачи, которые можно безопасно прервать.

### 7.3 Thread-local storage

**Thread-local storage** — переменные, уникальные для каждого потока.

```python
import threading

thread_local = threading.local()

def worker():
    thread_local.value = threading.current_thread().name
    print(thread_local.value)

threading.Thread(target=worker).start()
```

**Использование:**
- Хранение контекста запроса в веб-серверах.
- Избежание передачи параметров через все функции.

### 7.4 Memory model (модель памяти)

**Модель памяти** определяет, как потоки видят изменения в памяти.

**В Python:**
- **Последовательная консистентность**: изменения одного потока видны другим, но порядок не гарантирован без синхронизации.
- **Volatile переменных нет**: все переменные могут кэшироваться в регистрах CPU.
- **Атомарные операции**: простые операции (присваивание, чтение) атомарны для простых типов.

**Проблемы:**
- **Visibility**: изменения могут быть не видны другим потокам из-за кэширования.
- **Ordering**: порядок операций может быть переупорядочен компилятором/процессором.

**Решение:**
- Использовать **блокировки** для синхронизации.
- Использовать **volatile-подобные** механизмы (хотя в Python их нет напрямую).

### 7.5 Атомарные операции

**Атомарная операция** — операция, которая выполняется полностью или не выполняется вообще.

**В Python:**
- Простые операции (присваивание, чтение) атомарны для **простых типов** (int, float, bool).
- **Составные операции** (инкремент, append) **не атомарны**.

```python
# НЕ атомарно:
counter += 1  # Состоит из: read, increment, write

# Атомарно (для простых типов):
x = 5  # Атомарное присваивание
```

**Для атомарных операций:**
- Использовать блокировки.
- Использовать `queue.Queue` для обмена данными.
- Использовать `multiprocessing.Value` с блокировкой для процессов.

### 7.6 Производительность и оптимизация

**Оптимизация потоков:**
- Использовать **ThreadPoolExecutor** вместо создания потоков вручную.
- Ограничить количество потоков (обычно CPU_count * 2-4 для I/O).
- Избегать **излишней синхронизации** (блокировки замедляют выполнение).

**Оптимизация процессов:**
- Переиспользовать процессы через **ProcessPoolExecutor**.
- Минимизировать передачу данных между процессами (сериализация дорогая).
- Использовать **shared memory** для больших данных.

**Оптимизация async:**
- Избегать **блокирующего кода** в корутинах.
- Использовать **async версии** библиотек (aiohttp вместо requests).
- Группировать I/O операции через `asyncio.gather()`.

### 7.7 Выбор подхода: Decision Tree

**Алгоритм выбора:**

1. **Задача CPU-bound?** (интенсивные вычисления)
   - Да → **Multiprocessing**
   - Нет → Переход к шагу 2

2. **Задача I/O-bound?** (сеть, файлы, БД)
   - Да → Переход к шагу 3
   - Нет → Переход к шагу 4

3. **Много одновременных операций?** (>100)
   - Да → **Async**
   - Нет → **Threading**

4. **Смешанная задача?**
   - Использовать **комбинацию**: Async для I/O + ProcessPoolExecutor для CPU-bound частей

**Примеры:**
- Веб-сервер с тысячами соединений → **Async**
- Обработка изображений → **Multiprocessing**
- Простой веб-скрапинг (10-50 URL) → **Threading**
- Веб-сервер с обработкой изображений → **Async + ProcessPoolExecutor**

### 7.8 Отладка и профилирование

**Отладка потоков:**
- Использовать **threading.current_thread()** для идентификации потоков.
- Логировать с **идентификатором потока**.
- Использовать **threading.enumerate()** для списка всех потоков.

**Отладка процессов:**
- Использовать **multiprocessing.current_process()** для идентификации процессов.
- Логировать в **отдельные файлы** для каждого процесса.
- Использовать **multiprocessing.active_children()** для списка процессов.

**Отладка async:**
- Использовать **asyncio.current_task()** для идентификации задач.
- Включить **asyncio debug mode**: `asyncio.run(main(), debug=True)`.
- Использовать **asyncio.all_tasks()** для списка всех задач.

**Профилирование:**
- **cProfile** для CPU-bound задач.
- **py-spy** для профилирования работающих процессов.
- **memory_profiler** для анализа использования памяти.

### 7.9 Ошибки и антипаттерны

**Антипаттерны в Threading:**
- ❌ Использование потоков для CPU-bound задач.
- ❌ Забывание использовать блокировки для общих данных.
- ❌ Создание слишком большого количества потоков.
- ❌ Использование глобальных переменных без синхронизации.

**Антипаттерны в Multiprocessing:**
- ❌ Передача больших объектов между процессами (дорогая сериализация).
- ❌ Создание процессов в цикле без пула.
- ❌ Забывание `if __name__ == "__main__"` (вызовет ошибки на Windows).
- ❌ Использование процессов для I/O-bound задач.

**Антипаттерны в Async:**
- ❌ Блокирующий код в корутинах (`time.sleep` вместо `asyncio.sleep`).
- ❌ Использование синхронных библиотек в async коде.
- ❌ Создание корутин без await (забывание await).
- ❌ Бесконечные циклы без await (блокируют event loop).

### 7.10 Реализация под капотом

**Как работает Threading:**
- Python использует **нативные потоки ОС** (pthreads на Unix, Windows threads на Windows).
- GIL реализован через **mutex** (mutual exclusion lock).
- Переключение потоков контролируется **планировщиком ОС**.

**Как работает Multiprocessing:**
- На Unix использует **fork()** системный вызов.
- На Windows использует **spawn** (запуск нового процесса).
- Данные сериализуются через **pickle** при передаче между процессами.

**Как работает Async:**
- Event loop использует **select/epoll/kqueue** для мониторинга I/O.
- Корутины реализованы через **генераторы** (yield from).
- Переключение корутин происходит через **yield points** (await).

## 8. Краткая сводка для экзамена

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
