# Моки vs Реальные запросы в тестах

## Текущий тест (с моками)

```python
@patch('test_tasks.requests.post')
def test_api_client_post(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "name": "Test"}
    mock_post.return_value = mock_response
    
    client = APIClient("https://api.example.com")
    result = client.post("users", {"name": "Test"})
    
    assert result == {"id": 1, "name": "Test"}
    mock_post.assert_called_once()
```

**Тип теста:** Юнит-тест / Интеграционный тест с моками

## Тест с реальными запросами

```python
@pytest.mark.integration
def test_api_client_post_real_request(api_client):
    user_data = {"name": "Test User", "email": "test@example.com"}
    result = api_client.post("users", user_data)
    
    assert "id" in result
    assert result["name"] == user_data["name"]
```

**Тип теста:** Интеграционный тест (межсервисный)

## Ключевые различия

### 1. Что тестируется

**С моками:**
- Логика формирования запроса (URL, параметры)
- Обработка ответа (raise_for_status, json())
- Правильность возврата данных
- НЕ тестируется реальное взаимодействие с сервисом

**С реальными запросами:**
- Всё то же самое +
- Реальное HTTP-взаимодействие
- Реальная обработка ошибок сети
- Реальная сериализация/десериализация
- Реальная работа сервера

### 2. Требования

**С моками:**
- ✅ Не требует запущенного сервиса
- ✅ Работает офлайн
- ✅ Быстро выполняется
- ✅ Стабильно (нет зависимости от сети)

**С реальными запросами:**
- ❌ Требует запущенный сервис
- ❌ Требует сеть (или локальный сервер)
- ❌ Медленнее
- ❌ Может быть нестабильным (сеть, сервер)

### 3. Что может сломаться

**С моками:**
- Не обнаружит проблемы с реальным API
- Не обнаружит проблемы с сетью
- Не обнаружит проблемы с форматом данных

**С реальными запросами:**
- Обнаружит все проблемы реального взаимодействия
- Но может упасть из-за проблем инфраструктуры

## Когда использовать каждый подход

### Используйте моки когда:

1. **Быстрые юнит-тесты** - нужно проверить логику быстро
2. **CI/CD пайплайны** - не хотите зависимость от внешних сервисов
3. **Разработка** - сервис еще не готов или недоступен
4. **Изоляция** - нужно тестировать только ваш код

### Используйте реальные запросы когда:

1. **Интеграционные тесты** - нужно проверить взаимодействие сервисов
2. **Тестовый стенд** - есть выделенное окружение для тестов
3. **E2E тесты** - проверка полного потока
4. **Регрессионное тестирование** - проверка совместимости API

## Пирамида тестирования

```
        /\
       /E2E\          ← Мало, медленные, реальные запросы
      /------\
     /Integration\    ← Средне, реальные запросы между сервисами
    /------------\
   /   Unit Tests  \  ← Много, быстрые, с моками
  /------------------\
```

## Пример: Два микросервиса

### Сервис A (User Service)
```python
# user_service.py
class UserService:
    def create_user(self, name, email):
        # Создает пользователя в БД
        pass
```

### Сервис B (Notification Service)
```python
# notification_service.py
class NotificationService:
    def __init__(self, user_service_client):
        self.user_service = user_service_client
    
    def send_welcome_email(self, user_id):
        user = self.user_service.get(f"users/{user_id}")  # ← Реальный запрос!
        # Отправляет email
```

### Тест с моками
```python
@patch('notification_service.user_service_client.get')
def test_send_welcome_email(mock_get):
    mock_get.return_value = {"id": 1, "name": "Test"}
    
    service = NotificationService(mock_user_service)
    service.send_welcome_email(1)
    
    # Проверяем логику, но НЕ реальное взаимодействие
```

### Интеграционный тест с реальными запросами
```python
@pytest.mark.integration
def test_send_welcome_email_real():
    # Оба сервиса запущены
    user_service = APIClient("http://user-service:8000")
    notification_service = NotificationService(user_service)
    
    # Создаем реального пользователя
    user = user_service.post("users", {"name": "Test", "email": "test@test.com"})
    
    # Отправляем email (реальный запрос между сервисами)
    notification_service.send_welcome_email(user["id"])
    
    # Проверяем, что email действительно отправлен
    emails = get_test_emails()
    assert len(emails) == 1
```

## Лучшие практики

1. **Больше юнит-тестов с моками** - быстрые, стабильные
2. **Меньше интеграционных тестов** - проверяют реальное взаимодействие
3. **E2E тесты для критичных сценариев** - полный поток
4. **Используйте тестовые окружения** - не тестируйте на продакшене!

## Итог

- **Текущий тест (с моками)** - проверяет правильность кода клиента
- **Тест с реальными запросами** - проверяет реальное взаимодействие между микросервисами

Оба подхода важны и дополняют друг друга!
