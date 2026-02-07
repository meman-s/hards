# Работа с файлами: загрузка, хранение, обработка

## 1. Зачем нужно

Работа с файлами включает:

- Загрузку файлов от пользователей
- Хранение файлов (локально или в облаке)
- Обработку файлов (изменение размера, конвертация)
- Валидацию типов и размеров
- Безопасное хранение и доступ

---

## 2. Загрузка файлов

### 2.1 Базовая загрузка

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

### 3.1 Локальное хранение

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

### 4.1 Обработка изображений (Pillow)

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

### 5.1 Проверка типа по содержимому

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

### 6.1 Санитизация имени файла

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

### 7.1 Отдача статических файлов

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

### 8.1 Структура проекта

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
