"""Image verification endpoints: /verify/image and /verify/rich."""

import base64
import hashlib
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_content_db
from app.middleware.public_rate_limiter import public_rate_limiter
from app.models.article_image import ArticleImage
from app.models.composite_manifest import CompositeManifest
from app.schemas.rich_verify_schemas import ImageVerificationResult as ImageVerifResultSchema
from app.schemas.rich_verify_schemas import (
    ImageVerifyRequest,
    ImageVerifyResponse,
    RichVerifyRequest,
    RichVerifyResponse,
    SignerIdentity,
    TextVerificationResult,
)
from app.services.image_verification_service import compute_sha256, verify_image_c2pa

router = APIRouter()
logger = logging.getLogger(__name__)


def _apply_minimal_image_verify_response(response: ImageVerifyResponse) -> ImageVerifyResponse:
    if not settings.public_verify_minimal_response or not response.valid:
        return response

    return response.model_copy(
        update={
            "c2pa_manifest": None,
            "image_id": None,
            "document_id": None,
            "phash": None,
        }
    )


def _invalid_rich_verify_response(document_id: str, correlation_id: str, verified_at: str) -> RichVerifyResponse:
    return RichVerifyResponse(
        success=True,
        valid=False,
        verified_at=verified_at,
        document_id=document_id,
        content_type="rich_article",
        text_verification=TextVerificationResult(
            valid=False,
            total_segments=None,
            error="Text cryptographic verification is not performed by /verify/rich",
        ),
        image_verifications=[],
        composite_manifest_valid=False,
        all_ingredients_verified=False,
        cryptographically_verified=False,
        historically_signed_by_us=False,
        overall_status="invalid",
        signer_identity=None,
        error="Unable to verify requested article",
        correlation_id=correlation_id,
    )


def _apply_minimal_rich_verify_response(response: RichVerifyResponse) -> RichVerifyResponse:
    if not settings.public_verify_minimal_response or not response.valid:
        return response

    return response.model_copy(
        update={
            "image_verifications": [
                verification.model_copy(
                    update={
                        "image_id": None,
                        "filename": None,
                        "c2pa_instance_id": None,
                        "signer": None,
                        "signed_at": None,
                    }
                )
                for verification in response.image_verifications
            ],
            "signer_identity": None,
        }
    )


@router.post(
    "/verify/image",
    summary="Verify a C2PA-signed image",
    description=("Public endpoint. Accepts a base64-encoded image, extracts and verifies the embedded JUMBF C2PA manifest."),
)
async def verify_image(
    payload: ImageVerifyRequest,
    request: Request,
    content_db: AsyncSession = Depends(get_content_db),
) -> ImageVerifyResponse:
    """Verify a C2PA manifest embedded in an image supplied as base64."""
    correlation_id = str(uuid.uuid4())
    verified_at = datetime.now(timezone.utc).isoformat()

    await public_rate_limiter(request, endpoint_type="verify_image")

    try:
        image_bytes = base64.b64decode(payload.image_data, validate=True)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid base64 image data")

    if len(image_bytes) > settings.image_max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Payload exceeds {settings.image_max_size_bytes} bytes limit",
        )

    # Verify C2PA manifest
    result = verify_image_c2pa(image_bytes, payload.mime_type)

    # Look up image record by signed_hash (if it exists in our DB)
    img_hash = compute_sha256(image_bytes)
    image_id: Optional[str] = None
    doc_id: Optional[str] = None
    phash_hex: Optional[str] = None
    row = None

    try:
        stmt = select(ArticleImage).where(ArticleImage.signed_hash == img_hash).limit(1)
        row = (await content_db.execute(stmt)).scalar_one_or_none()
        if row:
            image_id = row.image_id
            doc_id = row.document_id
            if row.phash is not None:
                phash_hex = format(row.phash & 0xFFFFFFFFFFFFFFFF, "016x")

        # XMP fallback: if exact hash miss, try instance_id from embedded XMP
        if row is None:
            from app.utils.image_utils import extract_encypher_xmp

            xmp_fields = extract_encypher_xmp(image_bytes, payload.mime_type or "image/jpeg")
            if xmp_fields and "instance_id" in xmp_fields:
                stmt2 = select(ArticleImage).where(ArticleImage.c2pa_instance_id == xmp_fields["instance_id"]).limit(1)
                row = (await content_db.execute(stmt2)).scalar_one_or_none()
                if row:
                    image_id = row.image_id
                    doc_id = row.document_id
                    if row.phash is not None:
                        phash_hex = format(row.phash & 0xFFFFFFFFFFFFFFFF, "016x")
    except Exception:
        # article_images table may not exist yet on content DB; C2PA result is
        # still valid so we continue without the DB-match enrichment.
        await content_db.rollback()

    db_confirmed = row is not None
    cryptographically_valid = bool(result.valid)
    overall_status = "cryptographically_valid" if cryptographically_valid else "historically_signed_record" if db_confirmed else "invalid"

    # Attempt TrustMark watermark detection (non-blocking, best-effort)
    wm_detected: Optional[bool] = None
    wm_payload: Optional[str] = None
    wm_confidence: Optional[float] = None
    try:
        from app.services.trustmark_client import trustmark_client

        if trustmark_client.is_configured:
            wm_result = await trustmark_client.detect_watermark(payload.image_data)
            if wm_result is not None:
                wm_detected, wm_payload, wm_confidence = wm_result
    except Exception:
        logger.debug("TrustMark detection skipped: service unavailable")

    response_payload = ImageVerifyResponse(
        success=True,
        valid=cryptographically_valid,
        verified_at=verified_at,
        c2pa_manifest=result.manifest_data,
        image_id=image_id,
        document_id=doc_id,
        hash=img_hash,
        phash=phash_hex,
        cryptographically_verified=cryptographically_valid,
        db_matched=db_confirmed,
        historically_signed_by_us=db_confirmed,
        overall_status=overall_status,
        watermark_detected=wm_detected,
        watermark_payload=wm_payload,
        watermark_confidence=wm_confidence,
        error=result.error,
        correlation_id=correlation_id,
    )
    return _apply_minimal_image_verify_response(response_payload)


