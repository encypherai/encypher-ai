# PRD: PDF Provenance Engine Phased Implementation

**Status:** 🟡 Proposed
**Current Goal:** Deliver a production-grade PDF provenance engine/library and CLI that preserves invisible Unicode provenance markers through copy-paste while producing aesthetically strong PDFs suitable for normal publishing workflows
**Team:** TEAM_161

---

## Overview

This PRD defines the phased implementation plan for a production-grade PDF provenance engine built around deterministic Unicode-preserving text emission, embedded provenance recovery, and multi-viewer verification.

The engine must preserve variation selectors, zero-width characters, and related invisible provenance markers through PDF generation and copy-paste, while also supporting visually pleasing output comparable to common WYSIWYG document workflows. The system should support a curated font selection such as Roboto, Times-compatible fonts, Arial-compatible fonts, Liberation, DejaVu, and other approved families where licensing and technical constraints allow.

This work builds on the existing internal prototypes in `tools/encypher-pdf` and `tools/xml-to-pdf` and turns them into a hardened productized library, CLI, testing framework, and optional post-processing pipeline.

---

## Problem Statement

Most commodity PDF generators fail to preserve invisible Unicode provenance characters during copy-paste because one or more of the following occur:

- Fonts do not contain or expose glyphs for invisible characters
- PDF generators omit or incorrectly emit `ToUnicode` mappings
- Extractors drop width-0 glyphs or treat format characters as ignorable
- Generators normalize or reshape text in ways that lose provenance markers
- Output is visually acceptable but text-layer fidelity is not guaranteed

At the same time, users expect PDFs to be visually polished and generated from familiar authoring contexts such as WYSIWYG editors, templates, or styled HTML-like layouts. The implementation must therefore satisfy two requirements simultaneously:

- Preserve invisible provenance markers through selection and copy-paste in supported viewers
- Produce aesthetically pleasing PDFs with common font families and editorial layouts

---

## Objectives

- Productize the custom Unicode-faithful PDF generator into a stable internal library
- Preserve variation selectors, supplementary variation selectors, and zero-width characters through supported copy-paste flows
- Support visually polished PDF output using a curated font family set and editorial styles
- Provide a lossless embedded provenance recovery stream for exact verifier extraction
- Add a robust test harness for textual fidelity, visual fidelity, and cross-viewer compatibility
- Add a CLI and packaging strategy for operational adoption
- Support both generating new PDFs and injecting provenance into existing PDFs where feasible
- Define supported viewer matrix and acceptance criteria explicitly

---

## Non-Goals

- Build a general-purpose full PDF editing suite comparable to Acrobat
- Guarantee identical copy-paste behavior in every PDF viewer in the market
- Support arbitrary complex layout engines in Phase 1
- Support uncurated or user-uploaded fonts without validation in initial releases
- Build a browser-based WYSIWYG editor in this PRD

---

## Product Principles

- **Deterministic fidelity first**
  - Text-layer correctness and provenance survival take precedence over convenience abstractions

- **Aesthetic quality is mandatory**
  - Output must be publishable and visually competitive with standard editorial PDFs

- **Viewer-aware engineering**
  - Behavior must be validated against a defined viewer matrix rather than assumed from spec correctness alone

- **Defense in depth**
  - Provenance must be recoverable from both the text layer and an embedded metadata stream

- **Curated font support**
  - Only tested font families and variants are considered supported

---

## Users and Use Cases

### Primary Users

- Internal provenance/signing services
- Enterprise API customers generating or signing editorial PDFs
- Internal tooling that converts styled content into signed PDFs
- Verification tooling that must recover exact signed text

### Core Use Cases

- Generate a new PDF from structured content while preserving invisible markers
- Generate a polished PDF from template-driven or WYSIWYG-authored content
- Inject invisible provenance markers into an existing PDF without visibly degrading layout
- Recover exact original signed text from embedded metadata when text-layer extraction is lossy
- Automatically validate that generated PDFs look correct and retain markers in supported viewers

---

## Success Criteria

