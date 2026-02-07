# SQLAlchemy / Alembic: ORM и Миграции

## 1. Зачем нужны

**SQLAlchemy** — ORM (Object-Relational Mapping) для Python, позволяющая работать с БД через объекты Python вместо SQL.

**Alembic** — инструмент для миграций БД, создающий версионированные изменения схемы.

Преимущества:
- Работа с БД через Python-объекты
- Автоматическая генерация SQL
- Миграции схемы БД
- Поддержка множества БД
- Типобезопасность

---

## 2. SQLAlchemy: Базовое использование

### 2.1 Подключение к БД

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///example.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### 2.2 Определение моделей

```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    
    author = relationship("User", back_populates="posts")
```

### 2.3 Создание таблиц

```python
Base.metadata.create_all(bind=engine)
```

### 2.4 Работа с сессиями

```python
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db = SessionLocal()
user = User(name="John", email="john@example.com")
db.add(user)
db.commit()
db.refresh(user)
```

---

## 3. CRUD операции

### 3.1 Create

```python
def create_user(db: Session, name: str, email: str):
    user = User(name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

### 3.2 Read

```python
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()
```

### 3.3 Update

```python
def update_user(db: Session, user_id: int, name: str = None, email: str = None):
    user = db.query(User).filter(User.id == user_id).first()
    if name:
        user.name = name
    if email:
        user.email = email
    db.commit()
    db.refresh(user)
    return user
```

### 3.4 Delete

```python
def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(user)
    db.commit()
    return user
```

---

## 4. Запросы

### 4.1 Фильтрация

```python
from sqlalchemy import and_, or_

users = db.query(User).filter(User.name == "John").all()
users = db.query(User).filter(User.age > 18).all()
users = db.query(User).filter(
    and_(User.age > 18, User.email.like("%@example.com"))
).all()
users = db.query(User).filter(
    or_(User.name == "John", User.name == "Jane")
).all()
```

### 4.2 Сортировка

```python
users = db.query(User).order_by(User.name).all()
users = db.query(User).order_by(User.created_at.desc()).all()
```

### 4.3 Join

```python
posts = db.query(Post).join(User).filter(User.name == "John").all()
posts = db.query(Post, User).join(User).all()
```

### 4.4 Агрегация

```python
from sqlalchemy import func

count = db.query(func.count(User.id)).scalar()
avg_age = db.query(func.avg(User.age)).scalar()
```

### 4.5 Подзапросы

```python
subquery = db.query(Post.author_id).filter(Post.title.like("%Python%")).subquery()
users = db.query(User).filter(User.id.in_(subquery)).all()
```

---

## 5. Relationships

### 5.1 One-to-Many

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
```

### 5.2 Many-to-Many

```python
from sqlalchemy import Table, Column, Integer, ForeignKey

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id")),
    Column("tag_id", Integer, ForeignKey("tags.id"))
)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    posts = relationship("Post", secondary=post_tags, back_populates="tags")
```

### 5.3 One-to-One

```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    profile = relationship("Profile", back_populates="user", uselist=False)

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    user = relationship("User", back_populates="profile")
```

---

## 6. Типы данных

### 6.1 Базовые типы

```python
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text
from datetime import datetime

class User(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    balance = Column(Float)
    bio = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 6.2 JSON

```python
from sqlalchemy import Column, JSON

class User(Base):
    id = Column(Integer, primary_key=True)
    metadata = Column(JSON)
```

### 6.3 Enum

```python
from sqlalchemy import Column, Enum
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class User(Base):
    id = Column(Integer, primary_key=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
```

---

## 7. Alembic: Миграции

### 7.1 Инициализация

```bash
alembic init alembic
```

### 7.2 Конфигурация (alembic.ini)

```ini
sqlalchemy.url = sqlite:///example.db
```

### 7.3 Создание миграции

```bash
alembic revision --autogenerate -m "create users table"
```

### 7.4 Применение миграций

```bash
alembic upgrade head
alembic upgrade +1
alembic upgrade <revision>
```

### 7.5 Откат миграций

```bash
alembic downgrade -1
alembic downgrade <revision>
alembic downgrade base
```

---

## 8. Структура миграций

### 8.1 Пример миграции

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
```

### 8.2 Добавление колонки

```python
def upgrade():
    op.add_column('users', sa.Column('age', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('users', 'age')
```

### 8.3 Изменение колонки

```python
def upgrade():
    op.alter_column('users', 'name',
                    existing_type=sa.String(),
                    type_=sa.String(100),
                    nullable=False)

def downgrade():
    op.alter_column('users', 'name',
                    existing_type=sa.String(100),
                    type_=sa.String(),
                    nullable=True)
```

---

## 9. Интеграция с FastAPI

### 9.1 Dependency для БД

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)
    return user
```

### 9.2 CRUD endpoints

```python
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/")
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(User).offset(skip).limit(limit).all()
    return users
```

---

## 10. Продвинутые техники

### 10.1 Hybrid properties

```python
from sqlalchemy.ext.hybrid import hybrid_property

class User(Base):
    first_name = Column(String)
    last_name = Column(String)
    
    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
```

### 10.2 Events

```python
from sqlalchemy import event

@event.listens_for(User, 'before_insert')
def receive_before_insert(mapper, connection, target):
    target.created_at = datetime.utcnow()
```

### 10.3 Query events

```python
@event.listens_for(Session, 'before_flush')
def receive_before_flush(session, flush_context, instances):
    for obj in session.new:
        if isinstance(obj, User):
            obj.updated_at = datetime.utcnow()
```

### 10.4 Scoped sessions

```python
from sqlalchemy.orm import scoped_session, sessionmaker

Session = scoped_session(sessionmaker(bind=engine))
```

---

## 11. Best Practices

### 11.1 Структура проекта

```
project/
  models/
    __init__.py
    user.py
    post.py
  database.py
  alembic/
    versions/
```

### 11.2 Разделение моделей и схем

```python
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    class Config:
        from_attributes = True
```

### 11.3 Использование транзакций

```python
def create_user_with_posts(db: Session, user_data: dict, posts_data: list):
    try:
        user = User(**user_data)
        db.add(user)
        db.flush()
        
        for post_data in posts_data:
            post = Post(**post_data, author_id=user.id)
            db.add(post)
        
        db.commit()
        return user
    except Exception:
        db.rollback()
        raise
```

### 11.4 Lazy loading vs Eager loading

```python
posts = db.query(Post).options(joinedload(Post.author)).all()
posts = db.query(Post).options(selectinload(Post.author)).all()
```
