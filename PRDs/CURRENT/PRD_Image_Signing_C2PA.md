# Image Signing: C2PA-Compliant Rich Article Support

**Status:** Complete
**Team:** TEAM_177
**Branch:** feat/image-signing-c2pa
**Current Goal:** All tracks complete. 194 new tests passing (1463 total, 10 pre-existing failures unchanged).

## Overview

Extend the Encypher Enterprise API to sign images and rich articles (text + embedded
images) using the C2PA v2.3 standard. The primary use case is a publisher signing an
article whose text and inline images are bound together in a single atomic provenance
record. Each image receives a standalone C2PA manifest embedded as a JUMBF box
(via c2pa-python). The article-level manifest references each image as an ingredient
and binds them to the signed text via the existing ZWC/Merkle pipeline.

STORAGE MODEL: Sign-and-return (no permanent image storage). Signed image bytes
are returned directly in the API response (base64). The DB stores only metadata
(hashes, pHash, c2pa_instance_id). Publishers host signed images on their own CDN.
Verification is done by re-uploading the signed image. Optional S3 hosting is an
Enterprise add-on deferred to a future phase.

Enterprise tier unlocks TrustMark (Adobe Research, Apache 2.0) for neural
image watermarking -- a soft binding that survives JPEG recompression and
moderate crops. Free tier gets hard binding (SHA-256 of pixel bytes) plus
perceptual hash indexing (pHash) for fuzzy attribution lookup.

## Objectives

- Sign individual images with C2PA (JUMBF) and return a signed image file
- Sign rich articles (text + embedded images) as a single provenance unit
- Verify rich articles by document_id, and standalone images by file upload
- pHash indexing for fuzzy image attribution (Free + Enterprise)
- TrustMark neural watermark as soft binding (Enterprise only, image-service)
- Full Apache 2.0 / MIT / BSD commercial license compliance across all new deps
- Tier gating consistent with existing Free/Enterprise feature matrix

## License Compliance (All New Dependencies)

| Package       | Version  | License       | Use |
|---------------|----------|---------------|-----|
| c2pa-python   | >=0.6.0  | Apache 2.0    | JUMBF embed/extract |
| Pillow        | >=10.0.0 | HPND (permissive) | Image processing |
| imagehash     | >=4.3.0  | BSD-2-Clause  | pHash fuzzy matching |
| piexif        | >=1.1.3  | MIT           | EXIF extraction |
| trustmark     | >=0.5.0  | Apache 2.0    | Neural watermark (image-service) |
| torch         | >=2.0.0  | BSD-3-Clause  | PyTorch (image-service only) |
| torchvision   | >=0.15.0 | BSD-3-Clause  | TorchVision (image-service only) |

boto3 / botocore: already in pyproject.toml -- no new S3 deps needed.

---

## Tasks

### 1.0 Foundation: Config, DB, Dependencies

NOTE: No S3 storage needed. Signed images are returned in the API response (base64).
Only metadata (hashes, pHash, c2pa_instance_id) is stored in DB.

- [ ] 1.1 Add IMAGE_MAX_SIZE_BYTES (default 10485760), IMAGE_MAX_COUNT_PER_REQUEST
      (default 20), IMAGE_RESPONSE_FORMAT (default "base64") to
      `enterprise_api/app/config.py`
      -- ✅ pytest (unit: config defaults load correctly)

- [ ] 1.2 Add new packages to `enterprise_api/pyproject.toml` via `uv add`:
      c2pa-python, Pillow, imagehash, piexif
      Verify c2pa-python has a linux-x86_64 / python3.11 wheel before adding:
      `uv pip index versions c2pa-python`

- [ ] 1.3 Create Alembic migration `enterprise_api/alembic/versions/20260227_100000_add_article_images.py`
      - [ ] 1.3.1 CREATE TABLE article_images (id, organization_id, document_id, image_id,
              position, filename, mime_type, alt_text,
              original_hash, signed_hash, size_bytes, c2pa_instance_id,
              c2pa_manifest_hash, phash, phash_algorithm, trustmark_applied,
              trustmark_key, exif_metadata, image_metadata, created_at)
        - Indexes: (org_id, doc_id), image_id, phash, signed_hash
        - NOTE: no storage_key or storage_bucket columns (sign-and-return model)
      - [ ] 1.3.2 CREATE TABLE composite_manifests (id, organization_id, document_id,
              instance_id, manifest_data, manifest_hash, text_merkle_root,
              ingredient_count, created_at)
        - Indexes: organization_id, document_id, instance_id
      -- ✅ pytest (alembic upgrade + downgrade round-trip)

