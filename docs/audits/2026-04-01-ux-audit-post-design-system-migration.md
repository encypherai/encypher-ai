# UX/UI Audit - Encypher (Post-Design System SSOT Migration)

**Date:** 2026-04-01 | **Version:** v2 (post-migration) | **Overall Score:** 7.3 / 10

## Context

Encypher is an AI governance and content provenance platform targeting Fortune 500 GCs, compliance officers, and publishers. This audit evaluates both the marketing site and dashboard after the Design System SSOT Migration (TEAM_292), which unified 27 shadcn/ui components into a shared @encypher/design-system package, aligned color tokens across both apps, replaced hardcoded hex values with semantic tokens, and extended brand iconography (EncypherMark) across 21 pages.

**Pages reviewed:** Marketing site homepage, pricing, platform, try, content-provenance, solutions/publishers, enterprise, tools/encode-decode. Dashboard login, signup, forgot-password, loading-preview.

**Limitation:** Dashboard interior pages (authenticated views) could not be reviewed - backend API not running in this environment. Dashboard audit is limited to pre-auth flows.

## Score Summary

| Group | Category | Score | Grade |
|---|---|---|---|
| Visual | Color Palette | 8.0 | B |
| Visual | Typography | 7.0 | B |
| Visual | Iconography | 7.5 | B |
| Visual | Spacing & Layout | 7.5 | B |
| IA | Content Hierarchy | 7.5 | B |
| IA | Navigation Structure | 7.5 | B |
| IA | Onboarding UX | 7.0 | B |
| Functional | Data Presentation | 6.5 | C |
| Functional | Actionability | 8.0 | B |
| Functional | Empty/Zero States | 6.0 | C |
| Brand | Brand Identity | 8.0 | B |
| Brand | Professional Polish | 7.0 | B |
| **Overall** | | **7.3** | **B** |

Grade: A (9-10), B (7-8.9), C (5-6.9), D (3-4.9), F (0-2.9)

## Detailed Assessment

### Visual Design

**Color Palette (8.0):** The migration successfully eliminated all hardcoded #2a87c4 hex values in favor of semantic tokens (--primary, --accent, --destructive). The four-color brand palette (delft-blue, azure, columbia-blue, cyber-teal) is now applied consistently via CSS custom properties from a single theme.css. The primary azure CTA buttons, the delft-blue heading text, and the columbia-blue accents create clear visual hierarchy. One concern: the dashboard signup page renders in light mode while the login page renders in dark mode, creating a jarring tonal shift between adjacent auth flows.

