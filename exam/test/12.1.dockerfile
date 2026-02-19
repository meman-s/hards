FROM python:3.9-slim as builder

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.9-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

CMD ["python", "main.py"]


























FROM python:3.9 as builder

WORKDIR /app

COPY requirements.txt .

RUN --mount=type=secret,id=api_key \
    API_KEY=${cat /secret/api_key} \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.9 as runtime

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
CMD ["python", "main.py"]

