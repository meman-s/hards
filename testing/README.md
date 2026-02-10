# Тестирование на Python

Материалы для изучения тестирования: теория, задания и решения.

## Структура

### Теория
- `pytest_fixtures_parametrize_markers_теория.md` - теория по Pytest
- `unit_tests_теория.md` - теория по юнит тестам
- `integration_tests_теория.md` - теория по интеграционным тестам
- `e2e_tests_playwright_теория.md` - теория по E2E тестам с Playwright
- `моки_vs_реальные_запросы.md` - сравнение подходов к тестированию

### Примеры и решения
- `test_tasks.py` - код для тестирования (базовые примеры)
- `test_solutions.py` - решения с примерами тестов

### Практические задания
- `practice_code.py` - код для практики (классы и функции для тестирования)
- `test_practice.py` - файл для написания ваших тестов (TODO задания)
- `PRACTICE_ASSIGNMENTS.md` - подробные инструкции к заданиям

## Установка зависимостей

```bash
pip install pytest pytest-cov pytest-playwright pytest-xdist
playwright install
```

## Запуск тестов

### Все тесты
```bash
pytest testing/
```

### Конкретный файл
```bash
pytest testing/test_solutions.py
```

### С покрытием кода
```bash
pytest testing/ --cov=testing --cov-report=html
```

### С маркерами
```bash
pytest -m slow
pytest -m "not slow"
```

### Параллельно
```bash
pytest -n auto
```

### E2E тесты (Playwright)
```bash
pytest testing/test_solutions.py::test_example_homepage -v
```

### Практические задания
```bash
# Запустить все практические тесты
pytest test_practice.py -v

# Запустить конкретное задание
pytest test_practice.py::test_bank_account_deposit -v

# Запустить только быстрые тесты
pytest test_practice.py -m "not slow" -v
```

## Практические задания

### Быстрый старт

1. Откройте `PRACTICE_ASSIGNMENTS.md` - там подробные инструкции
2. Откройте `test_practice.py` - там TODO задания
3. Изучите `practice_code.py` - код, который нужно тестировать
4. Напишите тесты вместо TODO комментариев
5. Запустите: `pytest test_practice.py -v`

### Задания по темам

1. **Pytest: Fixtures, Parametrize, Markers**
   - Изучите теорию в `pytest_fixtures_parametrize_markers_теория.md`
   - Посмотрите примеры в `test_solutions.py`
   - Выполните задания 1, 3, 10 в `test_practice.py`

2. **Юнит тесты**
   - Изучите теорию в `unit_tests_теория.md`
   - Выполните задания 2, 4, 8, 9 в `test_practice.py`
   - Используйте мокирование для изоляции

3. **Интеграционные тесты**
   - Изучите теорию в `integration_tests_теория.md`
   - Выполните задание 6 в `test_practice.py`
   - Протестируйте взаимодействие между компонентами

4. **Тесты с моками**
   - Выполните задание 5 в `test_practice.py`
   - Изучите примеры в `test_solutions.py`

5. **E2E тесты: Playwright**
   - Изучите теорию в `e2e_tests_playwright_теория.md`
   - Выполните задание 11 в `test_practice.py`
   - Протестируйте реальные веб-страницы

## Рекомендации

1. Начните с юнит тестов - они проще и быстрее
2. Используйте фикстуры для переиспользования кода
3. Параметризуйте тесты для проверки разных входных данных
4. Используйте маркеры для организации тестов
5. Пишите изолированные тесты без зависимостей
6. Для E2E тестов используйте стабильные селекторы (data-testid)

## Дополнительные ресурсы

- [Pytest документация](https://docs.pytest.org/)
- [Playwright документация](https://playwright.dev/python/)
- [unittest.mock документация](https://docs.python.org/3/library/unittest.mock.html)
