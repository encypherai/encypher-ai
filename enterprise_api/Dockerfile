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
    pip install --no-cache-dir hatchling

# Copy source code
COPY encypher-ai /app/encypher-ai
COPY enterprise_api /app/enterprise_api

RUN pip install --no-cache-dir -e /app/encypher-ai && \
    pip install --no-cache-dir -e /app/enterprise_api && \
    python -m spacy download en_core_web_sm

WORKDIR /app/enterprise_api

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
