# Работа с файлами: загрузка, хранение, обработка

## 1. Зачем нужно

**Работа с файлами включает:**

- Загрузку файлов от пользователей
- Хранение файлов (локально или в облаке)
- Обработку файлов (изменение размера, конвертация)
- Валидацию типов и размеров
- Безопасное хранение и доступ

**Основные задачи:**
- Приём файлов через HTTP (multipart/form-data)
- Сохранение на диск или в облачное хранилище
- Обработка (ресайз изображений, конвертация форматов)
- Валидация (тип, размер, содержимое)
- Безопасность (санитизация имён, проверка на вирусы)
- Отдача файлов клиентам

---

## 2. Загрузка файлов

**Процесс загрузки:**
- Клиент отправляет файл через HTTP POST с `Content-Type: multipart/form-data`
- Сервер получает поток данных (stream)
- Сохранение в буфер или сразу на диск
- Методы: `read()`, `read(chunk_size)`, `copyfileobj()`

**Типы загрузки:**
- Одиночный файл
- Множественные файлы
- Файл + метаданные (form-data)

### 2.1 Базовая загрузка

**Основные операции:**
- Получение файла из запроса
- Чтение потока данных
- Сохранение на диск через `open()` в режиме `wb` (write binary)
- Использование `shutil.copyfileobj()` для эффективного копирования

```python
from fastapi import FastAPI, UploadFile, File
import shutil

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    with open(f"uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}
```

### 2.2 Множественная загрузка

**Множественная загрузка:**
- Клиент отправляет несколько файлов в одном запросе
- Сервер обрабатывает список файлов
- Каждый файл сохраняется отдельно
- Возвращается список загруженных имён

```python
from fastapi import FastAPI, UploadFile, File
from typing import List

app = FastAPI()

@app.post("/upload-multiple/")
async def upload_files(files: List[UploadFile] = File(...)):
    filenames = []
    for file in files:
        with open(f"uploads/{file.filename}", "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        filenames.append(file.filename)
    return {"filenames": filenames}
```

### 2.3 Загрузка с метаданными

**Метаданные:**
- Дополнительная информация о файле (описание, категория)
- Передаются через form-data вместе с файлом
- Сохраняются в БД или вместе с файлом
- Используются для организации и поиска файлов

```python
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel

app = FastAPI()

@app.post("/upload-with-metadata/")
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form(...),
    category: str = Form(...)
):
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "filename": file.filename,
        "description": description,
        "category": category,
        "size": file.size,
        "content_type": file.content_type
    }
```

### 2.4 Валидация типа файла

**Валидация:**
- Проверка расширения файла (`.jpg`, `.png`, `.pdf`)
- Проверка размера файла (максимальный лимит)
- Проверка MIME-типа (более надёжно)
- Проверка по содержимому (magic bytes)

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
import os

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024

def validate_file(file: UploadFile):
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed"
        )
    
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large"
        )

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    validate_file(file)
    
    with open(f"uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename}
```

---

## 3. Хранение файлов

**Стратегии хранения:**
- **Локальное** — на диске сервера (просто, но не масштабируется)
- **Облачное** — S3, MinIO, Azure Blob, Google Cloud Storage
- **CDN** — для статических файлов (быстрая отдача)

**Организация файлов:**
- Уникальные имена (UUID) — избегает конфликтов
- По датам (2024/01/) — удобно для бэкапов
- По типам (images/, documents/) — логическая организация
- Хеширование — распределение по подпапкам

### 3.1 Локальное хранение

**Особенности:**
- Простота реализации
- Быстрый доступ
- Проблемы: масштабирование, бэкапы, отказоустойчивость
- Генерация уникальных имён через UUID
- Использование `pathlib.Path` для работы с путями

```python
from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import uuid
import os

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

app = FastAPI()

def generate_unique_filename(original_filename: str) -> str:
    ext = os.path.splitext(original_filename)[1]
    return f"{uuid.uuid4()}{ext}"

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    unique_filename = generate_unique_filename(file.filename)
    file_path = UPLOAD_DIR / unique_filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "filename": unique_filename,
        "original_filename": file.filename,
        "path": str(file_path)
    }
```

### 3.2 Организация по датам

**Организация по датам:**
- Структура: `YYYY/MM/` или `YYYY/MM/DD/`
- Преимущества: удобные бэкапы, очистка старых файлов
- Автоматическое создание директорий через `mkdir(parents=True)`

```python
from datetime import datetime
from pathlib import Path

