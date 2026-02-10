"""
Примеры решений для всех заданий
Используйте это как образец для написания своих тестов
"""

import pytest
from unittest.mock import Mock
from playwright.sync_api import Page, expect
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


def test_bank_account_deposit_example(bank_account):
    """Пример теста с использованием фикстуры"""
    bank_account.deposit(50.0)
    assert bank_account.balance == 150.0


def test_user_repo_example(user_repo):
    """Пример теста с фикстурой scope="module" """
    user = user_repo.create("test_user", "test@example.com", 25)
    assert user["username"] == "test_user"


# ========== ЗАДАНИЕ 2: Юнит тесты для BankAccount ==========

def test_bank_account_withdraw(bank_account):
    """Тест для withdraw - проверка уменьшения баланса"""
    bank_account.withdraw(30.0)
    assert bank_account.balance == 70.0


def test_bank_account_withdraw_insufficient_funds(bank_account):
    """Тест для withdraw с недостаточным балансом"""
    with pytest.raises(ValueError, match="Insufficient funds"):
        bank_account.withdraw(200.0)


def test_bank_account_transfer():
    """Тест для transfer между двумя счетами"""
    account1 = BankAccount(initial_balance=100.0)
    account2 = BankAccount(initial_balance=50.0)

    account1.transfer(account2, 30.0)

    assert account1.balance == 70.0
    assert account2.balance == 80.0


def test_bank_account_transaction_history():
    """Тест для transaction_history - проверка истории операций"""
    account = BankAccount(initial_balance=100.0)
    account.deposit(50.0)
    account.withdraw(30.0)

    history = account.get_transaction_history()
    assert len(history) == 2
    assert history[0] == ("deposit", 50.0)
    assert history[1] == ("withdraw", 30.0)


# ========== ЗАДАНИЕ 3: Параметризованные тесты для Calculator ==========

@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (10.5, 2.5, 13.0),
])
def test_calculator_add_parametrize(a, b, expected):
    """Параметризованный тест для Calculator.add"""
    assert Calculator.add(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 6),
    (0, 5, 0),
    (-2, 4, -8),
    (2.5, 2, 5.0),
])
def test_calculator_multiply_parametrize(a, b, expected):
    """Параметризованный тест для Calculator.multiply"""
    assert Calculator.multiply(a, b) == expected


@pytest.mark.parametrize("a,b,expected", [
    (10, 2, 5.0),
    (15, 3, 5.0),
    (7, 2, 3.5),
])
def test_calculator_divide_parametrize(a, b, expected):
    """Параметризованный тест для Calculator.divide"""
    assert Calculator.divide(a, b) == expected


def test_calculator_divide_by_zero():
    """Тест для деления на ноль"""
    with pytest.raises(ZeroDivisionError, match="Division by zero"):
        Calculator.divide(10, 0)


# ========== ЗАДАНИЕ 4: Юнит тесты для StringProcessor ==========

def test_string_processor_reverse():
    """Тест для reverse - проверка переворота строки"""
    assert StringProcessor.reverse("hello") == "olleh"
    assert StringProcessor.reverse("Python") == "nohtyP"


def test_string_processor_capitalize_words():
    """Тест для capitalize_words"""
    assert StringProcessor.capitalize_words("hello world") == "Hello World"
    assert StringProcessor.capitalize_words("python programming") == "Python Programming"


def test_string_processor_is_palindrome():
    """Тест для is_palindrome - проверка палиндромов"""
    assert StringProcessor.is_palindrome("racecar") is True
    assert StringProcessor.is_palindrome("A man a plan") is False
    assert StringProcessor.is_palindrome("level") is True
    assert StringProcessor.is_palindrome("hello") is False


def test_string_processor_count_words():
    """Тест для count_words"""
    assert StringProcessor.count_words("hello world") == 2
    assert StringProcessor.count_words("one two three four") == 4
    assert StringProcessor.count_words("") == 0


def test_string_processor_type_error():
    """Тест для проверки TypeError при передаче не-строки"""
    with pytest.raises(TypeError, match="Input must be a string"):
        StringProcessor.reverse(123)

    with pytest.raises(TypeError, match="Input must be a string"):
        StringProcessor.capitalize_words(None)


# ========== ЗАДАНИЕ 5: Тесты с моками для EmailService ==========

