# Stripe Price Management Strategy

## Overview

The billing service uses a **hybrid approach** for managing Stripe price IDs:

1. **Primary Source**: `.env` file (fast, reliable)
2. **Validation**: API check on startup (ensures correctness)
3. **Caching**: Metadata cached for display purposes

This gives you the best of both worlds: performance + validation.

---

## 🎯 Architecture Decision

### Why .env as Primary Source?

**Your pricing model:**
- 2 tiers (Professional, Business)
- 4 total prices (monthly + annual for each)
- Fixed, strategic pricing ($99/$950 and $499/$4,790)
- Infrequent changes

**Benefits:**
- ✅ **Zero latency** - no API calls during checkout
- ✅ **High reliability** - works even if Stripe API is down
- ✅ **Simple** - direct tier → price_id mapping
- ✅ **Environment separation** - different IDs for test vs production
- ✅ **Cost-effective** - zero API calls for lookups
- ✅ **Predictable** - no unexpected price changes

### Why API Validation on Startup?

**Benefits:**
- ✅ **Early detection** - catches configuration errors immediately
- ✅ **Confidence** - confirms prices exist in Stripe
- ✅ **Metadata caching** - stores display info (amount, currency, etc.)
- ✅ **Non-blocking** - logs warnings but doesn't prevent startup

---

## 📁 File Structure

```
services/billing-service/
├── .env                          # Price IDs stored here
├── app/
│   ├── main.py                   # Validates on startup
│   ├── core/
│   │   └── config.py             # Loads from .env
│   └── services/
│       ├── price_cache.py        # NEW: Hybrid price management
│       └── stripe_service.py     # Uses price_cache
```

---

## 🔧 How It Works

### 1. Configuration (.env)

```bash
# Stripe Price IDs (set after running setup script)
STRIPE_PRICE_PROFESSIONAL_MONTHLY=price_1AbCdEfGhIjKlMnO
STRIPE_PRICE_PROFESSIONAL_ANNUAL=price_1PqRsTuVwXyZaBcD
STRIPE_PRICE_BUSINESS_MONTHLY=price_1CdEfGhIjKlMnOpQ
STRIPE_PRICE_BUSINESS_ANNUAL=price_1RsTuVwXyZaBcDeF
```

### 2. Startup Validation (main.py)

```python
# On service startup:
if settings.STRIPE_API_KEY:
    validation_results = await price_cache.validate_prices_on_startup()
    # ✅ Validates all 4 price IDs exist in Stripe
    # ✅ Caches metadata (amount, currency, interval)
    # ⚠️  Logs warnings if any prices are invalid
    # ✅ Service continues even if validation fails
```

**Startup logs:**
```
INFO: Validating Stripe price configuration...
INFO: ✅ Validated price professional_monthly: price_1AbCdEfGhIjKlMnO ($99.00/month)
INFO: ✅ Validated price professional_annual: price_1PqRsTuVwXyZaBcD ($950.00/year)
INFO: ✅ Validated price business_monthly: price_1CdEfGhIjKlMnOpQ ($499.00/month)
INFO: ✅ Validated price business_annual: price_1RsTuVwXyZaBcDeF ($4790.00/year)
INFO: ✅ All 4 Stripe prices validated successfully
```

### 3. Runtime Usage

```python
from app.services.price_cache import get_stripe_price_id

# Get price ID (uses .env - instant, no API call)
price_id = get_stripe_price_id("professional", "monthly")
# Returns: "price_1AbCdEfGhIjKlMnO"

# Create checkout session
session = await StripeService.create_checkout_session(
    customer_id=customer.id,
    price_id=price_id,  # From .env
    success_url="...",
    cancel_url="...",
)
```

---

## 🔄 When to Update Prices

### Scenario 1: Price Change (Rare)

If you change pricing (e.g., Professional becomes $109/month):

