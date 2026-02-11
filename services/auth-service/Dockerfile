FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy shared library (synced from /shared_commercial_libs/)
COPY shared_libs /shared_libs

# Install shared library first
RUN uv pip install --system /shared_libs

# Copy service files
COPY pyproject.toml ./
COPY README.md ./
COPY app ./app

# Copy Alembic configuration for migrations
COPY alembic.ini ./
COPY alembic ./alembic

# Install service dependencies
RUN uv pip install --system .

# Expose port (Railway provides PORT dynamically)
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8001}/health || exit 1

# Run migrations then start the application
CMD ["sh", "-c", "echo 'Running database migrations...' && alembic upgrade head && echo 'Starting auth-service...' && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}"]