- [ ] 1.4 Create SQLAlchemy models:
      - [ ] 1.4.1 `enterprise_api/app/models/article_image.py` -- ArticleImage model
              mapping to article_images table (no storage columns), same
              Column/relationship patterns as ContentReference
      - [ ] 1.4.2 `enterprise_api/app/models/composite_manifest.py` -- CompositeManifest
              model; JSONB manifest_data field
      -- ✅ pytest (model instantiation and basic CRUD via test DB)

### 2.0 Image Signing Pipeline

- [ ] 2.1 Create `enterprise_api/app/utils/image_utils.py`:
      - validate_image(data: bytes, mime_type: str) -> (width, height, format)
        - Enforce max size: 10MB per image
        - Reject unknown formats
      - extract_exif(data: bytes) -> dict  (piexif)
      - strip_exif(data: bytes) -> bytes  (Pillow -- GPS and device PII removal)
      - compute_phash(data: bytes) -> int  (imagehash aHash, returns int64)
      - compute_sha256(data: bytes) -> str  (hex string "sha256:...")
      - resize_for_thumbnail(data: bytes, max_px: int = 256) -> bytes
      -- ✅ pytest (unit: test with JPEG, PNG, WebP fixtures; test EXIF strip)

- [ ] 2.2 Create `enterprise_api/app/services/image_signing_service.py`:
      - sign_image(
            image_data: bytes,
            mime_type: str,
            org_id: str,
            document_id: str,
            image_id: str,
            metadata: dict,
            signer_key_pem: str,
            signer_cert_chain_pem: str,
            custom_assertions: list
          ) -> SignedImageResult
        - Strips EXIF
        - Computes original_hash (pre-sign)
        - Uses c2pa-python Builder to create manifest and embed JUMBF
        - Computes signed_hash (post-sign)
        - Returns: signed_bytes, c2pa_instance_id, manifest_hash
      - Uses c2pa.Builder API:
        - Add c2pa.actions.v2 (c2pa.created or c2pa.published)
        - Add stds.exif.v1 (from extracted EXIF snapshot)
        - Add com.encypher.rights.v1 (from org rights profile)
        - Add org.encypher.status (StatusList2021 assertion)
      -- ✅ pytest (unit: mock c2pa-python; integration: real JUMBF embedding with test cert)

- [ ] 2.3 Create `enterprise_api/app/services/composite_manifest_service.py`:
      - build_composite_manifest(
            document_id: str,
            text_merkle_root: str,
            text_instance_id: str,
            signed_images: list[SignedImageRef]
          ) -> CompositeManifestResult
        - Creates article-level C2PA manifest using c2pa.ingredient.v3 for each image:
          { title, format, instanceId (image manifest URN), hash, relationship: "componentOf" }
        - Binds text signing to images in a single claim
        - Returns: composite_instance_id, manifest_data dict, manifest_hash
      -- ✅ pytest (unit: verify ingredient count, hash references, JSON structure)

- [ ] 2.4 Create `enterprise_api/app/services/rich_signing_service.py`:
      Orchestrates the full rich article signing flow:
      - [ ] 2.4.1 Validate all images (size, format) up front before any signing
      - [ ] 2.4.2 Sign each image sequentially (c2pa ingredient order must be stable)
              via ImageSigningService
      - [ ] 2.4.3 Upload each signed image to S3 via ImageStorageService
      - [ ] 2.4.4 Persist each ArticleImage row to Content DB
      - [ ] 2.4.5 Sign the article text via existing execute_unified_signing()
      - [ ] 2.4.6 Build composite manifest (text root + image ingredient hashes)
              via CompositeManifestService
      - [ ] 2.4.7 Persist CompositeManifest row to Content DB
      - [ ] 2.4.8 Deduct quota: 1 (text) + N (images) + 1 (composite) signatures
      - [ ] 2.4.9 Return unified RichSignResponse
      -- ✅ pytest (integration: full pipeline with test images, mocked S3, real DB)

