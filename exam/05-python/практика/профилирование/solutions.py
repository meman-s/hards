"""
Задания по профилированию и оптимизации кода
Каждая функция содержит неоптимизированный код с узким местом
"""


def задание_1_неэффективный_поиск():
    """
    Задание 1: Неэффективный поиск в списке

    Проблема: Поиск пользователя по email выполняется за O(n) для каждого вызова.
    При большом количестве пользователей и множественных поисках это очень медленно.

    Задача: Найдите узкое место и оптимизируйте его.
    """
    class UserService:
        def __init__(self):
            self.users = []
            self.emails = {}

        def add_user(self, name, email):
            user = {"name": name, "email": email}
            self.users.append(user)
            self.emails[email] = user

        def find_user_by_email(self, email):
            return self.emails.get(email)

        def get_user_statistics(self):
            stats = {}
            for user in self.users:
                domain = user["email"].split("@")[1]
                stats[domain] = stats.get(domain, 0) + 1
            return stats

    service = UserService()
    for i in range(10000):
        service.add_user(f"User {i}", f"user{i}@example.com")

    for i in range(1000):
        service.find_user_by_email(f"user{i}@example.com")

    return service


def задание_2_n_plus_1_проблема():
    """
    Задание 2: N+1 проблема с базой данных

    Проблема: Для каждого заказа выполняется отдельный запрос к БД.
    При N заказах выполняется 1 + N запросов (N+1 проблема).

    Задача: Оптимизируйте код, чтобы уменьшить количество запросов.
    """
    class MockDB:
        def __init__(self):
            self.queries = []

        def query(self, sql):
            self.queries.append(sql)
            return []

    class OrderService:
        def __init__(self, db):
            self.db = db

        def get_orders_with_customers(self):
            orders = self.db.query("SELECT id, customer_id, total FROM orders")

            if not orders:
                return []

            customers_ids = [o["customer_id"] for o in orders]
            customers_ids_for_query = ','.join(map(str, customers_ids))
            customers = self.db.query(f"SELECT id, name, email FROM customers WHERE id IN ({customers_ids_for_query})")
            customers_dict = {c['id']: c for c in customers}

            result = []
            for order in orders:
                customer = customers_dict.get(order["customer_id"])
                if customer:
                    result.append({
                        "order_id": order["id"],
                        "total": order["total"],
                        "customer_name": customer["name"],
                        "customer_email": customer["email"]
                    })
            return result

    db = MockDB()
    service = OrderService(db)
    service.get_orders_with_customers()
    print(f"Выполнено запросов: {len(db.queries)}")

    return service, db


def задание_3_неэффективная_работа_со_строками():
    """
    Задание 3: Неэффективная работа со строками

    Проблема: Конкатенация строк через += создает новую строку при каждой операции.
    Это приводит к квадратичной сложности O(n²).

    Задача: Оптимизируйте код, используя эффективные методы работы со строками.
    """
    def process_text(text):
        import re
        from collections import Counter

        words = re.findall(r'\w+', text)
        return dict(Counter(w.lower() for w in words))

    large_text = "word " * 100000
    result = process_text(large_text)

    return result


def задание_4_избыточные_вычисления():
    """
    Задание 4: Избыточные вычисления и кэширование

    Проблема: Факториал вычисляется заново для каждого числа, даже если уже вычислялся.
    При повторяющихся значениях выполняется много избыточной работы.

    Задача: Добавьте кэширование, чтобы избежать повторных вычислений.
    """
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def factorial(n):
        if n <= 1:
            return 1
        return n * factorial(n - 1)

    def process_numbers(numbers):
        return [factorial(num) for num in numbers]

    numbers = [10, 15, 20, 10, 15, 20, 10, 15, 20] * 100
    result = process_numbers(numbers)

    return result


def задание_5_проблемы_с_памятью():
    """
    Задание 5: Проблемы с памятью при обработке больших файлов

    Проблема: readlines() загружает весь файл в память сразу.
    При больших файлах это может привести к нехватке памяти.

    Задача: Оптимизируйте код для построчной обработки файла.
    """
    def process_large_file(filename):
        with open(filename, 'r') as f:
            for line in f:
                yield line.strip().upper()

    with open('large_file.txt', 'w') as f:
        for i in range(1000000):
            f.write(f"Line {i} with some data\n")

    result = list(process_large_file('large_file.txt'))
    return result


