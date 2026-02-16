# Тестирование на Python

Материалы для изучения тестирования: теория, задания и решения.

## Структура

```
testing/
  conftest.py          # добавление корня testing в PYTHONPATH
  pytest.ini
  requirements.txt
  practice_code.py     # код для практики (импорт: from practice_code import ...)
  test_tasks.py        # код для тестов из unit/test_solutions.py и integration/

  docs/                # теория и задания
    pytest_fixtures_parametrize_markers_теория.md
    unit_tests_теория.md
    integration_tests_теория.md
    e2e_tests_playwright_теория.md
    моки_vs_реальные_запросы.md
    PRACTICE_ASSIGNMENTS.md

  unit/                # юнит-тесты
    oleg_tests.py
    test_practice.py
    test_practice_example.py
    test_solutions.py

  integration/         # интеграционные тесты
    integration_test_real_api_example.py

  e2e/                 # E2E тесты (Playwright)
    conftest.py        # form_url фикстура
    test_form.html
    test_e2e_form.py
    test_e2e_form_solutions.py
```

## Установка

```bash
pip install pytest pytest-cov pytest-playwright pytest-xdist
playwright install
```

## Запуск тестов

Запускать из корня проекта или из папки `testing/`:

```bash
cd testing
pytest
```

Или из корня проекта:

```bash
pytest testing/
```

### По папкам

```bash
pytest unit/ -v
pytest integration/ -v
pytest e2e/ -v
```

### Конкретный файл

```bash
pytest unit/test_solutions.py -v
pytest unit/test_practice.py -v
```

### С маркерами

```bash
pytest -m "not slow" -v
pytest -m integration -v
```

### С покрытием

```bash
pytest unit/ --cov=. --cov=practice_code --cov-report=html
```

## Практика

1. Инструкции: `docs/PRACTICE_ASSIGNMENTS.md`
2. Код для тестов: `practice_code.py`
3. Файл для своих тестов: `unit/test_practice.py`
4. Примеры решений: `unit/test_practice_example.py`

Дополнительные задания (функции для тестов разного уровня): `docs/ASSIGNMENTS_TESTS.md`, код — `assignment_functions.py`.  
E2E задания (Playwright, форма в `e2e/`): `docs/E2E_PLAYWRIGHT_ASSIGNMENTS.md`, тесты — `e2e/test_e2e_form.py`.

## Ресурсы

- [Pytest](https://docs.pytest.org/)
- [Playwright Python](https://playwright.dev/python/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
