# Encypher Billing Service

Billing and subscription microservice for the Encypher platform.

## Features

- ✅ Subscription management
- ✅ Invoice generation
- ✅ Payment tracking
- ✅ Billing statistics
- ✅ Multiple plans (Free, Pro, Enterprise)
- ✅ Monthly/Yearly billing cycles

## Tech Stack

- FastAPI, Uvicorn
- PostgreSQL, Redis
- SQLAlchemy, Pydantic
- Stripe integration (planned)

## Setup

```bash
cd services/billing-service
uv sync
cp .env.example .env.local
uv run python -m app.main
```

Service at: http://localhost:8007

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/billing/subscription` | Create subscription |
| GET | `/api/v1/billing/subscription` | Get subscription |
| DELETE | `/api/v1/billing/subscription/{id}` | Cancel subscription |
| GET | `/api/v1/billing/invoices` | List invoices |
| GET | `/api/v1/billing/stats` | Billing stats |
| GET | `/health` | Health check |

## Docker

```bash
docker build -t encypher-billing-service .
docker run -p 8007:8007 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e AUTH_SERVICE_URL=http://auth-service:8001 \
  encypher-billing-service
```

## Environment Variables

Required:
- `DATABASE_URL` - PostgreSQL connection
- `AUTH_SERVICE_URL` - Auth service URL

Optional:
- `SERVICE_PORT` - Port (default: 8007)
- `STRIPE_API_KEY` - Stripe API key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook secret

## License

Proprietary - Encypher AI