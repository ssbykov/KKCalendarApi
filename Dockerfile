# syntax=docker/dockerfile:1.4


# Финальный образ
FROM python:3.11-slim

# Установка Node.js и зависимостей
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    # Явное создание симлинков
    ln -sf /usr/bin/node /usr/local/bin/node && \
    ln -sf /usr/bin/npm /usr/local/bin/npm && \
    # Установка PostgreSQL
    apt-get install -y gnupg2 lsb-release && \
    curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg && \
    echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    apt-get install -y postgresql-client-16 && \
    # Очистка
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=2.1.2 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Установка зависимостей
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main

# Копирование кода приложения
COPY . .

# Проверка exejs
RUN python3 -c "from exejs import evaluate; print('JS test:', evaluate('1+1'))"

# Переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    NODE_PATH=/usr/bin/node \
    PATH="/usr/bin:/usr/local/bin:${PATH}"

CMD ["bash", "-c", "cd app && alembic upgrade head && python -m app.main"]