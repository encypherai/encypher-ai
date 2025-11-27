/**
 * Animation timing constants
 */
export const ANIMATION_DURATION = {
  fast: 0.3,
  normal: 0.6,
  slow: 1.0,
  verySlow: 1.5,
};

export const ANIMATION_EASING = {
  easeInOut: [0.65, 0, 0.35, 1],
  easeOut: [0.22, 1, 0.36, 1],
  easeIn: [0.4, 0, 1, 1],
  spring: { type: 'spring', stiffness: 100, damping: 15 },
};

/**
 * Section identifiers
 */
export const SECTIONS = {
  BLIND_SPOT: 1,
  BLACK_HOLE: 2,
  REGULATORY: 3,
  ANALYTICS: 4,
  SAFE_HARBOR: 5,
  INTEGRATION: 6,
} as const;

/**
 * Scroll thresholds
 */
export const SCROLL_THRESHOLDS = {
  section: 0.3,
  animation: 0.5,
};

/**
 * Breakpoints (matches Tailwind)
 */
export const BREAKPOINTS = {
  mobile: 0,
  tablet: 768,
  laptop: 1024,
  desktop: 1440,
} as const;

/**
 * Color scheme
 */
export const COLORS = {
  primary: {
    blue: '#3B82F6',
    cyan: '#06B6D4',
  },
  status: {
    success: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444',
  },
  text: {
    primary: '#F9FAFB',
    secondary: '#D1D5DB',
    muted: '#9CA3AF',
  },
} as const;

/**
 * Demo metrics (mock data)
 */
export const MOCK_METRICS = {
  rndCost: '2.7B',
  impressions: 2134567,
  engagementRate: 23.4,
  viralCoefficient: 2.3,
  timeToViral: 4.2,
  regulationsCount: 12,
  litigationCost: '3B+',
} as const;

/**
 * Regulatory data
 */
export const REGULATIONS = [
  {
    id: 'eu',
    region: 'EU',
    flag: '🇪🇺',
    name: 'EU AI Act',
    penalty: '€35M or 7% revenue',
    status: 'ACTIVE',
    year: 2024,
  },
  {
    id: 'china',
    region: 'China',
    flag: '🇨🇳',
    name: 'Watermarking Mandate',
    penalty: 'Business suspension',
    status: 'ACTIVE',
    year: 2023,
  },
  {
    id: 'california',
    region: 'California',
    flag: '🇺🇸',
    name: 'AB-2013',
    penalty: '$5K/violation',
    status: 'ACTIVE',
    year: 2024,
  },
  {
    id: 'italy',
    region: 'Italy',
    flag: '🇮🇹',
    name: 'Transparency Law',
    penalty: 'GDPR-level fines',
    status: 'ACTIVE',
    year: 2024,
  },
] as const;

/**
 * CTA labels
 */
export const CTA_LABELS = {
  primary: 'Schedule Technical Deep Dive',
  secondary: {
    docs: 'Download SDK Docs',
    examples: 'View Examples',
    roi: 'Calculate ROI',
    whitepaper: 'Read Whitepaper',
  },
} as const;
