"""Signing router for content signing with C2PA manifests.

This module provides the unified /sign endpoint with tier-gated options.
All signing features are available through this single endpoint.
"""

import asyncio
import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_content_db, get_db
from app.dependencies import get_current_organization_dep, require_sign_permission
from app.middleware.api_rate_limiter import api_rate_limiter
from app.observability.metrics import increment
from app.schemas.api_response import ErrorCode, get_batch_limit
from app.schemas.sign_schemas import UnifiedSignRequest
from app.services.organization_bootstrap import ensure_organization_exists
from app.services.unified_signing_service import execute_unified_signing
from app.services.webhook_dispatcher import emit_document_signed
from app.utils.print_stego import build_payload, encode_print_fingerprint
from app.utils.quota import QuotaManager, QuotaType

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Unified Sign Endpoint
# =============================================================================


@router.post(
    "/sign",
    status_code=status.HTTP_201_CREATED,
    summary="Sign content with C2PA manifest",
    description="""
Sign content with C2PA manifest. Features are gated by tier.

---

## Tier Feature Matrix

| Feature | Free | Enterprise |
|---------|------|------------|
| Basic C2PA signing | ✅ | ✅ |
| Sentence / paragraph / section segmentation | ✅ | ✅ |
| Advanced manifest modes | ✅ | ✅ |
| Attribution indexing | ✅ | ✅ |
| Custom assertions | ✅ | ✅ |
| Rights metadata | ✅ | ✅ |
| Batch signing | up to 10 | up to 100 |
| Word-level segmentation | ❌ | ✅ |
| Dual binding | ❌ | ✅ |
| Fingerprinting | ❌ | ✅ |

---

## Request Body

Provide **either** `text` (single document) **or** `documents` (batch), plus an `options` object.

### Top-level fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | one of `text` / `documents` | Content to sign (single document, max 1 MB). |
| `document_id` | string | no | Custom document identifier (1-255 chars). Auto-generated if omitted. |
| `document_title` | string | no | Human-readable title (max 500 chars). |
| `document_url` | string | no | Canonical URL of the document (max 1000 chars). |
| `metadata` | object | no | Arbitrary key-value metadata attached to the document. |
| `documents` | array | one of `text` / `documents` | List of `{text, document_id?, document_title?, document_url?, metadata?}` objects for batch signing. |
| `options` | object | no | Signing options (see below). All fields have sensible defaults. |

---

## Options Reference

### Segmentation & Structure

| Option | Type | Default | Values | Tier | Description |
|--------|------|---------|--------|------|-------------|
| `segmentation_level` | string | `"document"` | `document`, `sentence`, `paragraph`, `section`, `word` | `word` requires Enterprise | Granularity at which text is split and individually signed. Higher granularity enables per-segment tamper detection. |
| `segmentation_levels` | string[] | *null* | subset of `sentence`, `paragraph`, `section` | Free | Build Merkle trees at multiple levels simultaneously for multi-resolution verification. |

### Manifest & Embedding

| Option | Type | Default | Values | Tier | Description |
|--------|------|---------|--------|------|-------------|
| `manifest_mode` | string | `"full"` | `full`, `lightweight_uuid`, `minimal_uuid`, `hybrid`, `zw_embedding`, `micro` | Free | Controls how the C2PA manifest and per-segment markers are embedded. `full` = standard C2PA wrapper. `micro` = ultra-compact per-segment markers controlled by `ecc` and `embed_c2pa` flags. A C2PA manifest is always generated; `embed_c2pa` controls whether it's embedded in content; `store_c2pa_manifest` controls DB persistence. |
| `ecc` | bool | `true` | | Free | Enable Reed-Solomon error correction for micro mode (44 chars/segment vs 36). Ignored for non-micro modes. |
| `embed_c2pa` | bool | `true` | | Free | Embed full C2PA document manifest into signed content for micro mode. When false, per-sentence markers only; C2PA manifest is still generated and stored in DB. Ignored for non-micro modes. |
| `embedding_strategy` | string | `"single_point"` | `single_point`, `distributed`, `distributed_redundant` | `distributed_redundant` requires Enterprise | How the invisible signature is placed within each segment. `single_point` = one location. `distributed` = spread across the segment. `distributed_redundant` = distributed with ECC for resilience. |
| `distribution_target` | string | *null* | `whitespace`, `punctuation`, `all_chars` | Free | Which character positions are used when `embedding_strategy` is `distributed` or `distributed_redundant`. |

### C2PA Provenance

| Option | Type | Default | Values | Tier | Description |
|--------|------|---------|--------|------|-------------|
| `action` | string | `"c2pa.created"` | `c2pa.created`, `c2pa.edited` | Free | C2PA action type. Use `c2pa.created` for new content, `c2pa.edited` for modifications. |
| `previous_instance_id` | string | *null* | any | Free | The `instance_id` from a previous signing response. Required when `action` is `c2pa.edited` to form a provenance chain. |
| `document_type` | string | `"article"` | `article`, `legal_brief`, `contract`, `ai_output` | Free | Semantic document type included in the manifest. |
| `claim_generator` | string | *null* | any | Free | Optional claim generator identifier for C2PA manifests (e.g. your application name). |
| `digital_source_type` | string | *null* | IPTC URI | Free | IPTC digital source type URI, e.g. for AI-generated content. |

### Advanced Features

| Option | Type | Default | Tier | Description |
|--------|------|---------|------|-------------|
| `index_for_attribution` | bool | `false` | Free | Index content segments for later attribution and plagiarism detection via `/verify/advanced`. |
| `add_dual_binding` | bool | `false` | Enterprise | Enable an additional integrity binding layer for enhanced tamper resistance. |
| `include_fingerprint` | bool | `false` | Enterprise | Generate a robust content fingerprint that can survive minor text modifications. |
| `disable_c2pa` | bool | `false` | Enterprise | Opt out of C2PA manifest embedding for non-micro modes; only basic metadata is attached. For micro mode, use `embed_c2pa` instead. |
| `store_c2pa_manifest` | bool | `true` | Free | Persist generated C2PA manifest in content DB for DB-backed verification. Applies to all modes that generate a manifest. |
| `enable_print_fingerprint` | bool | `false` | Enterprise | Print Leak Detection — embed imperceptible spacing patterns (U+2009 THIN SPACE vs U+0020) that survive printing and scanning, enabling source identification from leaked physical or PDF copies. |

### Custom Assertions & Rights (Business+)

| Option | Type | Default | Tier | Description |
|--------|------|---------|------|-------------|
| `custom_assertions` | array | *null* | Free | List of `{label, data}` objects to include as custom C2PA assertions. |
| `template_id` | string | *null* | Free | ID of a pre-registered assertion template to apply. |
| `validate_assertions` | bool | `true` | Free | Whether to validate custom assertions against registered JSON schemas. |
| `rights` | object | *null* | Free | Rights metadata: `{copyright_holder, license_url, usage_terms, syndication_allowed, embargo_until, contact_email}`. |
| `license` | object | *null* | Free | License info: `{type, url, contact_email}`. |
| `actions` | array | *null* | Free | List of C2PA action assertion objects. |

### Output Options

| Option | Type | Default | Values | Description |
|--------|------|---------|--------|-------------|
| `embedding_options.format` | string | `"plain"` | `plain`, `html`, `markdown`, `json` | Output format for the signed text. |
| `embedding_options.method` | string | `"invisible"` | `invisible`, `data-attribute`, `span`, `comment` | How the embedding is represented. `invisible` uses zero-width Unicode characters. |
| `embedding_options.include_text` | bool | `true` | | Whether to include the embedded text in the response. |
| `return_embedding_plan` | bool | `false` | | When `true`, includes `document.embedding_plan` with codepoint-based marker insertion operations for formatting-preserving clients. |
| `expires_at` | datetime | *null* | ISO 8601 | Optional expiration timestamp for the embeddings. |

---

## Examples

**Single document (minimal):**
```json
{
    "text": "The Senate passed a landmark bill today.",
    "document_title": "Senate Bill"
}
```

**Single document (with options):**
```json
{
    "text": "The Senate passed a landmark bill today. The vote was 67-33.",
    "document_title": "Senate Bill",
    "options": {
        "segmentation_level": "sentence",
        "manifest_mode": "micro",
        "index_for_attribution": true,
        "action": "c2pa.created"
    }
}
```

**Batch:**
```json
{
    "documents": [
        {"text": "First article...", "document_title": "Article 1"},
        {"text": "Second article...", "document_title": "Article 2"}
    ],
    "options": {
        "segmentation_level": "sentence",
        "embedding_strategy": "distributed"
    }
}
```

**Edit provenance chain:**
```json
{
    "text": "Updated article content...",
    "options": {
        "action": "c2pa.edited",
        "previous_instance_id": "urn:uuid:abc123..."
    }
}
```

The response includes `meta.features_gated` showing features available at higher tiers.

When `options.return_embedding_plan=true`, each signed document may also include:

```json
"embedding_plan": {
  "index_unit": "codepoint",
  "operations": [
    {"insert_after_index": 128, "marker": "..."}
  ]
}
```

This allows clients (e.g. Office add-ins) to insert only invisible markers at indexed positions while preserving native formatting.
""",
    responses={
        201: {"description": "Content signed successfully"},
        400: {"description": "Invalid request"},
        403: {"description": "Feature requires higher tier"},
        429: {"description": "Rate limit exceeded"},
    },
)
async def sign_content(
    request: UnifiedSignRequest,
    http_request: Request,
    response: Response,
    organization: dict = Depends(require_sign_permission),
    core_db: AsyncSession = Depends(get_db),
    content_db: AsyncSession = Depends(get_content_db),
):
    """
    Unified sign endpoint with tier-gated options.
    
    This endpoint consolidates /sign and /sign/advanced into a single endpoint.
    Features are automatically gated based on the organization's tier.
    """
    correlation_id = f"req-{uuid.uuid4().hex[:12]}"
    # TEAM_145: Default to free tier
    tier = (organization.get("tier") or "free").lower().replace("-", "_")
    org_id = organization["organization_id"]
    
    # Get batch size for rate limiting
    documents = request.get_documents()
    batch_size = len(documents)
    
    # Check batch limit
    batch_limit = get_batch_limit(tier)
    if batch_size > batch_limit:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": ErrorCode.E_TIER_REQUIRED,
                    "message": f"Batch size {batch_size} exceeds limit of {batch_limit} for {tier} tier",
                    "hint": "Upgrade your plan to increase batch limits",
                },
                "correlation_id": correlation_id,
                "meta": {"tier": tier},
            },
        )
    
    # Rate limiting
    rate_result = api_rate_limiter.check_with_reset(
        organization_id=org_id,
        scope="sign",
        tier=tier,
    )
    
    for header, value in api_rate_limiter.get_headers(rate_result).items():
        response.headers[header] = value
    
    if not rate_result.allowed:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": ErrorCode.E_RATE_SIGN,
                    "message": "Signing rate limit exceeded",
                    "hint": f"Rate limit is {rate_result.limit} requests per minute for {tier} tier",
                },
                "correlation_id": correlation_id,
                "meta": {"tier": tier, "rate_limit_remaining": 0},
            },
            headers=api_rate_limiter.get_headers(rate_result),
        )
    
    await ensure_organization_exists(core_db, organization)
    
    # Check monthly quota
    await QuotaManager.check_quota(
        db=core_db,
        organization_id=org_id,
        quota_type=QuotaType.C2PA_SIGNATURES,
        increment=batch_size,
    )
    
    # Execute unified signing
    result = await execute_unified_signing(
        request=request,
        organization=organization,
        core_db=core_db,
        content_db=content_db,
        correlation_id=correlation_id,
    )
    
    # Post-sign: attach rights snapshot when use_rights_profile=True
    if result.get("success") and request.options.use_rights_profile:
        await _attach_rights_snapshot(
            result=result,
            org_id=org_id,
            core_db=core_db,
            content_db=content_db,
        )

    # Post-sign: apply Print Leak Detection when enable_print_fingerprint=True
    if result.get("success") and request.options.enable_print_fingerprint:
        _apply_print_fingerprint(result=result, org_id=org_id)

    # Add quota headers
    quota_headers = await QuotaManager.get_quota_headers(
        db=core_db,
        organization_id=org_id,
        quota_type=QuotaType.C2PA_SIGNATURES,
    )
    for header, value in quota_headers.items():
        response.headers[header] = value

    increment("sign_requests")
    
    # Emit webhook events for each document
    if result.get("success") and result.get("data"):
        data = result["data"]
        if data.get("document"):
            asyncio.create_task(
                emit_document_signed(
                    organization_id=org_id,
                    document_id=data["document"]["document_id"],
                    title=request.document_title,
                    document_type=request.options.document_type,
                )
            )
        elif data.get("documents"):
            for doc_result in data["documents"]:
                asyncio.create_task(
                    emit_document_signed(
                        organization_id=org_id,
                        document_id=doc_result["document_id"],
                        title=doc_result.get("metadata", {}).get("title"),
                        document_type=request.options.document_type,
                    )
                )
    
    # Return appropriate status code
    if result.get("success"):
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)
    else:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=result)


