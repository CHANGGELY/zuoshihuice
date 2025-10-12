# syntax=docker/dockerfile:1

FROM python:3.11-slim

ARG HTTP_PROXY
ARG HTTPS_PROXY
ENV HTTP_PROXY=${HTTP_PROXY}
ENV HTTPS_PROXY=${HTTPS_PROXY}
ENV NO_PROXY=localhost,127.0.0.1

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install basic build tools
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies (leverage Docker layer cache)
COPY requirements.txt /app/requirements.txt
RUN python -m pip install -U pip setuptools wheel && \
    pip install --no-cache-dir -r /app/requirements.txt

# Copy source
COPY . /app

EXPOSE 8000

ENV DATA_DIR=/app/K线data
ENV CACHE_DIR=/app/cache

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
 CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "fastapi_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
