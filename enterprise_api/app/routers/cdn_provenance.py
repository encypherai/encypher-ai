"""CDN Provenance router.

Provides endpoints for signing, registering, and verifying images for
CDN provenance continuity. Enterprise-only feature.

Authenticated endpoints require a valid org API key via
get_current_organization_dep. Public endpoints (manifest fetch, verify)
do not require auth but should be rate-limited by IP in production.

Prefix: /cdn (mounted at /api/v1/cdn via bootstrap/routers.py)
"""

import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization_dep
from app.models.cdn_image_record import CdnImageRecord
from app.models.organization import Organization, OrganizationTier
from app.schemas.cdn_schemas import (
    CdnImageRegisterResponse,
    CdnImageSignResponse,
    CdnManifestLookupResponse,
    CdnManifestResponse,
    CdnVariantsRequest,
    CdnVariantsResponse,
    CdnVerifyResponse,
)
from app.services.cdn_provenance_service import CdnProvenanceService
from app.services.image_signing_executor import execute_image_signing
from app.utils.image_utils import compute_sha256, extract_encypher_xmp
from app.utils.quota import QuotaManager, QuotaType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cdn", tags=["CDN Provenance"])

# ---------------------------------------------------------------------------
# Feature gate helper
# ---------------------------------------------------------------------------

_ENTERPRISE_TIERS = {OrganizationTier.ENTERPRISE, OrganizationTier.STRATEGIC_PARTNER}


def _require_cdn_provenance(org: Organization) -> None:
    """Raise 403 if org is not Enterprise tier and cdn_provenance_enabled is not set."""
    tier_str = org.tier if isinstance(org.tier, str) else org.tier.value
    try:
        tier = OrganizationTier(tier_str)
    except ValueError:
        tier = OrganizationTier.FREE

    cdn_enabled = getattr(org, "cdn_provenance_enabled", False)
    if tier not in _ENTERPRISE_TIERS and not cdn_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "FeatureNotAvailable",
                "message": "CDN Provenance is available on Enterprise tier only.",
                "upgrade_url": "https://dashboard.encypherai.com/billing",
            },
        )


# ---------------------------------------------------------------------------
# POST /cdn/images/sign
# ---------------------------------------------------------------------------


@router.post(
    "/images/sign",
    response_model=CdnImageSignResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign image and store provenance manifest",
    description="""
Sign an image with a C2PA manifest and register it in the CDN provenance store.
Returns the signed image bytes (base64), pHash, and SHA-256 for downstream
CDN tracking.

**Enterprise tier only.**
    """,
)
async def sign_image_endpoint(
    file: UploadFile = File(..., description="Image file to sign"),
    title: str = Form(default="Untitled Image", description="Image title for C2PA manifest"),
    original_url: Optional[str] = Form(default=None, description="Canonical URL of the image"),
    db: AsyncSession = Depends(get_db),
    org_context: dict = Depends(get_current_organization_dep),
) -> CdnImageSignResponse:
    org_id: str = org_context["organization_id"]

    # Load org for feature gate + signing keys
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found.")

    _require_cdn_provenance(org)

    # Quota check
    await QuotaManager.check_quota(db, org_id, QuotaType.CDN_IMAGE_REGISTRATIONS)

    image_bytes = await file.read()
    mime_type = file.content_type or "image/jpeg"

    exec_result = await execute_image_signing(
        image_bytes=image_bytes,
        mime_type=mime_type,
        title=title,
        org=org,
        db=db,
        original_url=original_url,
    )

    return CdnImageSignResponse(
        record_id=exec_result["record_id"],
        manifest_url=exec_result["manifest_url"],
        image_id=exec_result["image_id"],
        phash=exec_result.get("phash"),
        sha256=exec_result.get("sha256"),
        signed_image_b64=exec_result["signed_bytes_b64"],
        mime_type=exec_result["mime_type"],
    )


# ---------------------------------------------------------------------------
# POST /cdn/images/register
# ---------------------------------------------------------------------------


@router.post(
    "/images/register",
    response_model=CdnImageRegisterResponse,
    status_code=status.HTTP_200_OK,
    summary="Register a pre-signed image for CDN tracking",
    description="""
Register an already-signed image for CDN provenance tracking without re-signing.
Computes pHash and SHA-256, stores record.
    """,
)
async def register_image_endpoint(
    file: UploadFile = File(..., description="Image file to register"),
    original_url: Optional[str] = Form(default=None, description="Canonical URL of the image"),
    manifest_data: Optional[str] = Form(default=None, description="JSON-encoded manifest data"),
    db: AsyncSession = Depends(get_db),
    org_context: dict = Depends(get_current_organization_dep),
) -> CdnImageRegisterResponse:
    org_id: str = org_context["organization_id"]

    import json

    manifest_dict: Optional[dict] = None
    if manifest_data:
        try:
            manifest_dict = json.loads(manifest_data)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"manifest_data is not valid JSON: {exc}",
            ) from exc

    image_bytes = await file.read()

    record = await CdnProvenanceService.register_image(
        db=db,
        org_id=org_id,
        image_bytes=image_bytes,
        mime_type=file.content_type or "image/jpeg",
        manifest_data=manifest_dict,
        original_url=original_url,
    )
    await db.commit()

    return CdnImageRegisterResponse(
        record_id=str(record.id),
        phash=record.phash,
        sha256=record.content_sha256,
    )


