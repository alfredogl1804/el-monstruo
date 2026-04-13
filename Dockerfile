# El Monstruo — Kernel Dockerfile
# Sprint 1 — validated 2026-04-12
# Base: python:3.12-slim (LTS, pushed 2 days ago on Docker Hub)
# Deploy target: Railway

FROM python:3.12-slim AS base

WORKDIR /app

# System deps for asyncpg, pgvector native extensions, and healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python deps (exclude test packages for production image)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    grep -v "^#" requirements.txt | \
    grep -v "^$" | \
    grep -v "pytest" | \
    pip install --no-cache-dir -r /dev/stdin

# App code
COPY . .

# Environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
# Railway injects PORT automatically — default to 8000
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

EXPOSE ${PORT}

# Shell form allows ${PORT} expansion — confirmed fix from Railway community
CMD uvicorn kernel.main:app --host 0.0.0.0 --port ${PORT:-8000}
