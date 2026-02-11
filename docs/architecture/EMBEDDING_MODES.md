# Embedding Modes Reference

**Version 1.0 | February 2026**
**Status:** Current — reflects production implementation

---

## Overview

Encypher supports multiple invisible embedding modes for signing text content. Each mode embeds cryptographically signed UUIDs per sentence (or per document) using invisible Unicode characters. The choice of mode depends on the target platform, density requirements, and error-correction needs.

All modes share the same core architecture:
- **Sentence-level Merkle tree** authentication (patent-pending ENC0100)
- **HMAC-SHA256** cryptographic proof per sentence
- **Database-backed** — embedded UUID references full metadata, C2PA manifest, license info
- **Public verification** — anyone can verify signed content via API or verification page

---

## Mode Comparison

| Mode | API Value | Chars/Sentence | Encoding | Word | Google Docs | PDF | Browsers | Error Correction |
|------|-----------|---------------|----------|------|-------------|-----|----------|-----------------|
| **C2PA Full** | `full` | ~500+ | C2PA manifest (VS) | ❌ | ✅ | ✅ | ✅ | — |
| **Lightweight UUID** | `lightweight_uuid` | ~200 | C2PA manifest (VS) | ❌ | ✅ | ✅ | ✅ | — |
| **Minimal UUID** | `minimal_uuid` | ~100 | C2PA manifest (VS) | ❌ | ✅ | ✅ | ✅ | — |
| **VS256** | `vs256_embedding` | 36 | Base-256 Variation Selectors | ❌ | ✅ | ✅ | ✅ | ❌ |
| **VS256+RS** | `vs256_rs_embedding` | 36 | Base-256 VS + Reed-Solomon | ❌ | ✅ | ✅ | ✅ | ✅ (4 errors / 8 erasures) |
| **ZW** | `zw_embedding` | 128 | Base-4 Zero-Width chars | ✅ | ✅ | ✅ | ✅ | ❌ |

### Quick Selection Guide

- **Need Microsoft Word compatibility?** → Use **ZW** (`zw_embedding`)
- **Need maximum density (smallest footprint)?** → Use **VS256** or **VS256+RS** (36 chars vs 128)
- **Need error correction for lossy pipelines?** → Use **VS256+RS** (`vs256_rs_embedding`)
- **Need full C2PA manifest embedded in text?** → Use **Minimal UUID** or **C2PA Full**
- **Signing PDFs?** → Use **VS256+RS** (recommended) or **VS256** for best density

---

## Mode Details

### VS256 Embedding (`vs256_embedding`)

**Best for:** Maximum density signing where Word compatibility is not needed.

Uses all 256 Unicode Variation Selectors as a base-256 alphabet — each byte of the signature maps to exactly one invisible character.

**Alphabet:**
- VS1–VS16 (BMP): U+FE00 – U+FE0F (byte values 0–15)
- VS17–VS256 (Supplementary): U+E0100 – U+E01EF (byte values 16–255)

**Signature layout (36 chars):**
- Magic prefix: 4 chars (VS240–VS243, format marker)
- UUID: 16 chars (16 bytes, database reference)
- HMAC-SHA256: 16 chars (128-bit truncated, cryptographic proof)

**Security:** 128-bit UUID uniqueness + 128-bit HMAC security.

