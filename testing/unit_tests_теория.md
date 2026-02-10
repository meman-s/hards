# Юнит тесты

Юнит тесты проверяют изолированно отдельные функции, методы или классы без зависимостей от внешних систем.

## Принципы

1. **Изоляция** - тест не зависит от других тестов
2. **Быстрота** - выполняются быстро
3. **Детерминированность** - всегда одинаковый результат
4. **Один случай на тест** - один тест проверяет одну вещь

## Мокирование

### unittest.mock

```python
from unittest.mock import Mock, patch, MagicMock

def test_with_mock():
    mock_obj = Mock(return_value=42)
    assert mock_obj() == 42
    mock_obj.assert_called_once()
```

### Патчинг

```python
@patch('module.external_api_call')
def test_with_patch(mock_api):
    mock_api.return_value = {"status": "ok"}
    result = function_using_api()
    assert result["status"] == "ok"
```

### Патчинг через контекстный менеджер

```python
def test_with_context_manager():
    with patch('module.external_api_call') as mock_api:
        mock_api.return_value = {"status": "ok"}
        result = function_using_api()
        assert result["status"] == "ok"
```

## Структура теста (AAA)

- **Arrange** - подготовка данных
- **Act** - выполнение действия
- **Assert** - проверка результата

```python
def test_calculate_total():
    # Arrange
    items = [10, 20, 30]
    
    # Act
    total = sum(items)
    
    # Assert
    assert total == 60
```

## Тестирование исключений

```python
import pytest

def test_raises_exception():
    with pytest.raises(ValueError):
        raise ValueError("Error message")

def test_raises_with_message():
    with pytest.raises(ValueError, match="Error message"):
        raise ValueError("Error message")
```

## Тестирование классов

```python
class Calculator:
    def add(self, a, b):
        return a + b
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Division by zero")
        return a / b

def test_calculator_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_calculator_divide():
    calc = Calculator()
    assert calc.divide(10, 2) == 5

def test_calculator_divide_by_zero():
    calc = Calculator()
    with pytest.raises(ValueError):
        calc.divide(10, 0)
```

## Покрытие кода

```bash
pytest --cov=module_name --cov-report=html
```
