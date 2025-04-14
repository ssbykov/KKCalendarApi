# syntax=docker/dockerfile:1.4

# Этап сборки
FROM python:3.11-slim as builder

# 1. Установка системных зависимостей
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# 2. Установка Node.js
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl ca-certificates gnupg && \
    curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /usr/share/keyrings/nodesource.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" > /etc/apt/sources.list.d/nodesource.list && \
    apt-get update && \
    apt-get install -y nodejs && \
    npm install -g npm@latest && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 3. Установка Poetry
ENV POETRY_VERSION=2.1.2 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    /opt/poetry/bin/poetry --version

# 4. Установка зависимостей
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN /opt/poetry/bin/poetry install --only main --no-root --no-ansi

# Финальный образ
FROM python:3.11-slim

# 1. Установка PostgreSQL Client
RUN apt-get update && \
    apt-get install -y curl gnupg2 lsb-release && \
    echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    apt-get update && \
    apt-get install -y postgresql-client-16 && \
    rm -rf /var/lib/apt/lists/*

# 2. Копирование зависимостей
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 3. Копирование кода приложения
COPY . .

# 4. Настройка окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    NODE_ENV=production

# 5. Запуск приложения
CMD ["bash", "-c", "cd ./app && alembic upgrade head && python -m app.main"]