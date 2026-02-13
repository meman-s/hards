"""
РЕШЕНИЯ для E2E тестов формы
"""

import pytest
from playwright.sync_api import Page, expect


def test_form_loads(page: Page, form_url):
    page.goto(form_url)
    expect(page).to_have_title("Тестовая форма для E2E тестов")


def test_form_heading(page: Page, form_url):
    page.goto(form_url)
    heading = page.get_by_role("heading", name="Форма регистрации")
    expect(heading).to_be_visible()


def test_form_fill_and_submit(page: Page, form_url):
    page.goto(form_url)

    page.get_by_test_id("username-input").fill("testuser")
    page.get_by_test_id("email-input").fill("test@example.com")
    page.get_by_test_id("password-input").fill("password123")
    page.get_by_test_id("country-select").select_option("ru")
    page.get_by_test_id("message-textarea").fill("Тестовое сообщение")
    page.get_by_test_id("agree-checkbox").check()

    page.get_by_test_id("submit-button").click()

    success_message = page.get_by_test_id("success-message")
    expect(success_message).to_be_visible()


def test_form_success_message(page: Page, form_url):
    page.goto(form_url)

    page.get_by_test_id("username-input").fill("testuser")
    page.get_by_test_id("email-input").fill("test@example.com")
    page.get_by_test_id("password-input").fill("password123")
    page.get_by_test_id("agree-checkbox").check()
    page.get_by_test_id("submit-button").click()

    success_message = page.get_by_test_id("success-message")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text("Форма успешно отправлена")


def test_form_validation_short_username(page: Page, form_url):
    page.goto(form_url)

    page.get_by_test_id("username-input").fill("ab")
    page.get_by_test_id("email-input").fill("test@example.com")
    page.get_by_test_id("password-input").fill("password123")
    page.get_by_test_id("agree-checkbox").check()

    page.get_by_test_id("submit-button").click()

    error = page.locator("#username-error")
    expect(error).to_be_visible()
    expect(error).to_contain_text("не менее 3 символов")


def test_form_select_country(page: Page, form_url):
    page.goto(form_url)

    select = page.get_by_test_id("country-select")
    select.select_option("us")
    expect(select).to_have_value("us")

    select.select_option("ru")
    expect(select).to_have_value("ru")


def test_form_checkbox_agreement(page: Page, form_url):
    page.goto(form_url)

    checkbox = page.get_by_test_id("agree-checkbox")
    expect(checkbox).not_to_be_checked()

    checkbox.check()
    expect(checkbox).to_be_checked()

    checkbox.uncheck()
    expect(checkbox).not_to_be_checked()


def test_form_validation_invalid_email(page: Page, form_url):
    page.goto(form_url)

    page.get_by_test_id("username-input").fill("testuser")
    page.get_by_test_id("email-input").fill("invalid-email")
    page.get_by_test_id("password-input").fill("password123")
    page.get_by_test_id("agree-checkbox").check()

    page.get_by_test_id("submit-button").click()

    error = page.locator("#email-error")
    expect(error).to_be_visible()
    expect(error).to_contain_text("Некорректный email")


def test_form_validation_short_password(page: Page, form_url):
    page.goto(form_url)

    page.get_by_test_id("username-input").fill("testuser")
    page.get_by_test_id("email-input").fill("test@example.com")
    page.get_by_test_id("password-input").fill("12345")
    page.get_by_test_id("agree-checkbox").check()

    page.get_by_test_id("submit-button").click()

    error = page.locator("#password-error")
    expect(error).to_be_visible()
    expect(error).to_contain_text("не менее 6 символов")
