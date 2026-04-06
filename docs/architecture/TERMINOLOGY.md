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
| Internal / technical | **VS markers** / **ZWC markers** | Code, architecture docs, engineering |

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

## What to Call Things

| Context | Term to use |
|---------|-------------|
| Marketing copy, sales, product positioning | Content Provenance |
| API docs, customer guides, support | provenance markers |
| Architecture discussions (either technique) | invisible Unicode markers |
| VS256 / VS256-RS (technical) | VS markers |
| legacy_safe / legacy_safe_rs (technical) | ZWC markers |
| The API flag itself | `legacy_safe` (exact parameter name) |

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
  use "provenance markers" instead
- **"text provenance"** -- our positioning is "Content Provenance" (multi-media); avoid
  "text provenance" in external materials

---

## Key Differences

| Property | VS markers | ZWC markers |
|----------|-----------|-------------|
| Unicode category | Variation Selectors | Format/combining chars |
| Encoding base | Base-256 | Base-6 |
| Chars per segment (no ECC) | 36 | 100 |
| Chars per segment (with ECC) | 44 | 112 |
| C2PA spec aligned | Yes | No |
| Microsoft Word safe | No | Yes |
| Email pipeline safe | Depends on pipeline | More robust |
| Recommended default | Yes | No (Word pipelines only) |

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