1. **Create new price in Stripe Dashboard**
   - Go to https://dashboard.stripe.com/test/products
   - Edit "Encypher Professional" product
   - Add new price: $109/month
   - Copy new price ID: `price_NEW123`

2. **Update .env**
   ```bash
   STRIPE_PRICE_PROFESSIONAL_MONTHLY=price_NEW123
   ```

3. **Restart service**
   ```bash
   ./start-dev.sh --rebuild
   ```

4. **Verify in logs**
   ```
   INFO: ✅ Validated price professional_monthly: price_NEW123 ($109.00/month)
   ```

### Scenario 2: New Tier (Uncommon)

If you add a new tier (e.g., "Enterprise"):

1. **Run setup script** (or create manually in Stripe)
   ```bash
   cd services/billing-service
   # Modify setup script to include enterprise tier
   uv run python ../../scripts/setup_stripe_products.py
   ```

2. **Add to .env**
   ```bash
   STRIPE_PRICE_ENTERPRISE_MONTHLY=price_XYZ
   STRIPE_PRICE_ENTERPRISE_ANNUAL=price_ABC
   ```

3. **Update code**
   - Add to `config.py` settings
   - Add to `price_cache.py` price_map
   - Add to validation list

---

## 🧪 Testing

### Test Startup Validation

```bash
cd services/billing-service

# Test with valid config
uv run python -m app.main

# Test with invalid price ID
# Edit .env: STRIPE_PRICE_PROFESSIONAL_MONTHLY=price_INVALID
uv run python -m app.main
# Should log: ❌ Failed to validate price professional_monthly
```

### Test Price Lookup

```bash
cd services/billing-service
uv run python -c "
from app.services.price_cache import get_stripe_price_id

price_id = get_stripe_price_id('professional', 'monthly')
print(f'Professional Monthly: {price_id}')

price_id = get_stripe_price_id('business', 'annual')
print(f'Business Annual: {price_id}')
"
```

---

## 📊 Comparison: .env vs API Fetching

| Aspect | .env (Current) | API Fetching |
|--------|---------------|--------------|
| **Performance** | ✅ Instant | ❌ ~200-500ms per lookup |
| **Reliability** | ✅ Always available | ❌ Depends on Stripe API |
| **Simplicity** | ✅ Simple config | ❌ More complex code |
| **Validation** | ✅ On startup | ✅ Real-time |
| **Cost** | ✅ Zero API calls | ❌ API calls for every lookup |
| **Flexibility** | ⚠️  Manual updates | ✅ Auto-sync |
| **Best for** | ✅ Stable pricing | ❌ Dynamic pricing |

**Verdict**: For your use case (2 tiers, stable pricing), .env is the clear winner.

---

## 🔐 Security Notes

- ✅ Price IDs are **not secret** - safe to commit to git
- ✅ API keys are **secret** - never commit to git
- ✅ Different price IDs for test vs production
- ✅ Validation ensures no typos in production

---

## 🐛 Troubleshooting

### "Price validation failed on startup"

**Cause**: Price ID in .env doesn't exist in Stripe

**Solution**:
1. Check Stripe Dashboard for correct price ID
2. Verify you're using test price IDs with test API key
3. Run setup script to create missing prices

### "Service starts but checkout fails"

**Cause**: Price ID is invalid but validation was skipped

**Solution**:
1. Check startup logs for validation warnings
2. Verify STRIPE_API_KEY is set in .env
3. Manually test price ID in Stripe Dashboard

### "Validation takes too long"

**Cause**: Slow network or Stripe API latency

**Solution**:
- Validation is async and non-blocking
- Service will start even if validation is slow
- Check network connectivity to Stripe API

---

## 📚 Related Documentation

- [Stripe Setup Guide](../../../docs/STRIPE_SETUP_GUIDE.md)
- [Stripe Service API](../app/services/stripe_service.py)
- [Price Cache Implementation](../app/services/price_cache.py)
- [Stripe Dashboard](https://dashboard.stripe.com)
