# Pydantic: Валидация и Сериализация

## 1. Зачем нужен

**Pydantic** — библиотека для валидации данных и сериализации на основе аннотаций типов Python.

Основные возможности:
- Автоматическая валидация на основе типов
- Сериализация в JSON и другие форматы
- Валидаторы и кастомные типы
- Интеграция с FastAPI
- Производительность (написано на Rust)

---

## 2. Базовое использование

### 2.1 Простая модель

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    age: int = 18

user = User(id=1, name="John", email="john@example.com")
print(user.model_dump())
print(user.model_dump_json())
```

### 2.2 Валидация при создании

```python
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    id: int
    name: str
    age: int

try:
    user = User(id="1", name="John", age="25")
except ValidationError as e:
    print(e.json())
```

### 2.3 Обязательные и опциональные поля

```python
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    age: int = 18
```

---

## 3. Валидаторы

### 3.1 Field с ограничениями

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: int = Field(ge=0, le=150)
    score: float = Field(ge=0.0, le=100.0)
```

### 3.2 @field_validator

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    email: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()
```

### 3.3 @model_validator

```python
from pydantic import BaseModel, model_validator

class User(BaseModel):
    password: str
    password_confirm: str
    
    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self
```

### 3.4 Валидация нескольких полей

```python
from pydantic import BaseModel, field_validator

class Product(BaseModel):
    price: float
    discount: float
    
    @field_validator('discount')
    @classmethod
    def validate_discount(cls, v: float, info) -> float:
        price = info.data.get('price', 0)
        if v > price:
            raise ValueError('Discount cannot exceed price')
        return v
```

---

## 4. Кастомные типы

### 4.1 EmailStr, HttpUrl

```python
from pydantic import BaseModel, EmailStr, HttpUrl

class User(BaseModel):
    email: EmailStr
    website: HttpUrl
```

### 4.2 Создание кастомных типов

```python
from pydantic import BaseModel, field_validator
from typing import Annotated

class PhoneNumber(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
        )
    
    @classmethod
    def validate(cls, v: str) -> str:
        if not v.startswith('+'):
            raise ValueError('Phone must start with +')
        return v

class User(BaseModel):
    phone: PhoneNumber
```

### 4.3 Enum

```python
from pydantic import BaseModel
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class User(BaseModel):
    name: str
    role: UserRole
```

---

## 5. Сериализация

### 5.1 model_dump()

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

user = User(id=1, name="John", email="john@example.com")
print(user.model_dump())
print(user.model_dump(exclude={'email'}))
print(user.model_dump(include={'id', 'name'}))
print(user.model_dump(mode='json'))
```

### 5.2 model_dump_json()

```python
user = User(id=1, name="John", email="john@example.com")
json_str = user.model_dump_json()
json_str_indented = user.model_dump_json(indent=2)
json_str_exclude = user.model_dump_json(exclude={'email'})
```

### 5.3 Сериализация с alias

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    user_id: int = Field(alias='id')
    user_name: str = Field(alias='name')
    
    class Config:
        populate_by_name = True

user = User(id=1, name="John")
print(user.model_dump(by_alias=True))
print(user.model_dump(by_alias=False))
```

### 5.4 Сериализация вложенных моделей

```python
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    street: str
    city: str

class User(BaseModel):
    id: int
    name: str
    addresses: List[Address]

user = User(
    id=1,
    name="John",
    addresses=[
        Address(street="123 Main St", city="NYC"),
        Address(street="456 Oak Ave", city="LA")
    ]
)
print(user.model_dump_json())
```

---

## 6. Конфигурация моделей

### 6.1 ConfigDict (Pydantic v2)

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        frozen=True,
        extra='forbid'
    )
    
    id: int
    name: str
```

### 6.2 Допустимые настройки

```python
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        extra='forbid',
        json_encoders={datetime: lambda v: v.isoformat()},
        populate_by_name=True
    )
```

---

## 7. Работа с JSON

### 7.1 Парсинг из JSON

```python
from pydantic import BaseModel
import json

class User(BaseModel):
    id: int
    name: str

json_data = '{"id": 1, "name": "John"}'
user = User.model_validate_json(json_data)
```

### 7.2 Парсинг из словаря

```python
data = {"id": 1, "name": "John"}
user = User.model_validate(data)
```

### 7.3 Обработка невалидных данных

```python
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    id: int
    name: str

try:
    user = User.model_validate({"id": "invalid", "name": "John"})
except ValidationError as e:
    print(e.errors())
    print(e.json())
```

---

## 8. Продвинутые техники

### 8.1 Generic модели

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    status: str
    data: T

user_response = Response[User](status="ok", data=User(id=1, name="John"))
```

### 8.2 Union типы

```python
from pydantic import BaseModel
from typing import Union

class Cat(BaseModel):
    type: str = "cat"
    meow: bool = True

class Dog(BaseModel):
    type: str = "dog"
    bark: bool = True

Pet = Union[Cat, Dog]

pet1 = Pet.model_validate({"type": "cat", "meow": True})
pet2 = Pet.model_validate({"type": "dog", "bark": True})
```

### 8.3 Discriminated Union

```python
from pydantic import BaseModel, Field

class Cat(BaseModel):
    type: str = Field("cat", discriminator=True)
    meow: bool = True

class Dog(BaseModel):
    type: str = Field("dog", discriminator=True)
    bark: bool = True

Pet = Union[Cat, Dog]
```

### 8.4 Computed fields

```python
from pydantic import BaseModel, computed_field

class Rectangle(BaseModel):
    width: float
    height: float
    
    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height
```

### 8.5 Private attributes

```python
from pydantic import BaseModel, PrivateAttr

class User(BaseModel):
    id: int
    name: str
    _password: PrivateAttr(str)
    
    def __init__(self, **data):
        super().__init__(**data)
        self._password = data.get('password', '')
```

---

## 9. Интеграция с FastAPI

### 9.1 Request/Response модели

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate):
    return UserResponse(id=1, **user.model_dump())
```

### 9.2 Валидация query параметров

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel

class PaginationParams(BaseModel):
    skip: int = Query(0, ge=0)
    limit: int = Query(10, ge=1, le=100)

@app.get("/items/")
def get_items(params: PaginationParams = Depends()):
    return {"skip": params.skip, "limit": params.limit}
```

---

## 10. Производительность

### 10.1 model_validate vs parse_obj

```python
user = User.model_validate(data)
user = User(**data)
```

### 10.2 Кэширование схем

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

schema = User.model_json_schema()
```

### 10.3 Использование model_serializer

```python
from pydantic import BaseModel, model_serializer

class User(BaseModel):
    id: int
    name: str
    
    @model_serializer
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name.upper()
        }
```

---

## 11. Best Practices

### 11.1 Разделение моделей

```python
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None

class UserResponse(UserBase):
    id: int
```

### 11.2 Валидация в отдельном слое

```python
class UserService:
    def create_user(self, user_data: UserCreate) -> UserResponse:
        validated = UserCreate.model_validate(user_data)
        return UserResponse(id=1, **validated.model_dump())
```

### 11.3 Обработка ошибок

```python
from pydantic import ValidationError

try:
    user = User.model_validate(invalid_data)
except ValidationError as e:
    for error in e.errors():
        print(f"{error['loc']}: {error['msg']}")
```