def задание_6_неэффективная_сортировка():
    """
    Задание 6: Неэффективная сортировка и фильтрация

    Проблема: Использована пузырьковая сортировка O(n²) и неэффективная фильтрация.

    Задача: Используйте встроенные функции Python для оптимизации.
    """
    class ProductService:
        def __init__(self):
            self.products = []

        def add_product(self, name, price, category):
            self.products.append({
                "name": name,
                "price": price,
                "category": category
            })

        def get_expensive_products(self, min_price):
            expensive = [p for p in self.products if p['price'] >= min_price]
            expensive.sort(key=lambda x: x['price'], reverse=True)
            return expensive

    service = ProductService()
    for i in range(50000):
        service.add_product(f"Product {i}", i * 10, f"Category {i % 10}")

    result = service.get_expensive_products(100000)
    return result


def задание_7_неэффективные_списки():
    """
    Задание 7: Неэффективное использование списков

    Проблема: Использование list.insert(0, ...) для добавления в начало списка.
    Это операция O(n), так как все элементы нужно сдвинуть.

    Задача: Используйте более эффективную структуру данных.
    """
    def reverse_list(items):
        return list(reversed(items))

    def get_last_n_items(items, n):
        return items[-n:]

    def add_to_beggining(items, new_items):
        from collections import deque

        dq = deque(items)
        for item in new_items:
            dq.appendleft(item)
        return list(dq)

    large_list = list(range(100000))
    reversed_list = reverse_list(large_list)
    last_items = get_last_n_items(large_list, 1000)

    return reversed_list, last_items


def задание_8_избыточные_проверки():
    """
    Задание 8: Избыточные проверки и условия

    Проблема: Множественные проверки одного и того же условия в цикле.
    Условие проверяется на каждой итерации, хотя результат не меняется.

    Задача: Вынесите проверки за пределы цикла.
    """
    def process_items(items, filter_enabled, transform_enabled):
        if filter_enabled and transform_enabled:
            return [item * 2 for item in items if item > 0]
        elif filter_enabled:
            return [item for item in items if item > 0]
        elif transform_enabled:
            return [item * 2 for item in items]
        return items

    items = list(range(-1000, 10000))
    result = process_items(items, True, True)

    return result


def задание_9_неэффективная_работа_с_словарями():
    """
    Задание 9: Неэффективная работа со словарями

    Проблема: Множественные обращения к словарю с проверкой наличия ключа.
    Использование if key in dict вместо dict.get() или defaultdict.

    Задача: Оптимизируйте работу со словарями.
    """
    from collections import defaultdict

    def count_items(items):
        stats = defaultdict(int)
        for item in items:
            stats[item] += 1
        return stats

    def merge_dicts(dict1, dict2):
        result = defaultdict(int)
        for key, value in dict1.items():
            result[key] = value
        for key, value in dict2.items():
            result[key] += value
        return dict(result)

    items = [i % 100 for i in range(100000)]
    stats = count_items(items)

    dict1 = {i: i * 2 for i in range(1000)}
    dict2 = {i: i * 3 for i in range(500, 1500)}
    merged = merge_dicts(dict1, dict2)

    return stats, merged


def задание_10_неэффективные_генераторы():
    """
    Задание 10: Неэффективное использование генераторов и итераторов

    Проблема: Преобразование генератора в список несколько раз.
    Множественные проходы по данным вместо одного.

    Задача: Оптимизируйте использование генераторов.
    """
    def process_data(data):
        return sorted(x ** 2 for x in data if x ** 2 > 100)

    def get_statistics(data):
        total = 0
        count = 0
        maxv = float('-inf')
        minv = float('inf')

        for item in data:
            count += 1
            total += item
            if item > maxv:
                maxv = item
            if item < minv:
                minv = item

        average = total / count if count > 0 else 0

        return {
            "total": total,
            "count": count,
            "average": average,
            "max": maxv,
            "min": minv
        }

    large_data = list(range(100000))
    processed = process_data(large_data)
    stats = get_statistics(large_data)

    return processed, stats


if __name__ == "__main__":
    print("Запуск заданий по профилированию и оптимизации кода")
    print("=" * 60)
    задание_1_неэффективный_поиск()
    задание_2_n_plus_1_проблема()
    задание_3_неэффективная_работа_со_строками()
    задание_4_избыточные_вычисления()
    задание_5_проблемы_с_памятью()
    задание_6_неэффективная_сортировка()
    задание_7_неэффективные_списки()
    задание_8_избыточные_проверки()
    задание_9_неэффективная_работа_с_словарями()
    задание_10_неэффективные_генераторы()
    print("\nДля запуска конкретного задания вызовите соответствующую функцию")
    print("Например: задание_1_неэффективный_поиск()")
