# Encypher Embedding Terminology

**Status:** Canonical -- SSOT for embedding technique naming
**Last updated:** April 2026

This document is the single source of truth for how Encypher names its invisible text
embedding techniques. Use these terms consistently across code, docs, API references,
and customer-facing content.

---

## Term Hierarchy

Three layers, each appropriate for a different audience:

| Layer | Term | Audience |
|-------|------|----------|
| Brand / marketing | **Content Provenance** | All external, sales, product marketing |
| Product / customer | **provenance markers** | API docs, customer guides, support |
| Internal / technical | **VS markers** / **ZWC markers** / **print-space markers** | Code, architecture docs, engineering |

---

## Provenance Markers (customer-facing umbrella)

**Provenance markers** is the standard customer and product-facing term for any Encypher
technique that embeds cryptographic provenance data into content using invisible characters.

- Consistent with the "Content Provenance" brand positioning
- Covers both VS markers and ZWC markers without exposing the implementation
- Safe for API docs, onboarding flows, and technical customer guides

"Content Provenance" (the brand term) describes the capability; "provenance markers" describes
the specific artifact embedded in content. They are complementary, not alternatives:

> "Encypher embeds **provenance markers** into your content, enabling **Content Provenance**
> verification across any distribution channel."

---

## VS Markers (recommended default)

**Full name:** Variation Selector markers
**Internal code names:** `vs256_crypto`, `vs256_rs_crypto`
**API parameter:** `legacy_safe=false` (default)

Uses all 256 Unicode Variation Selectors as a base-256 alphabet:
- VS1-VS16 (BMP): U+FE00 - U+FE0F
- VS17-VS256 (Supplementary): U+E0100 - U+E01EF

VS markers are the **recommended default** and the approach the C2PA text-signing
specification is built on. The encypher-ai open-source library (`UnicodeMetadata`) also
uses variation selectors as its embedding alphabet.

Use VS markers for: web content, PDFs, APIs, Google Docs, any pipeline that does not
involve Microsoft Word copy-paste.

---

## ZWC Markers (legacy-compatible)

**Full name:** Zero-Width Character markers
**Internal code names:** `legacy_safe_crypto`, `legacy_safe_rs_crypto`
**API parameter:** `legacy_safe=true`

Uses six confirmed Word-safe and terminal-safe characters as a base-6 alphabet:

| Char | Codepoint | Digit |
|------|-----------|-------|
| ZWNJ | U+200C | 0 |
| ZWJ  | U+200D | 1 |
| CGJ  | U+034F | 2 |
| MVS  | U+180E | 3 |
| LRM  | U+200E | 4 |
| RLM  | U+200F | 5 |

ZWC markers are the **legacy-compatible approach**, designed to survive Microsoft Word
copy-paste workflows. These are true zero-width characters, unlike variation selectors.
ZWSP (U+200B) is intentionally excluded: Word strips it during copy-paste.

Caveat: CGJ (U+034F) and MVS (U+180E) render as visible glyphs in some fonts under
certain Microsoft Word builds. This is a known Word rendering bug, not an Encypher defect.

Use ZWC markers for: Microsoft Word workflows, email pipelines, any content that passes
through Word's copy-paste engine.

---

## Print-Space Markers (print-survivable, Enterprise)

**Full name:** Print-survivable space-width markers
**Internal code name:** `print_micro_ecc`
**API parameter:** `enable_print_micro_ecc=true`

Uses 4 Unicode space variants as a base-4 alphabet, encoding provenance data in
physically distinguishable inter-word spacing widths:

| Char | Codepoint | Symbol | Width |
|------|-----------|--------|-------|
| HAIR SPACE | U+200A | 0 | ~0.1 em |
| SIX-PER-EM SPACE | U+2006 | 1 | ~0.167 em |
| THIN SPACE | U+2009 | 2 | ~0.2 em |
| REGULAR SPACE | U+0020 | 3 | ~0.25 em |

Unlike VS and ZWC markers, print-space markers survive the rasterize-print-scan-OCR
pipeline because they modify a physical property (inter-word gap width) rather than
relying on invisible Unicode codepoints that OCR discards.

Print-space markers are a **parallel embedding layer**, not a replacement for VS or ZWC
markers. Both channels can coexist in the same document, carrying the same `log_id` for
unified transparency log resolution. They are orthogonal: VS/ZWC markers use invisible
characters inserted alongside visible text, while print-space markers replace existing
space characters with width-variant alternatives.

Protected by RS(48,32) error correction (8 unknown errors / 16 known erasures). Requires
192 inter-word positions (minimum 193 words). Enterprise tier only.

