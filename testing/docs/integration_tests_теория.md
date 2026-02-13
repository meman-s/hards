# Интеграционные тесты

Интеграционные тесты проверяют взаимодействие между компонентами системы: модулями, сервисами, базой данных.

## Отличия от юнит тестов

- **Юнит тесты**: изолированные, быстрые, мокируют зависимости
- **Интеграционные тесты**: проверяют реальное взаимодействие, медленнее, используют реальные зависимости

## Типы интеграционных тестов

### Тестирование с базой данных

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="module")
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_user(db_session):
    user = User(name="Test", email="test@example.com")
    db_session.add(user)
    db_session.commit()
    
    found = db_session.query(User).filter_by(email="test@example.com").first()
    assert found.name == "Test"
```

### Тестирование API

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_item():
    response = client.post("/items/", json={"name": "Test"})
    assert response.status_code == 200
    assert response.json()["name"] == "Test"
```

### Тестирование с внешними сервисами

Использование тестовых двойников (test doubles):
- **Stub** - возвращает предопределенные данные
- **Mock** - проверяет вызовы
- **Fake** - упрощенная реализация

```python
import pytest
from unittest.mock import patch

@patch('module.external_service')
def test_with_external_service(mock_service):
    mock_service.get_data.return_value = {"result": "ok"}
    result = process_with_external_service()
    assert result["result"] == "ok"
```

## Тестовые данные

### Фикстуры для данных

```python
@pytest.fixture
def sample_users():
    return [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]

def test_user_processing(sample_users):
    result = process_users(sample_users)
    assert len(result) == 2
```

### Очистка после тестов

```python
@pytest.fixture
def clean_database():
    # Setup
    db.create_all()
    yield
    # Teardown
    db.drop_all()
```

## Тестирование транзакций

```python
@pytest.fixture
def db_transaction():
    connection = db.connect()
    transaction = connection.begin()
    yield connection
    transaction.rollback()
    connection.close()
```

## Параллельное выполнение

```bash
pytest -n auto  # используя pytest-xdist
```

## Изоляция тестов

- Каждый тест должен быть независимым
- Использовать транзакции с откатом
- Очищать данные после каждого теста
- Использовать уникальные идентификаторы
