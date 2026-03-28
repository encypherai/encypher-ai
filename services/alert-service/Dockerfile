FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*
RUN groupadd --gid 1000 appuser && useradd --uid 1000 --gid 1000 -m appuser
COPY shared_libs /shared_libs
RUN uv pip install --system /shared_libs
COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic
RUN uv pip install --system .
USER appuser
EXPOSE 8011
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8011}/health || exit 1
CMD ["sh", "-c", "echo 'Starting alert-service...' && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8011}"]
