# Licensing API Documentation

The Licensing API enables AI companies to access coalition content under licensing agreements and provides tools for tracking content usage and distributing revenue to content creators.

## Architecture Overview

The Licensing API is part of the **Enterprise API** (port 9000), separate from the core microservices. This separation is intentional:

| Domain | Service | Purpose |
|--------|---------|---------|
| **Customer Billing** | `billing-service` (8007) | Encypher subscription tiers, Stripe integration |
| **AI Company Licensing** | `enterprise_api` (9000) | B2B agreements with AI companies |
| **Coalition Revenue** | `enterprise_api` (9000) | Revenue distribution to publishers |

## Authentication

AI companies authenticate using API keys with the `lic_` prefix:

```bash
curl -H "Authorization: Bearer lic_abc123..." \
  https://api.encypher.ai/api/v1/licensing/content
```

API keys are generated when creating a licensing agreement and are only shown once.

---

## Endpoints

### Agreement Management (Admin Only)

#### Create Agreement

```http
POST /api/v1/licensing/agreements
```

Creates a new licensing agreement with an AI company. If the company doesn't exist, it's created with a new API key.

**Request Body:**
```json
{
  "agreement_name": "OpenAI Training License 2025",
  "ai_company_name": "OpenAI",
  "ai_company_email": "licensing@openai.com",
  "agreement_type": "subscription",
  "total_value": 1200000.00,
  "currency": "USD",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "content_types": ["article", "blog", "news"],
  "min_word_count": 100
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "agreement_name": "OpenAI Training License 2025",
  "api_key": "lic_abc123...",  // Only shown once!
  "api_key_prefix": "lic_abc1",
  "status": "active",
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### List Agreements

```http
GET /api/v1/licensing/agreements?status=active&limit=100&offset=0
```

#### Get Agreement

```http
GET /api/v1/licensing/agreements/{agreement_id}
```

#### Update Agreement

```http
PATCH /api/v1/licensing/agreements/{agreement_id}
```

**Request Body:**
```json
{
  "agreement_name": "Updated Name",
  "total_value": 1500000.00,
  "end_date": "2026-06-30",
  "status": "active"
}
```

#### Terminate Agreement

```http
DELETE /api/v1/licensing/agreements/{agreement_id}
```

---

### Content Access (AI Company API Key Required)

#### List Available Content

```http
GET /api/v1/licensing/content?content_type=article&min_word_count=500&limit=100&offset=0
```

Returns content available under the AI company's active licensing agreement.

**Headers:**
```
Authorization: Bearer lic_abc123...
```

**Response:**
```json
{
  "content": [
    {
      "id": 2748395012,
      "content_type": "article",
      "word_count": 1500,
      "signed_at": "2025-01-15T10:30:00Z",
      "content_hash": "a3f9c2e1...",
      "verification_url": "https://verify.encypher.ai/a3f9c2e1"
    }
  ],
  "total": 15000,
  "quota_remaining": null
}
```

#### Track Content Access

```http
POST /api/v1/licensing/track-access
```

Logs when an AI company accesses content for revenue attribution.

**Headers:**
```
Authorization: Bearer lic_abc123...
```

**Request Body:**
```json
{
  "content_id": 2748395012,
  "access_type": "train"
}
```

**Access Types:**
- `view` - Content was viewed/read
- `train` - Content used for model training
- `download` - Content was downloaded
- `embed` - Content was embedded/indexed

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "agreement_id": "550e8400-e29b-41d4-a716-446655440000",
  "content_id": "550e8400-e29b-41d4-a716-446655440002",
  "member_id": "550e8400-e29b-41d4-a716-446655440003",
  "accessed_at": "2025-01-15T14:30:00Z",
  "access_type": "train",
  "ai_company_name": "OpenAI"
}
```

---

### Revenue Distribution (Admin Only)

#### Create Distribution

```http
POST /api/v1/licensing/distributions
```

Calculates and creates revenue distribution for a period. Implements 70/30 split (70% to members, 30% to Encypher).

**Request Body:**
```json
{
  "agreement_id": "550e8400-e29b-41d4-a716-446655440000",
  "period_start": "2025-01-01",
  "period_end": "2025-01-31"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440004",
  "agreement_id": "550e8400-e29b-41d4-a716-446655440000",
  "period_start": "2025-01-01",
  "period_end": "2025-01-31",
  "total_revenue": 100000.00,
  "encypher_share": 30000.00,
  "member_pool": 70000.00,
  "status": "completed",
  "created_at": "2025-02-01T00:00:00Z",
  "processed_at": "2025-02-01T00:01:00Z",
  "member_revenues": [
    {
      "id": "...",
      "member_id": "...",
      "content_count": 150,
      "access_count": 500,
      "revenue_amount": 35000.00,
      "status": "pending",
      "paid_at": null,
      "payment_reference": null
    }
  ]
}
```

