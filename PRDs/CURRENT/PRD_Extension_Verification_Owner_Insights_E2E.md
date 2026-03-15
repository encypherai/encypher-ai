# PRD: Extension Verification to Owner Insights (End-to-End)

**Status:** 🔄 In Progress
**Current Goal:** Define and implement an end-to-end workflow so any successful verification event on any webpage via `integrations/chrome-extension` becomes attributable, queryable, and actionable for the user or organization that originally signed the content.
**Created:** 2026-03-14

## Overview

We already have the building blocks for discovery reporting: the Chrome extension emits discovery telemetry, the analytics service can store raw discovery rows, and the dashboard has aggregate detection/crawler analytics. However, the current implementation does not yet guarantee the product outcome we want: when content signed by an Encypher customer is verified anywhere on the web, the original content owner should reliably see actionable insights in `apps/dashboard`.

This PRD closes the end-to-end gap between:
- verification on arbitrary webpages,
- secure attribution of that discovery to the original signer/organization,
- storage of raw evidence-quality discovery events,
- owner-facing dashboard UX,
- alerting and follow-up workflows.

This is a follow-on to `PRD_Content_Discovery_Tracking.md`, focused specifically on making the workflow production-ready and owner-actionable end to end.

## Problem Statement

Today, discovery data is only partially productized:
- the extension emits `pageUrl`, `pageDomain`, `pageTitle`, and a timestamp-like event payload,
- analytics ingestion can persist raw discoveries,
- dashboard UI mainly shows aggregate analytics rather than a concrete “where was my content found?” event feed,
- attribution of extension discovery events to the original owner may fail if ingestion relies on reporter authentication instead of signer/document identity derived from verification.

As a result, the intended promise is not fully met: the original owner may not reliably see where their content was found, when it was found, whether it was off-domain, and what to do next.

## Product Goal

Any verification of signed content on any webpage through the Chrome extension should create one or more owner-visible outcomes for the original signer:
- a durable discovery event stored with evidence-quality metadata,
- aggregated analytics in dashboard summaries,
- a raw event row visible in dashboard tables,
- an alert when content is found on unexpected domains,
- a clear next action such as review, export, acknowledge, or escalate.

## Objectives

- Guarantee owner attribution for discovery events even when the discovering verifier is anonymous or not signed in.
- Make all extension verification paths report discovery consistently.
- Persist raw discovery data with URL, normalized domain, page title, verification status, owner identifiers, and server timestamp.
- Expose dashboard-ready APIs for both raw events and rollups.
- Add dashboard UX in `apps/dashboard` for event drill-down, filtering, and actionability.
- Preserve reporter privacy and avoid collecting unnecessary PII.
- Define rollout, QA, and observability so the workflow is trustworthy in production.

## Non-Goals

- Building a full legal enforcement workflow in this phase.
- Fingerprinting or crawl detection outside the extension verification flow.
- Guaranteeing universal detection across the public web without a verifier present.
- Attributing anonymous discovery events to the person who viewed the page.

## Users

- Content owners who sign content via API, dashboard, CMS integrations, or future SDK flows.
- Org admins who need to monitor where signed content appears.
- Trust, legal, and partnerships teams reviewing off-domain reuse.

## Intended End-to-End Workflow

1. A customer signs content using Encypher.
2. The content appears on the original site and may later surface elsewhere.
3. A user with the Chrome extension visits any webpage containing that signed content.
4. The extension detects and verifies the embedded content.
5. The extension emits a discovery event with page context and verification outcome.
6. The backend attributes that discovery to the original signer or organization based on verified content identity, not on any client-supplied org field.
7. The event is stored as a raw discovery record and reflected in aggregate rollups.
8. If the found domain is unexpected, the owner gets an alert surface in the dashboard.
9. The owner can view the found URL, timestamp, page title, document identity, verification status, and next actions.
10. The owner can filter, export, acknowledge, or escalate the event.

## Core Product Requirements

### 1. Attribution Model

- Owner attribution must be derived from verified signer identity, document identity, or server-trusted ownership mapping.
- Discovery visibility must not depend on the discovering browser user being authenticated as the owner.
- The server must ignore or override untrusted client-supplied ownership fields.
- If the verification result lacks enough owner identity to attribute the event, the event may be stored as unattributed but must be flagged for instrumentation review.

### 2. Event Coverage

All meaningful extension verification paths must emit discovery data, including:
- first-time page scan verifications,
- cached detection replays,
- rescan flows,
- popup/detail-triggered verification paths,
- revoked and invalid outcomes where owner-relevant context still exists.

### 3. Required Event Data

Each stored discovery event must include at minimum:
- canonical page URL,
- normalized page domain,
- page title when available,
- server-side `discovered_at`,
- client event timestamp if available,
- signer ID and/or signer display name when available,
- organization ID when attributable,
- document ID when available,
- original domain and/or signing domain,
- verification status,
- marker type,
- source channel,
- external-domain flag,
- extension version,
- anonymous session identifier,
- detection correlation ID if available.

