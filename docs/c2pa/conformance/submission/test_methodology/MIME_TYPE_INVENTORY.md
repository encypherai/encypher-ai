# C2PA Conformance Submission -- MIME Type Inventory

**Library**: c2pa-python 0.29.0 (c2pa-rs 0.78.4)
**Date**: 2026-03-25
**Purpose**: Definitive type list for Scott / C2PA conformance program submission

---

## Generator (Sign) Capabilities

### Image (11 canonical + 2 aliases = 13 accepted MIME types)

| MIME Type | Format | Pipeline | Notes |
|-----------|--------|----------|-------|
| image/jpeg | JPEG | Pillow (Tier A) | Canonical; EXIF strip before sign |
| image/jpg | JPEG | Pillow (Tier A) | Alias -> image/jpeg |
| image/png | PNG | Pillow (Tier A) | EXIF strip supported |
| image/webp | WebP | Pillow (Tier A) | EXIF strip supported |
| image/tiff | TIFF | Pillow (Tier A) | EXIF strip supported |
| image/gif | GIF | Pillow (Tier A) | EXIF strip supported |
| image/heic | HEIC | pillow-heif plugin (Tier B) | EXIF strip supported |
| image/heif | HEIF | pillow-heif plugin (Tier B) | EXIF strip supported |
| image/heic-sequence | HEIC animated | pillow-heif plugin (Tier B) | Alias -> image/heic for c2pa-rs |
| image/heif-sequence | HEIF animated | pillow-heif plugin (Tier B) | Alias -> image/heif for c2pa-rs |
| image/avif | AVIF | Pillow native AVIF (Tier B) | EXIF strip supported |
| image/svg+xml | SVG | Bypass / magic-byte validation (Tier C) | c2pa-rs handles XML PI embedding |
| image/x-adobe-dng | DNG | Bypass / magic-byte validation (Tier C) | c2pa-rs treats as TIFF variant |
| image/jxl | JPEG XL | Custom ISOBMFF embedder | ISOBMFF container variant only; bare codestream not supported. Uses c2pa box with c2pa.hash.data exclusion. |

**Canonical count**: 11 distinct signable image types (JPEG, PNG, WebP, TIFF, GIF, HEIC, HEIF, AVIF, SVG, DNG, JXL).
image/jpg, image/heic-sequence, image/heif-sequence are accepted aliases only.

### Video (3 canonical + 3 aliases = 6 accepted MIME types)

| MIME Type | Format | Pipeline | Notes |
|-----------|--------|----------|-------|
| video/mp4 | MP4 | c2pa-rs ISO BMFF | Canonical |
| video/quicktime | MOV | c2pa-rs ISO BMFF | Canonical |
| video/x-m4v | M4V | c2pa-rs ISO BMFF | Canonical |
| video/x-msvideo | AVI | c2pa-rs RIFF | Canonical |
| video/avi | AVI | c2pa-rs RIFF | Alias -> video/x-msvideo |
| video/msvideo | AVI | c2pa-rs RIFF | Alias -> video/x-msvideo |

**Canonical count**: 4 distinct signable video types (MP4, MOV, M4V, AVI).
For the conformance submission the 3 primary types are MP4, MOV, AVI.

### Audio (4 canonical + 4 aliases = 8 accepted MIME types)

| MIME Type | Format | Pipeline | Notes |
|-----------|--------|----------|-------|
| audio/wav | WAV | c2pa-rs RIFF C2PA chunk | Canonical |
| audio/wave | WAV | c2pa-rs RIFF C2PA chunk | Alias -> audio/wav |
| audio/vnd.wave | WAV | c2pa-rs RIFF C2PA chunk | Alias -> audio/wav |
| audio/x-wav | WAV | c2pa-rs RIFF C2PA chunk | Alias -> audio/wav |
| audio/mpeg | MP3 | c2pa-rs ID3 GEOB frame | Canonical |
| audio/mpa | MP3 | c2pa-rs ID3 GEOB frame | Alias -> audio/mpeg (MPA alias) |
| audio/mp4 | M4A | c2pa-rs ISO BMFF uuid box | Canonical; covers M4A and AAC-in-M4A |
| audio/flac | FLAC | Custom JUMBF/COSE pipeline | Canonical; APPLICATION metadata block embedding |

**Canonical count**: 4 distinct signable audio types (WAV, MP3, M4A, FLAC).
audio/wave, audio/vnd.wave, audio/x-wav, audio/mpa are accepted aliases.

### Documents (5 types via custom JUMBF/COSE pipeline)

All document types use a two-pass custom pipeline (not c2pa.Builder):
pass 1 inserts a placeholder manifest, pass 2 replaces with the signed COSE structure.

