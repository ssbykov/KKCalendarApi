# syntax=docker/dockerfile:1.4

# Этап сборки
FROM python:3.11-slim as builder

# 2. Установка Poetry
ENV POETRY_VERSION=2.1.2 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -sf /opt/poetry/bin/poetry /usr/local/bin/poetry

# 3. Установка зависимостей
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-ansi

# Финальный образ
FROM python:3.11-slim

# 1. Установка Node.js (без dev-зависимостей)
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -sL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 1. Установка PostgreSQL Client
RUN apt-get update && \
    apt-get install -y curl gnupg2 lsb-release && \
    echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    apt-get update && \
    apt-get install -y postgresql-client-16 && \
    rm -rf /var/lib/apt/lists/*

    # Очистка
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    # Проверка установки Node.js
    node -v && npm -v

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