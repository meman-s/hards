# Pytest: Fixtures, Parametrize, Markers

## Fixtures

Фикстуры - это функции, которые выполняются перед тестами и предоставляют данные или настройки.

```python
import pytest

@pytest.fixture
def sample_data():
    return {"name": "test", "value": 42}

def test_example(sample_data):
    assert sample_data["name"] == "test"
```

### Scope фикстур
- `function` (по умолчанию) - выполняется для каждого теста
- `class` - один раз для класса
- `module` - один раз для модуля
- `session` - один раз за сессию

```python
@pytest.fixture(scope="module")
def db_connection():
    conn = create_connection()
    yield conn
    conn.close()
```

### Автоматические фикстуры (autouse)

```python
@pytest.fixture(autouse=True)
def setup():
    print("Выполняется перед каждым тестом")
```

## Parametrize

Параметризация позволяет запускать один тест с разными входными данными.

```python
@pytest.mark.parametrize("input,expected", [
    (2, 4),
    (3, 9),
    (4, 16),
])
def test_square(input, expected):
    assert input ** 2 == expected
```

### Множественная параметризация

```python
@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", [3, 4])
def test_multiply(x, y):
    assert x * y > 0
```

## Markers

Маркеры позволяют помечать тесты для группировки и фильтрации.

### Встроенные маркеры

- `@pytest.mark.skip` - пропустить тест
- `@pytest.mark.skipif` - пропустить при условии
- `@pytest.mark.xfail` - ожидаемый провал
- `@pytest.mark.parametrize` - параметризация

### Пользовательские маркеры

В `pytest.ini`:
```ini
[pytest]
markers =
    slow: медленные тесты
    integration: интеграционные тесты
    unit: юнит тесты
```

Использование:
```python
@pytest.mark.slow
def test_heavy_computation():
    pass

@pytest.mark.integration
def test_api():
    pass
```

Запуск с маркерами:
```bash
pytest -m slow
pytest -m "not slow"
pytest -m "slow or integration"
```

## Полезные фикстуры

- `tmp_path` - временная директория
- `tmpdir` - временная директория (устаревшая)
- `monkeypatch` - мокирование переменных окружения
- `capsys` - захват stdout/stderr
- `caplog` - работа с логами
