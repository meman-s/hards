"""
Файл для написания тестов
Напишите здесь свои тесты для классов и функций из practice_code.py

Запуск из папки testing: pytest unit/test_practice.py -v
Инструкции: docs/PRACTICE_ASSIGNMENTS.md
"""

import pytest
from unittest.mock import MagicMock, Mock
from practice_code import (
    BankAccount,
    StringProcessor,
    ShoppingCart,
    UserRepository,
    EmailService,
    Calculator,
    validate_password,
    process_numbers
)
from playwright.sync_api import Page, expect


# ========== ЗАДАНИЕ 1: Pytest Fixtures ==========
@pytest.fixture()
def bank_account():
    return BankAccount(initial_balance=100.0)


@pytest.fixture(scope="module")
def user_repo():
    return UserRepository()


@pytest.fixture(autouse=True)
def setup_test():
    print("\nStarting test")
    yield
    print("Test ended\n")


def test_bank_account_deposit(bank_account):
    bank_account.deposit(100.0)
    assert bank_account.balance == 200.0


def test_bank_account_withdraw_insufficient_funds(bank_account):
    with pytest.raises(ValueError, match="Insufficient funds"):
        bank_account.withdraw(333.3)


def test_bank_account_transfer(bank_account):
    acc1 = bank_account
    acc2 = BankAccount(initial_balance=100.0)

    acc1.transfer(acc2, 50)

    assert acc1.balance == 50
    assert acc2.balance == 150


@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0)
])
def test_calculator_add_parametrize(a, b, expected):
    assert Calculator.add(a, b) == expected


def test_string_processor_count_words():
    assert StringProcessor.reverse("test") == "tset"


def test_string_processor_type_error():
    with pytest.raises(TypeError, match="Input must be a string"):
        StringProcessor.reverse(1)


def test_email_service_send_email_with_mock():
    mock_smtp = Mock()
    service = EmailService(smtp_client=mock_smtp)

    result = service.send_email("test@gmail.com", "subject", "Body")

    assert result is True
    mock_smtp.send.assert_called_once_with("test@gmail.com", "subject", "Body")
    assert len(service.get_sent_emails()) == 1


@pytest.fixture
def mock_db():
    return []


# ========== ЗАДАНИЕ 6–11: TODO в docs/PRACTICE_ASSIGNMENTS.md ==========


def test_homepage(page: Page):
    page.goto("https://example.com")

    expect(page).to_have_title("Example Domain")


def test_title(page: Page):
    page.goto("https://example.com")
    page.screenshot(path="screenshot.png")
    heading = page.get_by_role("heading", name="Example Domain")

    expect(heading).to_be_visible()


@pytest.mark.parametrize('a,b,expected', [
    (1, 2, 3),
    (2, 3, 5)
])
def test_calc(a, b, expected):
    assert Calculator.add(a, b) == expected
