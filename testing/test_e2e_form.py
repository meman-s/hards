"""
E2E тесты для формы регистрации - ЗАДАНИЯ
Напишите свои тесты здесь, решения смотрите в test_e2e_form_solutions.py
"""

import pytest
from playwright.sync_api import Page, expect


def test_form_loads(page: Page):
    page.goto("file:///home/meman-s/Загрузки/rumicon/hards/testing/test_form.html")
    expect(page).to_have_title("Тестовая форма для E2E тестов")


def test_fullfill(page: Page):
    page.goto("file:///home/meman-s/Загрузки/rumicon/hards/testing/test_form.html")

    page.locator('input[name="username"]').fill("testuser")
    page.screenshot(path="screenshot.png")
# TODO: Напишите тест для открытия формы test_form.html
# TODO: Напишите тест для проверки заголовка страницы "Тестовая форма для E2E тестов"
# TODO: Напишите тест для заполнения всех полей формы и отправки
# TODO: Напишите тест для проверки сообщения об успехе после отправки
# TODO: Напишите тест для проверки валидации (например, короткое имя пользователя)
# TODO: Напишите тест для выбора страны из выпадающего списка
# TODO: Напишите тест для проверки чекбокса согласия

# Подсказки:
# - Используйте page.goto("file:///полный/путь/к/test_form.html")
# - Используйте page.get_by_test_id("username-input") для поиска элементов
# - Используйте expect() для проверок
# - Используйте .fill(), .select_option(), .check() для взаимодействия
