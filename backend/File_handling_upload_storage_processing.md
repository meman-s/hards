# Работа с файлами: загрузка, хранение, обработка

## 1. Зачем нужно

**Работа с файлами включает:**

- Загрузку файлов от пользователей
- Хранение файлов (локально или в облаке)
- Обработку файлов (изменение размера, конвертация)
- Валидацию типов и размеров
- Безопасное хранение и доступ

**Типичные задачи:**
- Загрузка изображений, документов, видео
- Обработка и преобразование файлов
- Организация хранения
- Контроль доступа к файлам

---

## 2. Работа с файлами в Python

### 2.1 Базовые операции

**Открытие файлов:**
- `open(filename, mode)` — открытие файла
- Режимы: `'r'` (чтение), `'w'` (запись), `'a'` (добавление), `'rb'` (бинарное чтение), `'wb'` (бинарная запись)
- Контекстный менеджер `with` — автоматическое закрытие

**Чтение файлов:**
- `read()` — весь файл
- `readline()` — одна строка
- `readlines()` — все строки в список
- `read(size)` — указанное количество байт

**Запись файлов:**
- `write(data)` — запись данных
- `writelines(lines)` — запись списка строк

```python
with open('file.txt', 'r') as f:
    content = f.read()

with open('file.txt', 'wb') as f:
    f.write(binary_data)
```

### 2.2 Работа с бинарными данными

**Байтовые объекты:**
- `bytes` — неизменяемая последовательность байт
- `bytearray` — изменяемая последовательность байт
- `io.BytesIO` — поток в памяти для работы с байтами

```python
import io

data = b'file content'
buffer = io.BytesIO(data)
content = buffer.read()
```

### 2.3 Копирование файлов

**Методы копирования:**
- `shutil.copyfileobj(src, dst)` — копирование объекта файла
- `shutil.copy(src, dst)` — копирование файла
- `shutil.copy2(src, dst)` — копирование с метаданными

```python
import shutil

with open('source.txt', 'rb') as src:
    with open('dest.txt', 'wb') as dst:
        shutil.copyfileobj(src, dst)
```

---

## 3. Валидация файлов

### 3.1 Проверка типа файла

**Методы проверки:**
- По расширению: `os.path.splitext(filename)[1]`
- По MIME-типу: библиотека `python-magic` или `mimetypes`
- По содержимому: проверка сигнатур файлов (magic bytes)

**Библиотеки:**
- `python-magic` — определение типа по содержимому
- `mimetypes` — стандартная библиотека для MIME-типов

```python
import os
import magic

def get_file_type(filename: str, content: bytes) -> str:
    ext = os.path.splitext(filename)[1].lower()
    mime = magic.from_buffer(content, mime=True)
    return mime
```

### 3.2 Проверка размера

**Методы:**
- `os.path.getsize(path)` — размер файла
- Проверка размера перед загрузкой
- Ограничение максимального размера

```python
import os

MAX_SIZE = 10 * 1024 * 1024  # 10 MB

file_size = os.path.getsize('file.txt')
if file_size > MAX_SIZE:
    raise ValueError("File too large")
```

### 3.3 Проверка содержимого

**Методы:**
- Проверка хеша файла (SHA256, MD5)
- Сравнение с базой известных вредоносных файлов
- Валидация структуры файла

```python
import hashlib

def get_file_hash(file_data: bytes) -> str:
    return hashlib.sha256(file_data).hexdigest()
```

---

## 4. Хранение файлов

### 4.1 Локальное хранение

**Организация:**
- Создание уникальных имён файлов (UUID)
- Организация по датам/категориям
- Использование `pathlib.Path` для работы с путями

**Структура:**
```
uploads/
  2024/
    01/
    02/
```

**Методы:**
- `Path.mkdir(parents=True, exist_ok=True)` — создание директорий
- `uuid.uuid4()` — генерация уникального имени
- `os.path.join()` или `Path / filename` — формирование пути

```python
from pathlib import Path
import uuid
import os

def save_file(content: bytes, original_name: str) -> str:
    ext = os.path.splitext(original_name)[1]
    unique_name = f"{uuid.uuid4()}{ext}"
    path = Path("uploads") / unique_name
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'wb') as f:
        f.write(content)
    
    return str(path)
```

### 4.2 Облачное хранение

**Варианты:**
- **AWS S3** — через `boto3`
- **MinIO** — S3-совместимое хранилище
- **Google Cloud Storage** — через `google-cloud-storage`
- **Azure Blob Storage** — через `azure-storage-blob`

**Преимущества:**
- Масштабируемость
- Резервное копирование
- CDN интеграция
- Управление доступом

**Основные операции:**
- `upload_fileobj()` — загрузка файла
- `download_fileobj()` — скачивание файла
- `generate_presigned_url()` — временная ссылка
- `delete_object()` — удаление файла

```python
import boto3

s3 = boto3.client('s3')

with open('file.txt', 'rb') as f:
    s3.upload_fileobj(f, 'bucket-name', 'key-name')
```

