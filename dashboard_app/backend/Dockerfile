# Dockerfile for dashboard_app backend
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /app

# Create a non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 -m appuser

COPY pyproject.toml uv.lock* /app/

# Install dependencies using uv
RUN uv pip sync --no-cache --system

COPY ./app /app/app

USER appuser

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