### 4. Dashboard Experience

The dashboard must provide:
- aggregate summary cards,
- a raw discovery event table,
- filters for date range, status, source, document, and external-only,
- a domain summary view,
- alert surfaces for newly observed external domains,
- links to the found URL and verification details,
- export capability for CSV/JSON.

### 5. Actionability

For each discovery row, the owner should be able to:
- open the found page,
- open verification details,
- understand whether the domain is owned or external,
- export evidence,
- acknowledge an alert,
- hand off to a downstream notice or evidence workflow in a later phase.

### 6. Privacy and Security

- Do not store reporter PII or browser history beyond the discovered page context needed for the product.
- Continue using anonymous session identifiers rather than user identity for reporters.
- Sanitize URLs to remove querystrings, fragments, usernames, and passwords before persistence.
- Apply rate limiting, abuse controls, and ingestion validation.
- Keep owner attribution server-trusted.

## Functional Requirements

### Extension Requirements

- The extension must send discovery events for all verification outcomes that are relevant to owners.
- The extension must include sanitized page context and verification metadata.
- Failed analytics flushes must retry safely without unbounded queue growth.
- The extension should include a stable correlation field so raw events can be traced back to a verification attempt during debugging.
- Discovery emission must remain on by default and not be user-toggleable for the owner-insights workflow.

### Backend Requirements

- The analytics ingestion path must support anonymous reporter submissions while still attributing events to the original owner.
- Owner attribution must use server-side trusted identifiers from verification results, document records, signer records, or ownership mappings.
- Raw discovery events must be persisted in a queryable table with proper indexes.
- Aggregate summaries must be updated or derivable efficiently from raw events.
- The system must support pagination, filtering, and sorting for raw event queries.
- The system must preserve both raw evidence rows and summary rollups.
- Duplicate event handling must be defined explicitly.

### Dashboard Requirements

- `apps/dashboard` must expose a dedicated owner-facing view for content discovery events.
- The UI must distinguish total detections from external-domain detections.
- The UI must show first seen / latest seen semantics where rollups exist.
- The UI must support empty, loading, and partially attributed states gracefully.
- The UI must explain privacy boundaries so customers understand that the discovering user remains anonymous.

## Data and API Requirements

### Required API Surfaces

- Raw discovery events list endpoint for owner-facing dashboard use.
- Domain summary endpoint for “where is my content appearing?” rollups.
- Alert list and acknowledge endpoints for newly seen external domains.
- Aggregate analytics endpoint that includes extension-driven discovery counts.
- Export endpoint or client-side export support for raw event data.

### Required Query Capabilities

- Filter by date range.
- Filter by external-only.
- Filter by verification status.
- Filter by source channel.
- Filter by document ID or signer.
- Sort by `discovered_at` descending by default.

### Required Data Quality Rules

- URL canonicalization must be consistent between extension and backend.
- `discovered_at` must be server-generated and authoritative.
- Client timestamps may be stored as secondary context only.
- The system must define idempotency or dedupe behavior for repeated discoveries.
- Events missing owner attribution must be measurable and reviewable.

## Key Risks

- Discovery events may be recorded but not linked to the original owner if attribution relies on reporter auth.
- The dashboard may continue to show only aggregates, leaving users without actionable evidence.
- Domain mismatch heuristics may generate false positives without robust owned-domain management.
- Duplicate discoveries on high-traffic pages could inflate analytics if dedupe rules are weak.
- Privacy regressions are possible if raw URL handling is not tightly sanitized.

## Decisions Required

- What is the primary trusted source for owner attribution: verification result organization ID, signer ID lookup, document registry lookup, or a fallback chain?
- What constitutes a duplicate event versus a valid repeated observation?
- Should raw event export be available to all plans or gated?
- Should alerting be in-dashboard only for phase 1, or also email/slack/webhook?
- Where should the feature live in the dashboard IA: `rights`, `ai-crawlers`, or a dedicated `content-discovery` page?

## WBS Tasks

### 1.0 Product and Ownership Model

- [ ] 1.1 Define the canonical owner-attribution model for extension discovery events.
- [ ] 1.2 Document the trusted fallback chain for attribution: document → signer → organization → unattributed.
- [ ] 1.3 Define duplicate-event semantics for raw rows and rollups.
- [ ] 1.4 Define the phase-1 dashboard IA and naming: Content Discovery, Content Spread, or similar.
- [ ] 1.5 Define plan/tier exposure and export policy.

### 2.0 Chrome Extension Event Coverage

- [ ] 2.1 Audit every extension verification path and enumerate where discovery events are emitted.
- [ ] 2.2 Ensure first-time verification, cached verification, and manual rescan flows all emit a conformant discovery event.
- [ ] 2.3 Add a stable correlation field for debugging cross-system event tracing.
- [ ] 2.4 Verify URL sanitization and normalization behavior for all emitted events.
- [ ] 2.5 Add extension tests covering all owner-relevant verification paths.

