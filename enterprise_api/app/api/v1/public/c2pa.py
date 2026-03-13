"""Public C2PA endpoints.

These endpoints do NOT require authentication.
Optional API key authentication is supported for higher rate limits.

All endpoints in this module are explicitly non-cryptographic.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from cryptography.hazmat.primitives import serialization
from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import core_session_factory, get_content_db, get_db
from app.dependencies import DEMO_KEYS, _normalize_org_context
from app.middleware.api_key_auth import authenticate_api_key, get_api_key_from_header
from app.middleware.public_rate_limiter import public_rate_limiter
from app.schemas.c2pa_schemas import C2PAAssertionValidationResult
from app.services.c2pa_validator import validator
from app.utils.crypto_utils import get_demo_private_key, load_organization_public_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/public/c2pa", tags=["Public - C2PA"])


async def _fire_detection_event(
    document_id: Optional[str],
    organization_id: str,
    request: Request,
) -> None:
    """Log a detection event in a standalone DB session (fire-and-forget)."""
    try:
        from app.services.detection_service import detection_service

        user_agent = request.headers.get("user-agent", "")
        referer = request.headers.get("referer")
        requester_ip = request.client.host if request.client else None

        async with core_session_factory() as session:
            await detection_service(
                session,
                document_id=document_id,
                organization_id=organization_id,
                detection_source="zw_resolve",
                requester_ip=requester_ip,
                requester_user_agent=user_agent,
                detected_on_url=referer,
            )
            await session.commit()
    except Exception:
        logger.debug("Background detection event failed", exc_info=True)


MAX_CREATE_MANIFEST_BYTES = 256 * 1024


class ValidateManifestRequest(BaseModel):
    manifest: Dict[str, Any] = Field(..., description="Manifest JSON object")
    schemas: Optional[Dict[str, Dict[str, Any]]] = Field(
        default=None,
        description="Optional mapping of assertion label -> JSON Schema used to validate assertion.data",
    )


class ValidateManifestResponse(BaseModel):
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    assertions: List[C2PAAssertionValidationResult] = Field(default_factory=list)


class CreateManifestRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Plaintext content to derive a manifest for")
    filename: Optional[str] = Field(default=None, description="Optional filename hint (e.g., 'example.txt')")
    document_title: Optional[str] = Field(default=None, description="Optional document title")
    claim_generator: Optional[str] = Field(default=None, description="Optional claim generator override")


class CreateManifestSigningPayload(BaseModel):
    claim_generator: str
    actions: List[Dict[str, Any]] = Field(default_factory=list)


class CreateManifestResponse(BaseModel):
    manifest: Dict[str, Any]
    signing: CreateManifestSigningPayload


class TrustAnchorResponse(BaseModel):
    """Response for trust anchor lookup.

    Enables external C2PA validators to verify Encypher-signed content
    by providing the signer's public key.

    See: https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_trust_lists
    """

    signer_id: str = Field(..., description="The signer identifier")
    signer_name: str = Field(..., description="Human-readable signer name")
    public_key: str = Field(..., description="PEM-encoded public key")
    public_key_algorithm: str = Field(default="Ed25519", description="Key algorithm")
    key_id: Optional[str] = Field(default=None, description="Key identifier if available")
    issued_at: Optional[str] = Field(default=None, description="ISO 8601 timestamp when key was issued")
    expires_at: Optional[str] = Field(default=None, description="ISO 8601 timestamp when key expires")
    revoked: bool = Field(default=False, description="Whether the key has been revoked")
    trust_anchor_type: str = Field(default="organization", description="Type of trust anchor")


async def _optional_authenticate(api_key: Optional[str], db: AsyncSession) -> Optional[Dict[str, Any]]:
    if not api_key:
        return None

    if api_key in DEMO_KEYS:
        return _normalize_org_context(DEMO_KEYS[api_key].copy())

    try:
        return await authenticate_api_key(api_key=api_key, db=db)
    except HTTPException:
        return None


@router.post(
    "/validate-manifest",
    response_model=ValidateManifestResponse,
    summary="Validate C2PA-like manifest JSON (Public - Non-Cryptographic)",
    description=(
        "Validate a manifest JSON payload and (optionally) validate assertion payloads against provided JSON Schemas. "
        "This endpoint performs structural/schema validation only and does not verify cryptographic signatures.\n\n"
        "Authentication is optional: unauthenticated requests are IP rate-limited; providing an API key may grant higher limits."
    ),
)
async def validate_manifest(
    request: Request,
    payload: ValidateManifestRequest,
    db: AsyncSession = Depends(get_db),
    api_key: Optional[str] = Depends(get_api_key_from_header),
) -> ValidateManifestResponse:
    organization = await _optional_authenticate(api_key=api_key, db=db)

    if not organization:
        await public_rate_limiter(request, endpoint_type="c2pa_validate_manifest")

    errors: List[str] = []
    warnings: List[str] = []

    manifest = payload.manifest

    if not isinstance(manifest, dict):
        return ValidateManifestResponse(valid=False, errors=["manifest must be an object"], warnings=[], assertions=[])

    claim_generator = manifest.get("claim_generator")
    if not isinstance(claim_generator, str) or not claim_generator.strip():
        errors.append("Missing or invalid claim_generator")

    assertions = manifest.get("assertions")
    if not isinstance(assertions, list):
        errors.append("Missing or invalid assertions (must be a list)")
        return ValidateManifestResponse(valid=False, errors=errors, warnings=warnings, assertions=[])

    # Ensure each assertion has required keys
    normalized_assertions: List[Dict[str, Any]] = []
    for idx, assertion in enumerate(assertions):
        if not isinstance(assertion, dict):
            errors.append(f"assertions[{idx}] must be an object")
            continue
        label = assertion.get("label")
        data = assertion.get("data")
        if not isinstance(label, str) or not label.strip():
            errors.append(f"assertions[{idx}].label is required")
        if not isinstance(data, dict):
            errors.append(f"assertions[{idx}].data must be an object")
        normalized_assertions.append({"label": label, "data": data if isinstance(data, dict) else {}})

    schemas = payload.schemas or {}

    all_valid, results = validator.validate_custom_assertions(
        assertions=normalized_assertions,
        registered_schemas=schemas,
    )

    assertion_results: List[C2PAAssertionValidationResult] = []
    for r in results.get("assertions", []):
        assertion_results.append(
            C2PAAssertionValidationResult(
                label=r.get("label") or "",
                valid=bool(r.get("valid")),
                errors=r.get("errors", []) or [],
                warnings=r.get("warnings", []) or [],
            )
        )

    valid = (not errors) and all_valid

    return ValidateManifestResponse(
        valid=valid,
        errors=errors,
        warnings=warnings,
        assertions=assertion_results,
    )


@router.post(
    "/create-manifest",
    response_model=CreateManifestResponse,
    summary="Create C2PA-like manifest JSON from plaintext (Public - Non-Cryptographic)",
    description=(
        "Create a C2PA-like manifest JSON payload from plaintext. This endpoint is intended for client-side workflows "
        "that want a server-generated starting point for a manifest before cryptographic signing.\n\n"
        "Authentication is optional: unauthenticated requests are IP rate-limited; providing an API key may grant higher limits."
    ),
)
async def create_manifest(
    request: Request,
    payload: CreateManifestRequest,
    db: AsyncSession = Depends(get_db),
    api_key: Optional[str] = Depends(get_api_key_from_header),
) -> CreateManifestResponse:
    organization = await _optional_authenticate(api_key=api_key, db=db)

    if not organization:
        await public_rate_limiter(request, endpoint_type="c2pa_create_manifest")

    payload_bytes = len(payload.text.encode("utf-8"))
    if payload_bytes > MAX_CREATE_MANIFEST_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "code": "ERR_CREATE_MANIFEST_PAYLOAD_TOO_LARGE",
                "message": f"Payload exceeds {MAX_CREATE_MANIFEST_BYTES} bytes limit.",
                "hint": "Submit smaller plaintext or chunk your content.",
            },
        )

    claim_generator = payload.claim_generator or "encypher.public.create-manifest"

    signing_actions: List[Dict[str, Any]] = [
        {
            "action": "c2pa.created",
        }
    ]

    doc_title = None
    if payload.document_title and payload.document_title.strip():
        doc_title = payload.document_title.strip()
    elif payload.filename and payload.filename.strip():
        doc_title = payload.filename.strip()

    assertions: List[Dict[str, Any]] = [
        {
            "label": "c2pa.training-mining.v1",
            "data": {
                "use": {
                    "ai_training": False,
                    "ai_inference": True,
                    "data_mining": False,
                }
            },
        }
    ]

    if doc_title:
        assertions.append(
            {
                "label": "com.encypher.document.v1",
                "data": {
                    "title": doc_title,
                    "filename": payload.filename,
                    "content_type": "text/plain",
                    "length": len(payload.text),
                },
            }
        )

    manifest: Dict[str, Any] = {
        "claim_generator": claim_generator,
        "assertions": assertions,
    }

    return CreateManifestResponse(
        manifest=manifest,
        signing=CreateManifestSigningPayload(
            claim_generator=claim_generator,
            actions=signing_actions,
        ),
    )


@router.get(
    "/trust-anchors/{signer_id}",
    response_model=TrustAnchorResponse,
    summary="Lookup trust anchor for C2PA verification (Public)",
    responses={
        404: {"description": "Signer not found"},
    },
)
async def get_trust_anchor(
    request: Request,
    signer_id: str = Path(..., description="Signer identifier from manifest"),
    db: AsyncSession = Depends(get_db),
) -> TrustAnchorResponse:
    """
    Lookup a trust anchor (public key) for external C2PA validators.

    This endpoint enables third-party validators to verify Encypher-signed
    content by providing the signer's public key. This implements the
    "Private Credential Store" model per C2PA spec §14.4.3.

    **Special signer IDs:**
    - `encypher.public` or `org_demo`: Returns Encypher's official demo/free-tier key
    - `demo-*`: Returns demo/test keys (non-production)

    **C2PA Spec Reference:**
    https://spec.c2pa.org/specifications/specifications/2.2/specs/C2PA_Specification.html#_trust_lists
    """
    await public_rate_limiter(request, endpoint_type="trust_anchor_lookup")

    # Handle Encypher's official public key (free tier / demo)
    # Also includes org_encypher_marketing which uses the shared demo key
    DEMO_SIGNER_IDS = {"encypher.public", settings.demo_organization_id, "org_encypher_marketing"}
    if signer_id in DEMO_SIGNER_IDS or signer_id.startswith("demo-"):
        demo_private_key = get_demo_private_key()
        demo_public_key = demo_private_key.public_key()

        public_key_pem = demo_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        return TrustAnchorResponse(
            signer_id=signer_id,
            signer_name="Encypher Demo / Free Tier",
            public_key=public_key_pem,
            public_key_algorithm="Ed25519",
            key_id="encypher-demo-key",
            issued_at=None,
            expires_at=None,
            revoked=False,
            trust_anchor_type="platform",
        )

    # Lookup organization metadata
    result = await db.execute(
        text("""
            SELECT
                id,
                name,
                certificate_status,
                created_at,
                certificate_expiry
            FROM organizations
            WHERE id = :org_id
        """),
        {"org_id": signer_id},
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "SIGNER_NOT_FOUND",
                "message": f"No trust anchor found for signer_id '{signer_id}'",
            },
        )

    org_id, org_name, cert_status, created_at, cert_expiry = row

    # Load public key using existing utility (handles encrypted private key -> public key derivation)
    try:
        public_key = await load_organization_public_key(signer_id, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NO_PUBLIC_KEY",
                "message": f"Organization '{signer_id}' has no public key configured: {e}",
            },
        )

    # Convert to PEM format
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    # Determine revocation status
    revoked = cert_status in ("revoked", "expired") if cert_status else False

    # Format timestamps
    issued_at_str = created_at.isoformat() if created_at else None
    expires_at_str = cert_expiry.isoformat() if cert_expiry else None

    return TrustAnchorResponse(
        signer_id=org_id,
        signer_name=org_name or org_id,
        public_key=public_key_pem,
        public_key_algorithm="Ed25519",
        key_id=None,
        issued_at=issued_at_str,
        expires_at=expires_at_str,
        revoked=revoked,
        trust_anchor_type="organization",
    )


# ---------------------------------------------------------------------------
# TEAM_156: ZW segment UUID resolution (used by verification-service)
# ---------------------------------------------------------------------------


class SegmentLocationResponse(BaseModel):
    """Location of a segment within the original document."""

    paragraph_index: int = Field(..., description="0-indexed paragraph number")
    sentence_in_paragraph: int = Field(..., description="0-indexed sentence within the paragraph")


class ZWResolveResponse(BaseModel):
    """Response for ZW segment UUID resolution."""

    segment_uuid: str
    organization_id: str
    document_id: Optional[str] = None
    manifest_mode: Optional[str] = None
    segment_location: Optional[SegmentLocationResponse] = None
    total_segments: Optional[int] = None
    leaf_index: Optional[int] = None
    manifest_data: Optional[Dict[str, Any]] = None
    rights_resolution_url: Optional[str] = None


_RESOLVE_SQL = """
    SELECT organization_id, document_id, leaf_index,
           embedding_metadata->>'manifest_mode' AS manifest_mode,
           embedding_metadata->'segment_location' AS segment_location,
           (embedding_metadata->>'total_segments')::int AS total_segments,
           manifest_data,
           rights_resolution_url
    FROM content_references
    WHERE embedding_metadata->>'segment_uuid' = :seg_uuid
       OR embedding_metadata->>'log_id' = REPLACE(:seg_uuid, '-', '')
    LIMIT 1
