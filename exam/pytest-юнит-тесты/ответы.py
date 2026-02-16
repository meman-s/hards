"""
Ответы: Тесты для заданий по Pytest
Каждая функция содержит примеры тестов с использованием fixtures, parametrize, markers
"""

import pytest
import tempfile
import os
from задания import (
    Calculator,
    UserValidator,
    DatabaseConnection,
    CacheService,
    fibonacci,
    FileProcessor,
)


class TestCalculator:
    """
    Ответ 1: Юнит-тесты для класса Calculator
    """

    def test_add(self):
        calc = Calculator()
        assert calc.add(2, 3) == 5
        assert calc.add(-1, 1) == 0
        assert calc.add(0, 0) == 0

    def test_subtract(self):
        calc = Calculator()
        assert calc.subtract(5, 3) == 2
        assert calc.subtract(0, 5) == -5
        assert calc.subtract(10, 10) == 0

    def test_multiply(self):
        calc = Calculator()
        assert calc.multiply(3, 4) == 12
        assert calc.multiply(-2, 5) == -10
        assert calc.multiply(0, 100) == 0

    def test_divide(self):
        calc = Calculator()
        assert calc.divide(10, 2) == 5
        assert calc.divide(7, 2) == 3.5
        assert calc.divide(-10, 2) == -5

    def test_divide_by_zero(self):
        calc = Calculator()
        with pytest.raises(ValueError, match="Деление на ноль невозможно"):
            calc.divide(10, 0)

    def test_power(self):
        calc = Calculator()
        assert calc.power(2, 3) == 8
        assert calc.power(5, 0) == 1
        assert calc.power(3, 2) == 9

    def test_history(self):
        calc = Calculator()
        calc.add(1, 2)
        calc.multiply(3, 4)
        history = calc.get_history()
        assert len(history) == 2
        assert "1 + 2 = 3" in history
        assert "3 * 4 = 12" in history

    def test_clear_history(self):
        calc = Calculator()
        calc.add(1, 2)
        calc.clear_history()
        assert len(calc.get_history()) == 0


class TestUserValidator:
    """
    Ответ 2: Тесты с использованием @pytest.mark.parametrize
    """
    @pytest.mark.parametrize("email", [
        "user@example.com",
        "test.email@domain.co.uk",
        "user+tag@example.com",
        "user123@test-domain.com",
        "a@b.co",
    ])
    def test_valid_emails(self, email):
        assert UserValidator.validate_email(email) is True

    @pytest.mark.parametrize("email", [
        "",
        "invalid",
        "@example.com",
        "user@",
        "user@domain",
        "user..name@example.com",
        "user@domain..com",
        None,
    ])
    def test_invalid_emails(self, email):
        if email is None:
            with pytest.raises(AttributeError):
                UserValidator.validate_email(email)
        else:
            assert UserValidator.validate_email(email) is False

    @pytest.mark.parametrize("password,expected_valid,expected_message", [
        ("ValidPass123", True, "Пароль валиден"),
        ("short", False, "Пароль должен содержать минимум 8 символов"),
        ("nouppercase123", False, "Пароль должен содержать хотя бы одну заглавную букву"),
        ("NOLOWERCASE123", False, "Пароль должен содержать хотя бы одну строчную букву"),
        ("NoDigitsHere", False, "Пароль должен содержать хотя бы одну цифру"),
    ])
    def test_validate_password(self, password, expected_valid, expected_message):
        is_valid, message = UserValidator.validate_password(password)
        assert is_valid == expected_valid
        assert expected_message in message