def get_upload_path(filename: str) -> Path:
    today = datetime.now()
    year_month = today.strftime("%Y/%m")
    upload_path = UPLOAD_DIR / year_month
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path / filename

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    unique_filename = generate_unique_filename(file.filename)
    file_path = get_upload_path(unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"path": str(file_path)}
```

### 3.3 Хранение в S3 (boto3)

**Amazon S3:**
- Объектное хранилище (Object Storage)
- Методы: `upload_fileobj()`, `download_fileobj()`, `generate_presigned_url()`
- Presigned URLs — временные ссылки для доступа
- Масштабируемость, репликация, версионирование

```python
import boto3
from fastapi import FastAPI, UploadFile, File

s3_client = boto3.client('s3')
BUCKET_NAME = "my-bucket"

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    
    s3_client.upload_fileobj(
        file.file,
        BUCKET_NAME,
        unique_filename,
        ExtraArgs={"ContentType": file.content_type}
    )
    
    url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': unique_filename},
        ExpiresIn=3600
    )
    
    return {"filename": unique_filename, "url": url}
```

### 3.4 Хранение в облаке (MinIO)

**MinIO:**
- S3-совместимое хранилище (можно использовать локально)
- API совместим с S3
- Методы: `put_object()`, `get_object()`, `remove_object()`
- Подходит для разработки и продакшена

```python
from minio import Minio
from fastapi import FastAPI, UploadFile, File

minio_client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)
BUCKET_NAME = "uploads"

app = FastAPI()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    
    minio_client.put_object(
        BUCKET_NAME,
        unique_filename,
        file.file,
        length=file.size,
        content_type=file.content_type
    )
    
    return {"filename": unique_filename}
```

---

## 4. Обработка файлов

**Типы обработки:**
- **Изображения:** ресайз, обрезка, конвертация форматов, сжатие
- **PDF:** извлечение текста, объединение, разделение
- **Видео:** конвертация, обрезка, сжатие
- **Документы:** парсинг, конвертация (DOCX → PDF)

**Библиотеки:**
- **Pillow (PIL)** — работа с изображениями
- **PyPDF2/pdfplumber** — работа с PDF
- **moviepy/ffmpeg** — обработка видео
- **python-magic** — определение типа файла

### 4.1 Обработка изображений (Pillow)

**Операции:**
- `Image.open()` — открытие из bytes или файла
- `thumbnail()` — создание миниатюры с сохранением пропорций
- `resize()` — изменение размера
- `save()` — сохранение в нужном формате
- Работа через `BytesIO` для обработки в памяти

```python
from PIL import Image
from fastapi import FastAPI, UploadFile, File
import io

app = FastAPI()

@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    image.thumbnail((800, 800))
    
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=85)
    output.seek(0)
    
    with open(f"uploads/thumb_{file.filename}", "wb") as f:
        f.write(output.getvalue())
    
    return {"message": "Image processed"}
```

### 4.2 Изменение размера изображения

**Ресайз изображений:**
- Методы: `resize()`, `thumbnail()`
- Алгоритмы: LANCZOS, BICUBIC, NEAREST
- Сохранение пропорций или принудительный размер
- Качество сжатия (quality для JPEG)

```python
from PIL import Image
import io

def resize_image(image_data: bytes, width: int, height: int) -> bytes:
    image = Image.open(io.BytesIO(image_data))
    image = image.resize((width, height), Image.Resampling.LANCZOS)
    
    output = io.BytesIO()
    image.save(output, format="JPEG")
    return output.getvalue()

@app.post("/resize-image/")
async def resize_image_endpoint(
    file: UploadFile = File(...),
    width: int = 800,
    height: int = 600
):
    contents = await file.read()
    resized = resize_image(contents, width, height)
    
    output_filename = f"resized_{file.filename}"
    with open(f"uploads/{output_filename}", "wb") as f:
        f.write(resized)
    
    return {"filename": output_filename}
```

### 4.3 Конвертация форматов

**Конвертация:**
- JPEG ↔ PNG ↔ GIF ↔ WebP
- Учёт цветовых режимов (RGB, RGBA)
- RGBA → RGB при конвертации в JPEG (удаление альфа-канала)
- Сохранение через `save(format=...)`

```python
from PIL import Image
import io

