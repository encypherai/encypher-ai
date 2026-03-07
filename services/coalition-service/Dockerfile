FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd --gid 1000 appuser && useradd --uid 1000 --gid 1000 -m appuser

# Copy shared library (synced from /shared_commercial_libs/)
COPY shared_libs /shared_libs
RUN uv pip install --system /shared_libs

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using UV
RUN uv pip install --system -r pyproject.toml

# Copy application code
COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic

USER appuser
# Expose port
EXPOSE 8009

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8009}/health || exit 1

# Run the application
CMD ["sh", "-c", "echo 'Starting coalition-service...' && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8009}"]
