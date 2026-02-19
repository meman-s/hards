# syntax=docker/dockerfile:1
FROM python:3.9-slim as deps

WORKDIR /deps

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

RUN --mount=type=ssh \
    git clone git@github.com:org/private-repo.git .

FROM python:3.9-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=secret,id=api_key \
    API_KEY=$(cat /run/secrets/api_key) \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.9-slim as runtime

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=deps /deps ./private-repo
COPY . .

CMD ["python", "app.py"]


export DOCKER_BUILDKIT=1

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

docker build \
    --ssh default \
    --secret id=api_key,src=./api_key.txt \
    -t myapp:latest .