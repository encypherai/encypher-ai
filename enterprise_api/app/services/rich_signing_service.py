"""Rich article signing service: signs text + embedded images as a single provenance unit.

Orchestrates the full rich article signing pipeline:
1. Validate tier and trustmark permissions
2. Sign each image sequentially with C2PA (composite manifest needs all hashes first)
3. Persist ArticleImage rows to content DB
4. Sign the article text via existing execute_unified_signing()
5. Build composite manifest (text root + image ingredient hashes)
6. Persist CompositeManifest row
7. Return unified RichSignResponse
"""

import base64
import logging
import secrets
import time
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings  # noqa: F401 (used for passthrough check)
from app.models.article_image import ArticleImage
from app.models.composite_manifest import CompositeManifest
from app.schemas.rich_sign_schemas import (
    RichArticleSignRequest,
    SignedImageResult,
)
from app.services.composite_manifest_service import (
    CompositeManifestResult,
    ImageIngredient,
    build_composite_manifest,
)
from app.services.image_signing_service import SignedImageResult as _ServiceSignedResult
from app.services.image_signing_service import sign_image
from app.utils.image_utils import compute_phash, generate_image_id

logger = logging.getLogger(__name__)


def _get_signer_credentials() -> tuple[str, str]:
    """
    Retrieve the managed signer private key PEM and certificate chain PEM.

    Uses settings.managed_signer_private_key_pem and
    settings.managed_signer_certificate_chain_pem (or certificate_pem as fallback).

    Raises:
        ValueError: If no signer credentials are configured.
    """
    private_key_pem = settings.managed_signer_private_key_pem
    cert_chain_pem = settings.managed_signer_certificate_chain_pem or settings.managed_signer_certificate_pem

    if not private_key_pem:
        raise ValueError("managed_signer_private_key_pem is not configured. Set MANAGED_SIGNER_PRIVATE_KEY_PEM environment variable.")
    if not cert_chain_pem:
        raise ValueError("managed_signer_certificate_chain_pem is not configured. Set MANAGED_SIGNER_CERTIFICATE_CHAIN_PEM environment variable.")

    return private_key_pem, cert_chain_pem


