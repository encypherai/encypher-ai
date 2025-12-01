# @encypher/pricing-config

Shared pricing configuration for all Encypher properties. This package is the **single source of truth** for pricing tiers, features, limits, and coalition revenue share.

## Usage

```typescript
import {
  PRICING_TIERS,
  getAllTiers,
  getSelfServeTiers,
  formatPrice,
  formatRevShare,
  calculatePublisherEarnings,
} from '@encypher/pricing-config';

// Get all tiers
const tiers = getAllTiers();

// Get self-serve tiers (excludes enterprise)
const selfServeTiers = getSelfServeTiers();

// Format for display
const price = formatPrice(tier, 'monthly'); // "$99" or "Free" or "Custom"
const revShare = formatRevShare(tier); // "70% you / 30% Encypher"

// Calculate earnings
const earnings = calculatePublisherEarnings(10000, 'professional');
// { publisher: 7000, encypher: 3000 }
```

## Tiers

| Tier | Price | Rev Share | Target |
|------|-------|-----------|--------|
| Starter | Free | 65/35 | Bloggers, small publishers |
| Professional | $99/mo | 70/30 | Regional news, niche pubs |
| Business | $499/mo | 75/25 | Major digital publishers |
| Enterprise | Custom | 80/20 | Global media giants |

## Used By

- `apps/marketing-site` - Pricing page
- `apps/dashboard` - Billing page
- `services/billing-service` - API reference (returns same data)

## Documentation

See [docs/pricing/PRICING_STRATEGY.md](../../docs/pricing/PRICING_STRATEGY.md) for the full pricing strategy.
