/**
 * @encypher/pricing-config — Freemium Model (Feb 2026)
 *
 * Shared pricing configuration for all Encypher properties.
 * Single source of truth for:
 * - Free tier (full signing infrastructure)
 * - Freemium add-ons (enforcement, infrastructure, operations)
 * - Bundles (Enforcement, Publisher Identity, Full Stack)
 * - Enterprise tier (custom implementation)
 * - Licensing revenue share (60/40 coalition, 80/20 self-service)
 *
 * Used by:
 * - apps/marketing-site (pricing page)
 * - apps/dashboard (billing page)
 * - services/billing-service (reference)
 *
 * @see docs/new_publisher_pricing_model_feb_2026.md
 */

// Types
export type {
  TierId,
  LicensingRevShare,
  FreeTierLimits,
  AddOnCategory,
  VolumePrice,
  AddOnConfig,
  BundleConfig,
  EnterpriseTierPricing,
  EnterpriseConfig,
  FreeTierConfig,
  PricingConfig,
} from './types';

// Pricing data and helpers
export {
  LICENSING_REV_SHARE,
  FREE_TIER,
  ADD_ONS,
  BUNDLES,
  ENTERPRISE_TIER,
  PRICING_CONFIG,
  getFreeTier,
  getEnterpriseTier,
  getAllAddOns,
  getAddOnsByCategory,
  getAddOn,
  getAllBundles,
  getBundle,
  formatAddOnPrice,
  formatBundlePrice,
  formatRevShare,
} from './tiers';

// Coalition & licensing helpers
export {
  getRevShare,
  calculatePublisherEarnings,
  COALITION_VALUE_PROP,
  LICENSING_TRACKS,
  WORKED_EXAMPLES,
} from './coalition';
