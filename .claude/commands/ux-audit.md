---
description: "Perform structured UX/UI design audits on the Encypher enterprise dashboard. Use when the user uploads a screenshot, mockup, or wireframe and asks for design feedback, review, critique, grade, score, or audit."
---

# UX/UI Audit — Encypher Enterprise Dashboard

Perform structured, repeatable design audits on the Encypher enterprise dashboard. Produce scored rubrics, track improvement across versions, and deliver actionable recommendations grounded in who actually uses this product and what they need to accomplish.

## Product Context (Always Active)

**Product**: Encypher enterprise dashboard — a B2B SaaS platform for digital content verification, compliance monitoring, and enforcement management.

**Primary Users (ICP)**:
- **Enterprise General Counsels (GCs)**: Non-technical. Need compliance posture at a glance, audit trails for board reporting, risk signals that map to legal exposure. Assess Encypher during 30-minute sales engineering demos. First impressions determine 7-figure deal progression.
- **Compliance Officers / Legal Ops Managers**: Moderately technical. Daily operators. Need verification status dashboards, CDN analytics, enforcement pipelines, API key management. Care about efficiency and actionability — every extra click is friction.
- **DevOps / Security Engineers**: Technical. Configure integrations, manage API keys, review audit logs. Need clean data presentation, clear error states, and developer-grade UX (monospace, syntax highlighting, copy buttons).

**Stage**: Production SaaS with active enterprise pilots. Demo-readiness is critical — this product is shown to Fortune 500 C-suite in live sales calls.

**Dashboard Architecture** (Next.js App Router):
- Routes: /admin, /ai-crawlers, /analytics, /api-keys, /audit-logs, /billing, /cdn-analytics, /compliance, /docs, /enforcement, /governance, /health, /image-signing
- Key components: MobileNav, CommandPalette, NotificationCenter, OrganizationSwitcher, TourSpotlight, ActivityFeed, ApiAccessGate
- Design system: apps/dashboard/design-system/ + src/components/ui/
- Styling: Tailwind CSS

## Scoring Rubric (12 Categories, 0-10 each)

### Visual Design
| Category | What to evaluate for Encypher specifically |
|---|---|
| **Color palette** | Brand consistency (Encypher blues/teals), enterprise gravitas, status color semantics (verified/unverified/warning/critical) |
| **Typography** | Readability for legal professionals scanning dense data, hierarchy in compliance dashboards, monospace for API/code elements |
| **Iconography** | Verification status icons clarity, enforcement action icons, navigation icons recognizability |
| **Spacing & layout** | Dashboard density appropriate for data-heavy compliance views, card layouts, responsive behavior |

### Information Architecture
| Category | What to evaluate for Encypher specifically |
|---|---|
| **Content hierarchy** | Is verification status the most prominent element? Can a GC see compliance posture in <3 seconds? |
| **Navigation structure** | 13+ route sections — is the sidebar overwhelming? Can users find enforcement vs. compliance vs. audit logs intuitively? |
| **Onboarding UX** | First-run experience for enterprise pilot users, TourSpotlight effectiveness, empty state guidance |

### Functional Design
| Category | What to evaluate for Encypher specifically |
|---|---|
| **Data presentation** | CDN analytics charts, verification trend lines, audit log tables, compliance score visualizations |
| **Actionability** | Clear CTAs for enforcement actions, API key generation, compliance report export. Every screen should drive toward an outcome. |
| **Empty/zero states** | New org with no verifications yet, no enforcement actions, no API keys — are these states educational and motivating? |

### Brand & Differentiation
| Category | What to evaluate for Encypher specifically |
|---|---|
| **Brand identity** | Does this look like a premium enterprise security product? Would a GC trust their content verification to this? |
| **Professional polish** | Edge cases, loading states, error handling. A single janky animation during a demo can kill a deal. |

### Scoring Scale
- **0-3**: Broken or actively harmful to the demo
- **4-5**: Functional but would cause a prospect to hesitate
- **6-7**: Good, demo-safe, but room for improvement
- **8**: Strong — competitive with enterprise SaaS leaders
- **9**: Best-in-class for B2B security/compliance dashboards
- **10**: Sets the standard others copy

**Overall score** = arithmetic mean of all 12 categories, rounded to one decimal.

## Assessment Format

For each category, write 2-4 sentences covering:
1. What is working (name the specific element, color, layout choice)
2. What is not working (describe the specific problem, not just "could be better")
3. Why it matters for the ICP (connect to GC demo experience or daily operator workflow)

## Recommendations

End with 3-5 ranked recommendations:
- **What to change** (specific, implementable — reference the actual component/route)
- **Why it matters** (connected to ICP — "A GC would see X and think Y")
- **Impact**: high / medium / low
- **Effort**: S (1-2 days), M (3-5 days), L (5-8 days)
- **Priority**: P0 (blocks demos), P1 (improves experience), P2 (polish at scale)

## Output Modes

**Casual ask** ("thoughts?" / "what do you think?"): Conversational. Overall score, 2-3 strengths, biggest gap, top recommendation. Under 400 words.

**Formal audit** ("audit this" / "grade it" / "rate this"): Full markdown rubric table + per-category assessment + prioritized recommendations.

**Iteration review** ("here is the updated version"): Version-comparison delta table showing score movement. Focus on what changed and whether previous recommendations were addressed.

## Version Tracking

Track scores across iterations:

| Category | v1 | v2 | v3 | Delta (v1-latest) |
|---|---|---|---|---|

For each version note: which recommendations were addressed, which remain open, any new issues introduced, trajectory pattern.

## What NOT to Do

- Do not score without seeing the interface — ask for a screenshot
- Do not produce a 2,000-word report for a casual "thoughts?"
- Do not recommend a complete redesign when targeted fixes work
- Do not inflate scores — an honest 6.5 with clear paths beats a generous 8.0
- Do not ignore the demo context — every observation should consider "what would a GC think seeing this for the first time?"

## Reading the Codebase

When the audit requires checking implementation details:
- Design system: apps/dashboard/design-system/
- UI components: apps/dashboard/src/components/ui/
- Route pages: apps/dashboard/src/app/<route>/
- Layouts: apps/dashboard/src/components/layout/
- Styles: apps/dashboard/src/app/globals.css + Tailwind config
