/**
 * AUTO-GENERATED FILE - DO NOT MODIFY
 * 
 * Source: packages/pricing-config/src/
 * Changes here will be overwritten on next build.
 * 
 * To update: edit the source file, then run npm run build.
 */

/**
 * Encypher Publisher Pricing Types — Freemium Model (Feb 2026)
 *
 * Model: Free infrastructure → Paid enforcement add-ons → Licensing revenue share
 * Rev share: Coalition 60/40, Self-Service 80/20 (flat across all tiers)
 *
 * @see docs/new_publisher_pricing_model_feb_2026.md
 */

/** Core tier identifiers: free signing infra or enterprise */
export type TierId = 'free' | 'enterprise';

export interface LicensingRevShare {
  coalition: { publisher: 60; encypher: 40 };
  selfService: { publisher: 80; encypher: 20 };
}

export interface FreeTierLimits {
  documentsPerMonth: number;
  overagePerDoc: number;
  verificationRequests: number;
  publicApiLookups: number;
}

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
  priceMonthly: number;
  pricePerUnit?: number;
  unitLabel?: string;
  description: string;
  includes?: string[];
  volumePricing?: VolumePrice[];
  replaces?: string;
  requires?: string;
  /** Feature not yet available — show 'Coming Soon' instead of price */
  comingSoon?: boolean;
}

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

export interface FreeTierConfig {
  id: 'free';
  name: string;
  signingFeatures: string[];
  distributionFeatures: string[];
  coalitionFeatures: string[];
  limits: FreeTierLimits;
  target: string;
}

export interface PricingConfig {
  freeTier: FreeTierConfig;
  enterprise: EnterpriseConfig;
  addOns: AddOnConfig[];
  bundles: BundleConfig[];
  revShare: LicensingRevShare;
}
