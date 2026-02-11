FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*
# Copy shared library (synced from /shared_commercial_libs/)
COPY shared_libs /shared_libs
RUN uv pip install --system /shared_libs
COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic
RUN uv pip install --system .
EXPOSE 8004
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8004}/health || exit 1
CMD ["sh", "-c", "echo 'Running migrations...' && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8004}"]
