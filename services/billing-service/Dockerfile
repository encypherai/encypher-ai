FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic

RUN uv pip install --system .

EXPOSE 8007

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8007}/health || exit 1

CMD ["sh", "-c", "echo 'Running migrations...' && alembic upgrade head && echo 'Starting billing-service...' && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8007}"]