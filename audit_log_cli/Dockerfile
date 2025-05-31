# Dockerfile for audit_log_cli
FROM python:3.11-slim

WORKDIR /app

# Create a non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 -m appuser

# Install uv
RUN pip install uv

COPY pyproject.toml uv.lock* /app/

# Install dependencies using uv
RUN uv pip sync --no-cache --system

COPY ./app /app/app

USER appuser

ENTRYPOINT ["uv", "run", "python", "app/main.py"]
