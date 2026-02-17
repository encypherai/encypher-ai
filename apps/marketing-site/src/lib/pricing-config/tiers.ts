/**
 * AUTO-GENERATED FILE - DO NOT MODIFY
 * 
 * Source: packages/pricing-config/src/
 * Changes here will be overwritten on next build.
 * 
 * To update: edit the source file, then run npm run build.
 */

import type {
  FreeTierConfig,
  EnterpriseConfig,
  AddOnConfig,
  BundleConfig,
  LicensingRevShare,
  PricingConfig,
} from './types';

/**
 * Encypher Publisher Pricing — Freemium Model (Feb 2026)
 *
 * Source of truth for all pricing across:
 * - Marketing site
 * - Dashboard
 * - Billing service (reference)
 *
 * Model: Free infrastructure → Paid enforcement tools → Licensing revenue share
 *
 * @see docs/new_publisher_pricing_model_feb_2026.md
 */

// ---------------------------------------------------------------------------
// Licensing Revenue Share — flat across ALL tiers
// ---------------------------------------------------------------------------

export const LICENSING_REV_SHARE: LicensingRevShare = {
  coalition: { publisher: 60, encypher: 40 },
  selfService: { publisher: 80, encypher: 20 },
};

// ---------------------------------------------------------------------------
// Free Tier — Full Signing Infrastructure
// ---------------------------------------------------------------------------

export const FREE_TIER: FreeTierConfig = {
  id: 'free',
  name: 'Free',
  signingFeatures: [
    'C2PA 2.3-compliant document signing',
    'Sentence-level Merkle tree authentication',
    'Invisible Unicode embeddings — survive copy-paste',
    'Public verification pages with shareable URLs',
    'Public verification API — no auth required',
    'Tamper detection for signed content',
    'Custom metadata (author, publisher, license, tags)',
  ],
  distributionFeatures: [
    'WordPress plugin — auto-sign on publish',
    'REST API with Python SDK',
    'CLI tool for local signing',
    'GitHub Action for CI/CD integration',
    'Browser extension for verification',
  ],
  coalitionFeatures: [
    'Auto-enrolled in Encypher Coalition',
    'Content indexed for coalition licensing',
    'Basic attribution view',
    'Coalition dashboard with content stats',
  ],
  limits: {
    documentsPerMonth: 1000,
    overagePerDoc: 0.02,
    verificationRequests: -1,
    publicApiLookups: -1,
  },
  target: 'Individual bloggers, small to mid-size publishers, independent media, academic researchers, content marketing teams, WordPress site owners',
};

// ---------------------------------------------------------------------------
// Freemium Add-Ons — self-service, no sales call required
// ---------------------------------------------------------------------------

