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

# Copy dependency files first for better caching
COPY pyproject.toml ./
COPY README.md ./

# Copy application code
COPY app ./app

# Install dependencies using UV
RUN uv pip install --system .

# Expose port (Railway provides PORT dynamically)
EXPOSE 8003

# Run the application - use PORT env var for Railway compatibility
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8003}"]