- [ ] Phase 1 library produces PDFs where supported invisible characters survive extraction in the supported viewer matrix
- [ ] Phase 1 includes unit tests, integration tests, content-stream validation, and `ToUnicode` validation
- [ ] Phase 1 includes a defined supported font matrix with at least one sans-serif, one serif, and one metrics-compatible fallback family
- [ ] Phase 2 CLI supports generate, inject, extract, and inspect workflows
- [ ] Phase 2 post-processing pipeline can inject provenance into existing PDFs for a defined supported subset of documents
- [ ] Phase 2 visual regression tests compare rendered output against baselines
- [ ] Phase 2 browser automation verifies selection/copy-paste behavior in Chromium-based viewers using Puppeteer or Playwright
- [ ] Phase 3 packaging supports internal distribution and repeatable release builds
- [ ] Phase 3 documents a stable public API and operational support boundaries
- [ ] End-to-end acceptance suite passes on CI for required viewers and fonts

---

## Supported Viewer Strategy

The product must define a support matrix instead of claiming universal compatibility.

### Required Supported Viewers

- Chromium / PDFium via browser automation
- `pdf.js` in browser
- Poppler `pdftotext`
- MuPDF / PyMuPDF for structural validation

### Stretch / Best-Effort Viewers

- Adobe Acrobat Reader desktop
- macOS Preview where available in manual verification workflows

### Viewer Policy

- **Required support**
  - Must pass automated fidelity gates

- **Best-effort support**
  - Must be tracked, documented, and regression-tested manually where automation is impractical

---

## Supported Font Strategy

The system must ship with a curated list of approved font families and variants.

### Required Families

- Sans-serif:
  - Roboto
  - Liberation Sans
  - DejaVu Sans
  - Arial-compatible metrics family where licensing permits bundling or system use

- Serif:
  - Liberation Serif
  - DejaVu Serif
  - Times New Roman-compatible metrics family where licensing permits bundling or system use

- Monospace:
  - Liberation Mono
  - DejaVu Sans Mono

### Font Support Requirements

- Regular, bold, italic, bold-italic where applicable
- Full visible text rendering for common editorial content
- Synthetic glyph augmentation for invisible provenance codepoints
- Stable metrics and deterministic subsetting behavior
- Clear fallback order when a requested font is unavailable

### Font Packaging Requirements

- Bundle only fonts whose licenses permit redistribution
- System-font discovery may be used as a fallback, but bundled fonts are preferred for deterministic builds
- Font manifest must declare:
  - family
  - style variants
  - license
  - bundling status
  - support tier

---

## WYSIWYG / Aesthetic Quality Requirements

Generated PDFs must be visually publishable and not merely technically correct.

### Required Visual Capabilities

- Titles, headings, paragraphs, block quotes, code blocks, badges, references
- Page margins, paragraph spacing, line height, indents, alignment
- Footer support and page numbering
- Font family selection from curated list
- Bold, italic, color, and limited typographic hierarchy
- Predictable wrapping and pagination
- Clean handling of mixed visible and invisible content without visible artifacts

### Source Content Compatibility Goals

- Structured content model support in Phase 1
- Styled template-based rendering in Phase 2
- Existing PDF post-processing in Phase 2
- HTML/WYSIWYG ingestion adapter in Phase 3 if needed

### Visual Quality Standards

- No visible spacing artifacts caused by invisible glyphs
- No broken ligatures or obviously malformed text runs in supported languages
- No clipped glyphs or page overflow in standard templates
- Rendering must remain aesthetically acceptable across approved font families

---

## Functional Requirements

### FR1. Unicode-Faithful Text Layer

- Emit PDF text operations using deterministic CID-based encoding
- Use embedded CID font strategy with `Identity-H`
- Emit correct `ToUnicode` mappings for all supported visible and invisible codepoints
- Preserve:
  - BMP variation selectors `U+FE00–U+FE0F`
  - supplementary variation selectors `U+E0100–U+E01EF`
  - zero-width space / joiner / non-joiner / BOM
  - approved additional invisible control characters used by provenance encoding

### FR2. Invisible Glyph Strategy

- Synthetic glyphs must be injected into fonts for invisible codepoints
- Invisible glyphs must use tiny non-zero widths if required by extraction/viewer behavior
- Layout logic must visually compensate for non-zero widths where necessary
- Glyph-to-Unicode mapping must remain one-to-one for provenance recovery

### FR3. Embedded Provenance Recovery Stream

