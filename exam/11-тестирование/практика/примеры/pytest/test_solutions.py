"""
    Задание 1: Написать юнит-тесты для класса Calculator

    Напишите тесты для всех методов класса Calculator:
    - test_add - тест сложения
    - test_subtract - тест вычитания
    - test_multiply - тест умножения
    - test_divide - тест деления (включая деление на ноль)
    - test_power - тест возведения в степень
    """
import pytest
from задания import Calculator, UserValidator


@pytest.fixture(scope="function")
def calculator() -> Calculator:
    return Calculator()


def test_add(calculator: Calculator):
    result = calculator.add(5, 4)
    assert result == 9
    assert "5 + 4 = 9" in calculator.history


def test_subtract(calculator: Calculator):
    result = calculator.subtract(5, 4)
    assert result == 1
    assert "5 - 4 = 1" in calculator.history


"""
Задание 2: Написать тесты с использованием @pytest.mark.parametrize

Напишите параметризованные тесты для метода validate_email:
- test_valid_emails - тесты для валидных email адресов
- test_invalid_emails - тесты для невалидных email адресов

Используйте @pytest.mark.parametrize для проверки множества случаев
"""


@pytest.mark.parametrize("email, result", [
    ('stepan.kalimullin@gmail.com', True),
    ('fsd', False),
    ('sdf@sdfs@dfs', False),
    ('fsdf@fsdf', False)
])
def test_valid_emails(email, result):
    uv = UserValidator()
    assert uv.validate_email(email) == result
