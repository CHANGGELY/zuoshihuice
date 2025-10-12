# syntax=docker/dockerfile:1

FROM python:3.11.9-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8

WORKDIR /app

# System deps
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app

# Dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose FastAPI port
EXPOSE 8000

# FastAPI Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
 CMD curl -f http://localhost:8000/health || exit 1

# FastAPI default command (one-time cutover path B)
CMD ["python", "-m", "uvicorn", "fastapi_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
+ # Note: legacy frontend builder and FastAPI command removed during migration to FastAPI skeleton.