- Store exact original signed text in an embedded PDF stream
- Provide extractor utilities for browser and server environments
- Define canonical object naming and retrieval rules
- Maintain byte-identical round-trip for verifier use cases

### FR4. New PDF Generation API

- Provide stable API for creating a PDF from structured content
- Support document metadata, page settings, fonts, styles, and signed text association
- Expose configuration for typography and layout while preserving deterministic output

### FR5. Existing PDF Injection

- Provide a supported path for injecting provenance into existing PDFs
- Preserve original visible content where possible
- Define unsupported document characteristics and fail safely when rewriting is unsafe

### FR6. Inspection and Debugging

- Provide tools to inspect:
  - embedded fonts
  - `ToUnicode` mappings
  - content streams
  - embedded provenance streams
  - extracted viewer outputs

### FR7. CLI

- Support commands for:
  - `generate`
  - `inject`
  - `extract`
  - `inspect`
  - `verify`

### FR8. Test Harness and Automation

- Provide automated text fidelity checks
- Provide visual regression capture
- Provide browser-based selection and copy-paste verification
- Produce human-readable test artifacts for debugging failures

---

## Non-Functional Requirements

### Performance

- Generate small-to-medium editorial PDFs within acceptable service latency
- Avoid pathological font embedding costs for typical documents
- Support deterministic output suitable for snapshot testing

### Reliability

- Fail explicitly when a font or document type is unsupported
- Avoid silent marker loss
- Preserve exact recovery path via metadata stream even if viewer extraction varies

### Security

- Do not execute active content from untrusted PDFs during inspection without clear sandboxing
- Validate input fonts and PDFs before mutation
- Avoid unsafe parsing shortcuts in post-processing mode

### Maintainability

- Separate font preparation, layout, PDF object writing, extraction, and verification concerns
- Keep the core text-fidelity engine independent from higher-level render adapters

---

## Phased Delivery Plan

## Phase 1: Harden and Productize the Core Generator

### Goals

- Convert `tools/encypher-pdf` from prototype to production-grade internal library
- Stabilize APIs and font handling
- Prove text fidelity across required automated extractors
- Deliver aesthetically acceptable document generation from structured content

### Deliverables

- Stable Python package structure
- Hardened Unicode-faithful generator
- Curated bundled font set and fallback strategy
- Expanded round-trip tests
- Viewer compatibility matrix documentation
- Developer docs and examples

### WBS

#### 1.0 Productization and API Stabilization

- [ ] 1.1 Audit existing `tools/encypher-pdf` modules and identify prototype assumptions
- [ ] 1.2 Define stable public API for document creation and saving
- [ ] 1.3 Separate internal APIs from supported APIs
- [ ] 1.4 Add semantic versioning and package metadata conventions
- [ ] 1.5 Define error model and failure messages for unsupported fonts and glyphs

#### 2.0 Font System Hardening

- [ ] 2.1 Create curated font manifest for approved families and licenses
- [ ] 2.2 Bundle redistributable fonts for deterministic builds
- [ ] 2.3 Implement system-font fallback rules for non-bundled environments
- [ ] 2.4 Add support for regular, bold, italic, and bold-italic variants
- [ ] 2.5 Validate font augmentation for invisible codepoints
- [ ] 2.6 Add font support tests across all approved families

#### 3.0 Text Fidelity Engine Hardening

- [ ] 3.1 Validate `Identity-H` / CID / `ToUnicode` generation for all supported codepoint classes
- [ ] 3.2 Add tests for supplementary variation selectors and surrogate pair mapping
- [ ] 3.3 Validate tiny non-zero width strategy across viewers
- [ ] 3.4 Add deterministic content-stream encoding tests
- [ ] 3.5 Add tests for mixed visible/invisible paragraphs, heavy payloads, and multi-page output

#### 4.0 Layout and Aesthetic Quality

- [ ] 4.1 Formalize typography model for titles, headings, body, quotes, references, badges, footer
- [ ] 4.2 Improve spacing, indentation, line-height, and wrapping behavior
- [ ] 4.3 Add template examples using serif and sans-serif families
- [ ] 4.4 Add regression documents for editorial layouts
- [ ] 4.5 Verify no visible artifacts from invisible glyph insertion

