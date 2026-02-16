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

        def add_user(self, name, email):
            self.users.append({"name": name, "email": email})

        def find_user_by_email(self, email):
            for user in self.users:
                if user["email"] == email:
                    return user
            return None

        def get_user_statistics(self):
            stats = {}
            for user in self.users:
                domain = user["email"].split("@")[1]
                if domain not in stats:
                    stats[domain] = 0
                stats[domain] += 1
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
            result = []
            for order in orders:
                customer = self.db.query(
                    f"SELECT name, email FROM customers WHERE id = {order['customer_id']}"
                )[0]
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
        words = []
        current_word = ""

        for char in text:
            if char.isalnum():
                current_word += char
            else:
                if current_word:
                    words.append(current_word)
                    current_word = ""

        if current_word:
            words.append(current_word)

        stats = {}
        for word in words:
            word_lower = word.lower()
            if word_lower not in stats:
                stats[word_lower] = 0
            stats[word_lower] += 1

        return stats

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


def задание_5_проблемы_с_памятью():
    """
    Задание 5: Проблемы с памятью при обработке больших файлов

    Проблема: readlines() загружает весь файл в память сразу.
    При больших файлах это может привести к нехватке памяти.

    Задача: Оптимизируйте код для построчной обработки файла.
    """
    def process_large_file(filename):
        with open(filename, 'r') as f:
            lines = f.readlines()

        processed = []
        for line in lines:
            processed.append(line.strip().upper())

        return processed

    with open('large_file.txt', 'w') as f:
        for i in range(1000000):
            f.write(f"Line {i} with some data\n")

    result = process_large_file('large_file.txt')
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
            expensive = []
            for product in self.products:
                if product["price"] >= min_price:
                    expensive.append(product)

            n = len(expensive)
            for i in range(n):
                for j in range(0, n - i - 1):
                    if expensive[j]["price"] < expensive[j + 1]["price"]:
                        expensive[j], expensive[j + 1] = expensive[j + 1], expensive[j]

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
        result = []
        for item in items:
            result.insert(0, item)
        return result

    def get_last_n_items(items, n):
        result = []
        for i in range(len(items) - n, len(items)):
            result.append(items[i])
        return result

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
        result = []
        for item in items:
            if filter_enabled:
                if item > 0:
                    if transform_enabled:
                        result.append(item * 2)
                    else:
                        result.append(item)
            else:
                if transform_enabled:
                    result.append(item * 2)
                else:
                    result.append(item)
        return result

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
    def count_items(items):
        stats = {}
        for item in items:
            if item not in stats:
                stats[item] = 0
            stats[item] = stats[item] + 1
        return stats

    def merge_dicts(dict1, dict2):
        result = {}
        for key in dict1:
            if key not in result:
                result[key] = 0
            result[key] = dict1[key]
        for key in dict2:
            if key not in result:
                result[key] = 0
            result[key] = result[key] + dict2[key]
        return result

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
        squared = [x ** 2 for x in data]
        filtered = [x for x in squared if x > 100]
        sorted_data = sorted(filtered)
        return sorted_data

    def get_statistics(data):
        total = sum(data)
        count = len(data)
        average = total / count if count > 0 else 0

        max_val = max(data)
        min_val = min(data)

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
    print("Запуск заданий по профилированию и оптимизации кода")
    print("=" * 60)
    print("\nДля запуска конкретного задания вызовите соответствующую функцию")
    print("Например: задание_1_неэффективный_поиск()")