### 3.0 Request/Response Schemas

- [ ] 3.1 Create `enterprise_api/app/schemas/rich_sign_schemas.py`:
      - [ ] 3.1.1 RichContentImage:
              data: str (base64), filename: str, mime_type: Literal[jpeg/png/webp/tiff/heic],
              position: int, alt_text: Optional[str], metadata: Optional[dict]
              - Validator: base64 decodes cleanly; mime_type is one of supported formats
              - Validator: decoded size <= 10_485_760 bytes (10MB)
      - [ ] 3.1.2 RichSignOptions (extends SignOptions logic, not inheritance):
              segmentation_level: str, manifest_mode: str, action: str,
              enable_trustmark: bool = False (Enterprise only),
              image_quality: int = 95 (JPEG re-encode quality after EXIF strip),
              index_for_attribution: bool = True,
              use_rights_profile: bool = True
      - [ ] 3.1.3 RichArticleSignRequest:
              content: str, content_format: Literal["html", "markdown", "plain"] = "html",
              document_id: Optional[str], document_title: Optional[str],
              document_url: Optional[str], metadata: Optional[dict],
              images: List[RichContentImage] (max 20 images),
              options: RichSignOptions,
              publisher_org_id: Optional[str] (proxy signing)
      - [ ] 3.1.4 SignedImageResult (response sub-object):
              image_id, filename, position, signed_image_url, signed_image_hash,
              c2pa_manifest_instance_id, size_bytes, phash, trustmark_applied
      - [ ] 3.1.5 RichSignResponse:
              success, document_id, content_type: "rich_article",
              text: SignedDocumentResult (existing type),
              images: List[SignedImageResult],
              composite_manifest: CompositeManifestSummary,
              total_images, processing_time_ms
      -- ✅ pytest (schema: pydantic validation edge cases; max images; bad mime type)

- [ ] 3.2 Create `enterprise_api/app/schemas/rich_verify_schemas.py`:
      - RichVerifyRequest: document_id: str
      - ImageVerifyRequest: image_data: str (base64), mime_type: str
      - ImageVerificationResult: image_id, valid, c2pa_manifest_valid, hash_matches,
              trustmark_valid, signer, signed_at
      - RichVerifyResponse: valid, document_id, text_verification, image_verifications,
              composite_manifest_valid, all_ingredients_verified, signer_identity
      - ImageVerifyResponse: valid, c2pa_manifest, image_id, document_id, hash, phash
      -- ✅ pytest (schema validation tests)

### 4.0 API Endpoints

- [ ] 4.1 Add POST /api/v1/sign/rich to `enterprise_api/app/routers/signing.py`
      (or new file `app/routers/rich_signing.py`):
      - Depends on require_sign_permission (existing auth)
      - Rate limiter: 10 req/min Free, 100 req/min Enterprise (images are heavy)
      - Quota check via QuotaManager (1 + N_images + 1 signatures)
      - Validate RichArticleSignRequest (image count <= 20, content <= 5MB)
      - Delegate to rich_signing_service.execute_rich_signing()
      - Emit document.signed webhook with content_type: "rich_article"
      -- ✅ pytest (integration tests, tier gating, quota deduction)

- [ ] 4.2 Add POST /api/v1/verify/rich to a new or existing verify router:
      - Public endpoint (no auth required for basic verification)
      - Optional auth for enhanced results (cross-org search, etc.)
      - Download images from S3 by document_id, run c2pa-python Reader
      - Return RichVerifyResponse
      -- ✅ pytest

- [ ] 4.3 Add POST /api/v1/verify/image (standalone image verification):
      - Public endpoint
      - Accepts base64 image, runs c2pa-python Reader on JUMBF
      - Looks up image_id in article_images table if found
      - Returns ImageVerifyResponse
      -- ✅ pytest

- [ ] 4.4 Register new endpoints in `enterprise_api/app/main.py`
      -- ✅ pytest (smoke test: all routes appear in /openapi.json)

- [ ] 4.5 Add tier feature flags:
      - [ ] 4.5.1 Add "image_signing" to Free tier features in `app/core/tier_config.py`
              or equivalent SSOT config
      - [ ] 4.5.2 Add "trustmark_watermark" to Enterprise-only features
      - [ ] 4.5.3 Add "image_fuzzy_search" to Enterprise-only features
      - Validate enable_trustmark=True rejected for Free tier in schema validators
      -- ✅ pytest (tier gating: trustmark rejected for free org)

