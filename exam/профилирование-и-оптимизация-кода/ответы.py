"""
Ответы: Оптимизированные решения заданий по профилированию
Каждая функция содержит оптимизированный код с объяснением улучшений
"""

from functools import lru_cache
from collections import Counter, defaultdict
import re


def ответ_1_неэффективный_поиск():
    """
    Оптимизация: Использование словаря для индексации по email

    Было: O(n) для каждого поиска
    Стало: O(1) для каждого поиска
    """
    class UserService:
        def __init__(self):
            self.users = []
            self.email_index = {}

        def add_user(self, name, email):
            user = {"name": name, "email": email}
            self.users.append(user)
            self.email_index[email] = user

        def find_user_by_email(self, email):
            return self.email_index.get(email)

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


def ответ_2_n_plus_1_проблема():
    """
    Оптимизация: Один запрос вместо N+1 запросов

    Было: 1 + N запросов
    Стало: 2 запроса (1 для заказов, 1 для всех клиентов)
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

            customer_ids = [order['customer_id'] for order in orders]
            placeholders = ','.join(map(str, customer_ids))
            customers_query = f"SELECT id, name, email FROM customers WHERE id IN ({placeholders})"
            customers = self.db.query(customers_query)

            # ВАЖНО: В реальном коде используйте параметризованные запросы для безопасности!
            # Пример: db.query("SELECT ... WHERE id IN (?)", customer_ids)

            customer_dict = {c['id']: c for c in customers}

            result = []
            for order in orders:
                customer = customer_dict.get(order['customer_id'])
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


def ответ_3_неэффективная_работа_со_строками():
    """
    Оптимизация: Использование регулярных выражений или списков вместо конкатенации

    Было: O(n²) из-за конкатенации строк
    Стало: O(n) с использованием regex или списков
    """
    def process_text(text):
        words = re.findall(r'\w+', text)
        stats = Counter(word.lower() for word in words)
        return dict(stats)

    large_text = "word " * 100000
    result = process_text(large_text)

    return result


def ответ_4_избыточные_вычисления():
    """
    Оптимизация: Мемоизация с помощью @lru_cache

    Было: Повторные вычисления для одинаковых значений
    Стало: Кэширование результатов, O(1) для повторных вызовов
    """
    @lru_cache(maxsize=None)
    def factorial(n):
        if n <= 1:
            return 1
        return n * factorial(n - 1)

    def process_numbers(numbers):
        results = []
        for num in numbers:
            results.append(factorial(num))
        return results

    numbers = [10, 15, 20, 10, 15, 20, 10, 15, 20] * 100
    result = process_numbers(numbers)

    return result


def ответ_5_проблемы_с_памятью():
    """
    Оптимизация: Построчная обработка файла вместо загрузки всего в память

    Было: O(n) памяти для всего файла
    Стало: O(1) памяти для каждой строки
    """
    def process_large_file(filename):
        processed = []
        with open(filename, 'r') as f:
            for line in f:
                processed.append(line.strip().upper())
        return processed

    with open('large_file.txt', 'w') as f:
        for i in range(1000000):
            f.write(f"Line {i} with some data\n")

    result = process_large_file('large_file.txt')
    return result


def ответ_6_неэффективная_сортировка():
    """
    Оптимизация: Встроенная сортировка Timsort вместо пузырьковой

    Было: O(n²) пузырьковая сортировка
    Стало: O(n log n) встроенная сортировка
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
            expensive = [
                product for product in self.products
                if product["price"] >= min_price
            ]
            expensive.sort(key=lambda x: x["price"], reverse=True)
            return expensive

    service = ProductService()
    for i in range(50000):
        service.add_product(f"Product {i}", i * 10, f"Category {i % 10}")

    result = service.get_expensive_products(100000)
    return result


def ответ_7_неэффективные_списки():
    """
    Оптимизация: Использование reversed() и срезов вместо insert(0, ...)

    Было: O(n²) из-за insert(0, ...) в цикле
    Стало: O(n) с использованием reversed() и срезов

    Примечание: Для частых операций добавления в начало используйте collections.deque
    """
    from collections import deque

    def reverse_list(items):
        return list(reversed(items))

    def get_last_n_items(items, n):
        return items[-n:]

    def reverse_list_with_deque(items):
        dq = deque(items)
        return list(reversed(dq))

    def add_to_beginning_efficient(items, new_items):
        dq = deque(items)
        for item in reversed(new_items):
            dq.appendleft(item)
        return list(dq)

    large_list = list(range(100000))
    reversed_list = reverse_list(large_list)
    last_items = get_last_n_items(large_list, 1000)

    new_items = [999, 998, 997]
    result_with_deque = add_to_beginning_efficient(large_list, new_items)

    return reversed_list, last_items, result_with_deque


def ответ_8_избыточные_проверки():
    """
    Оптимизация: Вынесение проверок за пределы цикла

    Было: Проверка условий на каждой итерации
    Стало: Проверка один раз перед циклом
    """
    def process_items(items, filter_enabled, transform_enabled):
        if filter_enabled and transform_enabled:
            return [item * 2 for item in items if item > 0]
        elif filter_enabled:
            return [item for item in items if item > 0]
        elif transform_enabled:
            return [item * 2 for item in items]
        else:
            return list(items)

    items = list(range(-1000, 10000))
    result = process_items(items, True, True)

    return result


def ответ_9_неэффективная_работа_с_словарями():
    """
    Оптимизация: Использование defaultdict и dict.get()

    Было: Множественные проверки if key in dict
    Стало: defaultdict или dict.get() для упрощения кода
    """
    def count_items(items):
        stats = defaultdict(int)
        for item in items:
            stats[item] += 1
        return dict(stats)

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


def ответ_10_неэффективные_генераторы():
    """
    Оптимизация: Один проход по данным, использование генераторов

    Было: Множественные проходы по данным
    Стало: Один проход с генераторами
    """
    def process_data(data):
        filtered_squared = (x ** 2 for x in data if x ** 2 > 100)
        return sorted(filtered_squared)

    def get_statistics(data):
        total = 0
        count = 0
        # This line initializes max_val to negative infinity to ensure any number in the data will be larger.
        max_val = float('-inf')
        min_val = float('inf')

        for item in data:
            total += item
            count += 1
            if item > max_val:
                max_val = item
            if item < min_val:
                min_val = item

        average = total / count if count > 0 else 0

        return {
            "total": total,
            "count": count,
            "average": average,
            "max": max_val,
            "min": min_val
        }

    large_data = list(range(100000))
    processed = process_data(large_data)
    stats = get_statistics(large_data)

    return processed, stats


if __name__ == "__main__":
    print("Оптимизированные решения заданий")
    print("=" * 60)
    print("\nДля запуска конкретного решения вызовите соответствующую функцию")
    print("Например: ответ_1_неэффективный_поиск()")