| MIME Type | Format | Notes |
|-----------|--------|-------|
| application/pdf | PDF | Custom JUMBF byte-range insertion; PDF cross-reference table updated |
| application/epub+zip | EPUB | ZIP-based; JUMBF manifest at META-INF/content_credential.c2pa |
| application/vnd.openxmlformats-officedocument.wordprocessingml.document | DOCX | ZIP-based; same ZIP JUMBF approach |
| application/vnd.oasis.opendocument.text | ODT | ZIP-based; same ZIP JUMBF approach |
| application/oxps | OXPS | ZIP-based; same ZIP JUMBF approach |

### Fonts (3 types via custom JUMBF/COSE pipeline)

All font types share the same SFNT C2PA table embedding approach. The embedder handles
all SFNT container variants (OTF, TTF, and the generic SFNT container type).

| MIME Type | Format | Notes |
|-----------|--------|-------|
| font/otf | OTF | SFNT C2PA table embedding; same two-pass COSE approach |
| font/ttf | TTF | SFNT C2PA table embedding; same two-pass COSE approach |
| font/sfnt | SFNT (generic) | Generic SFNT container; covers both OTF and TTF containers |

---

## Validator (Verify) Capabilities

The verify endpoint uses c2pa-python Reader plus custom document manifest parsing.
It accepts all types supported for signing, plus several additional read-only types
that the c2pa-rs Reader can parse even though Encypher does not generate them.

### Image (same 11 canonical + image/bmp added as read-only)

| MIME Type | Verify Support | Notes |
|-----------|----------------|-------|
| image/jpeg | Yes | Full c2pa-python Reader |
| image/png | Yes | Full c2pa-python Reader |
| image/webp | Yes | Full c2pa-python Reader |
| image/tiff | Yes | Full c2pa-python Reader |
| image/gif | Yes | Full c2pa-python Reader |
| image/heic | Yes | Full c2pa-python Reader |
| image/heif | Yes | Full c2pa-python Reader |
| image/avif | Yes | Full c2pa-python Reader |
| image/svg+xml | Yes | Full c2pa-python Reader |
| image/x-adobe-dng | Yes | Full c2pa-python Reader |
| image/jxl | Yes | Custom ISOBMFF JUMBF parser extracts c2pa box manifest |
| image/bmp | Read-only | c2pa-rs can read BMP manifests; Encypher does not sign BMP |

### Video (same 4 canonical)

| MIME Type | Verify Support |
|-----------|----------------|
| video/mp4 | Yes |
| video/quicktime | Yes |
| video/x-m4v | Yes |
| video/x-msvideo | Yes |

Verify also routes on: video/webm, video/ogg, video/x-matroska, video/mpeg (read-only,
c2pa-rs may parse; Encypher does not sign these).

### Audio (same 3 canonical + additional read-only)

| MIME Type | Verify Support | Notes |
|-----------|----------------|-------|
| audio/wav | Yes | Full c2pa-python Reader |
| audio/mpeg | Yes | Full c2pa-python Reader |
| audio/mp4 | Yes | Full c2pa-python Reader |
| audio/flac | Yes | Custom JUMBF parser for verify; same pipeline as PDF/ZIP documents |
| audio/aac | Read-only routing | Routes to audio Reader; c2pa-rs may parse ftyp-wrapped AAC. |
| audio/ogg | Read-only routing | Verify endpoint routes; Encypher does not sign OGG. |
| audio/webm | Read-only routing | Verify endpoint routes; Encypher does not sign WebM audio. |

### Documents (same 5 types -- custom JUMBF parser for verify)

### Fonts (same 3 types -- custom JUMBF parser for verify)

| MIME Type | Verify Support | Notes |
|-----------|----------------|-------|
| font/otf | Yes | Custom JUMBF parser reads embedded C2PA table |
| font/ttf | Yes | Custom JUMBF parser reads embedded C2PA table |
| font/sfnt | Yes | Custom JUMBF parser reads embedded C2PA table |

---

## Structurally Constrained Type: audio/aac

The C2PA spec lists `audio/aac` as a supported MIME type (28th of 28). However, raw AAC
(ADTS-framed bitstream) is a bare codec bitstream with no container structure. There is no
metadata block, box structure, or insertion point for a JUMBF manifest store.

**Constraint analysis:**
- Raw ADTS AAC: headerless bitstream of AAC frames with optional ADTS sync headers.
  No container, no metadata structure, no place to embed a C2PA manifest without
  fundamentally altering the bitstream structure.
- AAC-in-M4A: AAC codec data wrapped in an ISO BMFF (ftyp/moov/mdat) container.
  Fully supported via `audio/mp4` -- c2pa-rs embeds the manifest in the BMFF uuid box.
- AAC-in-ADTS with ID3v2: Some tools prepend an ID3v2 header to ADTS AAC, which
  could theoretically carry a GEOB frame (like MP3). However, this is non-standard
  and not reliable.