#### 5.0 Extraction and Recovery

- [ ] 5.1 Standardize embedded provenance stream schema and naming
- [ ] 5.2 Create browser/server extraction helpers as supported library utilities
- [ ] 5.3 Add exact round-trip verification tests against original source text
- [ ] 5.4 Add inspection utilities for debugging `ToUnicode` and content streams

#### 6.0 Testing and CI

- [ ] 6.1 Expand unit tests for encoding, font mutation, and layout behavior
- [ ] 6.2 Add integration tests across approved font families
- [ ] 6.3 Add extractor tests for Poppler, PyMuPDF, and pdf.js where practical
- [ ] 6.4 Publish viewer compatibility matrix and known limitations

### Phase 1 Acceptance Criteria

- [ ] Structured content can generate visually acceptable PDFs with at least Roboto-like, Times-like, and Arial-compatible support paths
- [ ] Invisible provenance markers survive extraction in required automated viewer/tool matrix
- [ ] Embedded provenance stream recovers exact original text byte-for-byte
- [ ] No blocker-level spacing or pagination defects remain in reference templates

---

## Phase 2: CLI, Existing PDF Injection, and Automated Visual Verification

### Goals

- Add operational CLI workflows
- Support provenance injection into an existing supported subset of PDFs
- Add browser-driven visual verification and copy-paste automation
- Introduce formal visual regression workflows

### Deliverables

- Production CLI
- Supported existing-PDF injection path
- Browser automation test harness
- Visual regression baselines and reports
- Debugging artifact collection for failed runs

### WBS

#### 7.0 CLI and Packaging

- [ ] 7.1 Implement CLI command structure for generate, inject, extract, inspect, verify
- [ ] 7.2 Add machine-readable and human-readable CLI output modes
- [ ] 7.3 Support input from structured JSON/Markdown/template sources
- [ ] 7.4 Add CLI docs and examples

#### 8.0 Existing PDF Injection Productization

- [ ] 8.1 Audit `tools/xml-to-pdf` injection prototype and identify supported document classes
- [ ] 8.2 Define safe-rewrite eligibility rules for PDFs
- [ ] 8.3 Implement fail-safe behavior for unsupported or dangerous rewrites
- [ ] 8.4 Add tests for font-switch injection and ordering preservation
- [ ] 8.5 Add verification for injected PDFs across required extractors

#### 9.0 Browser-Based Verification Harness

- [ ] 9.1 Choose automation stack: Puppeteer or Playwright
- [ ] 9.2 Build a minimal local viewer harness for PDFs in Chromium
- [ ] 9.3 Automate loading generated PDFs into browser viewer pages
- [ ] 9.4 Automate text selection and copy-paste extraction checks
- [ ] 9.5 Save screenshots, extracted text, codepoint dumps, and diffs on failure
- [ ] 9.6 Add support for pdf.js viewer verification in browser

#### 10.0 Visual Regression Testing

- [ ] 10.1 Render first-page and multi-page screenshots for golden baselines
- [ ] 10.2 Compare typography, spacing, and overflow regressions against baselines
- [ ] 10.3 Maintain per-font baseline fixtures
- [ ] 10.4 Add threshold rules and human review workflow for intentional changes

#### 11.0 Cross-Viewer Verification Matrix

- [ ] 11.1 Define canonical test corpus with visible and invisible marker patterns
- [ ] 11.2 Run the corpus through Chromium/PDFium, pdf.js, Poppler, and PyMuPDF
- [ ] 11.3 Record support outcomes by viewer, font, and content pattern
- [ ] 11.4 Document viewer-specific quirks and mitigation strategies

### Phase 2 Acceptance Criteria

- [ ] CLI is usable for internal teams without direct library integration
- [ ] Existing PDF injection succeeds for supported document classes without visible degradation
- [ ] Browser automation reliably verifies copy-paste retention in Chromium-based environments
- [ ] Visual regression suite catches layout drift and stores actionable artifacts

---

## Phase 3: Distribution, Adapters, and Production Readiness

### Goals

- Make the engine broadly consumable internally and optionally externally
- Add higher-level adapters and packaging
- Establish release, support, and observability practices

### Deliverables

