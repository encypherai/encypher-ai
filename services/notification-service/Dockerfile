FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Install UV
RUN pip install uv

# Copy shared library (copied from repo during build)
COPY shared_libs /shared_libs

# Install shared library
RUN uv pip install --system /shared_libs

# Copy dependency files
COPY pyproject.toml ./
COPY README.md ./

# Copy application code
COPY app ./app

# Install dependencies
RUN uv pip install --system .

EXPOSE 8009
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8009}"]