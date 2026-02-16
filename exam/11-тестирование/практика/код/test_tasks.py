"""
Задания для практики тестирования
"""


class Calculator:
    """Простой калькулятор для тестирования"""
    
    def add(self, a: float, b: float) -> float:
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Division by zero")
        return a / b
    
    def power(self, base: float, exponent: float) -> float:
        return base ** exponent


class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(self, db):
        self.db = db
    
    def create_user(self, name: str, email: str) -> dict:
        if not name or not email:
            raise ValueError("Name and email are required")
        if "@" not in email:
            raise ValueError("Invalid email format")
        
        user = {
            "id": len(self.db) + 1,
            "name": name,
            "email": email
        }
        self.db.append(user)
        return user
    
    def get_user(self, user_id: int) -> dict:
        for user in self.db:
            if user["id"] == user_id:
                return user
        raise ValueError(f"User with id {user_id} not found")
    
    def delete_user(self, user_id: int) -> bool:
        for i, user in enumerate(self.db):
            if user["id"] == user_id:
                self.db.pop(i)
                return True
        return False


class EmailValidator:
    """Валидатор email адресов"""
    
    def validate(self, email: str) -> bool:
        if not email:
            return False
        if "@" not in email:
            return False
        parts = email.split("@")
        if len(parts) != 2:
            return False
        if not parts[0] or not parts[1]:
            return False
        if "." not in parts[1]:
            return False
        return True


class Cache:
    """Простой кэш"""
    
    def __init__(self):
        self._cache = {}
    
    def set(self, key: str, value: any, ttl: int = None) -> None:
        self._cache[key] = {
            "value": value,
            "ttl": ttl
        }
    
    def get(self, key: str) -> any:
        if key not in self._cache:
            return None
        return self._cache[key]["value"]
    
    def delete(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        self._cache.clear()


class APIClient:
    """Клиент для работы с API"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
    
    def get(self, endpoint: str) -> dict:
        import requests
        response = requests.get(
            f"{self.base_url}/{endpoint}",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: dict) -> dict:
        import requests
        response = requests.post(
            f"{self.base_url}/{endpoint}",
            json=data,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()


def process_data(data: list, filter_func=None, transform_func=None) -> list:
    """Обработка данных с фильтрацией и трансформацией"""
    result = data
    
    if filter_func:
        result = [item for item in result if filter_func(item)]
    
    if transform_func:
        result = [transform_func(item) for item in result]
    
    return result


def calculate_statistics(numbers: list) -> dict:
    """Вычисление статистики для списка чисел"""
    if not numbers:
        return {
            "count": 0,
            "sum": 0,
            "average": 0,
            "min": None,
            "max": None
        }
    
    return {
        "count": len(numbers),
        "sum": sum(numbers),
        "average": sum(numbers) / len(numbers),
        "min": min(numbers),
        "max": max(numbers)
    }
