FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using UV
RUN uv pip install --system -r pyproject.toml

# Copy application code
COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic

# Expose port
EXPOSE 8009

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8009}/health || exit 1

# Run migrations then start the application
CMD ["sh", "-c", "echo 'Running migrations...' && alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8009}"]