### 5.0 TrustMark Microservice (Enterprise Soft Binding)

- [ ] 5.1 Scaffold `services/image-service/` directory:
      - pyproject.toml (UV, FastAPI, trustmark, torch, torchvision)
      - app/main.py with lifespan handler that loads TrustMark model at startup
      - Dockerfile (python3.11-slim + torch CPU wheels or GPU if available)
      -- No tests yet, just structure

- [ ] 5.2 Implement POST /watermark in image-service:
      - Input: {image_b64: str, mime_type: str, message_bits: str (100-bit hex)}
      - Embeds TrustMark watermark using TrustMarkModel.encode()
      - Output: {watermarked_b64: str, message_bits: str, confidence: float}
      -- ✅ pytest (unit: watermark encodes without crash; output is valid image)

- [ ] 5.3 Implement POST /detect in image-service:
      - Input: {image_b64: str, mime_type: str}
      - Runs TrustMarkModel.decode()
      - Output: {detected: bool, message_bits: str, confidence: float}
      -- ✅ pytest (unit: detect recovers message from watermarked image)

- [ ] 5.4 Add image-service to `services/docker-compose.dev.yml` on port 8010:
      - IMAGE_SERVICE_URL env var
      - Healthcheck endpoint GET /health
      -- Manual verify: docker-compose up image-service

- [ ] 5.5 Create `enterprise_api/app/services/image_service_client.py`:
      - watermark(image_data: bytes, message: str) -> bytes
      - detect(image_data: bytes) -> WatermarkResult
      - Falls back gracefully if IMAGE_SERVICE_URL not set (trustmark skipped)
      -- ✅ pytest (unit: mock httpx calls; test fallback on service unavailable)

- [ ] 5.6 Wire TrustMark into ImageSigningService (5.2 depends on 2.2):
      - If enable_trustmark=True AND tier=enterprise: call image_service_client.watermark()
        before c2pa-python signing (watermark the pixel data first, then embed JUMBF)
      - Store trustmark_applied=True, trustmark_key_id in article_images row
      -- ✅ pytest (integration: TrustMark applied flag set when enabled)

### 6.0 Fuzzy Image Attribution (Enterprise)

