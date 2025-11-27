# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Copy project files
COPY pyproject.toml /app/
# Lock may not exist initially; copy if present
# This is safe: if file missing, Docker will ignore
COPY uv.lock* /app/

# Install deps
RUN uv sync --frozen || uv sync

# Copy application
COPY app /app/app

EXPOSE ${PORT:-8000}

CMD uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