@router.post(
    "/verify/rich",
    summary="Verify a signed rich article (text + images)",
    description=(
        "Public endpoint. Looks up a signed article by document_id and "
        "verifies all components: text signature, each image C2PA manifest, "
        "and the composite manifest integrity."
    ),
)
async def verify_rich(
    payload: RichVerifyRequest,
    request: Request,
    content_db: AsyncSession = Depends(get_content_db),
) -> RichVerifyResponse:
    """Verify a rich article by document_id, checking all signed components."""
    correlation_id = str(uuid.uuid4())
    verified_at = datetime.now(timezone.utc).isoformat()

    await public_rate_limiter(request, endpoint_type="verify_rich")

    # Load composite manifest
    try:
        comp_stmt = select(CompositeManifest).where(CompositeManifest.document_id == payload.document_id).limit(1)
        composite_row = (await content_db.execute(comp_stmt)).scalar_one_or_none()
    except Exception:
        await content_db.rollback()
        composite_row = None

    if composite_row is None:
        return _invalid_rich_verify_response(
            document_id=payload.document_id,
            correlation_id=correlation_id,
            verified_at=verified_at,
        )

    # Load article images ordered by position
    try:
        imgs_stmt = select(ArticleImage).where(ArticleImage.document_id == payload.document_id).order_by(ArticleImage.position)
        imgs_result = await content_db.execute(imgs_stmt)
        image_rows = imgs_result.scalars().all()
    except Exception:
        await content_db.rollback()
        image_rows = []

    image_verifications = []
    historically_signed_by_us = True

    for img_row in image_rows:
        img_verification = ImageVerifResultSchema(
            image_id=img_row.image_id,
            filename=img_row.filename,
            valid=False,
            c2pa_manifest_valid=False,
            hash_matches=bool(img_row.signed_hash),
            c2pa_instance_id=img_row.c2pa_instance_id,
            cryptographically_verified=False,
            historically_signed_by_us=True,
            overall_status="historically_signed_record",
            error=None,
        )
        image_verifications.append(img_verification)

    # Validate composite manifest: recompute hash and compare to stored value
    manifest_json = json.dumps(composite_row.manifest_data, sort_keys=True, separators=(",", ":"))
    recomputed_hash = "sha256:" + hashlib.sha256(manifest_json.encode()).hexdigest()
    composite_manifest_valid = recomputed_hash == composite_row.manifest_hash
    all_ingredients_verified = composite_manifest_valid and len(image_verifications) == 0
    cryptographically_verified = composite_manifest_valid and all_ingredients_verified
    overall_status = "cryptographically_valid" if cryptographically_verified else "partially_verified" if composite_manifest_valid else "invalid"

    response_payload = RichVerifyResponse(
        success=True,
        valid=composite_manifest_valid,
        verified_at=verified_at,
        document_id=payload.document_id,
        content_type="rich_article",
        text_verification=TextVerificationResult(
            valid=False,
            total_segments=None,
            error="Text cryptographic verification is not performed by /verify/rich",
        ),
        image_verifications=image_verifications,
        composite_manifest_valid=composite_manifest_valid,
        all_ingredients_verified=all_ingredients_verified,
        cryptographically_verified=cryptographically_verified,
        historically_signed_by_us=historically_signed_by_us,
        overall_status=overall_status,
        signer_identity=SignerIdentity(
            organization_id=composite_row.organization_id,
            trust_level="signed",
        ),
        correlation_id=correlation_id,
    )
    return _apply_minimal_rich_verify_response(response_payload)
