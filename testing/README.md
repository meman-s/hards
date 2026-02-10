# Тестирование на Python

Материалы для изучения тестирования: теория, задания и решения.

## Структура

- `pytest_fixtures_parametrize_markers_теория.md` - теория по Pytest
- `unit_tests_теория.md` - теория по юнит тестам
- `integration_tests_теория.md` - теория по интеграционным тестам
- `e2e_tests_playwright_теория.md` - теория по E2E тестам с Playwright
- `test_tasks.py` - код для тестирования (задания)
- `test_solutions.py` - решения с примерами тестов

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

## Задания

1. **Pytest: Fixtures, Parametrize, Markers**
   - Изучите теорию в `pytest_fixtures_parametrize_markers_теория.md`
   - Посмотрите примеры в `test_solutions.py`
   - Напишите свои тесты для классов из `test_tasks.py`

2. **Юнит тесты**
   - Изучите теорию в `unit_tests_теория.md`
   - Напишите юнит тесты для всех методов классов из `test_tasks.py`
   - Используйте мокирование для изоляции

3. **Интеграционные тесты**
   - Изучите теорию в `integration_tests_теория.md`
   - Напишите интеграционные тесты для `UserService` с реальной базой данных (in-memory)
   - Протестируйте взаимодействие между компонентами

4. **E2E тесты: Playwright**
   - Изучите теорию в `e2e_tests_playwright_теория.md`
   - Напишите E2E тесты для реального веб-приложения
   - Протестируйте основные пользовательские сценарии

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
