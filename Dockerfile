# syntax=docker/dockerfile:1.4

# Этап сборки
FROM python:3.11-slim as builder

# 1. Сначала устанавливаем curl и системные зависимости
RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

# 2. Установка Poetry
ENV POETRY_VERSION=2.1.2 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# 3. Установка зависимостей Python
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-ansi

# Финальный образ
FROM python:3.11-slim

# 1. Установка всех системных зависимостей в одном RUN (оптимизация слоев)
RUN apt-get update && \
    # Установка базовых утилит
    apt-get install -y curl gnupg2 lsb-release && \
    # Установка Node.js
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    # Установка PostgreSQL Client
    curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg && \
    echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    apt-get install -y postgresql-client-16 && \
    # Очистка
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    # Проверка установки
    node -v && npm -v

# 2. Копирование зависимостей Python
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