FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml .
RUN uv sync --no-dev

# Install torch CPU (no CUDA to keep image smaller) and trustmark.
# These are large and installed separately so the layer cache is preserved.
RUN uv run pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu \
    && uv run pip install trustmark

COPY app/ ./app/

EXPOSE 8010

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
