"""
Файл для написания тестов
Напишите здесь свои тесты для классов и функций из practice_code.py

📖 ИНСТРУКЦИЯ:
1. Откройте PRACTICE_ASSIGNMENTS.md для подробных инструкций
2. Найдите задание по номеру (ЗАДАНИЕ 1, ЗАДАНИЕ 2, и т.д.)
3. Замените TODO комментарии на реальные тесты
4. Запустите: pytest test_practice.py -v

💡 ПРИМЕР:
   Смотрите test_practice_example.py для примера решения задания 1

🚀 ЗАПУСК ТЕСТОВ:
   pytest test_practice.py -v                    # все тесты
   pytest test_practice.py::test_name -v        # конкретный тест
   pytest test_practice.py -m "not slow" -v     # только быстрые
   pytest test_practice.py -k "bank" -v         # тесты с "bank" в имени
"""

import pytest
from unittest.mock import Mock
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


@pytest.mark.parametrize("a,b,expected", {
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0)
})
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

    # ========== ЗАДАНИЕ 6: Интеграционные тесты для UserRepository ==========
    # TODO: Напишите тест create_user - создание пользователя
    # TODO: Напишите тест find_by_id - поиск по ID
    # TODO: Напишите тест find_by_email - поиск по email
    # TODO: Напишите тест update - обновление пользователя
    # TODO: Напишите тест delete - удаление пользователя
    # TODO: Напишите тест для проверки, что изменения сохраняются между вызовами методов
    # ========== ЗАДАНИЕ 7: Тесты для ShoppingCart ==========
    # TODO: Напишите тест add_item - добавление товара
    # TODO: Напишите тест get_total - расчет общей стоимости
    # TODO: Напишите тест apply_discount - применение скидки
    # TODO: Напишите тест remove_item - удаление товара
    # TODO: Напишите тест clear - очистка корзины
    # ========== ЗАДАНИЕ 8: Тесты для validate_password ==========
    # TODO: Напишите тест для валидного пароля
    # TODO: Напишите тест для слишком короткого пароля
    # TODO: Напишите тест для пароля без заглавных букв
    # TODO: Напишите тест для пароля без строчных букв
    # TODO: Напишите тест для пароля без цифр
    # ========== ЗАДАНИЕ 9: Тесты для process_numbers ==========
    # TODO: Напишите тест для пустого списка
    # TODO: Напишите тест для списка с числами - проверка всех полей результата
    # TODO: Напишите тест для проверки even_count и odd_count
    # ========== ЗАДАНИЕ 10: Маркеры ==========
    # TODO: Пометить медленные тесты маркером @pytest.mark.slow
    # TODO: Пометить интеграционные тесты маркером @pytest.mark.integration
    # TODO: Запустить только быстрые тесты: pytest -m "not slow"


def test_homepage(page: Page):
    page.goto("https://example.com")

    expect(page).to_have_title("Examplt Domain")


def test_title(page: Page):
    page.goto("https://example.com")
    page.screenshot(path="screenshot.png")
    heading = page.get_by_role("heading", name="Example Domain")

    expect(heading).to_be_visible()


# ========== ЗАДАНИЕ 11: E2E тесты с Playwright ==========
# TODO: Напишите тест для открытия формы test_form.html
# TODO: Напишите тест для проверки заголовка страницы "Тестовая форма для E2E тестов"
# TODO: Напишите тест для заполнения всех полей формы и отправки
# TODO: Напишите тест для проверки сообщения об успехе после отправки
# TODO: Напишите тест для проверки валидации (например, короткое имя пользователя)
# TODO: Напишите тест для выбора страны из выпадающего списка
# TODO: Напишите тест для проверки чекбокса согласия

# Подсказка: используйте page.goto("file:///путь/к/test_form.html")
# Подсказка: используйте page.get_by_test_id("username-input") для поиска элементов