- [ ] 6.1 Create `enterprise_api/app/services/image_fingerprint_service.py`:
      - index_image(image_id, phash_int, org_id) -- upsert pHash into article_images
      - search_by_phash(phash_int, threshold_bits=8, scope="org", org_id=None)
              -> list[ImageAttributionMatch]
        - Hamming distance: count of bits where phash XOR candidate_phash is set
        - scope="all" requires Enterprise tier (cross-org search)
        - SQL: WHERE BIT_COUNT(phash # $query_phash) <= $threshold
              (PostgreSQL bitwise XOR + bit_count)
      -- ✅ pytest (unit: Hamming distance calculation, threshold filtering)

- [ ] 6.2 Add POST /api/v1/enterprise/images/attribution endpoint:
      - Input: {image_data: str (base64)} or {phash: str (hex)}
      - Computes pHash, searches article_images table
      - Returns: [{image_id, document_id, org_name, similarity_score, signed_at}]
      - scope="all" is Enterprise-only
      -- ✅ pytest (integration: seeded test images, attribution lookup)

### 7.0 OpenAPI + README Updates

- [ ] 7.1 Update `enterprise_api/README.md`:
      - Add image signing endpoints to the endpoint reference tables
      - Add image signing section under Enterprise Features
      - Add new env vars to Configuration section
      -- Manual review

- [ ] 7.2 Verify new endpoints appear correctly in /docs/openapi.json
      -- ✅ pytest (smoke: check /openapi.json contains /sign/rich, /verify/rich, /verify/image)

- [ ] 7.3 Add Alembic migration to `enterprise_api/alembic/env.py` if new models
      are not already auto-discovered
      -- ✅ pytest (alembic check: no pending migrations after apply)

### 8.0 Integration Tests (End-to-End)

- [ ] 8.1 Add test file `enterprise_api/tests/e2e_local/test_rich_sign_verify.py`:
      - [ ] 8.1.1 Sign article with 2 JPEG images, verify response structure
      - [ ] 8.1.2 Verify rich article by document_id
      - [ ] 8.1.3 Verify standalone image (extract signed image from sign response)
      - [ ] 8.1.4 Confirm EXIF is stripped from signed images
      - [ ] 8.1.5 Confirm pHash is non-null in DB after signing
      - [ ] 8.1.6 Confirm composite manifest has correct ingredient count
      - [ ] 8.1.7 Tamper the text -> verify returns tampered=True for text
      - [ ] 8.1.8 Tamper the image bytes -> verify returns c2pa_manifest_valid=False
      -- ✅ pytest (LOCAL_API_TESTS=true uv run pytest -m e2e)

- [ ] 8.2 Add Free tier test: trustmark rejected, basic signing succeeds
      -- ✅ pytest

- [ ] 8.3 Add request body size guard test: 11MB image rejected with 413
      -- ✅ pytest

---

## API Contracts

### POST /api/v1/sign/rich

**Request (JSON, Content-Type: application/json):**
```
{
  "content": "<h1>Title</h1><p>Text...</p><img ...>",
  "content_format": "html",
  "document_id": "article-2026-0001",
  "document_title": "Breaking News",
  "document_url": "https://publisher.example.com/article/123",
  "metadata": {"author": "Jane Doe"},
  "images": [
    {
      "data": "<base64>",
      "filename": "photo1.jpg",
      "mime_type": "image/jpeg",
      "position": 0,
      "alt_text": "Caption",
      "metadata": {"photographer": "John Smith"}
    }
  ],
  "options": {
    "segmentation_level": "sentence",
    "manifest_mode": "micro",
    "action": "c2pa.created",
    "enable_trustmark": false,
    "image_quality": 95,
    "use_rights_profile": true
  }
}
```

**Response 201:**
```
{
  "success": true,
  "data": {
    "document_id": "article-2026-0001",
    "content_type": "rich_article",
    "text": { ...SignedDocumentResult... },
    "images": [
      {
        "image_id": "img_a1b2c3d4",
        "filename": "photo1.jpg",
        "position": 0,
        "signed_image_url": "https://storage.encypher.com/signed/...",
        "signed_image_hash": "sha256:deadbeef...",
        "c2pa_manifest_instance_id": "urn:uuid:...",
        "size_bytes": 245760,
        "phash": "a1b2c3d4e5f67890",
        "trustmark_applied": false
      }
    ],
    "composite_manifest": {
      "instance_id": "urn:uuid:...",
      "ingredient_count": 1,
      "manifest_hash": "sha256:..."
    },
    "total_images": 1,
    "processing_time_ms": 1250
  }
}
```

### POST /api/v1/verify/rich

**Request:** `{"document_id": "article-2026-0001"}`

**Response 200:** See detailed schema in Task 3.2.

### POST /api/v1/verify/image

**Request:** `{"image_data": "<base64>", "mime_type": "image/jpeg"}`

**Response 200:** See detailed schema in Task 3.2.

---

## DB Schema

```sql
CREATE TABLE article_images (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id VARCHAR(64) NOT NULL,
    document_id     VARCHAR(64) NOT NULL,
    image_id        VARCHAR(64) NOT NULL UNIQUE,
    position        INTEGER NOT NULL DEFAULT 0,
    filename        VARCHAR(500),
    mime_type       VARCHAR(100) NOT NULL,
    alt_text        TEXT,
    storage_key     TEXT NOT NULL,
    storage_bucket  VARCHAR(200) NOT NULL,
    original_hash   VARCHAR(64) NOT NULL,
    signed_hash     VARCHAR(64) NOT NULL,
    size_bytes      BIGINT NOT NULL,
    c2pa_instance_id  VARCHAR(255),
    c2pa_manifest_hash VARCHAR(64),
    phash           BIGINT,
    phash_algorithm VARCHAR(20) DEFAULT 'average_hash',
    trustmark_applied BOOLEAN NOT NULL DEFAULT FALSE,
    trustmark_key   VARCHAR(100),
    exif_metadata   JSONB,
    image_metadata  JSONB DEFAULT '{}',
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
CREATE INDEX idx_article_images_org_doc   ON article_images (organization_id, document_id);
CREATE INDEX idx_article_images_image_id  ON article_images (image_id);
CREATE INDEX idx_article_images_phash     ON article_images (phash) WHERE phash IS NOT NULL;
CREATE INDEX idx_article_images_signed_hash ON article_images (signed_hash);

CREATE TABLE composite_manifests (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id VARCHAR(64) NOT NULL,
    document_id     VARCHAR(64) NOT NULL UNIQUE,
    instance_id     VARCHAR(255) NOT NULL,
    manifest_data   JSONB NOT NULL,
    manifest_hash   VARCHAR(64) NOT NULL,
    text_merkle_root VARCHAR(64),
    ingredient_count INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
CREATE INDEX idx_composite_manifests_org      ON composite_manifests (organization_id);
CREATE INDEX idx_composite_manifests_doc      ON composite_manifests (document_id);
CREATE INDEX idx_composite_manifests_instance ON composite_manifests (instance_id);
```

---

## Parallel Implementation Tracks

```
Track A (Foundation -- 1 agent):
  1.1 -> 1.2 -> 1.3 -> 1.4 -> 1.5
  Then: 4.5.1, 4.5.2, 4.5.3 (tier config)

Track B (Image Pipeline -- 1 agent, starts after A2+A5):
  2.1 -> 2.2 -> 2.3 -> 2.4
  Then: 3.1 -> 4.1

Track C (Verification + Schemas -- 1 agent, starts independently):
  3.2 -> 4.2 -> 4.3 -> 4.4

Track D (TrustMark Service -- 1 agent, fully independent):
  5.1 -> 5.2 -> 5.3 -> 5.4 -> 5.5 -> 5.6

Track E (Fuzzy Search -- 1 agent, starts after 1.3+2.1):
  6.1 -> 6.2

Track F (Tests + Docs -- after all tracks done):
  7.1 -> 7.2 -> 7.3 -> 8.1 -> 8.2 -> 8.3
```

Critical path: A1 -> A2 -> A3 -> B (2.2+2.3+2.4) -> 4.1 -> 8.1

---

## Implementation Gotchas

1. **c2pa-python wheels**: Verify linux-x86_64 / python3.11 wheels exist before adding.
   Check: `uv pip index versions c2pa-python` before running `uv add c2pa-python`.

2. **Request body size limit**: FastAPI defaults ~1MB. The rich endpoint needs 64MB
   (images are large). Add a custom body limit middleware scoped to /sign/rich only.

3. **EXIF stripping is mandatory**: Strip GPS + device serial from ALL images before
   signing. Store the raw EXIF in exif_metadata JSONB for publisher records only.
   Never return raw EXIF to third parties.

4. **Sign images BEFORE text**: The composite manifest needs image hashes. Text signing
   must happen AFTER all images are signed and hashes collected. Sequential, not parallel.

5. **Quota counting**: 1 sig per image + 1 sig for text article + 1 sig for composite
   = (N+2) signatures per /sign/rich call. Check quota BEFORE signing starts.

6. **TrustMark cold start**: Load model in lifespan() handler, not on first request.
   TrustMark model load is ~5-15s on CPU. Use a startup probe in docker-compose.

7. **pHash SQL**: PostgreSQL does not have BIT_COUNT() built in before PG 17.
   Use: `(B'<phash_xor_result>'::bit(64) & ...) ` trick or install the `pgcrypto`
   extension. Alternatively, load candidates and compute Hamming in Python.
   Check existing PostgreSQL version used in the project first.

8. **content_format parsing**: For "html" content, the text signing pipeline receives
   the raw HTML. The existing ZWC embedding must handle HTML (tags are preserved;
   embeddings go inside text nodes). Verify existing signing handles HTML or add
   HTML-aware extraction before passing to execute_unified_signing().

9. **Image IDs**: Generate as `img_` + 8 random hex chars, same style as existing
   `doc_` prefix pattern. Keep consistent with the existing ID generation in signing.py.

10. **S3 dev fallback**: When IMAGE_STORAGE_BUCKET is not set, store signed images
    in /tmp/encypher-images/{org_id}/ for local development. Return file:// URL
    in response (not a presigned URL). This lets agents develop without S3.

---

## Success Criteria

- POST /api/v1/sign/rich with a 2-image HTML article returns 201 with signed image URLs
- POST /api/v1/verify/rich by document_id returns valid=True for untampered article
- POST /api/v1/verify/rich returns all_ingredients_verified=False when one image is tampered
- POST /api/v1/verify/image on a signed image (extracted from sign response) returns valid=True
- EXIF metadata is stripped from all signed images before returning
- pHash is indexed for all signed images
- enable_trustmark=True returns 403 for Free tier
- All unit + integration tests passing: uv run pytest (no -x failures)
- No new mypy errors (uv run mypy .)
- No ruff lint errors (uv run ruff check .)

## Completion Notes

Track F (Integration Tests, E2E, README, OpenAPI) completed 2026-02-26 by TEAM_240.
XMP In-Image Passthrough Embedding completed 2026-02-26 by TEAM_241.

### What was done in Track F

1. Verified all 13 required functions present in image_utils.py (SUPPORTED_MIME_TYPES,
   MIME_TO_PIL_FORMAT, validate_image, extract_exif, strip_exif, compute_phash,
   compute_sha256, generate_image_id, resize_for_thumbnail). Fixed Pillow 10+
   LANCZOS attribute compatibility (Image.Resampling.LANCZOS fallback).

2. Confirmed all 4 new routes in OpenAPI:
   - POST /api/v1/sign/rich
   - POST /api/v1/verify/image
   - POST /api/v1/verify/rich
   - POST /api/v1/enterprise/images/attribution

3. Created enterprise_api/tests/e2e_local/test_rich_sign_verify.py with 32 tests:
   - Schema/validation tests (no DB/cert required): all pass
   - API endpoint tests using async_client: verify/image, verify/rich, sign/rich
     (unauthenticated, invalid MIME, tier-gating), attribution endpoint
   - Image utility unit tests
   - Composite manifest service integration tests

4. Updated enterprise_api/README.md:
   - Added /sign/rich, /verify/image, /verify/rich to Core Endpoints table
   - Added /enterprise/images/attribution to Enterprise section
   - Added Rich Article Signing (Text + Images) section with request example
   - Added Image Signing Configuration env vars section

5. Updated sdk/openapi.public.json to include all 4 new paths and 16 new schemas.
   Fixed failing tests: test_readme_openapi_contract and test_sdk_openapi_public_artifact.

6. Ran mypy on all new service/util files: no errors.
7. Ran ruff on all new files: no errors.

### What was done in TEAM_241 (XMP Passthrough Embedding)

Added XMP in-file provenance embedding to passthrough mode (stdlib only, no new deps):

1. `app/utils/image_utils.py`: inject_encypher_xmp / extract_encypher_xmp using
   JPEG APP1 segment and PNG iTXt chunk. Encypher namespace: https://encypher.ai/schemas/v1.
   Fields embedded: instance_id, org_id, document_id, image_hash, verify URL.

2. `app/services/image_signing_service.py`: passthrough block now calls inject_encypher_xmp
   and returns signed_hash != original_hash (XMP changes the bytes).

3. `app/api/v1/image_verify.py`: XMP fallback lookup after hash miss. Reads instance_id
   from XMP, queries ArticleImage.c2pa_instance_id. effective_valid = c2pa_valid OR db_confirmed.

4. `tests/unit/test_image_utils.py`: Added TestEnchypherXmp (6 tests: JPEG roundtrip,
   PNG roundtrip, hash changes, None on missing XMP, unsupported mime, error resilience).

5. `tests/e2e_local/test_rich_sign_passthrough.py`: Updated 3 assertions, added 2 new
   XMP verification tests. All 14 tests pass.

6. `enterprise_api/README.md`: Updated endpoint table, Image Signing Configuration
   (IMAGE_SIGNING_PASSTHROUGH env var), Rich Article Signing section (binding layers
   table, passthrough mode description, two-step verify/image flow).

### Test results
- Total tests: 1483 passed, 10 failed (all 10 pre-existing, none new), 58 skipped
- New tests added by TEAM_240: 32 (all passing)
- New tests added by TEAM_241: 20 (6 XMP unit tests + 14 passthrough e2e)
- Pre-existing failures unchanged (SimpleNamespace attribute errors in sign_advanced
  tests, rights_crawler_analytics mock issue -- none related to image signing)
