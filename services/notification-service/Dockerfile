FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

# Copy shared library (copied from repo during build)
COPY shared_libs /shared_libs

# Install shared library
RUN uv pip install --system /shared_libs

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Copy application code
COPY app ./app

# Install dependencies
RUN uv pip install --system .

COPY alembic.ini ./
COPY alembic ./alembic

EXPOSE 8008
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8008}/health || exit 1
CMD ["sh", "-c", "echo 'Running migrations...' && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8008}"]