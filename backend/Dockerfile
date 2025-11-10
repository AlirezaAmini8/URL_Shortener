FROM docker.arvancloud.ir/python:3.11.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN touch __init__.py || true
RUN mkdir -p logs

EXPOSE 8000

CMD until pg_isready -h db -p 5432 -U postgres; do \
      echo "Waiting for database..."; \
      sleep 2; \
    done && \
    python manage.py makemigrations && \
    python manage.py migrate  && \
    python manage.py runserver 0.0.0.0:8000