class TestDatabaseConnection:
    """
    Ответ 3: Тесты с использованием fixtures
    """
    @pytest.fixture
    def db_connection(self):
        db = DatabaseConnection("test://localhost/testdb")
        db.connect()
        yield db
        db.disconnect()

    @pytest.fixture
    def sample_data(self):
        return [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "age": 25},
            {"id": 3, "name": "Charlie", "age": 35},
        ]

    def test_connect(self):
        db = DatabaseConnection("test://localhost/testdb")
        assert db.connect() is True
        assert db.connected is True

    def test_connect_empty_string(self):
        db = DatabaseConnection("")
        with pytest.raises(ValueError, match="Connection string не может быть пустым"):
            db.connect()

    def test_insert(self, db_connection):
        record_id = db_connection.insert("users", {"name": "Test", "age": 20})
        assert record_id == 0
        assert len(db_connection.data["users"]) == 1

    def test_select_all(self, db_connection, sample_data):
        for record in sample_data:
            db_connection.insert("users", record)
        results = db_connection.select("users")
        assert len(results) == 3

    def test_select_with_condition(self, db_connection, sample_data):
        for record in sample_data:
            db_connection.insert("users", record)
        results = db_connection.select("users", lambda r: r["age"] > 30)
        assert len(results) == 1
        assert results[0]["name"] == "Charlie"

    def test_delete(self, db_connection, sample_data):
        for record in sample_data:
            db_connection.insert("users", record)
        deleted_count = db_connection.delete("users", lambda r: r["age"] < 30)
        assert deleted_count == 2
        assert len(db_connection.data["users"]) == 1

    def test_operations_without_connection(self):
        db = DatabaseConnection("test://localhost/testdb")
        with pytest.raises(RuntimeError, match="Нет подключения к базе данных"):
            db.insert("users", {"name": "Test"})


class TestCacheService:
    """
    Ответ 4: Тесты с использованием markers
    """
    @pytest.fixture
    def cache(self):
        return CacheService(max_size=10)

    @pytest.mark.fast
    def test_get_set(self, cache):
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        assert cache.get("nonexistent") is None

    @pytest.mark.fast
    def test_clear(self, cache):
        cache.set("key1", "value1")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get_stats()["hits"] == 0

    @pytest.mark.fast
    def test_stats(self, cache):
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("key1")
        cache.get("key2")
        stats = cache.get_stats()
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == pytest.approx(2/3, rel=1e-2)

    @pytest.mark.slow
    def test_max_size(self, cache):
        for i in range(15):
            cache.set(f"key{i}", f"value{i}")
        assert len(cache.cache) == 10

    @pytest.mark.integration
    def test_cache_workflow(self, cache):
        cache.set("user:1", {"name": "Alice"})
        cache.set("user:2", {"name": "Bob"})
        assert cache.get("user:1")["name"] == "Alice"
        cache.clear()
        assert cache.get("user:1") is None


class TestFibonacci:
    """
    Ответ 5: Комбинированное задание - fixtures + parametrize
    """
    @pytest.fixture
    def expected_results(self):
        return {
            0: 0,
            1: 1,
            2: 1,
            3: 2,
            4: 3,
            5: 5,
            6: 8,
            7: 13,
            8: 21,
            9: 34,
            10: 55,
        }

    @pytest.mark.parametrize("n,expected", [
        (0, 0),
        (1, 1),
        (2, 1),
        (3, 2),
        (4, 3),
        (5, 5),
        (10, 55),
        (20, 6765),
    ])
    def test_fibonacci(self, n, expected):
        assert fibonacci(n) == expected

    def test_fibonacci_negative(self):
        with pytest.raises(ValueError, match="n должно быть неотрицательным"):
            fibonacci(-1)

    def test_fibonacci_with_fixture(self, expected_results):
        for n, expected in expected_results.items():
            assert fibonacci(n) == expected


class TestFileProcessor:
    """
    Ответ 6: Тесты с временными файлами (fixtures с yield)
    """
    @pytest.fixture
    def temp_file(self):
        fd, path = tempfile.mkstemp(suffix=".txt", text=True)
        os.close(fd)
        with open(path, "w", encoding="utf-8") as f:
            f.write("Hello World\nTest Content")
        yield path
        if os.path.exists(path):
            os.remove(path)

    @pytest.fixture
    def temp_output_file(self):
        fd, path = tempfile.mkstemp(suffix=".txt", text=True)
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.remove(path)

    def test_read_file(self, temp_file):
        processor = FileProcessor()
        content = processor.read_file(temp_file)
        assert "Hello World" in content
        assert "Test Content" in content

    def test_write_file(self, temp_output_file):
        processor = FileProcessor()
        test_content = "Written Content\nLine 2"
        processor.write_file(temp_output_file, test_content)
        with open(temp_output_file, "r", encoding="utf-8") as f:
            assert f.read() == test_content

    def test_process_file(self, temp_file, temp_output_file):
        processor = FileProcessor()
        result = processor.process_file(temp_file, temp_output_file)
        assert "HELLO_WORLD" in result
        assert "TEST_CONTENT" in result
        with open(temp_output_file, "r", encoding="utf-8") as f:
            assert "HELLO_WORLD" in f.read()