# ---------------------------------------------------------------------------
# GET /cdn/manifests/lookup  (must be before /{record_id} to avoid ambiguity)
# ---------------------------------------------------------------------------


@router.get(
    "/manifests/lookup",
    response_model=CdnManifestLookupResponse,
    status_code=status.HTTP_200_OK,
    summary="Lookup manifest by canonical URL",
    description="""
Find a CDN image record by its canonical original URL.

No authentication required. IP-based rate limiting recommended in production.
    """,
)
async def lookup_manifest_by_url(
    url: str,
    db: AsyncSession = Depends(get_db),
) -> CdnManifestLookupResponse:
    result = await db.execute(select(CdnImageRecord).where(CdnImageRecord.original_url == url).limit(1))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No CDN image record found for the provided URL.",
        )

    record_id = str(record.id)
    return CdnManifestLookupResponse(
        record_id=record_id,
        manifest_url=f"/api/v1/cdn/manifests/{record_id}",
        original_url=record.original_url,
    )


# ---------------------------------------------------------------------------
# GET /cdn/manifests/{record_id}
# ---------------------------------------------------------------------------


@router.get(
    "/manifests/{record_id}",
    status_code=status.HTTP_200_OK,
    summary="Fetch C2PA manifest for a CDN image record",
    description="""
Public endpoint to retrieve the stored C2PA manifest for a registered image.

Supports `Accept: application/cbor` for CBOR-encoded manifest response.

No authentication required. IP-based rate limiting recommended in production.
    """,
)
async def get_manifest(
    record_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Response:
    import uuid as _uuid

    try:
        record_uuid = _uuid.UUID(record_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="record_id must be a valid UUID.",
        ) from exc

    record = await db.get(CdnImageRecord, record_uuid)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CDN image record not found.",
        )

    accept = request.headers.get("accept", "application/json")

    if "application/cbor" in accept and record.manifest_store:
        # Return CBOR-encoded manifest
        try:
            import cbor2

            cbor_bytes = cbor2.dumps(record.manifest_store)
            return Response(
                content=cbor_bytes,
                media_type="application/cbor",
                headers={"X-Record-Id": str(record.id)},
            )
        except ImportError:
            pass  # fall through to JSON

    # Default: JSON
    return JSONResponse(
        {
            "record_id": record_id,
            "manifest": record.manifest_store,
            "manifest_url": f"/api/v1/cdn/manifests/{record_id}",
        }
    )


# ---------------------------------------------------------------------------
# POST /cdn/images/{record_id}/variants
# ---------------------------------------------------------------------------


@router.post(
    "/images/{record_id}/variants",
    response_model=CdnVariantsResponse,
    status_code=status.HTTP_200_OK,
    summary="Pre-register expected CDN derivative variants",
    description="""
Pre-register the expected CDN derivative transforms (resize, reformat, quality
compression, etc.) for a registered image so they can be matched on re-upload.
    """,
)
async def pre_register_variants(
    record_id: str,
    body: CdnVariantsRequest,
    db: AsyncSession = Depends(get_db),
    org_context: dict = Depends(get_current_organization_dep),
) -> CdnVariantsResponse:
    import uuid as _uuid

    org_id: str = org_context["organization_id"]

    try:
        record_uuid = _uuid.UUID(record_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="record_id must be a valid UUID.",
        ) from exc

    parent_record = await db.get(CdnImageRecord, record_uuid)
    if parent_record is None or parent_record.organization_id != org_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CDN image record not found.",
        )

    variants = await CdnProvenanceService.pre_register_variants(
        db=db,
        parent_record=parent_record,
        transform_descriptions=body.transforms,
    )
    await db.commit()

    return CdnVariantsResponse(
        parent_record_id=record_id,
        variant_count=len(variants),
        variant_ids=[str(v.id) for v in variants],
    )


# ---------------------------------------------------------------------------
# POST /cdn/verify
# ---------------------------------------------------------------------------


@router.post(
    "/verify",
    response_model=CdnVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify image provenance by upload",
    description="""
Upload an image to verify its provenance. Attempts (in order):

1. Extract embedded Encypher XMP provenance data.
2. Exact SHA-256 match across all orgs.
3. pHash fuzzy lookup across all orgs (picks lowest Hamming distance).

Returns a verdict: ORIGINAL_SIGNED | VERIFIED_DERIVATIVE | PROVENANCE_LOST.

No authentication required. IP-based rate limiting recommended in production.
    """,
)
async def verify_image(
    file: UploadFile = File(..., description="Image to verify"),
    db: AsyncSession = Depends(get_db),
) -> CdnVerifyResponse:
    image_bytes = await file.read()
    mime_type = file.content_type or "image/jpeg"
    return await _verify_image_bytes(image_bytes, mime_type, db)


