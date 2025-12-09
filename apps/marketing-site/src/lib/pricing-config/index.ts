/**
 * AUTO-GENERATED FILE - DO NOT MODIFY
 * 
 * Source: packages/pricing-config/src/
 * Changes here will be overwritten on next build.
 * 
 * To update: edit the source file, then run npm run build.
 */

/**
 * @encypher/pricing-config
 * 
 * Shared pricing configuration for all Encypher properties.
 * This is the single source of truth for:
 * - Tier definitions (prices, features, limits)
 * - Coalition revenue share percentages
 * - Helper functions for formatting and calculations
 * 
 * Used by:
 * - apps/marketing-site (pricing page)
 * - apps/dashboard (billing page)
 * - services/billing-service (reference, API returns same data)
 * 
 * @see docs/pricing/PRICING_STRATEGY.md for full strategy documentation
 */

// Types
export type {
  TierId,
  TierConfig,
  TiersConfig,
  TierPricing,
  TierLimits,
  CoalitionRevShare,
} from './types';

// Tier configuration and helpers
export {
  PRICING_TIERS,
  getTier,
  getAllTiers,
  getSelfServeTiers,
  getPopularTier,
  formatPrice,
  formatRevShare,
} from './tiers';

// Coalition configuration and helpers
export {
  getRevShare,
  calculatePublisherEarnings,
  COALITION_VALUE_PROPS,
  EARNINGS_EXAMPLES,
} from './coalition';