def test_email_service_send_email_with_mock():
    """Тест send_email с проверкой вызова smtp_client.send"""
    mock_smtp = Mock()
    service = EmailService(smtp_client=mock_smtp)

    result = service.send_email("test@example.com", "Subject", "Body")

    assert result is True
    mock_smtp.send.assert_called_once_with("test@example.com", "Subject", "Body")
    assert len(service.get_sent_emails()) == 1


def test_email_service_send_welcome_email():
    """Тест send_welcome_email"""
    mock_smtp = Mock()
    service = EmailService(smtp_client=mock_smtp)

    result = service.send_welcome_email("user@example.com", "John")

    assert result is True
    mock_smtp.send.assert_called_once_with(
        "user@example.com",
        "Welcome, John!",
        "Hello John, welcome to our service!"
    )


def test_email_service_invalid_email():
    """Тест для проверки ValueError при невалидном email"""
    service = EmailService()

    with pytest.raises(ValueError, match="Invalid email address"):
        service.send_email("invalid-email", "Subject", "Body")


# ========== ЗАДАНИЕ 6: Интеграционные тесты для UserRepository ==========

@pytest.mark.integration
def test_user_repository_create_user(user_repo):
    """Тест create_user - создание пользователя"""
    user = user_repo.create("alice", "alice@example.com", 25)

    assert user["username"] == "alice"
    assert user["email"] == "alice@example.com"
    assert user["age"] == 25
    assert "id" in user


@pytest.mark.integration
def test_user_repository_find_by_id(user_repo):
    """Тест find_by_id - поиск по ID"""
    created_user = user_repo.create("bob", "bob@example.com", 30)
    user_id = created_user["id"]

    found_user = user_repo.find_by_id(user_id)
    assert found_user["username"] == "bob"


@pytest.mark.integration
def test_user_repository_find_by_email(user_repo):
    """Тест find_by_email - поиск по email"""
    user_repo.create("charlie", "charlie@example.com", 35)

    found_user = user_repo.find_by_email("charlie@example.com")
    assert found_user["username"] == "charlie"


@pytest.mark.integration
def test_user_repository_update(user_repo):
    """Тест update - обновление пользователя"""
    created_user = user_repo.create("david", "david@example.com", 28)
    user_id = created_user["id"]

    updated_user = user_repo.update(user_id, username="david_updated", age=29)
    assert updated_user["username"] == "david_updated"
    assert updated_user["age"] == 29


@pytest.mark.integration
def test_user_repository_delete(user_repo):
    """Тест delete - удаление пользователя"""
    created_user = user_repo.create("eve", "eve@example.com", 27)
    user_id = created_user["id"]

    result = user_repo.delete(user_id)
    assert result is True

    with pytest.raises(ValueError):
        user_repo.find_by_id(user_id)


@pytest.mark.integration
def test_user_repository_persistence(user_repo):
    """Тест для проверки, что изменения сохраняются между вызовами методов"""
    user1 = user_repo.create("user1", "user1@example.com", 20)
    user2 = user_repo.create("user2", "user2@example.com", 25)

    all_users = user_repo.get_all()
    assert len(all_users) >= 2

    found_user1 = user_repo.find_by_id(user1["id"])
    found_user2 = user_repo.find_by_id(user2["id"])

    assert found_user1["username"] == "user1"
    assert found_user2["username"] == "user2"


# ========== ЗАДАНИЕ 7: Тесты для ShoppingCart ==========

def test_shopping_cart_add_item():
    """Тест add_item - добавление товара"""
    cart = ShoppingCart()
    cart.add_item("item1", "Product 1", 10.0, 2)

    items = cart.get_items()
    assert "item1" in items
    assert items["item1"]["quantity"] == 2
    assert items["item1"]["price"] == 10.0


def test_shopping_cart_get_total():
    """Тест get_total - расчет общей стоимости"""
    cart = ShoppingCart()
    cart.add_item("item1", "Product 1", 10.0, 2)
    cart.add_item("item2", "Product 2", 5.0, 3)

    total = cart.get_total()
    assert total == 35.0


def test_shopping_cart_apply_discount():
    """Тест apply_discount - применение скидки"""
    cart = ShoppingCart()
    cart.add_item("item1", "Product 1", 100.0, 1)
    cart.apply_discount(10.0)

    total = cart.get_total()
    assert total == 90.0


