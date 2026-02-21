# User Story: Rights Management — Publisher E2E Experience

**Persona**: Sarah Chen, Head of Digital Strategy at a regional news publisher
**Session date**: 2026-02-21
**Tested by**: TEAM_215 automated Puppeteer testing at 1920×1080
**Result**: All flows verified ✅

---

## Background

Sarah's newsroom publishes original investigative journalism. She's noticed AI crawlers
ingesting her content without attribution or compensation. She wants to:
1. Declare machine-readable licensing terms so compliant AI companies can discover them
2. Have a legal paper trail if any AI company uses her content in bad faith
3. Manage incoming license requests from AI companies who want to pay for access

---

## Story 1 — First Visit: Setting Up a Rights Profile

**Entry point**: Dashboard sidebar → **Rights**

Sarah lands on the Rights Management page, Profile tab. She sees a yellow warning banner:
*"No rights profile set. Apply a template or use the API to define your licensing terms."*

Below the banner, three tier cards explain the usage categories her profile will govern:
- **Bronze — Scraping / Crawling** (read-only search indexing, web archiving)
- **Silver — RAG / Retrieval** (AI-powered retrieval-augmented generation pipelines)
- **Gold — Training / Fine-tuning** (incorporation into model weights)

Each card shows "No terms set — inherits platform defaults."

Sarah clicks **Apply template** (top-right button). A sheet/picker opens showing available
templates. She selects **"News Publisher Default"** which pre-populates sensible terms:
- Bronze: Permitted (automated crawling for indexing)
- Silver: Permitted with attribution required
- Gold: Permitted but **requires license** (commercial training must pay)

After applying, the profile tab refreshes to show:
- ✅ Green banner: *"Active rights profile — version 2 · Last updated Feb 21, 2026"*
- All three tier cards populated with real data (usage type, attribution requirements, notes)
- **Public discovery endpoints** section listing four machine-readable URLs:
  - Machine-readable JSON: `/api/v1/public/rights/organization/{org_id}`
  - W3C ODRL: `/api/v1/public/rights/organization/{org_id}`
  - RSL 1.0 XML: `/api/v1/public/rights/organization/{org_id}/rsl`
  - robots.txt additions: `/api/v1/public/rights/organization/{org_id}/robots-txt`

**Outcome**: Every document Sarah signs from now on will embed a `rights_resolution_url`
pointing to her live terms. Any AI company or crawler that checks C2PA provenance can
discover her licensing requirements programmatically.

---

## Story 2 — Issuing a Formal Notice

**Entry point**: Rights → **Notices** tab

Sarah's monitoring tools flag that a major AI lab appears to be using her articles in
training data without a license. She wants to create a formal legal notice.

The Notices tab loads with an empty state: *"No formal notices issued yet."*

She clicks **+ New notice**. A form appears with fields:
- **Recipient entity**: `OpenModelCo Inc.`
- **Contact email**: `legal@openmodelco.ai`
- **Violation type**: `Unauthorized Training` (maps to cease_and_desist notice type)
- **Notice text**: A detailed description of the violation and demands

