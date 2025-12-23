# Enterprise CMS Integration: Drupal Module

**Status:** 📋 Planning  
**Current Goal:** Task 1.2 — Define supported content types / fields.

## Overview

Many tier‑1 publishers and academic publishers use Drupal to power high-volume editorial workflows. This PRD defines a Drupal module that signs content with Encypher C2PA text manifests on publish/update, stores signed variants safely, and exposes reader-facing verification badges.

## Objectives

- Enable automatic C2PA signing on publish and re-signing on update
- Provide secure API key configuration and multi-site support
- Provide reader-facing verification badges and editor-facing status indicators
- Provide bulk signing tooling for existing archives
- Ensure the signed representation is stable (canonicalization) across deployments

## Tasks

### 1.0 Requirements & Architecture (Drupal + C2PA Constraints)

- [x] 1.1 Confirm supported Drupal versions and hosting targets
  - [x] 1.1.1 Drupal 10.x (supported)
  - [x] 1.1.2 Drupal 11.x (supported)
  - [ ] 1.1.3 Drupal 9.x (not supported for MVP)
- [ ] 1.2 Define supported content types / fields
  - [ ] 1.2.1 Node types: `article`, `page`, custom
  - [ ] 1.2.2 Source fields: `body`, custom rich-text fields
  - [ ] 1.2.3 Multi-language variants (per-language signing vs canonical language)
- [ ] 1.3 Decide signed representation strategy (critical)
  - [x] 1.3.1 Option A: Sign extracted plaintext (preferred for robustness + copy/paste verification)
  - [ ] 1.3.2 Option B: Sign HTML (risk: sanitizers/caching/rewriters)
  - [x] 1.3.3 Define deterministic extraction/canonicalization rules
  - [ ] 1.3.4 Add a “signing preview” tool so editors can confirm what is being signed
- [ ] 1.4 Define publishing workflow integration points
  - [x] 1.4.1 Simple publish (node save)
  - [x] 1.4.2 Moderation workflow (sign on transition to published)
  - [ ] 1.4.3 Re-sign policy on edits (always vs only when body changes)
- [ ] 1.5 Define where signed output is stored
  - [ ] 1.5.1 Separate field `field_encypher_signed_text` (recommended)
  - [ ] 1.5.2 Store manifest metadata fields: signer, signed_at, verification_url, status
  - [ ] 1.5.3 Backward compatibility and rollback plan

#### Canonical Plaintext v1 (SSOT)

This canonicalization defines the **exact plaintext bytes** that Drupal signs for C2PA hard binding (`c2pa.hash.data.v1`).

- The output of this algorithm is the string passed into the signing endpoint.
- C2PA hashing then follows `docs/c2pa/Manifests_Text.adoc` (NFC normalization + UTF-8 byte offsets + exclusions).

**Goals**
- Deterministic across PHP (Drupal/WordPress) and Python (Enterprise API/SDK)
- Matches typical reader copy/paste as closely as possible
- Avoids signing raw HTML (sanitizers/rewriters break reproducibility)

**Step 0 — Strip existing C2PA text embeddings (re-sign safety)**
- Before any processing, remove any existing C2PA wrapper characters:
  - `U+FE00..U+FE0F` (VS1–VS16)
  - `U+E0100..U+E01EF` (VS17–VS256)
  - `U+FEFF` (ZWNBSP/BOM)

**Step 1 — HTML to plaintext (render-order, deterministic)**
- Treat the source field as HTML.
- Decode HTML entities (e.g. `&amp;` → `&`).
- Ignore content inside: `script`, `style`, `noscript`.
- For element handling:
  - **Line break**: `br` → `\n`
  - **Block elements** (`p`, `div`, `section`, `article`, `header`, `footer`, `aside`, `nav`, `main`, `blockquote`, `h1..h6`, `figure`, `figcaption`) terminate with a paragraph break.
  - **Lists**:
    - `li` terminates with `\n`.
    - `ul`/`ol` are treated as block containers and terminate with a paragraph break.
    - List items do **not** receive bullets/numbers (to better match real-world copy).
  - **Links**: include only the visible anchor text; ignore `href`.
  - **Tables**:
    - `tr` terminates with `\n`.
    - `th`/`td` cells are separated by `\t`.
    - `table` terminates with a paragraph break.
  - **Preformatted**: `pre` preserves internal whitespace (no whitespace collapsing inside `pre`).

**Step 2 — Whitespace and newline normalization**
- Normalize line endings to `\n` (convert `\r\n` and `\r` → `\n`).
- Convert non-breaking spaces (`U+00A0`) to normal spaces.
- Outside of `pre`:
  - Collapse runs of whitespace (spaces/tabs/newlines) to a single space **within a line**.
  - Trim leading/trailing whitespace on each line.
- Collapse `\n{3,}` to `\n\n` (at most one blank line).
- Remove leading blank lines and trailing whitespace/newlines.

**Step 3 — Unicode normalization (C2PA compatibility)**
- Normalize the final plaintext to Unicode NFC.

**Canonical examples (test vectors)**

1) Headings + paragraphs + line breaks

Input (HTML):
```html
<h1>Heading</h1>
<p>Para 1 with  two   spaces<br>Line2</p>
<p>Para 2</p>
```

