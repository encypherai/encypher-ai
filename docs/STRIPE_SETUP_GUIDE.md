# Stripe Integration Setup Guide

Complete guide for setting up Stripe integration in the Encypher platform.

## 📋 Prerequisites

1. Stripe account (create at https://stripe.com)
2. Test mode API keys from Stripe Dashboard
3. Stripe CLI installed (optional, for local webhook testing)

---

## 🔑 Step 1: Get Your Stripe Keys

### Test Mode Keys (Development)

1. Go to https://dashboard.stripe.com/test/apikeys
2. Copy your **Publishable key** (starts with `pk_test_`)
3. Copy your **Secret key** (starts with `sk_test_`)

### Production Keys (Later)

1. Go to https://dashboard.stripe.com/apikeys
2. Copy your **Publishable key** (starts with `pk_live_`)
3. Copy your **Secret key** (starts with `sk_live_`)

⚠️ **NEVER commit secret keys to git!**

---

## ⚙️ Step 2: Configure Backend (Billing Service)

### Create Environment File

```bash
cd services/billing-service
cp .env.example .env
```

### Edit `.env` File

```bash
# Stripe Secret Key (Backend only - NEVER expose to frontend!)
STRIPE_API_KEY=sk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Webhook secrets (we'll set these up later)
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
STRIPE_CONNECT_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Price IDs (we'll generate these in Step 4)
STRIPE_PRICE_PROFESSIONAL_MONTHLY=price_xxxxxxxxxxxxxxxxxxxxx
STRIPE_PRICE_PROFESSIONAL_ANNUAL=price_xxxxxxxxxxxxxxxxxxxxx
STRIPE_PRICE_BUSINESS_MONTHLY=price_xxxxxxxxxxxxxxxxxxxxx
STRIPE_PRICE_BUSINESS_ANNUAL=price_xxxxxxxxxxxxxxxxxxxxx
```

---

## 🎨 Step 3: Configure Frontend (Dashboard)

### Create Environment File

```bash
cd apps/dashboard
touch .env.local
```

### Edit `.env.local` File

```bash
# Stripe Publishable Key (Safe to expose in frontend)
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_51xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 🛍️ Step 4: Create Stripe Products & Prices

You have two options:

### Option A: Use Our Setup Script (Recommended)

This automatically creates products for Professional and Business tiers:

```bash
cd services/billing-service

# Make sure your .env has STRIPE_API_KEY set
uv run python ../../scripts/setup_stripe_products.py
```

The script will output price IDs like:

```
# Professional Tier
STRIPE_PRICE_PROFESSIONAL_MONTHLY=price_1AbCdEfGhIjKlMnO
STRIPE_PRICE_PROFESSIONAL_ANNUAL=price_1PqRsTuVwXyZaBcD

# Business Tier
STRIPE_PRICE_BUSINESS_MONTHLY=price_1CdEfGhIjKlMnOpQ
STRIPE_PRICE_BUSINESS_ANNUAL=price_1RsTuVwXyZaBcDeF
```

**Copy these IDs to your `services/billing-service/.env` file.**

### Option B: Create Manually in Stripe Dashboard

1. Go to https://dashboard.stripe.com/test/products
2. Click **"+ Add product"**

**For Professional Tier:**
- Name: `Encypher Professional`
- Description: `Sentence-level tracking, streaming, BYOK, and better coalition revenue share.`
- Pricing:
  - Monthly: $99.00 USD, recurring monthly
  - Annual: $950.00 USD, recurring yearly

**For Business Tier:**
- Name: `Encypher Business`
- Description: `Merkle infrastructure, plagiarism detection, team management, and audit logs.`
- Pricing:
  - Monthly: $499.00 USD, recurring monthly
  - Annual: $4,790.00 USD, recurring yearly

3. Copy the **Price IDs** from each price and add to `.env`

---

## 🔔 Step 5: Set Up Webhooks

Webhooks allow Stripe to notify your backend about payment events.

### Local Development (Using Stripe CLI)

1. **Install Stripe CLI**: https://stripe.com/docs/stripe-cli

2. **Login to Stripe**:
   ```bash
   stripe login
   ```

3. **Forward webhooks to local billing service**:
   ```bash
   stripe listen --forward-to localhost:8007/api/v1/billing/webhooks/stripe
   ```

   **Tip:** `./start-dev.sh` now starts the Stripe CLI listener automatically unless you pass `--skip-stripe-listen`.
   You can override the target with `STRIPE_WEBHOOK_FORWARD_URL` (default: `localhost:4242/webhook`).

4. **Copy the webhook signing secret** (starts with `whsec_`) and add to `.env`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Production (Using Stripe Dashboard)

1. Go to https://dashboard.stripe.com/webhooks
2. Click **"+ Add endpoint"**
3. Endpoint URL: `https://api.encypher.com/api/v1/billing/webhooks/stripe`
4. Select events to listen to:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.paid`
   - `invoice.payment_failed`
   - `customer.created`

5. Copy the **Signing secret** and add to production `.env`

---

## ✅ Step 6: Verify Setup

### Test Backend Connection

```bash
cd services/billing-service
uv run python -c "
import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_API_KEY
print('✅ Stripe API Key is valid!')
print(f'Mode: {\"TEST\" if stripe.api_key.startswith(\"sk_test\") else \"LIVE\"}')

# List products
products = stripe.Product.list(limit=5)
print(f'✅ Found {len(products.data)} products')
for p in products.data:
    print(f'  - {p.name} ({p.id})')
"
```

### Test Frontend Integration

1. Start the dashboard:
   ```bash
   cd apps/dashboard
   npm run dev
   ```

2. Open browser console and check:
   ```javascript
   console.log(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY)
   // Should show: pk_test_51...
   ```

---

## 🧪 Testing Payments

### Test Card Numbers (UI Only)

Stripe provides test cards for different scenarios:

| Card Number | Scenario |
|-------------|----------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 9995` | Declined (insufficient funds) |
| `4000 0025 0000 3155` | Requires authentication (3D Secure) |

- **Expiry**: Any future date (e.g., `12/34`)
- **CVC**: Any 3 digits (e.g., `123`)
- **ZIP**: Any 5 digits (e.g., `12345`)

> **Important:** Enter these test card numbers **only** in Stripe-hosted Checkout or Elements. Never send raw card numbers to Stripe APIs or the Stripe CLI. Raw card data triggers Stripe security blocks and increases PCI scope.

### Test Subscription Flow

1. Navigate to billing page in dashboard
2. Click "Upgrade to Professional"
3. Use test card `4242 4242 4242 4242`
4. Complete checkout
5. Verify webhook received in billing service logs
6. Check subscription in Stripe Dashboard

---

## 🔐 Security Best Practices

### ✅ DO:
- Use test keys (`sk_test_`, `pk_test_`) for development
- Keep secret keys in `.env` files (gitignored)
- Use environment variables in production
- Verify webhook signatures
- Use HTTPS in production
- Use Stripe Checkout/Elements to collect card details

### ❌ DON'T:
- Commit `.env` files to git
- Expose secret keys in frontend code
- Use production keys in development
- Skip webhook signature verification
- Store keys in code or config files
- Send full card numbers to Stripe APIs or CLI

---

## 📚 Useful Resources

- **Stripe Dashboard**: https://dashboard.stripe.com
- **API Documentation**: https://stripe.com/docs/api
- **Webhook Events**: https://stripe.com/docs/webhooks
- **Test Cards**: https://stripe.com/docs/testing
- **Stripe CLI**: https://stripe.com/docs/stripe-cli

---

## 🐛 Troubleshooting

### "Invalid API Key"
- Check that `STRIPE_API_KEY` is set in `.env`
- Verify the key starts with `sk_test_` (test) or `sk_live_` (production)
- Make sure there are no extra spaces or quotes

### "No such price"
- Run the setup script to create products/prices
- Verify price IDs in `.env` match those in Stripe Dashboard
- Check you're using test mode price IDs with test mode keys

### Webhooks not received
- For local dev: Make sure `stripe listen` is running
- Check webhook endpoint URL is correct
- Verify webhook signing secret matches
- Check billing service logs for errors

### Frontend can't load Stripe
- Verify `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` is set in `.env.local`
- Restart Next.js dev server after changing env vars
- Check browser console for errors

---

## 📞 Support

- **Stripe Support**: https://support.stripe.com
- **Encypher Team**: Check internal documentation
