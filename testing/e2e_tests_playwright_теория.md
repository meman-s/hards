# E2E тесты: Playwright

End-to-End тесты проверяют работу приложения с точки зрения пользователя, включая UI и взаимодействие с браузером.

## Установка

```bash
pip install pytest-playwright
playwright install
```

## Базовый пример

```python
from playwright.sync_api import Page, expect

def test_homepage(page: Page):
    page.goto("https://example.com")
    expect(page).to_have_title("Example Domain")
```

## Основные операции

### Навигация

```python
page.goto("https://example.com")
page.go_back()
page.go_forward()
page.reload()
```

### Поиск элементов

```python
# По селектору
button = page.locator("button.submit")

# По тексту
link = page.get_by_text("Click me")

# По роли
heading = page.get_by_role("heading", name="Welcome")

# По placeholder
input = page.get_by_placeholder("Enter name")
```

### Взаимодействие

```python
# Клик
page.click("button")
page.locator("button").click()

# Ввод текста
page.fill("input[name='email']", "test@example.com")
page.type("input", "text", delay=100)

# Выбор опции
page.select_option("select", "option_value")

# Чекбокс
page.check("input[type='checkbox']")
page.uncheck("input[type='checkbox']")
```

### Ожидания

```python
from playwright.sync_api import expect

# Проверка видимости
expect(page.locator("button")).to_be_visible()

# Проверка текста
expect(page.locator("h1")).to_have_text("Welcome")

# Проверка атрибутов
expect(page.locator("input")).to_have_attribute("type", "text")

# Ожидание загрузки
page.wait_for_load_state("networkidle")
page.wait_for_selector("button")
```

## Фикстуры Playwright

```python
import pytest
from playwright.sync_api import Page, Browser, BrowserContext

def test_example(page: Page):
    page.goto("https://example.com")
    # page автоматически создается и закрывается
```

### Настройка браузера

```python
@pytest.fixture(scope="session")
def browser_type_launch_args():
    return {
        "headless": False,
        "slow_mo": 1000,
    }
```

## Работа с несколькими страницами

```python
def test_multiple_pages(page: Page):
    page.goto("https://example.com")
    
    with page.context.expect_page() as new_page_info:
        page.click("a[target='_blank']")
    new_page = new_page_info.value
    new_page.wait_for_load_state()
```

## Перехват запросов

```python
def test_api_interception(page: Page):
    page.route("**/api/users", lambda route: route.fulfill(
        status=200,
        body='{"users": []}'
    ))
    page.goto("https://example.com")
```

## Скриншоты и видео

```python
def test_with_screenshot(page: Page):
    page.goto("https://example.com")
    page.screenshot(path="screenshot.png")
    
    # Видео включается в конфиге
```

## Конфигурация pytest.ini

```ini
[pytest]
addopts = --headed
playwright_browser = chromium
playwright_browser_channel = 
playwright_headed = False
playwright_timeout = 30000
```

## Лучшие практики

1. Используйте data-testid для стабильных селекторов
2. Используйте page object pattern для сложных страниц
3. Группируйте связанные действия
4. Используйте ожидания вместо sleep
5. Изолируйте тесты друг от друга
