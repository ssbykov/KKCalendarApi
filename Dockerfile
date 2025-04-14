# syntax=docker/dockerfile:1.4

# Этап сборки
FROM python:3.11-slim as builder

# 1. Системные зависимости + Node.js + Poetry
RUN apt-get update && \
    apt-get install -y curl wget gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g npm@9 && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    /opt/poetry/bin/poetry --version && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Установка зависимостей
ENV POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    PATH="${PATH}:/opt/poetry/bin"

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root --no-ansi

# Финальный образ
FROM python:3.11-slim

# 1. Установка PostgreSQL client + Node.js
RUN apt-get update && \
    apt-get install -y curl gnupg2 lsb-release wget && \
    echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get update && \
    apt-get install -y postgresql-client-16 nodejs && \
    npm install -g npm@9 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 2. Копирование Python-зависимостей
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 3. Копирование исходного кода
COPY . .

# 4. Настройка окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    NODE_ENV=production \
    PATH="${PATH}:/usr/local/bin"

# 5. Запуск
CMD ["bash", "-c", "cd ./app && alembic upgrade head && python -m app.main"]
