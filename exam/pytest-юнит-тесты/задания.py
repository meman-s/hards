"""
Задания по Pytest: fixtures, parametrize, markers и Юнит тесты
Каждая функция содержит код, для которого нужно написать тесты
"""


class Calculator:
    """
    Задание 1: Написать юнит-тесты для класса Calculator

    Напишите тесты для всех методов класса Calculator:
    - test_add - тест сложения
    - test_subtract - тест вычитания
    - test_multiply - тест умножения
    - test_divide - тест деления (включая деление на ноль)
    - test_power - тест возведения в степень
    """

    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a, b):
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result

    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Деление на ноль невозможно")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result

    def power(self, base, exponent):
        result = base ** exponent
        self.history.append(f"{base} ^ {exponent} = {result}")
        return result

    def get_history(self):
        return self.history

    def clear_history(self):
        self.history = []


class UserValidator:
    """
    Задание 2: Написать тесты с использованием @pytest.mark.parametrize

    Напишите параметризованные тесты для метода validate_email:
    - test_valid_emails - тесты для валидных email адресов
    - test_invalid_emails - тесты для невалидных email адресов

    Используйте @pytest.mark.parametrize для проверки множества случаев
    """
    @staticmethod
    def validate_email(email):
        if not email or "@" not in email:
            return False
        parts = email.split("@")
        if len(parts) != 2:
            return False
        local, domain = parts
        if not local or not domain:
            return False
        if "." not in domain:
            return False
        return True

    @staticmethod
    def validate_password(password):
        if len(password) < 8:
            return False, "Пароль должен содержать минимум 8 символов"
        if not any(c.isupper() for c in password):
            return False, "Пароль должен содержать хотя бы одну заглавную букву"
        if not any(c.islower() for c in password):
            return False, "Пароль должен содержать хотя бы одну строчную букву"
        if not any(c.isdigit() for c in password):
            return False, "Пароль должен содержать хотя бы одну цифру"
        return True, "Пароль валиден"


class DatabaseConnection:
    """
    Задание 3: Написать тесты с использованием fixtures

    Напишите тесты для класса DatabaseConnection, используя fixtures:
    - Создайте fixture для подключения к базе данных
    - Создайте fixture для тестовых данных
    - Напишите тесты для методов insert, select, delete

    Используйте scope="function" для изоляции тестов
    """

    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.connected = False
        self.data = {}

    def connect(self):
        if not self.connection_string:
            raise ValueError("Connection string не может быть пустым")
        self.connected = True
        return True

    def disconnect(self):
        self.connected = False

    def insert(self, table, record):
        if not self.connected:
            raise RuntimeError("Нет подключения к базе данных")
        if table not in self.data:
            self.data[table] = []
        self.data[table].append(record)
        return len(self.data[table]) - 1

    def select(self, table, condition=None):
        if not self.connected:
            raise RuntimeError("Нет подключения к базе данных")
        if table not in self.data:
            return []
        if condition is None:
            return self.data[table]
        return [r for r in self.data[table] if condition(r)]

    def delete(self, table, condition):
        if not self.connected:
            raise RuntimeError("Нет подключения к базе данных")
        if table not in self.data:
            return 0
        initial_count = len(self.data[table])
        self.data[table] = [r for r in self.data[table] if not condition(r)]
        return initial_count - len(self.data[table])


class CacheService:
    """
    Задание 4: Написать тесты с использованием markers

    Напишите тесты для класса CacheService:
    - test_fast_operations - пометьте маркером @pytest.mark.fast
    - test_slow_operations - пометьте маркером @pytest.mark.slow
    - test_integration - пометьте маркером @pytest.mark.integration

    Создайте pytest.ini или conftest.py для регистрации маркеров
    """

    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, key):
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def set(self, key, value):
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = value

    def clear(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self):
        total = self.hits + self.misses
        if total == 0:
            return {"hits": 0, "misses": 0, "hit_rate": 0.0}
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / total
        }


def fibonacci(n):
    """
    Задание 5: Комбинированное задание - fixtures + parametrize

    Напишите тесты для функции fibonacci:
    - Используйте fixture для подготовки тестовых данных
    - Используйте @pytest.mark.parametrize для проверки различных значений n
    - Проверьте граничные случаи (n=0, n=1, n=2)
    - Проверьте большие значения (n=10, n=20)
    """
    if n < 0:
        raise ValueError("n должно быть неотрицательным")
    if n == 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


class FileProcessor:
    """
    Задание 6: Тесты с временными файлами (fixtures с yield)

    Напишите тесты для класса FileProcessor:
    - Создайте fixture, который создает временный файл с тестовыми данными
    - Используйте yield для очистки после теста
    - Напишите тесты для методов read_file, write_file, process_file
    """

    def __init__(self, encoding="utf-8"):
        self.encoding = encoding

    def read_file(self, filepath):
        with open(filepath, "r", encoding=self.encoding) as f:
            return f.read()

    def write_file(self, filepath, content):
        with open(filepath, "w", encoding=self.encoding) as f:
            f.write(content)

    def process_file(self, input_path, output_path):
        content = self.read_file(input_path)
        processed = content.upper().replace(" ", "_")
        self.write_file(output_path, processed)
        return processed