**Typography (7.0):** Roboto is applied consistently with a clear headline/body/caption hierarchy. Marketing site headlines are bold and scan well at 1440px. The type scale covers 4-5 distinct sizes across pages. However, body text on marketing pages (muted-foreground #64748b) could use slightly more contrast against the white background for longer-form content on pages like content-provenance. The dashboard login page typography is clean with proper label/input hierarchy.

**Iconography (7.5):** The EncypherMark replacement (from generic CheckCircle2 to branded EncypherMark) across 21 pages creates a strong, recognizable icon language. The azure-colored check circle with the Encypher "E" pattern is distinctive and consistent. Feature comparison tables (enterprise page) show icons at a uniform size with consistent stroke weight. The lucide-react icons used for navigation and feature categories (publishers, AI labs, enterprises) are stylistically compatible.

**Spacing & Layout (7.5):** Marketing site uses a consistent max-width container with responsive padding. Card components (pricing, persona sections) follow a uniform border-radius and shadow pattern. The two-panel login/signup layout with the animated provenance visualization on the right panel is well-balanced. The /try page has clean vertical rhythm with numbered steps. Spacing between sections on the homepage could be more generous to let each section breathe.

### Information Architecture

**Content Hierarchy (7.5):** Homepage hero immediately establishes the value proposition ("Your Content Carries Its Own Proof of Ownership"). The three-tier persona cards (Publishers, AI Labs, Enterprises) below provide clear audience segmentation. Pricing page leads with the "Free to Sign. Paid to License." headline, immediately resolving the cost question. The enterprise feature comparison table scans well with clear column headers and the EncypherMark check pattern.

**Navigation Structure (7.5):** Marketing navbar organizes content into logical groups (Solutions, Tools, Resources, Pricing, Company, Platform). Active states visible on links. "Get Started" CTA is visually prominent in the top-right with a distinct fill button style. The dashboard login provides clear pathways: OAuth buttons above, email/password below, forgot-password and create-account links positioned at expected locations.

**Onboarding UX (7.0):** The /try page is a strong onboarding tool - "See It Work in 30 Seconds" with pre-filled sample text and a single "Sign This Text" CTA. The dashboard signup form is straightforward (name, email, password, confirm). The loading-preview page shows a polished branded loading state (EncypherMark with progress bar) in both light and dark modes. Missing: no progressive disclosure or guided first-run experience visible.

### Functional Design

**Data Presentation (6.5):** Limited assessment - dashboard interior pages (analytics, audit logs, compliance) were not accessible. The enterprise feature comparison table presents data clearly with feature rows and tier columns. Pricing page shows tier differentiation with feature lists and check marks. No trend indicators, sparklines, or metric dashboards were visible in the audited pages.

**Actionability (8.0):** Every marketing page has a clear primary CTA. Button hierarchy is well-defined: filled primary (azure) for main action, outline for secondary, ghost/link for tertiary. The /try page connects the demo directly to the signup flow. Platform page offers three CTAs at different commitment levels ("Get Started Free", "See Live Demo", "Contact Sales"). The tools/encode-decode page correctly disables the "Sign Text" button when the textarea is empty, providing appropriate state feedback.

**Empty/Zero States (6.0):** The 404 page is minimal - "This page could not be found" with no guidance or navigation back. The tools/encode-decode page shows an empty textarea with a clear placeholder, but no sample text or guidance beyond the placeholder. The /try page demonstrates the correct pattern: pre-filled sample text with an explanation ("Sample article pre-filled. Edit it or paste your own."). Dashboard empty states could not be assessed.

### Brand & Differentiation

**Brand Identity (8.0):** The design system migration significantly strengthened brand consistency. The EncypherMark icon appearing across 21 pages creates a recognizable visual pattern that competitors lack. The animated provenance visualization on the login/signup right panel (floating model IDs, timestamps, signatures) is a distinctive brand element that communicates the product's purpose visually. The C2PA badge ("Built on the C2PA standard") and coalition logos (C2PA, Content Authenticity Initiative) reinforce credibility. The color palette (navy + azure + light blue) reads as enterprise-serious without being sterile.

**Professional Polish (7.0):** Components render cleanly across all reviewed pages. Border-radius, shadows, and spacing are consistent. The Cloudflare Turnstile widget on auth pages has a visible "For testing only" banner that should not appear in production. The dashboard has a Next.js dev mode indicator (bottom-left "N" icon) and "2 Issues" badge visible on some pages. The marketing site 404 page lacks polish. Login error state ("Incorrect email or password") is clean and appropriately styled.

## Prioritized Recommendations

| # | Recommendation | Impact | Effort | Priority |
|---|---|---|---|---|
| 1 | Fix dashboard auth mode inconsistency: login renders dark mode, signup renders light mode. Both should use the same theme for a cohesive auth flow. | High | S | P0 |
| 2 | Improve 404 page: add navigation links, search, or suggested pages. Current bare "This page could not be found" is a dead end for SEO traffic and prospects. | Med | S | P1 |
| 3 | Run authenticated dashboard audit: the interior pages (analytics, compliance, settings, team) represent the core product experience for enterprise buyers. Cannot assess data presentation, empty states, or navigation without API access. | High | M | P1 |
| 4 | Add semantic success/warning token usage to the feature comparison tables and tier badges. The green check marks on pricing pages still use utility classes rather than the new --success token. | Low | S | P2 |
| 5 | Remove dead local shadcn component files from both apps' src/components/ui/ directories. Shared components now import from @encypher/design-system, so the duplicate local files add confusion for developers. | Med | S | P2 |

## Migration Verification Summary

The design system SSOT migration is visually successful:

- **Color tokens:** All reviewed pages use semantic tokens (--primary, --accent, etc.) rather than hardcoded hex. No visual regressions detected.
- **Component rendering:** Buttons, cards, inputs, labels, badges, tabs, and dialogs render correctly from the shared design system.
- **EncypherMark icons:** Consistently rendered at uniform size and azure color across all pages where replacements were made.
- **Theme alignment:** Marketing site and dashboard login share the same brand palette (delft-blue backgrounds, azure accents, columbia-blue highlights).
- **CTA hierarchy:** Primary/outline/ghost button variants work correctly with semantic color tokens.

**One concern to monitor:** The dashboard's old design system had primary=columbia-blue and accent=blue-ncs (swapped from marketing site). The new unified theme sets primary=blue-ncs (#2a87c4). Dashboard interior pages may need spot-checking once the API is available, as any hardcoded references to the old semantic mapping could produce unexpected colors.
