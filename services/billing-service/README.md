# Encypher Billing Service

Billing and subscription microservice for the Encypher platform.

## Features

- ✅ Subscription management (Starter, Professional, Business, Enterprise)
- ✅ Stripe Checkout integration
- ✅ Stripe Billing Portal (self-service)
- ✅ Stripe Connect for publisher payouts
- ✅ Invoice generation and history
- ✅ Payment tracking
- ✅ Billing statistics
- ✅ Coalition revenue share tracking
- ✅ Monthly/Annual billing cycles

## Tech Stack

- FastAPI, Uvicorn
- PostgreSQL, Redis
- SQLAlchemy, Pydantic
- Stripe (Checkout, Billing Portal, Connect, Webhooks)

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
| POST | `/api/v1/billing/checkout` | Create Stripe Checkout session |
| GET | `/api/v1/billing/portal` | Get Stripe Billing Portal URL |
| POST | `/api/v1/billing/upgrade` | Upgrade subscription |
| GET | `/api/v1/billing/plans` | Get available plans |
| POST | `/api/v1/webhooks/stripe` | Stripe webhook handler |

## Stripe Local Development

### 1. Install Stripe CLI

```powershell
# Using Scoop
scoop install stripe

# Or using winget
winget install Stripe.StripeCLI
```

### 2. Login to Stripe

```powershell
stripe login
```

### 3. Start Local Webhook Listener

In one terminal, run:
```powershell
.\scripts\stripe-listen.ps1
```

This will output a webhook signing secret (`whsec_...`). Copy it to your `.env` file:
```
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 4. Test Webhook Events

In another terminal, trigger test events:
```powershell
# Show available events
.\scripts\stripe-trigger.ps1

# Trigger specific events
.\scripts\stripe-trigger.ps1 checkout
.\scripts\stripe-trigger.ps1 sub_created
.\scripts\stripe-trigger.ps1 invoice_paid
```

### 5. Setup Stripe Products (One-time)

```powershell
uv run python scripts/setup_stripe.py
```

This creates the Professional and Business products/prices in Stripe and outputs the price IDs for your `.env`.

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
- `STRIPE_BILLING_PORTAL_CONFIG_ID` - Billing portal configuration ID (enables plan changes)
- `INTERNAL_SERVICE_TOKEN` - Shared token for auth-service tier sync

## License

Proprietary - Encypher Corporation