# ---------------------------------------------------------------------------
# POST /cdn/verify/url
# ---------------------------------------------------------------------------


@router.post(
    "/verify/url",
    response_model=CdnVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify image provenance by URL",
    description="""
Fetch an image from a URL then run the same provenance verification as
POST /cdn/verify.

No authentication required. IP-based rate limiting recommended in production.
    """,
)
async def verify_image_url(
    url: str,
    db: AsyncSession = Depends(get_db),
) -> CdnVerifyResponse:
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to fetch image from URL: HTTP {exc.response.status_code}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to fetch image from URL: {exc}",
        ) from exc

    image_bytes = response.content
    content_type = response.headers.get("content-type", "image/jpeg").split(";")[0].strip()
    return await _verify_image_bytes(image_bytes, content_type, db)


# ---------------------------------------------------------------------------
# Internal verification logic
# ---------------------------------------------------------------------------


async def _verify_image_bytes(
    image_bytes: bytes,
    mime_type: str,
    db: AsyncSession,
) -> CdnVerifyResponse:
    """Run provenance verification pipeline on raw image bytes.

    Steps:
    1. Try to extract embedded Encypher XMP → ORIGINAL_SIGNED
    2. SHA-256 exact match (cross-org) → ORIGINAL_SIGNED
    3. pHash fuzzy lookup (cross-org, all records) → VERIFIED_DERIVATIVE
    4. Fallback → PROVENANCE_LOST
    """

    # Step 1: Extract embedded XMP
    try:
        xmp = extract_encypher_xmp(image_bytes, mime_type)
    except Exception:
        xmp = None

    if xmp:
        doc_id = xmp.get("document_id") or xmp.get("instance_id")
        if doc_id:
            # Try looking up by instance_id stored in manifest_store
            result = await db.execute(select(CdnImageRecord).where(CdnImageRecord.manifest_store["c2pa_instance_id"].astext == doc_id).limit(1))
            record = result.scalar_one_or_none()
            if record and record.manifest_store:
                return CdnVerifyResponse(
                    verdict="ORIGINAL_SIGNED",
                    verification_path="EMBEDDED",
                    record_id=str(record.id),
                    manifest=record.manifest_store,
                    hamming_distance=0,
                    confidence=1.0,
                )

    # Step 2: SHA-256 exact match (cross-org)
    sha256 = compute_sha256(image_bytes)
    result = await db.execute(select(CdnImageRecord).where(CdnImageRecord.content_sha256 == sha256).limit(1))
    record = result.scalar_one_or_none()
    if record:
        return CdnVerifyResponse(
            verdict="ORIGINAL_SIGNED",
            verification_path="URL_LOOKUP",
            record_id=str(record.id),
            manifest=record.manifest_store,
            hamming_distance=0,
            confidence=1.0,
        )

    # Step 3: pHash fuzzy lookup across all orgs
    from app.services.cdn_provenance_service import _hamming_distance
    from app.utils.image_utils import compute_phash

    query_phash = compute_phash(image_bytes)
    if query_phash != 0:
        all_result = await db.execute(select(CdnImageRecord).where(CdnImageRecord.phash.isnot(None)).limit(10000))
        all_records = all_result.scalars().all()

        best_record = None
        best_dist = 9  # threshold + 1
        _threshold = 8

        for r in all_records:
            dist = _hamming_distance(query_phash, r.phash)
            if dist < best_dist:
                best_dist = dist
                best_record = r

        if best_record is not None and best_dist <= _threshold:
            confidence = round(1.0 - best_dist / 64.0, 4)
            return CdnVerifyResponse(
                verdict="VERIFIED_DERIVATIVE",
                verification_path="PHASH_SIDECAR",
                record_id=str(best_record.id),
                manifest=best_record.manifest_store,
                hamming_distance=best_dist,
                confidence=confidence,
            )

    return CdnVerifyResponse(
        verdict="PROVENANCE_LOST",
        verification_path="NONE",
        record_id=None,
        manifest=None,
        hamming_distance=None,
        confidence=0.0,
    )


# ---------------------------------------------------------------------------
# Well-known C2PA discovery endpoint (no /cdn prefix)
# ---------------------------------------------------------------------------

well_known_router = APIRouter(tags=["CDN Provenance"])


@well_known_router.get(
    "/.well-known/c2pa/manifests/{record_id}",
    summary="Well-known C2PA manifest discovery",
    description="Standards-aligned discovery alias. Redirects to the canonical manifest endpoint.",
    include_in_schema=True,
)
async def well_known_manifest(record_id: str) -> Response:
    from fastapi.responses import RedirectResponse

    return RedirectResponse(
        url=f"/api/v1/cdn/manifests/{record_id}",
        status_code=301,
    )
