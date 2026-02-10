"""
Пример решения для задания 1: Pytest Fixtures
Это пример того, как можно решить первое задание.
Используйте это как образец для остальных заданий.
"""

import pytest
from practice_code import BankAccount, UserRepository


# ========== ЗАДАНИЕ 1: Pytest Fixtures ==========

@pytest.fixture
def bank_account():
    """Фикстура для BankAccount с начальным балансом 100.0"""
    return BankAccount(initial_balance=100.0)


@pytest.fixture(scope="module")
def user_repo():
    """Фикстура scope="module" для UserRepository"""
    return UserRepository()


@pytest.fixture(autouse=True)
def setup_test():
    """Фикстура с autouse=True, которая выводит сообщение"""
    print("\n>>> Starting test")
    yield
    print(">>> Test finished\n")


# Пример использования фикстур
def test_bank_account_deposit_example(bank_account):
    """Пример теста с использованием фикстуры"""
    bank_account.deposit(50.0)
    assert bank_account.balance == 150.0


def test_user_repo_example(user_repo):
    """Пример теста с фикстурой scope="module" """
    user = user_repo.create("test_user", "test@example.com", 25)
    assert user["username"] == "test_user"
    # user_repo сохраняет данные между тестами благодаря scope="module"