export const ADD_ONS: AddOnConfig[] = [
  // --- Enforcement Add-Ons ---
  {
    id: 'attribution-analytics',
    name: 'Attribution Analytics',
    category: 'enforcement',
    priceMonthly: 0,
    description: 'Full dashboard showing where your signed content appears in AI outputs. Usage patterns, frequency, context analysis.',
    includes: [
      'Where your signed content appears in AI model outputs',
      'Which AI companies are using your content and how frequently',
      'Usage context — training, grounding, retrieval, direct reproduction',
      'Trend data over time',
      'Export targeting lists for formal notice campaigns',
    ],
    comingSoon: true,
  },
  {
    id: 'formal-notice',
    name: 'Formal Notice Package',
    category: 'enforcement',
    priceMonthly: 0,
    description: 'Cryptographically-backed formal notice to a specific AI company establishing willful infringement framework.',
    includes: [
      'Formal notification letter with cryptographic evidence citations',
      'Verification API access instructions for the recipient',
      'Documentation of marked content in their training pipeline',
      'Chain-of-custody record for the notification itself',
      'Delivery confirmation and timestamped proof of receipt',
    ],
    comingSoon: true,
  },
  {
    id: 'evidence-package',
    name: 'Evidence Package',
    category: 'enforcement',
    priceMonthly: 0,
    description: 'Court-ready evidence bundle for a specific infringement claim.',
    includes: [
      'Merkle tree proofs establishing sentence-level provenance',
      'Chain-of-custody documentation from signing through detection',
      'Tamper-evident manifest records',
      'Formal notice delivery records (if applicable)',
      'Timeline reconstruction',
      'Cryptographic verification instructions for opposing counsel',
      'Export in standard litigation support formats',
    ],
    comingSoon: true,
  },

  // --- Infrastructure Add-Ons ---
  {
    id: 'custom-signing-identity',
    name: 'Custom Signing Identity',
    category: 'infrastructure',
    priceMonthly: 9,
    description: 'Unlock a custom signer label for your verified organization identity in signed and verified content.',
  },
  {
    id: 'white-label-verification',
    name: 'White-Label Verification',
    category: 'infrastructure',
    priceMonthly: 299,
    description: 'Verification pages hosted on your domain with your branding. Remove Encypher branding from all public-facing verification.',
    requires: 'custom-signing-identity',
  },
  {
    id: 'custom-verification-domain',
    name: 'Custom Verification Domain',
    category: 'infrastructure',
    priceMonthly: 29,
    description: 'Point a custom domain to your verification pages without full white-label. Quick DNS setup, no development required.',
  },
  {
    id: 'byok',
    name: 'BYOK (Bring Your Own Keys)',
    category: 'infrastructure',
    priceMonthly: 499,
    description: 'Use your organization\'s existing PKI infrastructure and signing certificates. Validated against C2PA trust list.',
  },

  // --- Operations Add-Ons ---
  {
    id: 'bulk-archive-backfill',
    name: 'Bulk Archive Backfill',
    category: 'operations',
    priceMonthly: 0,
    pricePerUnit: 0.01,
    unitLabel: '/document',
    description: 'One-time batch signing of existing content archives. Sign 5 years of articles in one operation.',
  },
  {
    id: 'data-export',
    name: 'Data Export (Full)',
    category: 'operations',
    priceMonthly: 0,
    pricePerUnit: 49,
    unitLabel: '/export',
    description: 'Full export of all attribution and analytics data as CSV/JSON.',
  },
  {
    id: 'priority-support',
    name: 'Priority Support',
    category: 'operations',
    priceMonthly: 199,
    description: 'Email support with 4-hour response SLA during business hours. Dedicated onboarding assistance. Priority bug fixes.',
  },
];

// ---------------------------------------------------------------------------
// Bundles
// ---------------------------------------------------------------------------

export const BUNDLES: BundleConfig[] = [
  {
    id: 'enforcement-bundle',
    name: 'Enforcement Bundle',
    priceMonthly: 0,
    includes: [
      'Attribution Analytics',
      '2 Formal Notices per month',
      '1 Evidence Package per month',
    ],
    savings: '57%',
    description: 'The "I want to start licensing" package. Full enforcement pipeline in one subscription.',
    comingSoon: true,
  },
  {
    id: 'publisher-identity',
    name: 'Publisher Identity',
    priceMonthly: 329,
    includes: [
      'Custom Signing Identity ($9/mo value)',
      'White-Label Verification ($299/mo value)',
      'Custom Verification Domain ($29/mo value)',
    ],
    savings: '2%',
    description: 'Professional brand presence on all verification pages and signed content.',
  },
  {
    id: 'full-stack',
    name: 'Full Stack',
    priceMonthly: 0,
    includes: [
      'Enforcement Bundle',
      'Publisher Identity',
    ],
    savings: '51%',
    description: 'Everything you need to sign, enforce, and license — with your brand on everything.',
    comingSoon: true,
  },
];

// ---------------------------------------------------------------------------
// Enterprise Tier
// ---------------------------------------------------------------------------

