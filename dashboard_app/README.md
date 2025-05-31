# Compliance Readiness Dashboard Application

This application provides a web-based dashboard for AI content authenticity, metadata policy compliance, and usage insights.

It consists of a:
-   **Backend:** FastAPI application located in `/backend`
-   **Frontend:** Next.js application located in `/frontend`

Refer to the `README.md` files in each respective directory for specific setup and running instructions.

## Running with Docker Compose (Local Development)

From the `dashboard_app` directory, you can build and run both services:

```bash
docker-compose up --build
```

The frontend will typically be available at `http://localhost:3000` and the backend at `http://localhost:8000`.
