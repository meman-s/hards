"""
Код для практики написания тестов
Используйте этот файл для написания тестов в test_practice.py
"""


class BankAccount:
    """Банковский счет для тестирования"""

    def __init__(self, initial_balance: float = 0.0):
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")
        self._balance = initial_balance
        self._transaction_history = []

    @property
    def balance(self) -> float:
        return self._balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount
        self._transaction_history.append(("deposit", amount))

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
        self._transaction_history.append(("withdraw", amount))

    def get_transaction_history(self) -> list:
        return self._transaction_history.copy()

    def transfer(self, other_account: 'BankAccount', amount: float) -> None:
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        if amount > self._balance:
            raise ValueError("Insufficient funds for transfer")
        self.withdraw(amount)
        other_account.deposit(amount)


class StringProcessor:
    """Обработчик строк для тестирования"""

    @staticmethod
    def reverse(text: str) -> str:
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        return text[::-1]

    @staticmethod
    def capitalize_words(text: str) -> str:
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        return " ".join(word.capitalize() for word in text.split())

    @staticmethod
    def remove_whitespace(text: str) -> str:
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        return "".join(text.split())

    @staticmethod
    def is_palindrome(text: str) -> bool:
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        cleaned = text.lower().replace(" ", "")
        return cleaned == cleaned[::-1]

    @staticmethod
    def count_words(text: str) -> int:
        if not isinstance(text, str):
            raise TypeError("Input must be a string")
        if not text.strip():
            return 0
        return len(text.split())


class ShoppingCart:
    """Корзина покупок для тестирования"""

    def __init__(self):
        self._items = {}
        self._discount = 0.0

    def add_item(self, item_id: str, name: str, price: float, quantity: int = 1) -> None:
        if price < 0:
            raise ValueError("Price cannot be negative")
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        if item_id in self._items:
            self._items[item_id]["quantity"] += quantity
        else:
            self._items[item_id] = {
                "name": name,
                "price": price,
                "quantity": quantity
            }

    def remove_item(self, item_id: str, quantity: int = None) -> None:
        if item_id not in self._items:
            raise ValueError(f"Item {item_id} not in cart")

        if quantity is None:
            del self._items[item_id]
        else:
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            if quantity >= self._items[item_id]["quantity"]:
                del self._items[item_id]
            else:
                self._items[item_id]["quantity"] -= quantity

    def get_total(self) -> float:
        total = sum(item["price"] * item["quantity"] for item in self._items.values())
        return total * (1 - self._discount)

    def apply_discount(self, discount_percent: float) -> None:
        if discount_percent < 0 or discount_percent > 100:
            raise ValueError("Discount must be between 0 and 100")
        self._discount = discount_percent / 100

    def get_items(self) -> dict:
        return self._items.copy()

    def clear(self) -> None:
        self._items.clear()
        self._discount = 0.0


class UserRepository:
    """Репозиторий пользователей для интеграционного тестирования"""

    def __init__(self, db: list = None):
        self._db = db if db is not None else []
        self._next_id = 1

    def create(self, username: str, email: str, age: int) -> dict:
        if not username or not email:
            raise ValueError("Username and email are required")
        if "@" not in email:
            raise ValueError("Invalid email format")
        if age < 0:
            raise ValueError("Age cannot be negative")

        user = {
            "id": self._next_id,
            "username": username,
            "email": email,
            "age": age
        }
        self._db.append(user)
        self._next_id += 1
        return user

    def find_by_id(self, user_id: int) -> dict:
        for user in self._db:
            if user["id"] == user_id:
                return user
        raise ValueError(f"User with id {user_id} not found")

    def find_by_email(self, email: str) -> dict:
        for user in self._db:
            if user["email"] == email:
                return user
        raise ValueError(f"User with email {email} not found")

    def update(self, user_id: int, **kwargs) -> dict:
        user = self.find_by_id(user_id)
        for key, value in kwargs.items():
            if key in ["username", "email", "age"]:
                if key == "email" and "@" not in value:
                    raise ValueError("Invalid email format")
                if key == "age" and value < 0:
                    raise ValueError("Age cannot be negative")
                user[key] = value
        return user

    def delete(self, user_id: int) -> bool:
        for i, user in enumerate(self._db):
            if user["id"] == user_id:
                self._db.pop(i)
                return True
        return False

    def get_all(self) -> list:
        return self._db.copy()


class EmailService:
    """Сервис отправки email для тестирования с моками"""

    def __init__(self, smtp_client=None):
        self.smtp_client = smtp_client
        self.sent_emails = []

    def send_email(self, to: str, subject: str, body: str) -> bool:
        if not to or "@" not in to:
            raise ValueError("Invalid email address")
        if not subject:
            raise ValueError("Subject is required")

        if self.smtp_client:
            self.smtp_client.send(to, subject, body)

        self.sent_emails.append({
            "to": to,
            "subject": subject,
            "body": body
        })
        return True

    def send_welcome_email(self, user_email: str, username: str) -> bool:
        subject = f"Welcome, {username}!"
        body = f"Hello {username}, welcome to our service!"
        return self.send_email(user_email, subject, body)

    def get_sent_emails(self) -> list:
        return self.sent_emails.copy()


class Calculator:
    """Калькулятор для параметризованных тестов"""

    @staticmethod
    def add(a: float, b: float) -> float:
        return a + b

    @staticmethod
    def subtract(a: float, b: float) -> float:
        return a - b

    @staticmethod
    def multiply(a: float, b: float) -> float:
        return a * b

    @staticmethod
    def divide(a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        return a / b

    @staticmethod
    def power(base: float, exponent: float) -> float:
        return base ** exponent

    @staticmethod
    def sqrt(value: float) -> float:
        if value < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return value ** 0.5


def validate_password(password: str) -> tuple[bool, str]:
    """
    Валидация пароля.
    Возвращает (is_valid, error_message)
    """
    if not password:
        return False, "Password cannot be empty"

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"

    return True, ""


def process_numbers(numbers: list) -> dict:
    """
    Обработка списка чисел.
    Возвращает статистику.
    """
    if not numbers:
        return {
            "count": 0,
            "sum": 0,
            "average": 0,
            "min": None,
            "max": None,
            "even_count": 0,
            "odd_count": 0
        }

    even_count = sum(1 for n in numbers if n % 2 == 0)
    odd_count = len(numbers) - even_count

    return {
        "count": len(numbers),
        "sum": sum(numbers),
        "average": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "even_count": even_count,
        "odd_count": odd_count
    }
