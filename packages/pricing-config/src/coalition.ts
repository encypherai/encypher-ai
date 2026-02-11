import type { LicensingRevShare } from './types';
import { LICENSING_REV_SHARE } from './tiers';

/**
 * Coalition & Licensing Revenue Configuration — Freemium Model (Feb 2026)
 *
 * Two-track licensing model (flat across ALL tiers):
 * - Coalition deals (60/40): Encypher negotiates on behalf of the coalition
 * - Self-service deals (80/20): Publisher negotiates directly
 *
 * @see docs/new_publisher_pricing_model_feb_2026.md
 */

/**
 * Get the licensing revenue share configuration
 */
export function getRevShare(): LicensingRevShare {
  return LICENSING_REV_SHARE;
}

/**
 * Calculate publisher earnings from a gross licensing amount
 */
export function calculatePublisherEarnings(
  grossAmount: number,
  track: 'coalition' | 'selfService'
): { publisher: number; encypher: number } {
  const share = LICENSING_REV_SHARE[track];
  return {
    publisher: (grossAmount * share.publisher) / 100,
    encypher: (grossAmount * share.encypher) / 100,
  };
}

/**
 * Coalition value proposition — single message for all publishers
 */
export const COALITION_VALUE_PROP = {
  headline: 'Free to sign. Paid to enforce. Aligned on outcomes.',
  subheadline: 'Every signed document strengthens the coalition. We only charge for enforcement tools — and we only win when you win.',
  philosophy: 'Every signed document strengthens the coalition. Every publisher in the network increases leverage for all members. We don\'t charge for signing because signing is the supply that makes the marketplace valuable. We charge for the tools that extract value from the network — enforcement, evidence, analytics, and identity.',
} as const;

/**
 * Two-track licensing explanation
 */
export const LICENSING_TRACKS = {
  coalition: {
    name: 'Coalition Deals',
    split: '60/40',
    publisherPercent: 60,
    encypherPercent: 40,
    description: 'Encypher negotiates licensing deals on behalf of the coalition. We do the work — formal notice, evidence, negotiation. Publishers get 60%, Encypher takes 40%.',
  },
  selfService: {
    name: 'Self-Service Deals',
    split: '80/20',
    publisherPercent: 80,
    encypherPercent: 20,
    description: 'Publishers use our signing tech, formal notice tools, and evidence packages to negotiate their own deals directly with AI companies. They do the work — they keep more.',
  },
} as const;

/**
 * Worked examples from the pricing doc — for marketing/sales
 */
export const WORKED_EXAMPLES = {
  midSizePublisher: {
    title: 'Mid-Size Publisher (~$10M/year) — Self-Service Track',
    steps: [
      'Signs content on Free tier (no cost)',
      'Adds Attribution Analytics to identify AI companies',
      'Sends Formal Notices to AI companies',
      'Builds Evidence Package for licensing negotiation',
      'Negotiates a $2M licensing deal directly',
    ],
    result: {
      publisherKeeps: 1_600_000,
      encypherReceives: 400_000,
      enforcementSpend: 0,
      monthlyOngoing: 0,
      netNewRevenue: 1_600_000,
    },
    track: 'selfService' as const,
  },
  majorWireService: {
    title: 'Major Wire Service — Coalition Track',
    steps: [
      'Enterprise tier — unlimited signing, all tools included',
      'Encypher identifies widespread content usage across 8 AI companies',
      'Encypher serves formal notices, builds evidence packages, leads negotiation',
      'Coalition negotiates $15M deal; wire service attributed share: $5M',
    ],
    result: {
      publisherKeeps: 3_000_000,
      encypherReceives: 2_000_000,
      enforcementSpend: 0,
      monthlyOngoing: 0,
      netNewRevenue: 3_000_000,
    },
    track: 'coalition' as const,
  },
  regionalNews: {
    title: 'Regional News Publisher (~$2M/year) — Enforcement Bundle',
    steps: [
      'Signs content on Free tier (no cost)',
      'Subscribes to Enforcement Bundle',
      'Attribution Analytics reveals content in 3 AI company outputs',
      'Sends formal notices with monthly allocation',
      'Uses evidence package to support $300K licensing deal (self-service)',
    ],
    result: {
      publisherKeeps: 240_000,
      encypherReceives: 60_000,
      enforcementSpend: 0,
      monthlyOngoing: 0,
      netNewRevenue: 240_000,
    },
    track: 'selfService' as const,
  },
} as const;
