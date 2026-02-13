"""
E2E тесты для формы регистрации - ЗАДАНИЯ
Решения: test_e2e_form_solutions.py
Фикстуры page и form_url — в e2e/conftest.py
"""
from playwright.sync_api import Page, expect


def test_form_loads_page_title(page: Page, form_url: str):
    page.goto(form_url)
    expect(page).to_have_title("Тестовая форма для E2E тестов")


def test_form_heading_visible(page: Page, form_url: str):
    page.goto(form_url)
    heading = page.get_by_role("heading", name="Форма регистрации")
    expect(heading).to_be_visible()


def test_full_fill(page: Page, form_url: str):
    page.goto(form_url)

    page.locator("input[name='username']").fill("Stepan")

    page.locator("input[name='email']").fill("stepan.kalimullin@gmail.com")

    page.locator("input[name='password']").fill("qazxswedc123")

    page.locator("select[name='country']").select_option(value="ru")

    page.locator("textarea[name='message']").fill("I'm doing it")

    page.locator("input[name='agree']").check()

    page.locator("button[id='submitBtn']").click()

    success = page.locator("div[id='successMessage']")
    expect(success).to_be_visible()
    expect(success).to_have_text("Форма успешно отправлена!")