Expected canonical plaintext:
```text
Heading

Para 1 with two spaces
Line2

Para 2
```

2) Lists (no bullets/numbers)

Input (HTML):
```html
<ul><li>Item 1</li><li>Item 2</li></ul>
<ol><li>First</li><li>Second</li></ol>
```

Expected canonical plaintext:
```text
Item 1
Item 2

First
Second
```

3) Links + HTML entities

Input (HTML):
```html
<p>Link: <a href="https://example.com">Example</a> &amp; AT&amp;T &lt; 5</p>
```

Expected canonical plaintext:
```text
Link: Example & AT&T < 5
```

### 2.0 Drupal Module Implementation

- [ ] 2.1 Create module scaffolding
  - [ ] 2.1.1 Module name: `encypher_provenance`
  - [ ] 2.1.2 Config schema + default config
  - [ ] 2.1.3 Admin routes, permissions, and UI pages
- [ ] 2.2 Implement secure settings UI
  - [ ] 2.2.1 API base URL
  - [ ] 2.2.2 API key storage approach (Key module integration if available)
  - [ ] 2.2.3 Default `claim_generator`
  - [ ] 2.2.4 Default actions template (created/edited)
  - [ ] 2.2.5 Enable/disable auto-sign on publish and update
  - [ ] 2.2.6 Copy UX mode (default: show “Copy Verified Text” button)
- [ ] 2.3 Implement signing service wrapper
  - [ ] 2.3.1 HTTP client with retries/backoff
  - [ ] 2.3.2 Call signing API (basic `POST /api/v1/sign` or advanced `/api/v1/enterprise/embeddings/encode-with-embeddings`)
  - [ ] 2.3.3 Handle transient failures without blocking editorial save (queue/defer)
  - [ ] 2.3.4 Store correlation IDs for audit/debug
- [ ] 2.4 Implement auto-sign on publish
  - [ ] 2.4.1 Hook into publish transition (content moderation) if enabled
  - [ ] 2.4.2 Hook into node insert if no moderation
- [ ] 2.5 Implement re-sign on update
  - [ ] 2.5.1 Detect meaningful changes (body/text) to avoid unnecessary re-sign
  - [ ] 2.5.2 Ensure `c2pa.edited` action emitted (or `c2pa.created` only on first publish)
- [ ] 2.6 Implement editor UI indicators
  - [ ] 2.6.1 Status widget: signed/unsigned/error
  - [ ] 2.6.2 “Re-sign now” button
  - [ ] 2.6.3 Display verification URL

### 3.0 Reader-Facing Verification Experience

- [ ] 3.1 Add verification badge block
  - [ ] 3.1.1 Badge variants: minimal + detailed
  - [ ] 3.1.2 Link to public verification URL
  - [ ] 3.1.3 Optional “Copy Verified Text” button (copies signed plaintext including wrapper)
- [ ] 3.2 Add structured metadata (optional)
  - [ ] 3.2.1 Add `<meta>` tags or JSON-LD snippet pointing to verification URL
- [ ] 3.3 Ensure caching compatibility
  - [ ] 3.3.1 Confirm CDN and Drupal page cache do not strip variation selectors
  - [ ] 3.3.2 Verify correct behavior with AMP/instant articles if applicable

### 4.0 Bulk Signing (Archive / Backfill)

- [ ] 4.1 Implement bulk signing admin tool
  - [ ] 4.1.1 Filter by content type, date range, language
  - [ ] 4.1.2 Use Drupal Batch API for progress + retry
- [ ] 4.2 Implement safety controls
  - [ ] 4.2.1 Rate limiting to avoid API quota blow-ups
  - [ ] 4.2.2 Dry-run mode
  - [ ] 4.2.3 Export failure report

### 5.0 Security & Compliance

- [ ] 5.1 Protect secrets
  - [ ] 5.1.1 Do not expose API keys in rendered HTML
  - [ ] 5.1.2 Prefer Drupal Key module integration (encrypted storage)
- [ ] 5.2 Data handling policy
  - [ ] 5.2.1 Document what content is sent to Encypher API
  - [ ] 5.2.2 Provide on-prem option guidance for sensitive publishers (future)

### 6.0 Packaging & Distribution

- [ ] 6.1 Documentation
  - [ ] 6.1.1 Install guide
  - [ ] 6.1.2 Configuration guide
  - [ ] 6.1.3 Troubleshooting guide
- [ ] 6.2 Release packaging
  - [ ] 6.2.1 Drupal.org project page
  - [ ] 6.2.2 Semantic versioning

### 7.0 Testing & Validation

- [ ] 7.1 Unit tests passing — ✅ PHPUnit
- [ ] 7.2 Integration tests passing — ✅ Drupal test harness
- [ ] 7.3 End-to-end verification — ✅ manual + scripted
  - [ ] 7.3.1 Publish article → signed field populated
  - [ ] 7.3.2 Reader page contains signed content and badge
  - [ ] 7.3.3 Copy verified text (via button) verifies via Encypher

## Success Criteria

- Drupal publisher can auto-sign on publish and re-sign on update
- Signed content remains stable through caching, sanitization, and rendering
- Verification badge is displayed and links to valid verification output
- Bulk signing can backfill existing content safely
- All tests passing with verification markers

## Completion Notes

(Filled when PRD is complete.)
