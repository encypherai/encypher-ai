FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*
# Copy shared library (synced from /shared_commercial_libs/)
COPY services/verification-service/shared_libs /shared_libs
RUN uv pip install --system /shared_libs
# Copy and install local c2pa-text and encypher-ai packages (v3.0.2 with C2PA v2.3 support)
COPY c2pa-text /c2pa-text
RUN uv pip install --system /c2pa-text/python
COPY encypher-ai /encypher-ai
RUN uv pip install --system /encypher-ai
COPY services/verification-service/pyproject.toml services/verification-service/README.md ./
COPY services/verification-service/app ./app
COPY services/verification-service/alembic.ini ./
COPY services/verification-service/alembic ./alembic
RUN uv pip install --system .
EXPOSE 8005
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8005}/health || exit 1
CMD ["sh", "-c", "echo 'Running migrations...' && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8005}"]
