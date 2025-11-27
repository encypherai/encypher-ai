FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

# Copy shared library (copied from repo during build)
COPY shared_libs /shared_libs

# Install shared library first
RUN uv pip install --system /shared_libs

# Copy service files
COPY pyproject.toml ./
COPY README.md ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# Install service dependencies
RUN uv pip install --system .

# Expose port (Railway provides PORT dynamically)
EXPOSE 8001

# Run migrations and start the application
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}"]