def convert_image(image_data: bytes, output_format: str) -> bytes:
    image = Image.open(io.BytesIO(image_data))
    
    if image.mode == "RGBA" and output_format.upper() == "JPEG":
        image = image.convert("RGB")
    
    output = io.BytesIO()
    image.save(output, format=output_format)
    return output.getvalue()

@app.post("/convert-image/")
async def convert_image_endpoint(
    file: UploadFile = File(...),
    format: str = "PNG"
):
    contents = await file.read()
    converted = convert_image(contents, format)
    
    output_filename = f"converted_{file.filename}.{format.lower()}"
    with open(f"uploads/{output_filename}", "wb") as f:
        f.write(converted)
    
    return {"filename": output_filename}
```

### 4.4 Обработка PDF

**Операции с PDF:**
- Чтение: `PdfReader()` — извлечение страниц, текста
- Запись: `PdfWriter()` — создание, объединение PDF
- Методы: `add_page()`, `write()`, `get_page()`
- Извлечение метаданных, количества страниц

```python
from PyPDF2 import PdfReader, PdfWriter
from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.post("/process-pdf/")
async def process_pdf(file: UploadFile = File(...)):
    reader = PdfReader(file.file)
    writer = PdfWriter()
    
    for page in reader.pages:
        writer.add_page(page)
    
    output_filename = f"processed_{file.filename}"
    with open(f"uploads/{output_filename}", "wb") as output_file:
        writer.write(output_file)
    
    return {
        "filename": output_filename,
        "pages": len(reader.pages)
    }
```

### 4.5 Обработка в фоне

**Асинхронная обработка:**
- Тяжёлые операции выполняются в фоне
- Клиент получает ответ сразу после загрузки
- Обработка через фоновые задачи или очереди (Celery, RQ)
- Улучшает UX для больших файлов

```python
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from PIL import Image
import io

app = FastAPI()

def process_image_async(file_path: str, filename: str):
    with open(file_path, "rb") as f:
        image = Image.open(f)
        image.thumbnail((800, 800))
        
        output_path = f"uploads/thumb_{filename}"
        image.save(output_path, format="JPEG")

@app.post("/upload-image/")
async def upload_image(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks
):
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    background_tasks.add_task(process_image_async, file_path, file.filename)
    
    return {"message": "Image uploaded, processing in background"}
```

---

## 5. Валидация файлов

**Методы валидации:**
- **По расширению** — быстро, но ненадёжно (можно подделать)
- **По MIME-типу** — из заголовка Content-Type (тоже можно подделать)
- **По содержимому** — magic bytes (первые байты файла) — самый надёжный
- **По размеру** — проверка лимитов

**Библиотеки:**
- `python-magic` — определение типа по содержимому
- `filetype` — определение типа файла
- Проверка magic bytes вручную

### 5.1 Проверка типа по содержимому

**Magic bytes:**
- Первые байты файла определяют его тип
- JPEG: `FF D8 FF`
- PNG: `89 50 4E 47`
- PDF: `25 50 44 46`
- `magic.from_buffer()` — определение MIME-типа

```python
import magic
from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI()

ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "application/pdf"]

