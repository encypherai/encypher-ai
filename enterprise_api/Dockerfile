FROM python:3.11-slim

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

# Install project dependencies in editable mode for live reload during development
RUN pip install --upgrade pip && \
    pip install --no-cache-dir hatchling setuptools

# Copy source code - c2pa-text needs parent README.md so copy whole directory
COPY c2pa-text /app/c2pa-text
COPY encypher-ai /app/encypher-ai
COPY enterprise_api /app/enterprise_api
COPY services/migrations /app/services/migrations

# Install c2pa-text first (dependency of encypher-ai), then encypher-ai, then enterprise_api
# Also install asyncpg for database initialization and pytest for testing
RUN pip install --no-cache-dir -e /app/c2pa-text/python && \
    pip install --no-cache-dir -e /app/encypher-ai && \
    pip install --no-cache-dir -e /app/enterprise_api && \
    pip install --no-cache-dir asyncpg pytest pytest-asyncio httpx && \
    python -m spacy download en_core_web_sm

WORKDIR /app/enterprise_api

# Make entrypoint script executable
RUN chmod +x scripts/docker-entrypoint.sh

EXPOSE 8000

# Use entrypoint script for database initialization
ENTRYPOINT ["scripts/docker-entrypoint.sh"]
# Default CMD - Railway will override via startCommand if needed
# Note: Railway provides PORT env var dynamically
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
