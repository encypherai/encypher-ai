/**
 * AUTO-GENERATED FILE - DO NOT MODIFY
 * 
 * Source: packages/pricing-config/src/
 * Changes here will be overwritten on next build.
 * 
 * To update: edit the source file, then run npm run build.
 */

/**
 * Pricing tier identifiers
 */
export type TierId = 'starter' | 'professional' | 'business' | 'enterprise';

/**
 * Coalition revenue share configuration
 */
export interface CoalitionRevShare {
  /** Percentage the publisher receives (e.g., 65 = 65%) */
  publisher: number;
  /** Percentage Encypher receives (e.g., 35 = 35%) */
  encypher: number;
}

/**
 * Tier usage limits
 */
export interface TierLimits {
  /** Number of API keys allowed (-1 = unlimited) */
  apiKeys: number;
  /** Rate limit in requests per second (-1 = unlimited) */
  rateLimit: number;
  /** C2PA signatures per month (-1 = unlimited) */
  c2paSignatures: number;
  /** Sentences tracked per month (-1 = unlimited, 0 = not available) */
  sentencesTracked: number;
  /** Merkle encodings per month (-1 = unlimited, 0 = not available) */
  merkleEncodings?: number;
  /** Attribution lookups per month (-1 = unlimited, 0 = not available) */
  attributionLookups?: number;
  /** Plagiarism checks per month (-1 = unlimited, 0 = not available) */
  plagiarismChecks?: number;
}

/**
 * Pricing information for a tier
 */
export interface TierPricing {
  /** Monthly price in USD (0 = free) */
  monthly: number;
  /** Annual price in USD (0 = free, typically ~20% discount) */
  annual: number;
}

/**
 * Complete tier configuration
 */
export interface TierConfig {
  /** Unique tier identifier */
  id: TierId;
  /** Display name */
  name: string;
  /** Pricing information */
  price: TierPricing;
  /** Coalition revenue share split */
  revShare: CoalitionRevShare;
  /** Feature list for display */
  features: string[];
  /** Usage limits */
  limits: TierLimits;
  /** Target customer description */
  target: string;
  /** Whether this is the recommended/popular tier */
  popular?: boolean;
  /** Whether this requires custom/enterprise sales */
  enterprise?: boolean;
}

/**
 * All tiers configuration object
 */
export type TiersConfig = Record<TierId, TierConfig>;