**Our approach:** The API accepts `audio/aac` at the boundary and canonicalizes it to
`audio/mp4` for signing. This correctly handles the vast majority of AAC content, which
is M4A-wrapped. If a user submits raw ADTS AAC, the signing pipeline will reject it
with a clear error explaining that the file must be in an M4A/MP4 container.

**For conformance submission:** We list `audio/aac` as supported with the constraint that
the AAC content must be in an M4A/ISOBMFF container. Raw ADTS bitstreams cannot carry
C2PA manifests -- this is a fundamental format limitation, not an implementation gap.

## Previously Removed Types (Now Supported)

| MIME Type | Status |
|-----------|--------|
| image/jxl | MOVED TO GENERATOR. Custom ISOBMFF embedder using c2pa box with c2pa.hash.data. Supports JXL ISOBMFF container variant only. |
| audio/flac | MOVED TO GENERATOR. Custom JUMBF/COSE pipeline using FLAC APPLICATION metadata block embedding. |
| font/otf, font/ttf, font/sfnt | MOVED TO GENERATOR. Custom SFNT C2PA table embedding; all three types included. |

---

## MIME Type Aliases

The following aliases are accepted at the API boundary and normalized to their
canonical form before signing or verification.

| Alias | Canonical | Category |
|-------|-----------|----------|
| image/jpg | image/jpeg | Image |
| image/heic-sequence | image/heic | Image |
| image/heif-sequence | image/heif | Image |
| audio/wave | audio/wav | Audio |
| audio/vnd.wave | audio/wav | Audio |
| audio/x-wav | audio/wav | Audio |
| audio/mp3 | audio/mpeg | Audio |
| audio/mpa | audio/mpeg | Audio (MPA alias) |
| audio/m4a | audio/mp4 | Audio |
| audio/x-m4a | audio/mp4 | Audio |
| audio/aac | audio/mp4 | Audio (M4A-wrapped AAC only) |
| video/avi | video/x-msvideo | Video |
| video/msvideo | video/x-msvideo | Video |

---

## Submission JSON (generate / validate lists for Scott)

```json
{
  "generate": {
    "image": [
      "image/jpeg",
      "image/png",
      "image/webp",
      "image/tiff",
      "image/gif",
      "image/heic",
      "image/heif",
      "image/avif",
      "image/svg+xml",
      "image/x-adobe-dng",
      "image/jxl"
    ],
    "video": [
      "video/mp4",
      "video/quicktime",
      "video/x-msvideo",
      "video/x-m4v"
    ],
    "audio": [
      "audio/wav",
      "audio/mpeg",
      "audio/mp4",
      "audio/flac",
      "audio/aac"
    ],
    "document": [
      "application/pdf",
      "application/epub+zip",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/vnd.oasis.opendocument.text",
      "application/oxps"
    ],
    "font": [
      "font/otf",
      "font/ttf",
      "font/sfnt"
    ]
  },
  "validate": {
    "image": [
      "image/jpeg",
      "image/png",
      "image/webp",
      "image/tiff",
      "image/gif",
      "image/heic",
      "image/heif",
      "image/avif",
      "image/svg+xml",
      "image/x-adobe-dng",
      "image/jxl",
      "image/bmp"
    ],
    "video": [
      "video/mp4",
      "video/quicktime",
      "video/x-msvideo",
      "video/x-m4v"
    ],
    "audio": [
      "audio/wav",
      "audio/mpeg",
      "audio/mp4",
      "audio/flac",
      "audio/aac"
    ],
    "document": [
      "application/pdf",
      "application/epub+zip",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/vnd.oasis.opendocument.text",
      "application/oxps"
    ],
    "font": [
      "font/otf",
      "font/ttf",
      "font/sfnt"
    ]
  }
}
```

### Notes on the submission JSON

**All 28 C2PA-specified MIME types are covered.**

- Image: 11 generate types. JXL uses a custom ISOBMFF embedder (c2pa box with
  c2pa.hash.data exclusion). ISOBMFF container variant required; bare codestream not
  supported for signing but is accepted for format detection.
- Video: 4 types including M4V (BMFF variant of MP4).
- Audio: 5 types. audio/aac is accepted at the API boundary and canonicalized to
  audio/mp4 for signing. Raw ADTS AAC without an ISOBMFF container cannot carry a
  C2PA manifest (structural limitation of the format). See "Structurally Constrained
  Type: audio/aac" section above.
- Document: 5 types, all via custom JUMBF/COSE pipeline (not c2pa.Builder).
- Font: 3 types (font/otf, font/ttf, font/sfnt); font/sfnt is the generic SFNT container
  type that covers both OTF and TTF. All three use the same SFNT C2PA table embedder.
- Validate includes all generate types plus image/bmp (read-only) and audio/aac
  (routed to audio/mp4 reader for M4A-wrapped AAC).
