FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p staticfiles media && \
    chown -R appuser:appuser /app

EXPOSE 8000
USER appuser
CMD ["gunicorn", "srtapp.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
