FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

# Copy shared library first (for caching)
COPY shared_commercial_libs /shared_libs

# Install shared library
RUN uv pip install --system /shared_libs

# Copy dependency files
COPY services/notification-service/pyproject.toml ./
COPY services/notification-service/README.md ./

# Copy application code
COPY services/notification-service/app ./app

# Install dependencies
RUN uv pip install --system .

EXPOSE 8009
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8009}"]