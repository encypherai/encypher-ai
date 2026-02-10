FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies for psycopg2 and cryptography
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy project metadata
COPY enterprise_api/pyproject.toml enterprise_api/pyproject.toml
COPY encypher-ai/pyproject.toml encypher-ai/pyproject.toml

# Install build backends
RUN uv pip install --system hatchling setuptools

# Copy source code - c2pa-text needs parent README.md so copy whole directory
COPY c2pa-text /app/c2pa-text
COPY encypher-ai /app/encypher-ai
COPY enterprise_api /app/enterprise_api
COPY services/migrations /app/services/migrations

# Install c2pa-text first (dependency of encypher-ai), then encypher-ai, then enterprise_api
# Also install asyncpg for database initialization and pytest for testing
RUN uv pip install --system -e /app/c2pa-text/python && \
    uv pip install --system -e /app/encypher-ai && \
    uv pip install --system -e /app/enterprise_api && \
    uv pip install --system asyncpg pytest pytest-asyncio httpx && \
    python -m spacy download en_core_web_sm

WORKDIR /app/enterprise_api

# Install curl for health checks and fix line endings
RUN apt-get update && apt-get install -y --no-install-recommends curl dos2unix && \
    rm -rf /var/lib/apt/lists/* && \
    dos2unix scripts/docker-entrypoint.sh && \
    chmod +x scripts/docker-entrypoint.sh

EXPOSE 8000

# Use entrypoint script for database initialization
ENTRYPOINT ["/bin/sh", "scripts/docker-entrypoint.sh"]
# Default CMD - Railway will override via startCommand if needed
# Note: Railway provides PORT env var dynamically
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