def validate_file_type(file: UploadFile):
    contents = file.file.read()
    file.file.seek(0)
    
    mime_type = magic.from_buffer(contents, mime=True)
    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type {mime_type} not allowed"
        )

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    validate_file_type(file)
    
    with open(f"uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename}
```

### 5.2 Проверка размера

**Проверка размера:**
- Лимиты: максимальный размер файла
- Проверка до сохранения (экономия ресурсов)
- Разные лимиты для разных типов файлов
- `file.size` или `len(contents)` для проверки

```python
from fastapi import FastAPI, UploadFile, File, HTTPException

MAX_FILE_SIZE = 10 * 1024 * 1024

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE} bytes"
        )
    
    with open(f"uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename}
```

---

## 6. Безопасность

**Угрозы:**
- Path traversal (`../../../etc/passwd`) — доступ к системным файлам
- Перезапись существующих файлов
- Вредоносные файлы (вирусы, эксплойты)
- DoS через большие файлы

**Меры защиты:**
- Санитизация имён файлов
- Генерация уникальных имён
- Проверка на известные вредоносные хеши
- Ограничение размера и типов
- Изоляция загруженных файлов

### 6.1 Санитизация имени файла

**Санитизация:**
- Удаление опасных символов (`../`, `\`, `/`)
- Оставление только безопасных символов (буквы, цифры, дефис, подчёркивание)
- Нормализация (замена пробелов на дефисы)
- Удаление ведущих/конечных символов
- Использование regex для очистки

```python
import re
from pathlib import Path

def sanitize_filename(filename: str) -> str:
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.strip('-_')

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    safe_filename = sanitize_filename(file.filename)
    file_path = UPLOAD_DIR / safe_filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": safe_filename}
```

### 6.2 Проверка на вредоносные файлы

**Проверка на вредоносность:**
- Хеширование файла (SHA256, MD5)
- Сравнение с базой известных вредоносных хешей
- Сканирование антивирусом (ClamAV)
- Анализ содержимого (для исполняемых файлов)
- Sandbox для подозрительных файлов

```python
import hashlib
from fastapi import FastAPI, UploadFile, File

KNOWN_MALICIOUS_HASHES = set()

def check_file_hash(file_data: bytes) -> bool:
    file_hash = hashlib.sha256(file_data).hexdigest()
    return file_hash not in KNOWN_MALICIOUS_HASHES

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    
    if not check_file_hash(contents):
        raise HTTPException(status_code=400, detail="File blocked")
    
    with open(f"uploads/{file.filename}", "wb") as buffer:
        buffer.write(contents)
    
    return {"filename": file.filename}
```

---

## 7. Отдача файлов

**Способы отдачи:**
- **Статические файлы** — прямая отдача через веб-сервер
- **Через приложение** — контроль доступа, логирование
- **Стриминг** — для больших файлов (по частям)
- **Presigned URLs** — временные ссылки из облачного хранилища

**HTTP заголовки:**
- `Content-Type` — MIME-тип файла
- `Content-Disposition` — inline (просмотр) или attachment (скачивание)
- `Content-Length` — размер файла
- `Cache-Control` — кэширование

### 7.1 Отдача статических файлов

**Статическая отдача:**
- Прямая отдача файла через `FileResponse`
- Проверка существования файла
- Установка правильного Content-Type
- Быстрая отдача без обработки

```python
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()

@app.get("/files/{filename}")
async def get_file(filename: str):
    file_path = Path("uploads") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)
```

### 7.2 Скачивание файлов

**Скачивание:**
- `StreamingResponse` — потоковая отдача больших файлов
- `Content-Disposition: attachment` — принудительное скачивание
- Генератор для чтения файла по частям (экономия памяти)
- Поддержка Range-запросов для докачки

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pathlib import Path

app = FastAPI()

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = Path("uploads") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    def iterfile():
        with open(file_path, "rb") as f:
            yield from f
    
    return StreamingResponse(
        iterfile(),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

---

## 8. Best Practices

**Рекомендации:**
- Организованная структура директорий
- Очистка временных файлов
- Логирование операций
- Обработка ошибок
- Мониторинг использования диска

### 8.1 Структура проекта

**Организация:**
- `uploads/` — загруженные файлы
- `processed/` — обработанные файлы
- `temp/` — временные файлы
- Организация по датам/типам
- Отдельные директории для разных типов контента

```
project/
  uploads/
    2024/
      01/
      02/
  processed/
  temp/
```

### 8.2 Очистка временных файлов

**Очистка:**
- Удаление старых временных файлов по расписанию
- Проверка времени модификации (`st_mtime`)
- Cron-задачи или фоновые процессы
- Очистка после обработки

```python
from fastapi import FastAPI, BackgroundTasks
from datetime import datetime, timedelta
import os

def cleanup_temp_files():
    cutoff = datetime.now() - timedelta(hours=24)
    temp_dir = Path("temp")
    
    for file_path in temp_dir.iterdir():
        if file_path.stat().st_mtime < cutoff.timestamp():
            file_path.unlink()

@app.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(cleanup_temp_files)
    # ... загрузка файла
```

### 8.3 Логирование загрузок

**Логирование:**
- Запись всех операций с файлами
- Информация: имя, размер, тип, пользователь, время
- Отслеживание ошибок
- Аудит для безопасности
- Метрики использования хранилища

```python
import logging
from fastapi import FastAPI, UploadFile, File

logger = logging.getLogger(__name__)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Uploading file: {file.filename}, size: {file.size}")
    
    with open(f"uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    logger.info(f"File uploaded successfully: {file.filename}")
    return {"filename": file.filename}
```
