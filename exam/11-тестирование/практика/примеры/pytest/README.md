# Pytest: fixtures, parametrize, markers и Юнит тесты

## Структура файлов

- `задания.py` - код, для которого нужно написать тесты
- `задания.md` - описание заданий с требованиями
- `ответы.py` - примеры правильных решений (тесты)
- `ответы.md` - подробные объяснения решений
- `conftest.py` - конфигурация pytest с регистрацией маркеров

## Задания

### Задание 1: Юнит-тесты для класса Calculator
Написать полный набор юнит-тестов для класса Calculator, включая проверку исключений.

### Задание 2: Параметризованные тесты
Использовать `@pytest.mark.parametrize` для тестирования валидации email и паролей.

### Задание 3: Тесты с fixtures
Создать fixtures для подключения к базе данных и тестовых данных, написать тесты для DatabaseConnection.

### Задание 4: Тесты с markers
Разделить тесты на категории (fast, slow, integration) с помощью маркеров.

### Задание 5: Комбинированное задание
Использовать fixtures и parametrize вместе для тестирования функции fibonacci.

### Задание 6: Тесты с временными файлами
Создать fixtures с yield для работы с временными файлами.

## Как использовать

1. Изучите код в `задания.py`
2. Прочитайте требования в `задания.md`
3. Напишите тесты в отдельном файле (например, `test_задания.py`)
4. Проверьте свои решения, сравнив с `ответы.py` и `ответы.md`

## Запуск тестов

### Запуск всех тестов

```bash
# Запустить все тесты в проекте
pytest

# Запустить все тесты из текущей директории
pytest примеры/pytest/

# Запустить все тесты из директории pytest (из корня практики)
cd /home/meman-s/Загрузки/rumicon/hards/exam/11-тестирование/практика
pytest примеры/pytest/
```

### Запуск конкретных тестов из test_solutions.py

```bash
# Из корня практики (exam/11-тестирование/практика)
cd /home/meman-s/Загрузки/rumicon/hards/exam/11-тестирование/практика

# Запустить все тесты из файла test_solutions.py
pytest примеры/pytest/test_solutions.py

# Запустить конкретный тест по имени функции
pytest примеры/pytest/test_solutions.py::test_add

# Запустить несколько конкретных тестов
pytest примеры/pytest/test_solutions.py::test_add примеры/pytest/test_solutions.py::test_subtract

# Запустить тесты, содержащие подстроку в имени
pytest примеры/pytest/test_solutions.py -k "add or subtract"

# Запустить тесты из test_solutions.py с подробным выводом
pytest примеры/pytest/test_solutions.py -v

# Запустить тесты из test_solutions.py и остановиться на первой ошибке
pytest примеры/pytest/test_solutions.py -x

# Или из самой директории pytest
cd примеры/pytest
pytest test_solutions.py
pytest test_solutions.py::test_add
```

### Запуск тестов по маркерам

Все доступные маркеры определены в `pytest.ini`:
- `fast` - быстрые тесты
- `slow` - медленные тесты
- `integration` - интеграционные тесты
- `unit` - юнит тесты
- `e2e` - end-to-end тесты

```bash
# Запустить только быстрые тесты
pytest -m fast

# Запустить только медленные тесты
pytest -m slow

# Исключить медленные тесты
pytest -m "not slow"

# Запустить интеграционные тесты
pytest -m integration

# Комбинация: быстрые тесты из test_solutions.py
pytest примеры/pytest/test_solutions.py -m fast

# Комбинация: все тесты кроме медленных из test_solutions.py
pytest примеры/pytest/test_solutions.py -m "not slow"
```

### Дополнительные опции

```bash
# Запустить с подробным выводом
pytest -v

# Запустить с очень подробным выводом
pytest -vv

# Показать print-выводы в тестах
pytest -s

# Запустить с покрытием кода
pytest --cov=задания --cov-report=html

# Запустить только последние упавшие тесты
pytest --lf

# Запустить с остановкой на первой ошибке
pytest -x

# Запустить с остановкой после N ошибок
pytest --maxfail=3
```

### Примеры комбинаций для test_solutions.py

```bash
# Запустить все тесты из test_solutions.py с подробным выводом и остановкой на первой ошибке
pytest примеры/pytest/test_solutions.py -v -x

# Запустить только тесты, содержащие "calculator" в имени
pytest примеры/pytest/test_solutions.py -k calculator

# Запустить тесты из test_solutions.py и показать print-выводы
pytest примеры/pytest/test_solutions.py -s -v
```

## Требования

- Python 3.7+
- pytest
- pytest-cov (опционально, для покрытия кода)

## Установка зависимостей

```bash
pip install pytest pytest-cov
```