### 3.0 Analytics Ingestion and Attribution

- [ ] 3.1 Refactor ingestion so owner attribution does not depend on reporter JWT presence.
- [ ] 3.2 Resolve owner organization from server-trusted verification metadata or document lookup.
- [ ] 3.3 Preserve anonymous reporter context while attaching the event to the original owner.
- [ ] 3.4 Add explicit handling for unattributed events with instrumentation and monitoring.
- [ ] 3.5 Define and implement idempotency or dedupe rules.
- [ ] 3.6 Add tests for anonymous reporter + attributed owner flows.

### 4.0 Discovery Data Model and Query Layer

- [ ] 4.1 Confirm raw event schema covers all required page, ownership, verification, and source fields.
- [ ] 4.2 Add or validate indexes for org, domain, document, and timestamp queries.
- [ ] 4.3 Ensure raw event queries support pagination, sorting, and filtering.
- [ ] 4.4 Ensure summary rollups can be derived without scanning full event history inefficiently.
- [ ] 4.5 Add data-retention and backfill guidance where required.

### 5.0 API Contract for Owner Insights

- [ ] 5.1 Finalize raw discovery events endpoint contract for dashboard consumption.
- [ ] 5.2 Finalize domain summary endpoint contract.
- [ ] 5.3 Finalize alerts list and acknowledge contracts.
- [ ] 5.4 Add export contract for CSV/JSON evidence-friendly data.
- [ ] 5.5 Add API tests for filtering, pagination, auth, and unattributed edge cases.

### 6.0 Dashboard UX in `apps/dashboard`

- [ ] 6.1 Add an owner-facing discovery page or tab with summary cards and raw event table.
- [ ] 6.2 Add columns for found URL, domain, page title, discovered time, status, document, and original domain.
- [ ] 6.3 Add filters for time range, external-only, status, source, and document.
- [ ] 6.4 Add empty-state copy that explains how discoveries are collected.
- [ ] 6.5 Add row actions: open found page, open verification details, export.
- [ ] 6.6 Add alert surfaces for newly seen external domains.
- [ ] 6.7 Add owned-domain management links where false positives are possible.

### 7.0 Actionability and Alerts

- [ ] 7.1 Define what counts as a “new external domain” alert.
- [ ] 7.2 Add in-dashboard alert inbox or banner for new external discoveries.
- [ ] 7.3 Add acknowledge / dismiss workflow for alerts.
- [ ] 7.4 Define follow-on hooks to formal notice or evidence workflows.
- [ ] 7.5 Add export-ready evidence views for customer success, legal, and trust teams.

### 8.0 Observability and QA

- [ ] 8.1 Add instrumentation for emitted events, accepted events, attributed events, unattributed events, and dashboard-visible events.
- [ ] 8.2 Add end-to-end test coverage from extension event emission through dashboard API visibility.
- [ ] 8.3 Add regression tests for anonymous reporter submissions that still surface correctly for the owner org.
- [ ] 8.4 Add seeded demo/test fixtures for external-domain discoveries.
- [ ] 8.5 Create a QA checklist covering sign → publish → discover → alert → dashboard drill-down.

### 9.0 Rollout and Adoption

- [ ] 9.1 Ship behind a feature flag if needed.
- [ ] 9.2 Backfill or reconcile existing discovery events where feasible.
- [ ] 9.3 Monitor attribution success rate and dashboard usage post-launch.
- [ ] 9.4 Publish customer-facing guidance describing discovery insights and privacy boundaries.
- [ ] 9.5 Define support playbooks for missing events, false positives, and unattributed discoveries.

## Success Criteria

- Any extension verification of attributable signed content creates an owner-visible discovery event.
- Owner visibility does not depend on the discovering reporter being authenticated as that owner.
- `apps/dashboard` exposes both aggregate analytics and raw “where/when found” event views.
- New external-domain discoveries generate actionable alert surfaces for owners.
- Event rows show at least URL, domain, timestamp, status, and document or signer context.
- Reporter privacy remains preserved and documented.
- End-to-end tests cover the full workflow from extension verification through dashboard visibility.
- Teams can measure attribution rate, unattributed rate, and dashboard event visibility rate in production.

## Acceptance Checklist

- [ ] Anonymous reporter verifies signed content on an external domain.
- [ ] Discovery event is accepted and stored.
- [ ] Event is attributed to the original owner organization.
- [ ] Event appears in raw discovery API queries for that owner.
- [ ] Event contributes to aggregate analytics.
- [ ] Event triggers an external-domain alert when appropriate.
- [ ] Event is visible in dashboard UI with correct URL and time.
- [ ] Owner can export or otherwise act on the event.

## Dependencies

- `integrations/chrome-extension`
- `services/analytics-service`
- auth and signer/document identity sources used for trusted attribution
- `apps/dashboard`
- owned-domain configuration and domain matching rules

## Completion Notes

(To be filled upon implementation. Must include evidence that extension verification events are attributable, queryable, and actionable for original content owners end to end.)
