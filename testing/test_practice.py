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
# TODO: Создайте фикстуру для BankAccount с начальным балансом 100.0
# TODO: Создайте фикстуру scope="module" для UserRepository
# TODO: Создайте фикстуру с autouse=True, которая выводит "Starting test"


# ========== ЗАДАНИЕ 2: Юнит тесты для BankAccount ==========
# TODO: Напишите тест для deposit - проверка увеличения баланса
# TODO: Напишите тест для withdraw - проверка уменьшения баланса
# TODO: Напишите тест для withdraw с недостаточным балансом - должен вызывать ValueError
# TODO: Напишите тест для transfer между двумя счетами
# TODO: Напишите тест для transaction_history - проверка истории операций


# ========== ЗАДАНИЕ 3: Параметризованные тесты для Calculator ==========
# TODO: Используя @pytest.mark.parametrize, напишите тест для Calculator.add с разными значениями:
#       (2, 3, 5), (0, 0, 0), (-1, 1, 0), (10.5, 2.5, 13.0)
# TODO: Напишите параметризованный тест для Calculator.multiply
# TODO: Напишите параметризованный тест для Calculator.divide, включая проверку деления на ноль


# ========== ЗАДАНИЕ 4: Юнит тесты для StringProcessor ==========
# TODO: Напишите тест для reverse - проверка переворота строки
# TODO: Напишите тест для capitalize_words
# TODO: Напишите тест для is_palindrome - проверка палиндромов ("racecar", "A man a plan")
# TODO: Напишите тест для count_words
# TODO: Напишите тест для проверки TypeError при передаче не-строки


# ========== ЗАДАНИЕ 5: Тесты с моками для EmailService ==========
# TODO: Создайте мок для smtp_client
# TODO: Напишите тест send_email с проверкой вызова smtp_client.send
# TODO: Напишите тест send_welcome_email
# TODO: Напишите тест для проверки ValueError при невалидном email


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


# ========== ЗАДАНИЕ 11: E2E тесты с Playwright ==========
# TODO: Напишите тест для открытия https://example.com
# TODO: Напишите тест для проверки заголовка страницы
# TODO: Напишите тест для поиска элемента на странице
# TODO: Напишите тест для взаимодействия с формой (если есть)