---

## 5. Обработка файлов

### 5.1 Обработка изображений (Pillow)

**Библиотека:** `PIL` (Pillow)

**Основные операции:**
- `Image.open()` — открытие изображения
- `resize()` — изменение размера
- `thumbnail()` — создание миниатюры
- `convert()` — конвертация формата
- `save()` — сохранение

**Форматы:**
- JPEG, PNG, GIF, BMP, TIFF, WebP

```python
from PIL import Image
import io

def resize_image(image_data: bytes, width: int, height: int) -> bytes:
    image = Image.open(io.BytesIO(image_data))
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    
    output = io.BytesIO()
    image.save(output, format='JPEG')
    return output.getvalue()
```

### 5.2 Обработка PDF

**Библиотеки:**
- `PyPDF2` / `pypdf` — чтение и запись PDF
- `pdfplumber` — извлечение текста и таблиц
- `reportlab` — создание PDF

**Операции:**
- Чтение страниц
- Объединение PDF
- Извлечение текста
- Добавление страниц

```python
from PyPDF2 import PdfReader, PdfWriter

reader = PdfReader('input.pdf')
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

with open('output.pdf', 'wb') as f:
    writer.write(f)
```

### 5.3 Обработка других форматов

**CSV:**
- `csv.reader()` / `csv.writer()` — стандартная библиотека
- `pandas.read_csv()` — для анализа данных

**JSON:**
- `json.load()` / `json.dump()` — стандартная библиотека

**Excel:**
- `openpyxl` — для .xlsx
- `xlrd` — для .xls

**Архивы:**
- `zipfile` — работа с ZIP
- `tarfile` — работа с TAR

---

## 6. Безопасность

### 6.1 Санитизация имён файлов

**Проблемы:**
- Путь-траверсал (`../../../etc/passwd`)
- Специальные символы
- Длинные имена

**Методы:**
- Удаление опасных символов
- Ограничение длины
- Использование UUID для имён
- Проверка пути на выход за пределы директории

```python
import re
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.strip('-_')

def safe_path(base_dir: Path, filename: str) -> Path:
    safe_name = sanitize_filename(filename)
    full_path = base_dir / safe_name
    if not full_path.resolve().is_relative_to(base_dir.resolve()):
        raise ValueError("Path traversal detected")
    return full_path
```

### 6.2 Защита от вредоносных файлов

**Методы:**
- Проверка хеша файла
- Сканирование антивирусом
- Ограничение типов файлов
- Проверка сигнатур (magic bytes)
- Изоляция обработки файлов

**Практики:**
- Хранение файлов вне web root
- Ограничение прав доступа
- Валидация перед обработкой
- Логирование подозрительных файлов

---

## 7. Оптимизация

### 7.1 Потоковая обработка

**Для больших файлов:**
- Чтение по частям (chunks)
- Потоковая запись
- Использование генераторов

```python
def read_file_in_chunks(file_path: str, chunk_size: int = 8192):
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk
```

### 7.2 Асинхронная обработка

**Методы:**
- Фоновые задачи (background tasks)
- Очереди задач (Celery, RQ)
- Асинхронная загрузка в облако

**Преимущества:**
- Не блокирует основной поток
- Параллельная обработка
- Масштабируемость

### 7.3 Кэширование

**Методы:**
- Кэширование обработанных файлов
- CDN для статических файлов
- Кэширование метаданных

---

## 8. Best Practices

### 8.1 Организация структуры

**Рекомендации:**
- Разделение на директории (uploads, processed, temp)
- Организация по датам/категориям
- Очистка временных файлов
- Резервное копирование

### 8.2 Обработка ошибок

**Важно:**
- Обработка исключений при работе с файлами
- Проверка существования файлов
- Валидация перед обработкой
- Логирование ошибок

### 8.3 Производительность

**Оптимизация:**
- Потоковая обработка больших файлов
- Асинхронная загрузка
- Кэширование результатов
- Использование облачного хранилища для масштабирования

### 8.4 Безопасность

**Правила:**
- Всегда валидировать файлы
- Санитизировать имена
- Ограничивать типы и размеры
- Хранить файлы вне web root
- Использовать уникальные имена
- Логировать операции

---

## 9. Полезные библиотеки

**Работа с файлами:**
- `pathlib` — современная работа с путями
- `shutil` — операции с файлами
- `tempfile` — временные файлы

**Обработка изображений:**
- `Pillow` (PIL) — обработка изображений
- `opencv-python` — компьютерное зрение

**Обработка документов:**
- `PyPDF2` / `pypdf` — PDF
- `python-docx` — Word документы
- `openpyxl` — Excel файлы

**Облачное хранилище:**
- `boto3` — AWS S3
- `minio` — MinIO
- `google-cloud-storage` — Google Cloud

**Валидация:**
- `python-magic` — определение типа файла
- `filetype` — определение типа по содержимому