"""


def _row_to_resolve_response(segment_uuid: str, row) -> ZWResolveResponse:
    """Convert a DB row to a ZWResolveResponse."""
    seg_loc = None
    raw_loc = row.segment_location
    if isinstance(raw_loc, dict):
        seg_loc = SegmentLocationResponse(
            paragraph_index=raw_loc.get("paragraph_index", 0),
            sentence_in_paragraph=raw_loc.get("sentence_in_paragraph", 0),
        )
    elif isinstance(raw_loc, str):
        import json as _json

        try:
            parsed = _json.loads(raw_loc)
            seg_loc = SegmentLocationResponse(
                paragraph_index=parsed.get("paragraph_index", 0),
                sentence_in_paragraph=parsed.get("sentence_in_paragraph", 0),
            )
        except (ValueError, TypeError):
            pass

    manifest = None
    if hasattr(row, "manifest_data") and row.manifest_data:
        manifest = row.manifest_data if isinstance(row.manifest_data, dict) else None

    return ZWResolveResponse(
        segment_uuid=segment_uuid,
        organization_id=row.organization_id,
        document_id=row.document_id,
        manifest_mode=row.manifest_mode,
        segment_location=seg_loc,
        total_segments=row.total_segments if hasattr(row, "total_segments") else None,
        leaf_index=row.leaf_index if hasattr(row, "leaf_index") else None,
        manifest_data=manifest,
        rights_resolution_url=row.rights_resolution_url if hasattr(row, "rights_resolution_url") else None,
    )


@router.get(
    "/zw/resolve/{segment_uuid}",
    response_model=ZWResolveResponse,
    summary="Resolve ZW segment UUID (Public, internal)",
    responses={
        404: {"description": "Segment UUID not found"},
    },
)
async def resolve_zw_segment_uuid(
    request: Request,
    segment_uuid: str = Path(..., description="Segment UUID from ZW embedding"),
    content_db: AsyncSession = Depends(get_content_db),
) -> ZWResolveResponse:
    """
    Resolve a ZW (zero-width) embedding segment UUID to its organization.

    Used internally by the verification-service to look up ZW embeddings
    in the content database without needing direct DB access.
    """
    await public_rate_limiter(request, endpoint_type="trust_anchor_lookup")

    result = await content_db.execute(text(_RESOLVE_SQL), {"seg_uuid": segment_uuid})
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "SEGMENT_NOT_FOUND",
                "message": f"No content reference found for segment_uuid '{segment_uuid}'",
            },
        )

    response = _row_to_resolve_response(segment_uuid, row)
    asyncio.create_task(
        _fire_detection_event(
            document_id=row.document_id,
            organization_id=row.organization_id,
            request=request,
        )
    )
    return response


class BulkResolveRequest(BaseModel):
    """Request body for bulk UUID resolution."""

    segment_uuids: List[str] = Field(..., description="List of segment UUIDs to resolve", max_length=200)


class BulkResolveResponse(BaseModel):
    """Response for bulk UUID resolution."""

    results: List[ZWResolveResponse] = Field(default_factory=list)
    not_found: List[str] = Field(default_factory=list)


@router.post(
    "/zw/resolve",
    response_model=BulkResolveResponse,
    summary="Bulk resolve segment UUIDs (Public, internal)",
)
async def bulk_resolve_segment_uuids(
    request: Request,
    body: BulkResolveRequest,
    content_db: AsyncSession = Depends(get_content_db),
) -> BulkResolveResponse:
    """
    Resolve multiple segment UUIDs in a single call.

    Used internally by the verification-service when verifying text that
    contains multiple embedded signatures (e.g. a copied paragraph).
    """
    await public_rate_limiter(request, endpoint_type="trust_anchor_lookup")

    if not body.segment_uuids:
        return BulkResolveResponse(results=[], not_found=[])

    # Convert UUID strings (with dashes) to hex (no dashes) for log_id lookup.
    # New micro+ecc signing stores log_id as hex without dashes; old ZWC/VS256
    # signing stored segment_uuid with dashes.  Support both formats.
    log_id_hexes = [u.replace("-", "") for u in body.segment_uuids]

    result = await content_db.execute(
        text(
            """
            SELECT organization_id, document_id, leaf_index,
                   embedding_metadata->>'manifest_mode' AS manifest_mode,
                   embedding_metadata->'segment_location' AS segment_location,
                   (embedding_metadata->>'total_segments')::int AS total_segments,
                   embedding_metadata->>'segment_uuid' AS segment_uuid,
                   embedding_metadata->>'log_id' AS log_id,
                   manifest_data
            FROM content_references
            WHERE embedding_metadata->>'segment_uuid' = ANY(:seg_uuids)
               OR embedding_metadata->>'log_id' = ANY(:log_id_hexes)
            """
        ),
        {"seg_uuids": body.segment_uuids, "log_id_hexes": log_id_hexes},
    )
    rows = result.fetchall()

    # Build lookup: input UUID string -> DB row.
    # A row may match via segment_uuid (old) or log_id (new).
    found_uuids: Dict[str, Any] = {}
    for row in rows:
        uuid_val = getattr(row, "segment_uuid", None)
        if uuid_val and uuid_val not in found_uuids:
            found_uuids[uuid_val] = row
        log_id_val = getattr(row, "log_id", None)
        if log_id_val:
            # Store under the raw hex (no-dashes) key so callers that pass
            # hex log_ids directly (e.g. legacy_safe / VS256 verification)
            # can look up the result without a format conversion.
            if log_id_val not in found_uuids:
                found_uuids[log_id_val] = row
            # Also store under UUID-with-dashes form for callers that pass
            # UUID-formatted segment_uuids.
            try:
                from uuid import UUID as _UUID

                uuid_from_log_id = str(_UUID(hex=log_id_val))
                if uuid_from_log_id not in found_uuids:
                    found_uuids[uuid_from_log_id] = row
            except (ValueError, AttributeError):
                pass

    results = []
    not_found = []
    for uuid_str in body.segment_uuids:
        row = found_uuids.get(uuid_str)
        if row:
            results.append(_row_to_resolve_response(uuid_str, row))
        else:
            not_found.append(uuid_str)

    # Fire detection events for all resolved segments (one task per unique org)
    seen_orgs: set[str] = set()
    for row in found_uuids.values():
        if row.organization_id not in seen_orgs:
            seen_orgs.add(row.organization_id)
            asyncio.create_task(
                _fire_detection_event(
                    document_id=row.document_id,
                    organization_id=row.organization_id,
                    request=request,
                )
            )

    return BulkResolveResponse(results=results, not_found=not_found)