- Versioned release process
- Stable API and documentation
- Optional adapter layer for HTML/WYSIWYG or richer content ingestion
- Operational release criteria and support policy

### WBS

#### 12.0 Distribution and Release Engineering

- [ ] 12.1 Finalize package naming, versioning, and release workflow
- [ ] 12.2 Publish internal package artifacts and CLI distribution path
- [ ] 12.3 Add reproducible build documentation
- [ ] 12.4 Add changelog and upgrade guidance

#### 13.0 Higher-Level Render Adapters

- [ ] 13.1 Define adapter interfaces for structured content, template content, and optional HTML/WYSIWYG inputs
- [ ] 13.2 Implement a template adapter for common editorial layouts
- [ ] 13.3 Evaluate HTML-to-intermediate-layout adapter for WYSIWYG compatibility
- [ ] 13.4 Define unsupported HTML/CSS features explicitly

#### 14.0 Production Supportability

- [ ] 14.1 Add operational diagnostics and inspection commands
- [ ] 14.2 Define supported document size and complexity bounds
- [ ] 14.3 Add observability hooks for service-side generation/injection failures
- [ ] 14.4 Publish support matrix for viewers, fonts, adapters, and document classes

#### 15.0 Documentation and Adoption

- [ ] 15.1 Write developer guide for generation, injection, extraction, and verification
- [ ] 15.2 Write operational guide for CI and debugging
- [ ] 15.3 Add sample documents demonstrating aesthetic and fidelity guarantees
- [ ] 15.4 Publish known limitations and fallback guidance

### Phase 3 Acceptance Criteria

- [ ] Internal consumers can adopt the library or CLI with documented support expectations
- [ ] Release process is repeatable and versioned
- [ ] Higher-level adapters are documented and safe to use within explicit bounds
- [ ] Support and debugging workflows are documented for engineering teams

---

## Testing Strategy

## 1. Unit Testing

### Scope

- Font augmentation
- Unicode-to-CID/GID mapping
- `ToUnicode` generation
- surrogate pair handling
- invisible width behavior
- layout measurement and wrapping
- embedded provenance stream serialization

### Acceptance

- 100 percent pass rate on supported Python versions in CI

---

## 2. Integration Testing

### Scope

- Generate PDFs from structured fixtures
- Inject provenance into supported existing PDFs
- Extract text via supported extractors
- Validate exact original-text recovery from metadata stream

### Required Fixtures

- Single paragraph with VS markers
- Multi-page editorial document with heavy invisible payload
- Mixed serif/sans templates
- Footers and page numbers
- Existing PDF injection samples
- Supplementary variation selector fixtures

---

## 3. Structural PDF Validation

### Scope

- Parse content streams
- Parse embedded fonts
- Parse and verify `ToUnicode` CMaps
- Count expected invisible CIDs in text operators
- Inspect font resource dictionaries

### Acceptance

- Structural validation must prove that the PDF contains the intended invisible codepoints independent of viewer extraction behavior

---

## 4. Browser Automation Verification

### Primary Recommendation

Use **Puppeteer** first because Chromium/PDFium behavior is a primary support target and browser automation is straightforward. If the team wants broader browser coverage later, add **Playwright** in a follow-up.

### Browser Automation Scope

- Open test harness page hosting a generated PDF
- Render via Chromium built-in viewer or a controlled pdf.js viewer page
- Capture screenshots of target pages
- Select known text ranges programmatically where possible
- Trigger copy operations and collect clipboard output
- Compare extracted clipboard text to expected Unicode codepoint sequence
- Save screenshots and clipboard dumps as CI artifacts

### Browser Automation WBS

- [ ] BA.1 Build local test harness page for loading fixture PDFs
- [ ] BA.2 Add Puppeteer flow for Chromium built-in PDF viewer
- [ ] BA.3 Add Puppeteer flow for pdf.js viewer page
- [ ] BA.4 Implement clipboard capture helpers
- [ ] BA.5 Add codepoint diff reporting for extracted results
- [ ] BA.6 Capture screenshots before and after selection for debugging
- [ ] BA.7 Run browser checks in CI where environment permits

### Browser Verification Acceptance Criteria

- [ ] Chromium/PDFium copy-paste preserves expected marker sequence for required fixtures
- [ ] pdf.js-based extraction path matches expected output for required fixtures
- [ ] Failures include screenshots, extracted text, and codepoint diffs