#### List Distributions

```http
GET /api/v1/licensing/distributions?agreement_id=...&status=completed&limit=100&offset=0
```

#### Get Distribution

```http
GET /api/v1/licensing/distributions/{distribution_id}
```

#### Process Payouts

```http
POST /api/v1/licensing/payouts
```

Initiates payment processing for all members in a distribution.

**Request Body:**
```json
{
  "distribution_id": "550e8400-e29b-41d4-a716-446655440004",
  "payment_method": "stripe"
}
```

**Response:**
```json
{
  "distribution_id": "550e8400-e29b-41d4-a716-446655440004",
  "total_members_paid": 25,
  "total_amount_paid": 70000.00,
  "failed_payments": []
}
```

---

## Data Models

### Agreement Types

| Type | Description |
|------|-------------|
| `subscription` | Monthly/annual recurring agreement |
| `one_time` | Single payment agreement |
| `usage_based` | Pay-per-access agreement |

### Agreement Status

| Status | Description |
|--------|-------------|
| `active` | Agreement is active and within date range |
| `suspended` | Temporarily suspended |
| `terminated` | Permanently ended |
| `expired` | Past end date |

### Distribution Status

| Status | Description |
|--------|-------------|
| `pending` | Calculation in progress |
| `processing` | Payouts being processed |
| `completed` | All calculations done |
| `failed` | Error during processing |

### Payout Status

| Status | Description |
|--------|-------------|
| `pending` | Awaiting payout |
| `processing` | Payment in progress |
| `paid` | Successfully paid |
| `failed` | Payment failed |

---

## Revenue Distribution Logic

### 70/30 Split

Revenue from AI company agreements is split:
- **70%** → Coalition member pool (distributed to content creators)
- **30%** → Encypher platform fee

### Member Attribution

Member revenue is calculated based on content access:

```
member_share = (member_access_count / total_access_count) * member_pool
```

Example:
- Total revenue: $100,000
- Member pool (70%): $70,000
- Member A: 500 accesses (50% of total) → $35,000
- Member B: 300 accesses (30% of total) → $21,000
- Member C: 200 accesses (20% of total) → $14,000

---

## Error Codes

| Code | Description |
|------|-------------|
| 401 | Missing or invalid API key |
| 403 | No active agreement for AI company |
| 404 | Resource not found (agreement, content, distribution) |
| 400 | Invalid request data |
| 500 | Internal server error |

---

## Integration with Billing Service

The Licensing API integrates with the `billing-service` for:

1. **Revenue Share Rates** - Tier-based rates defined in billing-service
2. **Stripe Connect** - Future: Publisher payouts via Stripe Connect

Current tier rates:
| Tier | Publisher Share | Encypher Share |
|------|-----------------|----------------|
| Starter | 65% | 35% |
| Professional | 70% | 30% |
| Business | 75% | 25% |
| Enterprise | 80% | 20% |
| Strategic Partner | 85% | 15% |

---

## Example Flow

### 1. Create Agreement (Admin)

```bash
curl -X POST https://api.encypher.ai/api/v1/licensing/agreements \
  -H "Content-Type: application/json" \
  -d '{
    "agreement_name": "Anthropic Training License",
    "ai_company_name": "Anthropic",
    "ai_company_email": "licensing@anthropic.com",
    "agreement_type": "subscription",
    "total_value": 500000.00,
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }'
```

### 2. List Content (AI Company)

```bash
curl https://api.encypher.ai/api/v1/licensing/content \
  -H "Authorization: Bearer lic_abc123..."
```

### 3. Track Access (AI Company)

```bash
curl -X POST https://api.encypher.ai/api/v1/licensing/track-access \
  -H "Authorization: Bearer lic_abc123..." \
  -H "Content-Type: application/json" \
  -d '{"content_id": 2748395012, "access_type": "train"}'
```

### 4. Create Distribution (Admin, Monthly)

```bash
curl -X POST https://api.encypher.ai/api/v1/licensing/distributions \
  -H "Content-Type: application/json" \
  -d '{
    "agreement_id": "...",
    "period_start": "2025-01-01",
    "period_end": "2025-01-31"
  }'
```

### 5. Process Payouts (Admin)

```bash
curl -X POST https://api.encypher.ai/api/v1/licensing/payouts \
  -H "Content-Type: application/json" \
  -d '{"distribution_id": "...", "payment_method": "stripe"}'
```
