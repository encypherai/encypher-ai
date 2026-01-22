/**
 * AUTO-GENERATED FILE - DO NOT MODIFY
 * 
 * Source: packages/pricing-config/src/
 * Changes here will be overwritten on next build.
 * 
 * To update: edit the source file, then run npm run build.
 */

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
      'C2PA signing (1K/mo)',
      'Unlimited verifications',
      '2 API keys',
      'Community support',
      '7-day analytics',
      'Auto-join licensing coalition',
    ],
    limits: {
      apiKeys: 2,
      rateLimit: 10,
      c2paSignatures: 1000, // Soft cap for abuse prevention
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
      'Sentence-level Merkle roots (5K/mo)',
      'C2PA + Merkle encoding choice',
      'Source attribution (10K lookups/mo)',
      'Invisible embeddings',
      '10 API keys',
      'Email support (48hr SLA)',
      '90-day analytics',
      'Bring Your Own Keys (BYOK)',
      'WordPress Pro (no branding)',
    ],
    limits: {
      apiKeys: 10,
      rateLimit: 50,
      c2paSignatures: -1, // Unlimited
      sentencesTracked: 50000,
      merkleEncodings: 5000,
      attributionLookups: 10000,
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
      'Merkle encodings (10K/mo)',
      'Similarity detection (5K/mo)',
      'Source attribution (50K lookups/mo)',
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
      merkleEncodings: 10000,
      attributionLookups: 50000,
      plagiarismChecks: 5000,
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
 * Note: Per PRD, specific percentages are removed from public marketing pages.
 * Actual terms are discussed during sales consultation.
 */
export function formatRevShare(tier: TierConfig): string {
  if (tier.enterprise) {
    return 'Best terms available';
  }
  if (tier.id === 'business') {
    return 'Premium revenue share';
  }
  if (tier.id === 'professional') {
    return 'Enhanced revenue share';
  }
  return 'Standard revenue share';
}
