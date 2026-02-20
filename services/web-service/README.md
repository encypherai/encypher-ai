# Encypher Web Service

Backend service for the Encypher marketing website, handling demo requests, sales contact forms, and web analytics.

## Features

- **AI Demo Requests**: `/api/v1/ai-demo/demo-requests` - Handle demo requests from AI demo page
- **Publisher Demo Requests**: `/api/v1/publisher-demo/demo-requests` - Handle demo requests from publisher demo page
- **Sales Contact**: `/api/v1/sales/enterprise-requests` and `/api/v1/sales/general-requests`
- **Analytics**: Event tracking for page views and user interactions
- **Email Notifications**: Automated email notifications for new leads and confirmations
- **Database**: PostgreSQL integration with Alembic migrations

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/ai-demo/demo-requests` | POST | Submit AI demo request |
| `/api/v1/ai-demo/analytics/events` | POST | Track AI demo analytics |
| `/api/v1/publisher-demo/demo-requests` | POST | Submit publisher demo request |
| `/api/v1/publisher-demo/analytics/events` | POST | Track publisher demo analytics |
| `/api/v1/sales/enterprise-requests` | POST | Submit enterprise sales inquiry |
| `/api/v1/sales/general-requests` | POST | Submit general sales inquiry |
| `/api/v1/demo-requests` | POST/GET | Legacy generic demo requests |
| `/api/v1/marketing-analytics` | POST | Marketing analytics events |
| `/health` | GET | Health check |

## Setup

1. **Install Dependencies** (using UV):
   ```bash
   uv sync
   ```

2. **Environment Variables**:
   Copy `.env.example` to `.env` and update the values.
   ```bash
   cp .env.example .env
   ```

3. **Database Migration**:
   Run Alembic migrations to set up the database schema.
   ```bash
   uv run alembic upgrade head
   ```

4. **Run Server**:
   ```bash
   uv run uvicorn app.main:app --reload --port 8002
   ```

## API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: `http://localhost:8002/api/v1/docs`
- ReDoc: `http://localhost:8002/api/v1/redoc`

## Testing

Run the test suite:
```bash
uv run pytest
```

## Environment Variables

See `.env.example` for all available configuration options:

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_SERVER` | Database host | `localhost` |
| `POSTGRES_DB` | Database name | `encypher_web` |
| `EMAILS_ENABLED` | Enable email sending | `false` |
| `CONTACT_EMAIL` | Primary inbound lead mailbox | `contact@encypherai.com` |
| `SALES_EMAIL` | Sales notification recipient | `contact@encypherai.com` |
| `DEMO_EMAIL` | Demo notification recipient | `contact@encypherai.com` |