---

## 5. Visual Regression Testing

### Goals

- Verify aesthetic quality and layout stability
- Detect spacing regressions introduced by invisible glyph handling
- Protect typography consistency across supported fonts

### Scope

- Full-page screenshot comparisons
- Region-level comparisons for headings, paragraphs, and footer blocks
- Per-font baseline sets for approved templates

### Acceptance Criteria

- [ ] Approved reference templates render within allowed visual diff thresholds
- [ ] No visual displacement caused by invisible marker embedding is detectable in reference documents

---

## 6. Manual Verification

### Scope

- Acrobat Reader smoke checks where available
- Manual spot-checks for print preview quality
- Manual editorial review of reference PDFs for publishability

### Required Manual Checks

- Font aesthetics
- paragraph rhythm
- heading hierarchy
- page breaks
- selection UX
- copy-paste result into plain-text editor

---

## Risks and Mitigations

- **[viewer variance]**
  - Risk: Different viewers treat invisible characters differently
  - Mitigation: Support matrix, automated multi-viewer testing, embedded metadata fallback

- **[font licensing]**
  - Risk: Desired families may not be redistributable
  - Mitigation: Curated bundled alternatives plus documented system-font fallbacks

- **[layout regressions from tiny non-zero widths]**
  - Risk: Preserving extractability may subtly shift text
  - Mitigation: visual regression tests, negative kerning compensation, per-viewer tuning if needed

- **[unsafe PDF rewriting]**
  - Risk: Existing PDF injection may break complex documents
  - Mitigation: eligibility checks, fail-safe mode, supported document class definition

- **[false confidence from one extractor]**
  - Risk: Passing one tool does not prove user-visible success
  - Mitigation: structural validation plus browser and extractor matrix

---

## Dependencies

- `fontTools`
- existing `tools/encypher-pdf` codebase
- existing `tools/xml-to-pdf` codebase
- Chromium for browser automation
- Puppeteer or Playwright
- Poppler tools for `pdftotext`
- PyMuPDF for structural analysis and sanity extraction
- approved font assets and associated licensing review

---

## Open Questions

- Should approved fonts be fully bundled, partially bundled, or primarily system-discovered?
- Do we want to support user-provided fonts in Phase 2 or defer to Phase 3+?
- Should HTML/WYSIWYG ingestion be part of Phase 3 or a separate PRD?
- Which existing-PDF classes are officially supported for provenance injection?
- Do we want Acrobat automation in scope or manual-only validation?

---

## Suggested Initial File Targets

- `tools/encypher-pdf/`
- `tools/xml-to-pdf/`
- `apps/marketing-site/src/lib/pdfTextExtractor.ts`
- `apps/marketing-site/src/lib/pdfTextExtractorServer.ts`
- `scripts/` for automation entrypoints
- `docs/` for support matrix and implementation docs
- `e2e/` or tool-specific test folders for browser automation

---

## Milestone Summary

- **Milestone A**
  - Phase 1 generator hardened, fonts curated, round-trip fidelity proven

- **Milestone B**
  - CLI released, existing-PDF injection supported for approved subset, browser verification live

- **Milestone C**
  - Distribution and release workflow complete, adapters documented, support policy published

---

## Final Acceptance Definition

This initiative is complete when engineering can generate or inject provenance-preserving PDFs that:

- remain visually publishable with approved fonts and styles
- preserve invisible provenance markers through required copy-paste flows in supported viewers
- support exact provenance recovery through an embedded metadata stream
- are covered by automated structural, extraction, visual, and browser-based verification suites
- are documented and packaged for reliable internal adoption

---

## References

- `tools/encypher-pdf/src/encypher_pdf/font.py`
- `tools/encypher-pdf/src/encypher_pdf/fonttools_subset.py`
- `tools/encypher-pdf/src/encypher_pdf/writer.py`
- `tools/encypher-pdf/tests/test_unicode_roundtrip.py`
- `tools/xml-to-pdf/src/xml_to_pdf/sign_existing.py`
- `apps/marketing-site/src/lib/pdfTextExtractor.ts`
- `apps/marketing-site/src/lib/pdfTextExtractorServer.ts`
