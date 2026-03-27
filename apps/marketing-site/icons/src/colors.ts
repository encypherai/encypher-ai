/**
 * Encypher brand color constants.
 * SSOT for all icon color references.
 */

export const BRAND_COLORS = {
  navy: "#1b2f50",
  azure: "#2A87C4",
  teal: "#00CED1",
  white: "#ffffff",
} as const;

export type BrandColor = keyof typeof BRAND_COLORS;
