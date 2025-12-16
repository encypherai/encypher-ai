FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

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

# Install dependencies using UV
RUN uv pip install --system .

# Expose port (Railway provides PORT env var)
EXPOSE ${PORT:-8000}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; import os; requests.get(f'http://localhost:{os.environ.get(\"PORT\", 8000)}/health')"

# Run the application (use PORT env var for Railway compatibility)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
