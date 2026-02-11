/**
 * Encypher Publisher Pricing Types — Freemium Model (Feb 2026)
 *
 * Model: Free infrastructure → Paid enforcement add-ons → Licensing revenue share
 * Rev share: Majority to publisher (flat across all tiers)
 *
 * @see docs/new_publisher_pricing_model_feb_2026.md
 */

// ---------------------------------------------------------------------------
// Tier identifiers
// ---------------------------------------------------------------------------

/** Core tier identifiers: free signing infra or enterprise */
export type TierId = 'free' | 'enterprise';

// ---------------------------------------------------------------------------
// Licensing revenue share (flat — same for all tiers)
// ---------------------------------------------------------------------------

export interface LicensingRevShare {
  /** Coalition deals: Encypher negotiates — publisher gets 60%, Encypher 40% */
  coalition: { publisher: 60; encypher: 40 };
  /** Self-service deals: Publisher negotiates — publisher gets 80%, Encypher 20% */
  selfService: { publisher: 80; encypher: 20 };
}

// ---------------------------------------------------------------------------
// Free tier usage limits
// ---------------------------------------------------------------------------

export interface FreeTierLimits {
  /** New documents signed per month */
  documentsPerMonth: number;
  /** Overage cost per document (USD) */
  overagePerDoc: number;
  /** Verification requests (-1 = unlimited) */
  verificationRequests: number;
  /** Public API lookups (-1 = unlimited) */
  publicApiLookups: number;
}

// ---------------------------------------------------------------------------
// Add-on definitions
// ---------------------------------------------------------------------------

export type AddOnCategory = 'enforcement' | 'infrastructure' | 'operations';

export interface VolumePrice {
  quantity: number | string;
  priceEach: number;
  savings?: string;
}

export interface AddOnConfig {
  id: string;
  name: string;
  category: AddOnCategory;
  /** Monthly price in USD (0 = one-time or per-unit) */
  priceMonthly: number;
  /** Per-unit price (for one-time purchases like notices, evidence, backfill) */
  pricePerUnit?: number;
  /** Unit label (e.g., '/notice', '/package', '/document', '/export') */
  unitLabel?: string;
  description: string;
  includes?: string[];
  volumePricing?: VolumePrice[];
  /** What this replaces (cost comparison) */
  replaces?: string;
  /** Requires another add-on */
  requires?: string;
  /** Feature not yet available — show 'Coming Soon' instead of price */
  comingSoon?: boolean;
}

// ---------------------------------------------------------------------------
// Bundle definitions
// ---------------------------------------------------------------------------

export interface BundleConfig {
  id: string;
  name: string;
  priceMonthly: number;
  includes: string[];
  savings: string;
  description: string;
  /** Feature not yet available — show 'Coming Soon' instead of price */
  comingSoon?: boolean;
}

// ---------------------------------------------------------------------------
// Enterprise tier
// ---------------------------------------------------------------------------

export interface EnterpriseTierPricing {
  label: string;
  licensingPotential: string;
  implementationFee: string;
}

export interface EnterpriseConfig {
  id: 'enterprise';
  name: string;
  tiers: EnterpriseTierPricing[];
  features: string[];
  exclusiveCapabilities: string[];
  foundingCoalition: string[];
}

// ---------------------------------------------------------------------------
// Core tier configuration (Free tier)
// ---------------------------------------------------------------------------

export interface FreeTierConfig {
  id: 'free';
  name: string;
  /** Feature list for display — signing & provenance */
  signingFeatures: string[];
  /** Distribution & tools */
  distributionFeatures: string[];
  /** Coalition membership features */
  coalitionFeatures: string[];
  /** Usage limits */
  limits: FreeTierLimits;
  /** Target customer description */
  target: string;
}

// ---------------------------------------------------------------------------
// Complete pricing configuration
// ---------------------------------------------------------------------------

export interface PricingConfig {
  freeTier: FreeTierConfig;
  enterprise: EnterpriseConfig;
  addOns: AddOnConfig[];
  bundles: BundleConfig[];
  revShare: LicensingRevShare;
}
