FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
RUN pip install uv
COPY pyproject.toml README.md ./
COPY app ./app
RUN uv pip install --system .
EXPOSE 8005
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8005}"]
