FROM python:3.12.3-slim

# Установить рабочую директорию
WORKDIR /app

# Установить системные зависимости
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    redis-tools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Скопировать файл зависимостей и установить Python-зависимости
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Скопировать все файлы приложения в контейнер
COPY . .

# Команда запуска
CMD ["gunicorn", "-w", "10", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"]