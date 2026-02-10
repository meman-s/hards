"""
Решения заданий по тестированию
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from playwright.sync_api import Page, expect
from test_tasks import (
    Calculator,
    UserService,
    EmailValidator,
    Cache,
    APIClient,
    process_data,
    calculate_statistics
)


# ========== Pytest: Fixtures, Parametrize, Markers ==========

@pytest.fixture
def calculator():
    return Calculator()


@pytest.fixture(scope="module")
def shared_data():
    return {"initialized": True}


@pytest.fixture(autouse=True)
def setup_test():
    print("\nНачало теста")
    yield
    print("Конец теста")


@pytest.mark.parametrize("a,b,expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (10.5, 2.5, 13.0),
])
def test_calculator_add_parametrize(calculator, a, b, expected):
    assert calculator.add(a, b) == expected


@pytest.mark.parametrize("a", [2, 3, 4])
@pytest.mark.parametrize("b", [1, 2])
def test_calculator_multiply_double_parametrize(calculator, a, b):
    result = calculator.multiply(a, b)
    assert result == a * b


@pytest.mark.slow
def test_calculator_power_slow(calculator):
    result = calculator.power(2, 1000)
    assert result > 0


@pytest.mark.skip(reason="Тест временно отключен")
def test_skipped():
    assert False


@pytest.mark.skipif(True, reason="Условный пропуск")
def test_skipif():
    assert False


# ========== Юнит тесты ==========

def test_calculator_add(calculator):
    assert calculator.add(2, 3) == 5


def test_calculator_subtract(calculator):
    assert calculator.subtract(5, 3) == 2


def test_calculator_multiply(calculator):
    assert calculator.multiply(4, 3) == 12


def test_calculator_divide(calculator):
    assert calculator.divide(10, 2) == 5


def test_calculator_divide_by_zero(calculator):
    with pytest.raises(ValueError, match="Division by zero"):
        calculator.divide(10, 0)


def test_email_validator_valid():
    validator = EmailValidator()
    assert validator.validate("test@example.com") is True
    assert validator.validate("user.name@domain.co.uk") is True


def test_email_validator_invalid():
    validator = EmailValidator()
    assert validator.validate("") is False
    assert validator.validate("invalid") is False
    assert validator.validate("@domain.com") is False
    assert validator.validate("user@") is False
    assert validator.validate("user@domain") is False


def test_cache_set_get():
    cache = Cache()
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"


def test_cache_get_nonexistent():
    cache = Cache()
    assert cache.get("nonexistent") is None


def test_cache_delete():
    cache = Cache()
    cache.set("key1", "value1")
    assert cache.delete("key1") is True
    assert cache.get("key1") is None
    assert cache.delete("nonexistent") is False


def test_cache_clear():
    cache = Cache()
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.clear()
    assert cache.get("key1") is None
    assert cache.get("key2") is None


def test_process_data_filter():
    data = [1, 2, 3, 4, 5]
    result = process_data(data, filter_func=lambda x: x > 3)
    assert result == [4, 5]


def test_process_data_transform():
    data = [1, 2, 3]
    result = process_data(data, transform_func=lambda x: x * 2)
    assert result == [2, 4, 6]


def test_process_data_filter_and_transform():
    data = [1, 2, 3, 4, 5]
    result = process_data(
        data,
        filter_func=lambda x: x > 2,
        transform_func=lambda x: x * 2
    )
    assert result == [6, 8, 10]


def test_calculate_statistics():
    numbers = [1, 2, 3, 4, 5]
    stats = calculate_statistics(numbers)
    assert stats["count"] == 5
    assert stats["sum"] == 15
    assert stats["average"] == 3.0
    assert stats["min"] == 1
    assert stats["max"] == 5


def test_calculate_statistics_empty():
    stats = calculate_statistics([])
    assert stats["count"] == 0
    assert stats["sum"] == 0
    assert stats["average"] == 0
    assert stats["min"] is None
    assert stats["max"] is None


# ========== Интеграционные тесты ==========

@pytest.fixture
def mock_db():
    return []


def test_user_service_create_user(mock_db):
    service = UserService(mock_db)
    user = service.create_user("Alice", "alice@example.com")
    
    assert user["name"] == "Alice"
    assert user["email"] == "alice@example.com"
    assert user["id"] == 1
    assert len(mock_db) == 1


def test_user_service_create_user_validation(mock_db):
    service = UserService(mock_db)
    
    with pytest.raises(ValueError, match="Name and email are required"):
        service.create_user("", "test@example.com")
    
    with pytest.raises(ValueError, match="Invalid email format"):
        service.create_user("Test", "invalid-email")


def test_user_service_get_user(mock_db):
    service = UserService(mock_db)
    created_user = service.create_user("Bob", "bob@example.com")
    user_id = created_user["id"]
    
    found_user = service.get_user(user_id)
    assert found_user["name"] == "Bob"
    assert found_user["email"] == "bob@example.com"


def test_user_service_get_user_not_found(mock_db):
    service = UserService(mock_db)
    
    with pytest.raises(ValueError, match="User with id 999 not found"):
        service.get_user(999)


def test_user_service_delete_user(mock_db):
    service = UserService(mock_db)
    user = service.create_user("Charlie", "charlie@example.com")
    user_id = user["id"]
    
    assert service.delete_user(user_id) is True
    assert len(mock_db) == 0
    
    with pytest.raises(ValueError):
        service.get_user(user_id)


def test_user_service_delete_nonexistent(mock_db):
    service = UserService(mock_db)
    assert service.delete_user(999) is False


@patch('test_tasks.requests.get')
def test_api_client_get(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"status": "ok"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    client = APIClient("https://api.example.com")
    result = client.get("users")
    
    assert result == {"status": "ok"}
    mock_get.assert_called_once_with(
        "https://api.example.com/users",
        timeout=30
    )


@patch('test_tasks.requests.post')
def test_api_client_post(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "name": "Test"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    client = APIClient("https://api.example.com")
    result = client.post("users", {"name": "Test"})
    
    assert result == {"id": 1, "name": "Test"}
    mock_post.assert_called_once()


# ========== E2E тесты: Playwright ==========

def test_example_homepage(page: Page):
    page.goto("https://example.com")
    expect(page).to_have_title("Example Domain")
    
    heading = page.get_by_role("heading", name="Example Domain")
    expect(heading).to_be_visible()


def test_example_navigation(page: Page):
    page.goto("https://example.com")
    
    more_info_link = page.get_by_text("More information...")
    expect(more_info_link).to_be_visible()
    
    more_info_link.click()
    expect(page).to_have_url("https://www.iana.org/domains/example")


def test_form_interaction(page: Page):
    page.goto("https://example.com")
    
    page.fill("input[name='q']", "test search")
    page.press("input[name='q']", "Enter")
    
    page.wait_for_load_state("networkidle")


def test_element_visibility(page: Page):
    page.goto("https://example.com")
    
    paragraph = page.locator("p")
    expect(paragraph.first).to_be_visible()
    expect(paragraph.first).to_contain_text("This domain is for use in illustrative examples")


def test_multiple_elements(page: Page):
    page.goto("https://example.com")
    
    paragraphs = page.locator("p")
    count = paragraphs.count()
    assert count > 0
    
    for i in range(count):
        expect(paragraphs.nth(i)).to_be_visible()
