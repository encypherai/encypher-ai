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

# Copy shared library (expects build context from repo root)
COPY shared_commercial_libs /shared_libs

# Install shared library first
RUN uv pip install --system /shared_libs

# Copy service files
COPY services/auth-service/pyproject.toml ./
COPY services/auth-service/README.md ./
COPY services/auth-service/app ./app

# Install service dependencies
RUN uv pip install --system .

# Expose port (Railway provides PORT dynamically)
EXPOSE 8001

# Run the application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8001}"]