Mutually exclusive with `enable_print_fingerprint`, the legacy 128-bit binary print
channel that carries only an HMAC lookup key without a `log_id` or error correction.

Use print-space markers for: government documents, invoices, bank statements, legal
filings, any content that will be printed and later needs provenance verification from
the physical or scanned copy.

---

## What to Call Things

| Context | Term to use |
|---------|-------------|
| Marketing copy, sales, product positioning | Content Provenance |
| API docs, customer guides, support | provenance markers |
| Architecture discussions (either technique) | invisible Unicode markers |
| VS256 / VS256-RS (technical) | VS markers |
| legacy_safe / legacy_safe_rs (technical) | ZWC markers |
| print_micro_ecc (technical) | print-space markers |
| The `legacy_safe` API flag | `legacy_safe` (exact parameter name) |
| The print-survivable API flag | `enable_print_micro_ecc` (exact parameter name) |

### Terms to avoid

- **"ZWC" for VS markers** -- variation selectors are not zero-width characters; conflating
  them obscures the technical distinction and is wrong
- **"watermarking" for text embedding** -- implies degradation of original content; our
  text technique is lossless and additive. Use "provenance markers" or "Content Provenance"
  instead. Note: "watermarking" is the correct term for image (TrustMark neural), audio
  (spread-spectrum), and video (spread-spectrum) soft-binding, where signal modification is
  inherent and expected. The API parameters `enable_image_watermark`, `enable_audio_watermark`,
  and `enable_video_watermark` use this term deliberately.
- **"steganography"** in customer-facing use -- carries connotations of hiding or concealment;
  use "provenance markers" instead. Note: the internal code filename `print_stego.py` (legacy
  print fingerprint) uses this term for historical reasons; do not surface it externally.
- **"print fingerprint" for the new channel** -- `enable_print_fingerprint` is the legacy
  128-bit lookup-only print channel. The newer `enable_print_micro_ecc` carries a full
  provenance payload (log_id + HMAC + RS ECC). Externally, refer to both as
  "print-survivable provenance markers" and distinguish by capability, not by the API flag name.
- **"text provenance"** -- our positioning is "Content Provenance" (multi-media); avoid
  "text provenance" in external materials

---

## Key Differences

| Property | VS markers | ZWC markers | Print-space markers |
|----------|-----------|-------------|-------------------|
| Unicode category | Variation Selectors | Format/combining chars | Space characters (Zs) |
| Encoding base | Base-256 | Base-6 | Base-4 |
| Chars per segment (no ECC) | 36 | 100 | N/A (document-level) |
| Chars per segment (with ECC) | 44 | 112 | 192 inter-word positions |
| C2PA spec aligned | Yes | No | No (parallel channel) |
| Microsoft Word safe | No | Yes | Yes (space chars render normally) |
| Email pipeline safe | Depends on pipeline | More robust | No (MUAs normalize spaces) |
| Survives print/scan | No | No | Yes (300-600 DPI) |
| Recommended default | Yes | No (Word pipelines only) | No (print workflows only) |
| Tier | All | All | Enterprise only |

---

## Product and Service Concepts

### Composite manifest

The article-level C2PA manifest that binds signed text and signed media (images, audio,
video) into a single provenance unit. A composite manifest references each signed media
file as a C2PA ingredient, so one verification call covers the full article. Built by
`composite_manifest_service.py` and exposed via the `/sign/rich` endpoint.

The composite manifest is Encypher's proprietary orchestration layer on top of the C2PA
ingredient model. Do not conflate it with C2PA's native manifest structure -- it is the
output artifact produced by combining one text manifest with one or more media manifests.

### MediaIngredient

Dataclass representing a signed media file (image, audio, or video) to include as a C2PA
ingredient in a composite manifest. Generalizes the former `ImageIngredient` with a
`media_type` discriminator field (`image`, `audio`, `video`). Used internally by
`composite_manifest_service.py`; not exposed directly in the public API schema.

### Prebid auto-provenance

Public, rate-limited signing service for ad creatives distributed via the Prebid RTD
module. Signs text content with C2PA manifests and caches results for reuse across bid
requests. Distinct from the authenticated Enterprise signing endpoints in three ways:

- No API key required (public endpoint, rate-limited by IP and creative hash)
- Results are cached by content hash to avoid re-signing identical creatives
- Designed for latency budgets imposed by the OpenRTB bid lifecycle

The Prebid RTD module calls this endpoint automatically during bid enrichment; publishers
do not interact with it directly.

---

## See Also

- `docs/architecture/EMBEDDING_MODES.md` -- full technical specification for all sub-modes,
  platform compatibility, and API usage
