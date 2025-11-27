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

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using UV
RUN uv pip install --system -r pyproject.toml

# Copy application code
COPY app ./app

# Expose port (Railway provides PORT env var)
EXPOSE ${PORT:-8009}

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; import os; requests.get(f'http://localhost:{os.environ.get(\"PORT\", 8009)}/health')"

# Run the application (use PORT env var for Railway compatibility)
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8009}
