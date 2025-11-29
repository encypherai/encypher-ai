import type { TierConfig, TiersConfig, TierId } from './types';

/**
 * Encypher Pricing Tiers
 * 
 * Source of truth for all pricing across:
 * - Marketing site
 * - Dashboard
 * - Billing service (reference)
 * 
 * @see docs/pricing/PRICING_STRATEGY.md for full strategy documentation
 */
export const PRICING_TIERS: TiersConfig = {
  starter: {
    id: 'starter',
    name: 'Starter',
    price: {
      monthly: 0,
      annual: 0,
    },
    revShare: {
      publisher: 65,
      encypher: 35,
    },
    features: [
      'Unlimited C2PA signing',
      'Unlimited verifications',
      '2 API keys',
      'Community support',
      '7-day analytics',
      'Auto-join licensing coalition',
    ],
    limits: {
      apiKeys: 2,
      rateLimit: 10,
      c2paSignatures: 10000, // Soft cap for abuse prevention
      sentencesTracked: 0,   // Not available
    },
    target: 'Bloggers, small publishers',
  },

  professional: {
    id: 'professional',
    name: 'Professional',
    price: {
      monthly: 99,
      annual: 950, // ~20% discount
    },
    revShare: {
      publisher: 70,
      encypher: 30,
    },
    features: [
      'Everything in Starter',
      'Sentence-level tracking (50K/mo)',
      'Invisible embeddings',
      '10 API keys',
      'Email support (48hr SLA)',
      '90-day analytics',
      'BYOK encryption',
      'WordPress Pro (no branding)',
    ],
    limits: {
      apiKeys: 10,
      rateLimit: 50,
      c2paSignatures: -1, // Unlimited
      sentencesTracked: 50000,
    },
    target: 'Regional news, niche publications',
    popular: true,
  },

  business: {
    id: 'business',
    name: 'Business',
    price: {
      monthly: 499,
      annual: 4790, // ~20% discount
    },
    revShare: {
      publisher: 75,
      encypher: 25,
    },
    features: [
      'Everything in Professional',
      'Merkle tree encoding',
      'Plagiarism detection',
      'Source attribution API',
      'Batch operations (100 docs)',
      '50 API keys',
      'Priority support (24hr SLA)',
      '1-year analytics',
      'Team management (10 users)',
      'Audit logs',
    ],
    limits: {
      apiKeys: 50,
      rateLimit: 200,
      c2paSignatures: -1,
      sentencesTracked: 500000,
    },
    target: 'Major digital publishers',
  },

  enterprise: {
    id: 'enterprise',
    name: 'Enterprise',
    price: {
      monthly: 0, // Custom pricing
      annual: 0,  // Custom pricing
    },
    revShare: {
      publisher: 80,
      encypher: 20,
    },
    features: [
      'Everything in Business',
      'Unlimited everything',
      'Custom C2PA assertions',
      'SSO/SCIM integration',
      'Dedicated TAM + Slack',
      'Custom SLAs',
      'On-premise option',
      'White-label WordPress',
    ],
    limits: {
      apiKeys: -1,
      rateLimit: -1,
      c2paSignatures: -1,
      sentencesTracked: -1,
    },
    target: 'Global media giants, wire services',
    enterprise: true,
  },
} as const;

/**
 * Get a specific tier configuration
 */
export function getTier(tierId: TierId): TierConfig {
  return PRICING_TIERS[tierId];
}

/**
 * Get all tiers as an array (useful for mapping in UI)
 */
export function getAllTiers(): TierConfig[] {
  return Object.values(PRICING_TIERS);
}

/**
 * Get tiers available for self-serve (excludes enterprise)
 */
export function getSelfServeTiers(): TierConfig[] {
  return getAllTiers().filter(tier => !tier.enterprise);
}

/**
 * Get the popular/recommended tier
 */
export function getPopularTier(): TierConfig | undefined {
  return getAllTiers().find(tier => tier.popular);
}

/**
 * Format price for display
 */
export function formatPrice(tier: TierConfig, period: 'monthly' | 'annual' = 'monthly'): string {
  if (tier.enterprise) {
    return 'Custom';
  }
  const price = period === 'monthly' ? tier.price.monthly : tier.price.annual;
  if (price === 0) {
    return 'Free';
  }
  return `$${price}`;
}

/**
 * Format revenue share for display
 */
export function formatRevShare(tier: TierConfig): string {
  return `${tier.revShare.publisher}% you / ${tier.revShare.encypher}% Encypher`;
}
