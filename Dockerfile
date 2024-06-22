FROM python:3.12.3-slim

WORKDIR /app

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get install -y redis-tools

COPY . /app

CMD ["gunicorn", "-w", "10", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000"] 