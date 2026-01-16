/**
 * AUTO-GENERATED FILE - DO NOT MODIFY
 * 
 * Source: packages/pricing-config/src/
 * Changes here will be overwritten on next build.
 * 
 * To update: edit the source file, then run npm run build.
 */

import type { CoalitionRevShare, TierId } from './types';
import { PRICING_TIERS } from './tiers';

/**
 * Coalition Revenue Share Configuration
 * 
 * The licensing coalition enables publishers to earn revenue when AI companies
 * use their content for training. Revenue share improves with higher tiers.
 * 
 * @see docs/pricing/PRICING_STRATEGY.md for full coalition economics
 */

/**
 * Get the revenue share for a specific tier
 */
export function getRevShare(tierId: TierId): CoalitionRevShare {
  return PRICING_TIERS[tierId].revShare;
}

/**
 * Calculate publisher earnings from a gross licensing amount
 */
export function calculatePublisherEarnings(
  grossAmount: number,
  tierId: TierId
): { publisher: number; encypher: number } {
  const revShare = getRevShare(tierId);
  return {
    publisher: (grossAmount * revShare.publisher) / 100,
    encypher: (grossAmount * revShare.encypher) / 100,
  };
}

/**
 * Coalition value propositions by tier
 */
export const COALITION_VALUE_PROPS = {
  starter: {
    headline: 'Get paid when AI uses your content',
    subheadline: 'Zero risk, pure upside. Sign unlimited content for free.',
  },
  professional: {
    headline: 'Track every sentence, earn more',
    subheadline: 'Know exactly which content drives AI value. Better rev share.',
  },
  business: {
    headline: 'Enterprise-grade tracking, best self-serve terms',
    subheadline: 'Merkle proofs, similarity detection, 75% revenue share.',
  },
  enterprise: {
    headline: 'Maximum revenue, custom terms',
    subheadline: 'Dedicated support, custom SLAs, 80%+ revenue share.',
  },
} as const;

/**
 * Example earnings projections (for marketing/sales)
 * Based on hypothetical AI licensing deals
 */
export const EARNINGS_EXAMPLES = {
  smallBlog: {
    description: 'Small blog (10K monthly visitors)',
    monthlyArticles: 20,
    estimatedAnnualLicensing: 500,
    byTier: {
      starter: 325,      // 65%
      professional: 350, // 70%
      business: 375,     // 75%
      enterprise: 400,   // 80%
    },
  },
  regionalNews: {
    description: 'Regional news site (500K monthly visitors)',
    monthlyArticles: 200,
    estimatedAnnualLicensing: 25000,
    byTier: {
      starter: 16250,      // 65%
      professional: 17500, // 70%
      business: 18750,     // 75%
      enterprise: 20000,   // 80%
    },
  },
  majorPublisher: {
    description: 'Major digital publisher (5M monthly visitors)',
    monthlyArticles: 1000,
    estimatedAnnualLicensing: 250000,
    byTier: {
      starter: 162500,      // 65%
      professional: 175000, // 70%
      business: 187500,     // 75%
      enterprise: 200000,   // 80%
    },
  },
} as const;