def test_shopping_cart_remove_item():
    """Тест remove_item - удаление товара"""
    cart = ShoppingCart()
    cart.add_item("item1", "Product 1", 10.0, 5)
    cart.remove_item("item1", 2)

    items = cart.get_items()
    assert items["item1"]["quantity"] == 3


def test_shopping_cart_clear():
    """Тест clear - очистка корзины"""
    cart = ShoppingCart()
    cart.add_item("item1", "Product 1", 10.0, 1)
    cart.apply_discount(10.0)

    cart.clear()

    assert cart.get_total() == 0.0
    assert len(cart.get_items()) == 0


# ========== ЗАДАНИЕ 8: Тесты для validate_password ==========

def test_validate_password_valid():
    """Тест для валидного пароля"""
    is_valid, message = validate_password("Password123")
    assert is_valid is True
    assert message == ""


def test_validate_password_too_short():
    """Тест для слишком короткого пароля"""
    is_valid, message = validate_password("Pass1")
    assert is_valid is False
    assert "at least 8 characters" in message


def test_validate_password_no_uppercase():
    """Тест для пароля без заглавных букв"""
    is_valid, message = validate_password("password123")
    assert is_valid is False
    assert "uppercase" in message


def test_validate_password_no_lowercase():
    """Тест для пароля без строчных букв"""
    is_valid, message = validate_password("PASSWORD123")
    assert is_valid is False
    assert "lowercase" in message


def test_validate_password_no_digit():
    """Тест для пароля без цифр"""
    is_valid, message = validate_password("Password")
    assert is_valid is False
    assert "digit" in message


# ========== ЗАДАНИЕ 9: Тесты для process_numbers ==========

def test_process_numbers_empty():
    """Тест для пустого списка"""
    result = process_numbers([])

    assert result["count"] == 0
    assert result["sum"] == 0
    assert result["average"] == 0
    assert result["min"] is None
    assert result["max"] is None
    assert result["even_count"] == 0
    assert result["odd_count"] == 0


def test_process_numbers_with_values():
    """Тест для списка с числами - проверка всех полей результата"""
    result = process_numbers([1, 2, 3, 4, 5])

    assert result["count"] == 5
    assert result["sum"] == 15
    assert result["average"] == 3.0
    assert result["min"] == 1
    assert result["max"] == 5
    assert result["even_count"] == 2
    assert result["odd_count"] == 3


def test_process_numbers_even_odd_count():
    """Тест для проверки even_count и odd_count"""
    result = process_numbers([2, 4, 6, 8])
    assert result["even_count"] == 4
    assert result["odd_count"] == 0

    result = process_numbers([1, 3, 5, 7])
    assert result["even_count"] == 0
    assert result["odd_count"] == 4


# ========== ЗАДАНИЕ 10: Маркеры ==========

@pytest.mark.slow
def test_slow_computation():
    """Медленный тест с маркером @pytest.mark.slow"""
    import time
    time.sleep(0.1)
    assert Calculator.power(2, 10) == 1024


@pytest.mark.integration
def test_integration_example(user_repo):
    """Интеграционный тест с маркером @pytest.mark.integration"""
    user = user_repo.create("integration_user", "int@example.com", 30)
    assert user["username"] == "integration_user"


# ========== ЗАДАНИЕ 11: E2E тесты с Playwright ==========

def test_example_homepage(page: Page):
    """Тест для открытия https://example.com"""
    page.goto("https://example.com")
    expect(page).to_have_title("Example Domain")


def test_example_page_title(page: Page):
    """Тест для проверки заголовка страницы"""
    page.goto("https://example.com")

    heading = page.get_by_role("heading", name="Example Domain")
    expect(heading).to_be_visible()


def test_example_find_element(page: Page):
    """Тест для поиска элемента на странице"""
    page.goto("https://example.com")

    paragraph = page.locator("p").first
    expect(paragraph).to_be_visible()
    expect(paragraph).to_contain_text("This domain is for use")


def test_example_navigation(page: Page):
    """Тест для взаимодействия со страницей"""
    page.goto("https://example.com")

    more_info_link = page.get_by_text("More information...")
    expect(more_info_link).to_be_visible()

    more_info_link.click()
    page.wait_for_load_state("networkidle")

    expect(page).to_have_url("https://www.iana.org/domains/example")
