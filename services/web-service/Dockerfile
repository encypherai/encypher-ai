FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy shared library (synced from /shared_commercial_libs/)
COPY shared_libs ./shared_libs
RUN uv pip install --system ./shared_libs

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Copy application code
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

RUN groupadd --gid 1000 appuser && useradd --uid 1000 --gid 1000 -m appuser

# Install dependencies using UV
RUN uv pip install --system .

USER appuser
# Expose port (Railway provides PORT env var)
EXPOSE ${PORT:-8000}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; import os; requests.get(f'http://localhost:{os.environ.get(\"PORT\", 8000)}/health')"

# Run the application (use PORT env var for Railway compatibility)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