async def execute_rich_signing(
    *,
    request: RichArticleSignRequest,
    organization: Dict[str, Any],
    content_db: AsyncSession,
    core_db: AsyncSession,
    correlation_id: str,
) -> Dict[str, Any]:
    """
    Execute the full rich article signing pipeline.

    Args:
        request: Validated RichArticleSignRequest.
        organization: Authenticated organization context dict.
        content_db: Content database session.
        core_db: Core database session.
        correlation_id: Request correlation ID.

    Returns:
        Response dict with success, data, error, and correlation_id keys.
    """
    from fastapi import HTTPException, status

    start_time = time.time()
    tier = (organization.get("tier") or "free").lower().replace("-", "_")
    org_id = organization["organization_id"]
    features = organization.get("features") or {}

    # --- Validate Enterprise-only features ---
    if request.options.enable_trustmark:
        if not features.get("trustmark_watermark", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "E_TIER_REQUIRED",
                    "message": "enable_trustmark requires Enterprise tier",
                    "hint": "Upgrade to Enterprise to use TrustMark watermarking",
                },
            )

    # Validate image_signing feature is enabled
    if not features.get("image_signing", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "E_FEATURE_DISABLED",
                "message": "image_signing is not enabled for this organization",
            },
        )

    # Generate document_id if not provided
    doc_id = request.document_id or ("doc_" + secrets.token_hex(4))

    # Get signer credentials for C2PA signing.
    # When certs are missing and passthrough mode is active, sign_image() will
    # skip JUMBF embedding automatically. If passthrough is disabled and certs
    # are missing we still raise 503 so production deployments fail loudly.
    try:
        signer_private_key_pem, signer_cert_chain_pem = _get_signer_credentials()
    except ValueError as e:
        if settings.signing_passthrough or settings.image_signing_passthrough:
            logger.warning("No signer credentials configured; using passthrough mode for doc=%s", doc_id)
            signer_private_key_pem, signer_cert_chain_pem = "", ""
        else:
            logger.error("Signer credential error: %s", e)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "code": "E_SIGNER_NOT_CONFIGURED",
                    "message": str(e),
                    "hint": "Set MANAGED_SIGNER_PRIVATE_KEY_PEM / MANAGED_SIGNER_CERTIFICATE_CHAIN_PEM, "
                    "or set IMAGE_SIGNING_PASSTHROUGH=true for local dev.",
                },
            )

    # --- Sign each image SEQUENTIALLY ---
    # Composite manifest needs all image hashes, so we cannot parallelize.
    signed_image_results: List[SignedImageResult] = []
    article_image_rows: List[ArticleImage] = []
    ingredients: List[ImageIngredient] = []

    for img_req in sorted(request.images, key=lambda x: x.position):
        image_id = generate_image_id()
        raw_bytes = base64.b64decode(img_req.data)

        try:
            svc_result: _ServiceSignedResult = await sign_image(
                image_data=raw_bytes,
                mime_type=img_req.mime_type,
                title=img_req.filename,
                org_id=org_id,
                document_id=doc_id,
                image_id=image_id,
                custom_assertions=[],
                rights_data={},
                signer_private_key_pem=signer_private_key_pem,
                signer_cert_chain_pem=signer_cert_chain_pem,
                action=request.options.action,
                image_quality=request.options.image_quality,
            )
        except Exception as e:
            logger.error(
                "Image signing failed for image_id=%s in doc=%s: %s",
                image_id,
                doc_id,
                e,
                exc_info=True,
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "E_IMAGE_SIGN_FAILED",
                    "message": f"Failed to sign image {img_req.filename!r}: {e}",
                },
            )

        # Compute pHash on the signed image
        phash_val = compute_phash(svc_result.signed_bytes)
        phash_hex = format(phash_val & 0xFFFFFFFFFFFFFFFF, "016x")

        # Apply TrustMark neural watermark (Enterprise only)
        trustmark_applied = False
        trustmark_key_val = None
        if request.options.enable_trustmark:
            from app.services.trustmark_client import (
                compute_trustmark_key,
                compute_trustmark_payload,
                trustmark_client,
            )

            if trustmark_client.is_configured:
                signed_b64 = base64.b64encode(svc_result.signed_bytes).decode()
                message_bits = compute_trustmark_payload(image_id, org_id)
                tm_result = await trustmark_client.apply_watermark(signed_b64, img_req.mime_type, message_bits)
                if tm_result is not None:
                    watermarked_b64, _confidence = tm_result
                    svc_result.signed_bytes = base64.b64decode(watermarked_b64)
                    from app.utils.hashing import compute_sha256

                    svc_result.signed_hash = compute_sha256(svc_result.signed_bytes)
                    svc_result.size_bytes = len(svc_result.signed_bytes)
                    trustmark_applied = True
                    trustmark_key_val = compute_trustmark_key(image_id, org_id)
                    logger.info(
                        "TrustMark applied: image_id=%s doc=%s",
                        image_id,
                        doc_id,
                    )
                else:
                    logger.warning(
                        "TrustMark failed for image_id=%s, continuing without watermark",
                        image_id,
                    )

        # Build ArticleImage DB row
        row = ArticleImage(
            organization_id=org_id,
            document_id=doc_id,
            image_id=image_id,
            position=img_req.position,
            filename=img_req.filename,
            mime_type=img_req.mime_type,
            alt_text=img_req.alt_text,
            original_hash=svc_result.original_hash,
            signed_hash=svc_result.signed_hash,
            size_bytes=svc_result.size_bytes,
            c2pa_instance_id=svc_result.c2pa_instance_id,
            c2pa_manifest_hash=svc_result.c2pa_manifest_hash,
            phash=phash_val,
            image_metadata=img_req.metadata or {},
            trustmark_applied=trustmark_applied,
            trustmark_key=trustmark_key_val,
        )
        article_image_rows.append(row)

        signed_image_results.append(
            SignedImageResult(
                image_id=image_id,
                filename=img_req.filename,
                position=img_req.position,
                signed_image_b64=base64.b64encode(svc_result.signed_bytes).decode(),
                signed_image_hash=svc_result.signed_hash,
                c2pa_manifest_instance_id=svc_result.c2pa_instance_id,
                size_bytes=svc_result.size_bytes,
                phash=phash_hex,
                mime_type=img_req.mime_type,
                c2pa_signed=svc_result.c2pa_signed,
            )
        )

        ingredients.append(
            ImageIngredient(
                image_id=image_id,
                filename=img_req.filename,
                mime_type=img_req.mime_type,
                c2pa_instance_id=svc_result.c2pa_instance_id,
                signed_hash=svc_result.signed_hash,
                position=img_req.position,
            )
        )

    # --- Sign the text portion via existing pipeline ---
    from app.schemas.sign_schemas import SignOptions, UnifiedSignRequest
    from app.services.unified_signing_service import execute_unified_signing

    text_request = UnifiedSignRequest(
        text=request.content,
        document_id=doc_id,
        document_title=request.document_title,
        document_url=request.document_url,
        metadata=request.metadata,
        options=SignOptions(
            segmentation_level=request.options.segmentation_level,
            manifest_mode=request.options.manifest_mode,
            index_for_attribution=request.options.index_for_attribution,
            use_rights_profile=request.options.use_rights_profile,
        ),
    )

    text_result = await execute_unified_signing(
        request=text_request,
        organization=organization,
        core_db=core_db,
        content_db=content_db,
        correlation_id=correlation_id,
    )

    # Extract text signing metadata for composite manifest
    text_data = text_result.get("data", {})
    if isinstance(text_data, dict):
        document_data = text_data.get("document") or {}
        if not document_data and isinstance(text_data.get("documents"), list):
            docs = text_data.get("documents") or []
            document_data = docs[0] if docs else {}
    else:
        document_data = {}

    text_merkle_root = document_data.get("merkle_root") or ""
    text_instance_id = document_data.get("instance_id") or ""

    # --- Build composite manifest ---
    composite: CompositeManifestResult = build_composite_manifest(
        document_id=doc_id,
        org_id=org_id,
        document_title=request.document_title or doc_id,
        text_merkle_root=text_merkle_root,
        text_instance_id=text_instance_id,
        images=ingredients,
    )

    # --- Persist to DB ---
    for row in article_image_rows:
        content_db.add(row)

    composite_row = CompositeManifest(
        organization_id=org_id,
        document_id=doc_id,
        instance_id=composite.instance_id,
        manifest_data=composite.manifest_data,
        manifest_hash=composite.manifest_hash,
        text_merkle_root=text_merkle_root,
        ingredient_count=composite.ingredient_count,
    )
    content_db.add(composite_row)

    try:
        await content_db.commit()
    except Exception as e:
        logger.error("DB commit failed for rich signing doc=%s: %s", doc_id, e)
        await content_db.rollback()

        # IntegrityError (duplicate doc_id, constraint violation) must always
        # be surfaced -- passthrough mode only forgives infrastructure failures,
        # not data conflicts.
        from sqlalchemy.exc import IntegrityError

        if isinstance(e, IntegrityError):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "E_DUPLICATE_DOCUMENT",
                    "message": f"Document {doc_id!r} already signed (constraint violation)",
                },
            )

        if not (settings.signing_passthrough or settings.image_signing_passthrough):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "E_DB_ERROR",
                    "message": "Failed to persist signing results",
                },
            )
        logger.warning("Passthrough mode: returning signed data despite DB failure for doc=%s", doc_id)

    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    return {
        "success": True,
        "data": {
            "document_id": doc_id,
            "content_type": "rich_article",
            "text": document_data,
            "images": [img.model_dump() for img in signed_image_results],
            "composite_manifest": {
                "instance_id": composite.instance_id,
                "ingredient_count": composite.ingredient_count,
                "manifest_hash": composite.manifest_hash,
            },
            "total_images": len(signed_image_results),
            "processing_time_ms": elapsed_ms,
        },
        "error": None,
        "correlation_id": correlation_id,
    }