**Platform compatibility:**
| Platform | Status | Notes |
|----------|--------|-------|
| Google Docs | ✅ Renders invisibly | |
| PDF (standard fonts) | ✅ Survives signing + extraction | TrueType, OpenType, Type1 fonts |
| PDF (Type3 fonts) | ⚠️ Verification works, copy-paste limited | See [PDF Font Compatibility](#pdf-font-compatibility) |
| Web browsers | ✅ Renders invisibly | |
| Microsoft Word | ❌ Shows □ box glyphs | Use `zw_embedding` instead |

---

### VS256+RS Embedding (`vs256_rs_embedding`)

**Best for:** PDF signing and lossy distribution pipelines where some characters may be dropped.

Extends VS256 with **Reed-Solomon error correction** (GF(256), 8 parity symbols). Same 36-character footprint as plain VS256, but trades HMAC length for parity bytes.

**Signature layout (36 chars):**
- Magic prefix: 4 chars (VS240–VS243, same as VS256)
- UUID: 16 chars (16 bytes, database reference)
- HMAC-SHA256/64: 8 chars (64-bit truncated)
- RS parity: 8 chars (8 bytes Reed-Solomon)

**Error correction capacity:**
- Corrects up to **4 unknown errors** (corrupted VS chars)
- Corrects up to **8 known erasures** (missing VS chars with known positions)
- In practice: poppler (pdftotext) drops ~2.3 VS chars on average from a contiguous block — well within the 8-erasure capacity

**Security:** 128-bit UUID uniqueness + 64-bit HMAC security. 64-bit HMAC is sufficient because the primary verification path is database lookup (UUID → org), not HMAC alone.

**Detection:** Same magic prefix as VS256 — detection is identical. Verification distinguishes RS vs non-RS by attempting RS decode first.

**Platform compatibility:** Same as VS256 (see table above).

---

### ZW Embedding (`zw_embedding`)

**Best for:** Cross-platform content that must survive Microsoft Word copy-paste.

Uses 4 zero-width Unicode characters as a base-4 alphabet. Larger footprint (128 chars vs 36) but works everywhere including Word.

**Alphabet (all Word-compatible):**
- ZWNJ (U+200C) = 0
- ZWJ (U+200D) = 1
- CGJ (U+034F) = 2
- MVS (U+180E) = 3

**Characters NOT used (Word-incompatible):**
- ZWSP (U+200B) — stripped by Word during copy-paste
- WJ (U+2060) — appears as visible space in Word

**Signature layout (128 chars):**
- UUID: 64 chars (16 bytes × 4 chars/byte)
- HMAC-SHA256: 64 chars (16 bytes × 4 chars/byte)
- No magic prefix — detected by scanning for 128 contiguous base-4 characters

**Security:** 128-bit UUID uniqueness + 128-bit HMAC security.

**Platform compatibility:**
| Platform | Status | Notes |
|----------|--------|-------|
| Microsoft Word | ✅ Survives copy-paste | All 4 chars verified Word-safe |
| Google Docs | ✅ Renders invisibly | |
| PDF (standard fonts) | ✅ Survives signing + extraction | |
| PDF (Type3 fonts) | ⚠️ Verification works, copy-paste limited | See [PDF Font Compatibility](#pdf-font-compatibility) |
| Web browsers | ✅ Renders invisibly | |

---

### C2PA Manifest Modes

These modes embed a full or partial C2PA 2.3 manifest (Section A.7) using Variation Selector encoding. They carry more metadata inline but have a larger per-sentence footprint.

| Mode | API Value | Description |
|------|-----------|-------------|
| **C2PA Full** | `full` | Complete C2PA manifest with all assertions, actions, ingredients |
| **Lightweight UUID** | `lightweight_uuid` | UUID pointer to database-stored manifest |
| **Minimal UUID** | `minimal_uuid` | Per-sentence signed UUID with C2PA wrapper |
| **Hybrid** | `hybrid` | Per-sentence lightweight UUID + full C2PA document wrapper |

C2PA modes are **not Word-compatible** (they use Variation Selectors). They are best suited for web publishing and PDF workflows where the full provenance chain must be embedded inline.

---

## PDF-Specific Behavior

### How PDF Signing Works

When signing an existing PDF, Encypher uses a **font-switching injection** approach:

1. The original PDF content streams and fonts are left **completely untouched**
2. A custom CID font (`EncSgn`) containing only invisible glyphs is embedded in the PDF
3. Invisible characters are injected inline via font-switch sequences:
   ```
   /EncSgn 12 Tf [<GID> -1] TJ /OriginalFont 12 Tf
   ```
4. The signed text (with VS/ZW chars in correct positions) is also stored in an `EncypherSignedText` metadata stream for reliable extraction

This approach preserves visual rendering for all font types, including Type3 and custom-encoded fonts.

### PDF Font Compatibility

| Font Type | Visual Rendering | Copy-Paste (pdftotext) | Copy-Paste (Chrome viewer) | Verification |
|-----------|-----------------|----------------------|---------------------------|-------------|
| **TrueType / OpenType** | ✅ Perfect | ✅ VS/ZW chars preserved | ✅ VS/ZW chars preserved | ✅ Always works |
| **Type1** (base-14) | ✅ Perfect | ✅ VS/ZW chars preserved | ✅ VS/ZW chars preserved | ✅ Always works |
| **CID-keyed** | ✅ Perfect | ✅ VS/ZW chars preserved | ✅ VS/ZW chars preserved | ✅ Always works |
| **Type3** (custom encoding) | ✅ Perfect | ✅ VS/ZW chars preserved | ⚠️ Limited — Chrome PDFium has limited Type3 text extraction | ✅ Always works |

**Key points:**
- **Visual rendering** is always preserved regardless of font type
- **Verification always works** because it uses the `EncypherSignedText` metadata stream, not copy-paste
- **pdftotext** (poppler) reliably extracts invisible chars from all font types
- **Chrome's PDF viewer** (PDFium) has limited text extraction for Type3 fonts — this affects the original unsigned PDF too, not just signed ones

### Recommendation for PDF Publishers

For best copy-paste survivability across all PDF viewers, use **standard TrueType or OpenType fonts** (e.g., Arial, Helvetica, Times New Roman, Noto) when creating PDFs. Avoid Type3 fonts, which are sometimes generated by:

- Browser "Save as PDF" / "Print to PDF" features
- Certain LaTeX configurations
- Some legacy PDF generators

**Note:** This only affects copy-paste text extraction in Chrome's built-in PDF viewer. Verification, visual rendering, and pdftotext extraction all work correctly regardless of font type.

---

## API Usage

### Signing (Enterprise API)

```bash
curl -X POST https://api.encypherai.com/api/v1/sign \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "article_001",
    "text": "Full article text...",
    "segmentation_level": "sentence",
    "manifest_mode": "vs256_rs_embedding"
  }'
```

**Available `manifest_mode` values:**
- `full` — C2PA full manifest
- `lightweight_uuid` — Lightweight UUID manifest
- `minimal_uuid` — Minimal UUID per-sentence
- `hybrid` — Hybrid (per-sentence + document C2PA)
- `zw_embedding` — ZW base-4 (Word-compatible, 128 chars/sentence)
- `vs256_embedding` — VS256 base-256 (max density, 36 chars/sentence)
- `vs256_rs_embedding` — VS256+RS (error-correcting, 36 chars/sentence)

### PDF Signing (xml-to-pdf tool)

```python
from xml_to_pdf.sign_existing import sign_existing_pdf

result = sign_existing_pdf(
    input_path="article.pdf",
    output_path="article_signed.pdf",
    mode="vs256_rs_sentence",
    document_title="My Article",
    api_key="your-api-key",
)
```

**Available PDF signing modes:**
- `c2pa_full` — C2PA full manifest
- `lightweight` — Lightweight UUID manifest
- `minimal` — Minimal UUID per-sentence
- `zw_sentence` — ZW embedding (sentence-level)
- `zw_document` — ZW embedding (document-level)
- `vs256_sentence` — VS256 embedding (sentence-level)
- `vs256_rs_sentence` — VS256+RS embedding (sentence-level, recommended for PDF)

---

## Size Impact

For a 1,000-word article (~50 sentences):

| Mode | Chars Added | Approximate Bytes | Overhead |
|------|------------|-------------------|----------|
| VS256 / VS256+RS | 1,800 | 7.2 KB (UTF-8, 4 bytes/char) | ~1.4% |
| ZW | 6,400 | 12.8 KB (UTF-8, 2–3 bytes/char) | ~2.5% |
| Minimal UUID (C2PA) | ~5,000 | ~10 KB | ~2.0% |
| C2PA Full | ~25,000 | ~50 KB | ~10% |

---

## Verification

All modes are verified through the same endpoint. The verification service auto-detects the embedding format:

1. **VS256-RS** — tried first (error-correcting, highest priority)
2. **VS256** — tried if RS decode fails
3. **ZW** — tried if no VS256 signatures found
4. **C2PA manifest** — tried for full/lightweight/minimal/hybrid modes

```bash
curl -X POST https://api.encypherai.com/api/v1/verify \
  -H "Content-Type: application/json" \
  -d '{"text": "Text with invisible embeddings..."}'
```

For PDF verification, the service extracts text from the `EncypherSignedText` metadata stream (preferred) or falls back to content stream extraction.

---

## Security Summary

| Property | VS256 | VS256+RS | ZW | C2PA Modes |
|----------|-------|----------|-----|-----------|
| UUID bits | 128 | 128 | 128 | 128 |
| HMAC bits | 128 | 64 | 128 | 256 (Ed25519) |
| Error correction | ❌ | ✅ (RS GF(256)) | ❌ | ❌ |
| Tamper detection | ✅ | ✅ | ✅ | ✅ |
| Signing key | HMAC (org-specific) | HMAC (org-specific) | HMAC (org-specific) | Ed25519 private key |

---

## Tier Availability

| Mode | Free | Professional | Enterprise |
|------|------|-------------|-----------|
| C2PA Full | ✅ | ✅ | ✅ |
| Lightweight UUID | ❌ | ✅ | ✅ |
| Minimal UUID | ❌ | ✅ | ✅ |
| Hybrid | ❌ | ❌ | ✅ |
| ZW Embedding | ❌ | ✅ | ✅ |
| VS256 Embedding | ❌ | ✅ | ✅ |
| VS256+RS Embedding | ❌ | ✅ | ✅ |

---

*Last updated: February 2026 — TEAM_158*