export const ENTERPRISE_TIER: EnterpriseConfig = {
  id: 'enterprise',
  name: 'Enterprise',
  tiers: [
    { label: 'Tier 1 Publisher', licensingPotential: '>$20M', implementationFee: '$30K' },
    { label: 'Tier 2 Publisher', licensingPotential: '$3–20M', implementationFee: '$20K' },
    { label: 'Tier 3 Publisher', licensingPotential: '<$3M', implementationFee: '$10K' },
  ],
  features: [
    'Unlimited document signing (no monthly cap)',
    'Unlimited sentence-level Merkle tree authentication',
    'Unlimited invisible embeddings',
    'Unlimited verification and public API',
    'All add-ons included at no additional charge',
    'Attribution Analytics — full dashboard, unlimited',
    'Formal Notice Generation — unlimited',
    'Evidence Package Generation — unlimited',
    'Custom Signing Identity',
    'White-Label Verification',
    'Bulk Archive Backfill — unlimited',
    'BYOK / Custom Certificates',
    'Full Data Export — unlimited',
    'Priority Support — included',
  ],
  exclusiveCapabilities: [
    'Streaming LLM signing (WebSocket/SSE)',
    'OpenAI-compatible /chat/completions endpoint with automatic signing',
    'Custom C2PA assertions and schema registry',
    'C2PA provenance chain — full edit history tracking',
    'Batch operations (100+ documents per request)',
    'Document revocation capability (StatusList2021)',
    'Robust fingerprinting — survives paraphrasing, rewriting, translation',
    'Multi-source attribution with authority ranking',
    'Fuzzy fingerprint matching',
    'Plagiarism detection with Merkle proof linkage',
    'Dedicated SLA — 99.9% uptime, 15-minute incident response',
    '24/7 priority support with named account manager',
    'SSO integration (SAML, OAuth)',
    'Team management with role-based access controls',
    'Webhooks for signing, verification, and attribution events',
    'Full audit trail for compliance',
  ],
  foundingCoalition: [
    'Implementation fee waived',
    'Same licensing revenue splits as all tiers',
    'Syracuse Symposium seat — define market licensing frameworks',
    'Advisory board participation',
    'Priority coalition positioning in all licensing negotiations',
  ],
};

// ---------------------------------------------------------------------------
// Complete pricing configuration
// ---------------------------------------------------------------------------

export const PRICING_CONFIG: PricingConfig = {
  freeTier: FREE_TIER,
  enterprise: ENTERPRISE_TIER,
  addOns: ADD_ONS,
  bundles: BUNDLES,
  revShare: LICENSING_REV_SHARE,
};

// ---------------------------------------------------------------------------
// Helper functions
// ---------------------------------------------------------------------------

/** Get the free tier configuration */
export function getFreeTier(): FreeTierConfig {
  return FREE_TIER;
}

/** Get the enterprise tier configuration */
export function getEnterpriseTier(): EnterpriseConfig {
  return ENTERPRISE_TIER;
}

/** Get all add-ons */
export function getAllAddOns(): AddOnConfig[] {
  return ADD_ONS;
}

/** Get add-ons by category */
export function getAddOnsByCategory(category: AddOnConfig['category']): AddOnConfig[] {
  return ADD_ONS.filter(a => a.category === category);
}

/** Get a specific add-on by ID */
export function getAddOn(id: string): AddOnConfig | undefined {
  return ADD_ONS.find(a => a.id === id);
}

/** Get all bundles */
export function getAllBundles(): BundleConfig[] {
  return BUNDLES;
}

/** Get a specific bundle by ID */
export function getBundle(id: string): BundleConfig | undefined {
  return BUNDLES.find(b => b.id === id);
}

/** Format add-on price for display */
export function formatAddOnPrice(addOn: AddOnConfig): string {
  if (addOn.priceMonthly > 0) {
    return `$${addOn.priceMonthly}/mo`;
  }
  if (addOn.pricePerUnit !== undefined && addOn.pricePerUnit > 0) {
    return `$${addOn.pricePerUnit}${addOn.unitLabel || ''}`;
  }
  return 'Free';
}

/** Format bundle price for display */
export function formatBundlePrice(bundle: BundleConfig): string {
  return `$${bundle.priceMonthly}/mo`;
}

/** Format revenue share for display */
export function formatRevShare(type: 'coalition' | 'selfService'): string {
  const share = LICENSING_REV_SHARE[type];
  return `${share.publisher}/${share.encypher}`;
}
