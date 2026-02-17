# MongoDB: запуск MongoDB в Docker одной командой + запуск Python файлов

Теория и задачи лежат рядом:
- `теория.md`
- `задания.md`
- `ответы.md`

## 1) Запуск MongoDB одной командой (без compose)

```bash
docker run -d --name exam_mongo --restart unless-stopped -p 27017:27017 -v exam_mongo_data:/data/db mongo:7
```

Проверка:

```bash
docker ps --filter name=exam_mongo
```

## 2) Запуск Python файлов

Один раз установи зависимости:

```bash
cd /home/meman-s/Загрузки/rumicon/hards/exam/09-базы-данных/теория/mongodb
python -m pip install pymongo
```

### Вариант A: запускать файл целиком

```bash
python mongodb_example.py
```

### Вариант B: запускать конкретную функцию без правки файла

```bash
python -c "from mongodb_example import task_1_basic_queries; task_1_basic_queries()"
python -c "from mongodb_example import task_2_aggregations; task_2_aggregations()"
python -c "from mongodb_example import task_3_lookup; task_3_lookup()"
python -c "from mongodb_example import task_4_indexes; task_4_indexes()"
```

### Вариант C: тренажер заданий (твои решения)

Сначала можно посмотреть список заданий:

```bash
python mongodb_my_tasks.py list
```

Запуск задания по номеру автоматически делает `seed` перед запуском:

```bash
python mongodb_my_tasks.py 1
python mongodb_my_tasks.py 2
python mongodb_my_tasks.py 3
python mongodb_my_tasks.py 4
python mongodb_my_tasks.py 5
```

## Остановка MongoDB

```bash
docker rm -f exam_mongo
```