def _apply_print_fingerprint(result: dict, org_id: str) -> None:
    """Post-sign hook: encode a thin-space fingerprint into signed_text.

    Operates in-place on ``result["data"]``.  Modifies ``signed_text`` for each
    document (single or batch) and injects ``print_fingerprint`` metadata.
    Errors are swallowed so they never break a successful sign response.
    """
    try:
        data = result.get("data", {})

        def _fingerprint_doc(doc: dict) -> None:
            doc_id = doc.get("document_id", "")
            signed_text = doc.get("signed_text")
            if not signed_text or not doc_id:
                return
            payload = build_payload(org_id, doc_id)
            doc["signed_text"] = encode_print_fingerprint(signed_text, payload)
            doc["print_fingerprint"] = {
                "enabled": True,
                "payload_hex": payload.hex(),
            }

        if data.get("document"):
            _fingerprint_doc(data["document"])
        if data.get("documents"):
            for doc in data["documents"]:
                _fingerprint_doc(doc)
    except Exception:
        logger.warning("Failed to apply print fingerprint after signing; continuing", exc_info=True)


async def _attach_rights_snapshot(
    result: dict,
    org_id: str,
    core_db: AsyncSession,
    content_db: AsyncSession,
) -> None:
    """
    Post-sign hook: fetches the publisher's rights profile, stores a rights snapshot
    on each signed ContentReference, and injects rights_resolution_url into the result.

    Operates in-place on `result["data"]`. Errors are swallowed so they never
    break a successful sign response.
    """
    from sqlalchemy import update
    from app.config import settings
    from app.models.content_reference import ContentReference
    from app.services.rights_service import rights_service

    try:
        profile = await rights_service.get_current_profile(
            db=core_db, organization_id=org_id
        )
        if profile is None:
            return

        snapshot = {
            "profile_version": profile.profile_version,
            "publisher_name": profile.publisher_name,
            "default_license_type": profile.default_license_type,
            "bronze_tier": profile.bronze_tier,
            "silver_tier": profile.silver_tier,
            "gold_tier": profile.gold_tier,
            "notice_status": profile.notice_status,
        }

        data = result.get("data", {})
        document_ids: list[str] = []

        if data.get("document"):
            doc_id = data["document"].get("document_id")
            if doc_id:
                document_ids.append(doc_id)
                rights_url = f"{settings.api_base_url}/api/v1/public/rights/{doc_id}"
                data["document"]["rights_resolution_url"] = rights_url

        if data.get("documents"):
            for doc in data["documents"]:
                doc_id = doc.get("document_id")
                if doc_id:
                    document_ids.append(doc_id)
                    rights_url = f"{settings.api_base_url}/api/v1/public/rights/{doc_id}"
                    doc["rights_resolution_url"] = rights_url

        for doc_id in document_ids:
            rights_url = f"{settings.api_base_url}/api/v1/public/rights/{doc_id}"
            await content_db.execute(
                update(ContentReference)
                .where(ContentReference.document_id == doc_id)
                .where(ContentReference.organization_id == org_id)
                .values(
                    rights_snapshot=snapshot,
                    rights_resolution_url=rights_url,
                )
            )
        if document_ids:
            await content_db.commit()

    except Exception:
        logger.warning("Failed to attach rights snapshot after signing; continuing", exc_info=True)


# =============================================================================
# Legacy /sign/advanced Endpoint (REMOVED)
# =============================================================================


@router.post(
    "/sign/advanced",
    deprecated=True,
    summary="REMOVED - Use POST /sign with options instead",
    description="""
**⚠️ REMOVED: This endpoint has been removed.**

Please use `POST /sign` with options instead.

Migration example:
```json
// Old /sign/advanced request
{
    "document_id": "doc1",
    "text": "...",
    "segmentation_level": "sentence"
}

// New /sign request
{
    "text": "...",
    "document_id": "doc1",
    "options": {
        "segmentation_level": "sentence"
    }
}
```
""",
    responses={
        410: {"description": "Endpoint removed"},
    },
)
async def sign_advanced():
    """REMOVED: Use /sign with options instead."""
    logger.warning("Removed endpoint /sign/advanced called. Use /sign with options instead.")
    
    return JSONResponse(
        status_code=status.HTTP_410_GONE,
        content={
            "error": "This endpoint has been removed",
            "message": "Please use POST /sign with options instead",
            "migration_guide": "Move segmentation_level and other advanced options into the 'options' object",
            "new_endpoint": "/api/v1/sign",
        },
    )
