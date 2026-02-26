# Image Signing Implementation Guide

## Overview

Encypher image signing embeds provenance metadata into image binaries so that
authenticity can be verified even after an image has been re-hosted on a CDN,
re-encoded, or stripped of EXIF data. The system uses a layered strategy:

| Layer | Mechanism | Survives re-encode? | Tier |
|-------|-----------|---------------------|------|
| Hard binding | SHA-256 of original pixel bytes (`original_hash`) | No | All |
| In-file reference | XMP (ISO 16684) with `instance_id` in APP1/iTXt | Yes | All |
| C2PA JUMBF | Full cryptographic manifest in JUMBF box | Yes | When cert configured |
| Soft binding | TrustMark neural watermark (survives JPEG recompression) | Yes | Enterprise only |
| pHash fuzzy index | Perceptual hash Hamming distance search | Near-duplicate | All |

---

## Storage Model (sign-and-return)

Encypher does NOT store image bytes. Publishers sign images via `/api/v1/sign/rich`
and receive back base64-encoded signed bytes. Publishers host signed images on their
own CDN. The `article_images` table records only:

- `original_hash` -- SHA-256 of EXIF-stripped pixel data before signing
- `signed_hash` -- SHA-256 of the returned bytes (differs from original because XMP is injected)
- `c2pa_instance_id` -- XMP `instance_id` field; lookup key for hash-miss verification
- `phash` -- 64-bit perceptual hash for fuzzy attribution
- `c2pa_manifest_hash` -- sentinel `sha256:000...` in passthrough mode; full JUMBF hash when cert present

---

## XMP In-File Reference

### Why XMP?

XMP (ISO 16684) is a standards-compatible metadata layer:
- Readable by major image editors and CMS platforms
- Survives CDN re-hosting (unlike EXIF which many CDNs strip)
- No new Python dependencies: implemented with `struct` + `zlib` + `xml.etree.ElementTree`
- Works in JPEG (APP1 segment) and PNG (iTXt chunk)

### JPEG embedding

XMP is inserted as an APP1 segment immediately after the SOI (`\xff\xd8`) marker:

```
\xff\xd8                        -- SOI
\xff\xe1 <len-2b>               -- APP1 marker + segment length
http://ns.adobe.com/xap/1.0/\0  -- XMP header (29 bytes, NUL-terminated)
<?xpacket begin='...' id='...'>
<x:xmpmeta ...>
  <rdf:RDF>
    <rdf:Description rdf:about=''
      xmlns:ency='https://encypher.ai/schemas/v1'
      ency:instance_id='urn:uuid:<uuid>'
      ency:org_id='<org_id>'
      ency:document_id='<document_id>'
      ency:image_hash='<original_hash>'
      ency:verify='https://verify.encypher.ai/'
    />
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end='r'?>
<remaining JPEG segments...>
```

### PNG embedding

XMP is inserted as an `iTXt` chunk immediately after the `IHDR` chunk (offset 33):

```
<IHDR chunk (always at bytes 8-32)>
4-byte length | "iTXt" | "XML:com.adobe.xmp\0\0\0\0\0" | <xmp bytes> | 4-byte CRC
<remaining PNG chunks...>
```

The 23-byte keyword prefix is `XML:com.adobe.xmp\x00\x00\x00\x00\x00`
(keyword + NUL + compression_flag + compression_method + language + NUL + translated_kw + NUL).

### Encypher XMP namespace fields

| Field | Value | Example |
|-------|-------|---------|
| `ency:instance_id` | `urn:uuid:<uuid4>` | `urn:uuid:550e8400-e29b-41d4-a716-446655440000` |
| `ency:org_id` | Organization ID | `org_acme_publishing` |
| `ency:document_id` | Article document ID | `article-2026-001` |
| `ency:image_hash` | SHA-256 of original pixel bytes | `sha256:abc123...` |
| `ency:verify` | Verification URL | `https://verify.encypher.ai/` |

### Unsupported formats

WebP and TIFF are not modified -- `inject_encypher_xmp()` returns the original bytes
unchanged. These images are still registered in the DB (hard binding + pHash).

---

## Passthrough Mode

When `IMAGE_SIGNING_PASSTHROUGH=true` (or when no signing certificate is configured),
full C2PA JUMBF embedding is skipped. XMP is still injected.

Key behaviors:
- `c2pa_signed=false` in the `sign/rich` response
- `signed_hash != original_hash` -- XMP bytes are appended inside the binary
- `c2pa_manifest_hash` = `sha256:000...` (sentinel value, not a real JUMBF hash)
- `/verify/image` can still return `valid=true` via XMP instance_id DB lookup

This mode is used in local development and CI where no X.509 signing certificate
is available.

---

## Two-Step Image Verification

`POST /api/v1/verify/image` uses a two-step process:

```
[Submit base64 image]
        |
        v
[1. C2PA JUMBF check]
   - Extract JUMBF manifest from image binary
   - Validate manifest signature against trust list
   - Compute signed_hash, look up in article_images
        |
        v
   hash matched? --> valid=true (C2PA verified)
        |
        v (no match)
[2. XMP fallback]
   - Parse XMP APP1 (JPEG) or iTXt (PNG)
   - Extract ency:instance_id
   - SELECT * FROM article_images WHERE c2pa_instance_id = ?
        |
        v
   record found? --> valid=true (DB-confirmed, c2pa_signed may be false)
        |
        v (not found)
   valid=false
```

The XMP fallback is the primary verification path for passthrough-mode images,
and also handles images where a CDN re-encoded the JPEG (changing signed_hash).

---

## Traefik Routing

In the local dev stack, `/api/v1/verify/image` must be routed to the **enterprise-api**
(port 9000), not the verification-service (port 8005). The Traefik config uses
priority to achieve this:

```yaml
# infrastructure/traefik/routes-local.yml
verify-image-router:
  rule: "PathPrefix(`/api/v1/verify/image`)"
  service: enterprise-api
  priority: 110          # higher than verify-router (100)

verify-router:
  rule: "PathPrefix(`/api/v1/verify`)"
  service: verification-service
  priority: 100          # catches all other /verify/* paths
```

Without the `verify-image-router` at priority 110, `verify-router` captures the
request and sends it to the verification-service, which returns 405 because it
lacks the `/verify/image` endpoint.

---

## Source Files

| File | Role |
|------|------|
| `app/utils/image_utils.py` | `inject_encypher_xmp()`, `extract_encypher_xmp()`, JPEG/PNG helpers |
| `app/services/image_signing_service.py` | Passthrough block: calls inject, computes signed_hash |
| `app/api/v1/image_verify.py` | `/verify/image` endpoint; JUMBF check then XMP fallback |
| `app/models/article_image.py` | `ArticleImage` SQLAlchemy model (`article_images` table) |
| `app/routers/rich_signing.py` | `/sign/rich` endpoint |
| `infrastructure/traefik/routes-local.yml` | `verify-image-router` priority 110 |

---

## Screenshots

| State | Screenshot |
|-------|-----------|
| Drop zone (idle) | `docs/images/tools/inspect/01-dropzone.png` |
| No Provenance Found | `docs/images/tools/inspect/02-no-provenance-found.png` |
| Provenance Verified | `docs/images/tools/inspect/03-provenance-verified.png` |