She submits. The notice appears in the list immediately with:
- Status badge: **created** (slate/neutral — the notice exists but hasn't been sent)
- Recipient: `OpenModelCo Inc.`
- A **Deliver** button

Sarah clicks **Deliver**. The API records the delivery event, timestamps it, and locks
the notice content cryptographically. The status badge changes to **delivered** (green),
showing *"Delivered Feb 21, 2026"*.

**Legal significance**: Once delivered, the notice content is SHA-256 locked. Any
subsequent use of Sarah's content by `OpenModelCo Inc.` is provably *willful* infringement,
not innocent infringement — a critical distinction for damages in court.

Sarah can navigate to the notice detail to view:
- Full cryptographic evidence chain (append-only linked list of events)
- Delivery receipt with timestamp and hash
- A court-ready evidence package via the "Evidence" endpoint

---

## Story 3 — Reviewing the Analytics Tab

**Entry point**: Rights → **Analytics** tab

The Analytics tab has two sections:

**Detection summary**: Shows aggregate stats from AI crawlers that have hit her
`rights_resolution_url` (currently zeros on a fresh account, will populate as crawlers
phone home with C2PA-embedded content):
- Total detection events
- Rights served count
- Rights acknowledged count
- Breakdown by source, category, and integrity status

**Known AI crawlers**: Lists known AI system operators (GPTBot, ClaudeBot, Common Crawl,
etc.) with their operator organization and last-seen timestamps.

The empty states are informative — Sarah understands data will appear as AI crawlers
encounter her signed content and check her rights endpoint.

---

## Story 4 — Managing a Licensing Request (Approve flow)

**Entry point**: Rights → **Licensing** tab

An AI company discovers Sarah's rights profile and submits a Gold tier licensing request
(they want to use her journalism for model fine-tuning). This appears in the
**Licensing requests** table:

| From | Tier | Status | Message | Date | Actions |
|------|------|--------|---------|------|---------|
| org_07dd7ff7… | 🟡 gold | pending | — | Feb 21, 2026 | Approve / Reject |

Sarah reviews the proposed terms (attribution required, 80/20 revenue split under
self-service model) and clicks **Approve**.

The table immediately updates:
- Status badge → **approved** (green)
- Actions → `—` (no more action buttons)

The **Active agreements** section below populates with the new agreement:

| Licensee | Tier | Status | Expires |
|----------|------|--------|---------|
| org_07dd7ff7… | 🟡 gold | active | — |

**Outcome**: A binding licensing agreement is created and both parties have a cryptographic
audit trail. The licensee can now use Sarah's content within the agreed terms.

---

## Story 5 — Managing a Licensing Request (Reject flow)

A second request comes in for Silver tier (RAG/Retrieval access). Sarah reviews the
proposed terms but finds them unacceptable — they don't include proper attribution.

She clicks **Reject** on the silver pending row. An inline form expands *below* that row
(without navigating away) showing:
- Text input: "Optional rejection message..."
- **Confirm reject** (red) button
- **Cancel** button

Sarah types a reason: *"Terms do not meet our current licensing requirements. Please
review our Silver tier terms and resubmit."*

She clicks **Confirm reject**. The inline form collapses and the row updates:
- Status badge → **rejected** (red)
- Actions → `—`

The active agreements section is unchanged (rejected requests don't create agreements).

---

## UX Observations & Verified Bugs Fixed

During E2E testing, the following issues were discovered and fixed:

| # | Issue | Fix |
|---|-------|-----|
| 1 | Templates not loading in picker | `getRightsTemplates` expected `{success,data}` envelope; API returns plain array. Fixed interface + array check. |
| 2 | Profile not showing after template applied | All rights GET methods incorrectly appended `.data` to `fetchWithAuth`. Removed envelope assumption. |
| 3 | `DetectionEvent` interface wrong shape | API returns aggregate summary, not event array. Renamed to `DetectionSummary` with correct fields. |
| 4 | Crawler analytics field mismatch | `summary`/`total_events` → `crawlers`/`total_crawler_events` |
| 5 | Notice creation 500 error | Router missing field normalization (frontend sends `recipient_entity`; service expects `target_entity_name`). Added mapping dict. |
| 6 | Notice list showing "Unknown recipient" | `_notice_to_dict` missing `recipient_entity` alias. Added dashboard-friendly aliases. |
| 7 | Notice deliver 422 required body | `delivery_data: Dict = ...` was required; dashboard sends no body. Fixed to `Optional[Dict] = None`. |
| 8 | Licensing tier/from showing `—` | Interface used `requesting_org_id`/`usage_tier`; API returns `requester_org_id`/`tier`. Fixed interface. |
| 9 | Notice status "created" not showing Deliver button | Dashboard checked `status === 'draft'`; API returns `"created"`. Removed server-side status mapping, updated dashboard condition. |

---

## Test Results

```
Backend (enterprise_api): 1162 passed, 0 failed, 58 skipped
Frontend TypeScript:       0 errors
E2E Puppeteer flows:       All 4 tabs verified, all CRUD operations tested
```

---

## What's Not Yet in the UI

These features exist in the API but have no dashboard surface yet:

- **Profile history**: `GET /api/v1/rights/profile/history` — previous versions of the rights profile
- **Document-level overrides**: Per-document rights that override the org profile
- **Evidence package download**: `GET /api/v1/notices/{id}/evidence` — court-ready PDF/JSON bundle
- **Agreement usage metrics**: `GET /api/v1/rights-licensing/agreements/{id}/usage`
- **Notification emails**: No email templates for licensing request received / notice delivered

These are appropriate scope for a follow-up sprint.
