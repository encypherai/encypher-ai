"""Rich article signing service: signs text + embedded media as a single provenance unit.

Orchestrates the full rich article signing pipeline:
1. Validate tier and watermark permissions
2. Sign each media file sequentially (composite manifest needs all hashes first)
3. Persist ArticleImage/ArticleAudio/ArticleVideo rows to content DB
4. Sign the article text via existing execute_unified_signing()
5. Build composite manifest (text root + all media ingredient hashes)
6. Persist CompositeManifest row
7. Return unified RichSignResponse
"""

import base64
import logging
import secrets
import time
import uuid
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings  # noqa: F401 (used for passthrough check)
from app.models.article_audio import ArticleAudio
from app.models.article_image import ArticleImage
from app.models.article_video import ArticleVideo
from app.models.composite_manifest import CompositeManifest
from app.schemas.rich_sign_schemas import (
    RichArticleSignRequest,
    SignedAudioResult,
    SignedImageResult,
    SignedVideoResult,
)
from app.services.composite_manifest_service import (
    CompositeManifestResult,
    MediaIngredient,
    build_composite_manifest,
)
from app.services.image_signing_service import SignedImageResult as _ServiceSignedImageResult
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


async def _sign_images_for_article(
    *,
    request: RichArticleSignRequest,
    doc_id: str,
    org_id: str,
    signer_private_key_pem: str,
    signer_cert_chain_pem: str,
) -> tuple[List[SignedImageResult], List[ArticleImage], List[MediaIngredient]]:
    """Sign all images in the request and return results, DB rows, and ingredients."""
    from fastapi import HTTPException, status

    signed_results: List[SignedImageResult] = []
    db_rows: List[ArticleImage] = []
    ingredients: List[MediaIngredient] = []

    for img_req in sorted(request.images, key=lambda x: x.position):
        image_id = generate_image_id()
        raw_bytes = base64.b64decode(img_req.data)

        try:
            svc_result: _ServiceSignedImageResult = await sign_image(
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
            logger.error("Image signing failed for image_id=%s in doc=%s: %s", image_id, doc_id, e, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "E_IMAGE_SIGN_FAILED", "message": f"Failed to sign image {img_req.filename!r}: {e}"},
            )

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
                    logger.info("TrustMark applied: image_id=%s doc=%s", image_id, doc_id)
                else:
                    logger.warning("TrustMark failed for image_id=%s, continuing without watermark", image_id)

        db_rows.append(
            ArticleImage(
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
        )

        signed_results.append(
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
                trustmark_applied=trustmark_applied,
            )
        )

        ingredients.append(
            MediaIngredient(
                asset_id=image_id,
                filename=img_req.filename,
                mime_type=img_req.mime_type,
                media_type="image",
                c2pa_instance_id=svc_result.c2pa_instance_id,
                signed_hash=svc_result.signed_hash,
                position=img_req.position,
            )
        )

    return signed_results, db_rows, ingredients


async def _sign_audios_for_article(
    *,
    request: RichArticleSignRequest,
    doc_id: str,
    org_id: str,
    signer_private_key_pem: str,
    signer_cert_chain_pem: str,
) -> tuple[List[SignedAudioResult], List[ArticleAudio], List[MediaIngredient]]:
    """Sign all audio files in the request and return results, DB rows, and ingredients."""
    from fastapi import HTTPException, status

    from app.services.audio_signing_service import sign_audio

    signed_results: List[SignedAudioResult] = []
    db_rows: List[ArticleAudio] = []
    ingredients: List[MediaIngredient] = []

    for aud_req in sorted(request.audios, key=lambda x: x.position):
        audio_id = f"aud_{uuid.uuid4().hex[:16]}"
        raw_bytes = base64.b64decode(aud_req.data)

        # Add soft-binding assertion when watermarking is enabled
        custom_assertions: list[dict] = []
        if request.options.enable_audio_watermark:
            from app.services.audio_watermark_client import SOFT_BINDING_ASSERTION

            custom_assertions.append(SOFT_BINDING_ASSERTION)

        try:
            svc_result = await sign_audio(
                audio_data=raw_bytes,
                mime_type=aud_req.mime_type,
                title=aud_req.filename,
                org_id=org_id,
                document_id=doc_id,
                audio_id=audio_id,
                custom_assertions=custom_assertions,
                rights_data={},
                signer_private_key_pem=signer_private_key_pem,
                signer_cert_chain_pem=signer_cert_chain_pem,
                action=request.options.action,
            )
        except Exception as e:
            logger.error("Audio signing failed for audio_id=%s in doc=%s: %s", audio_id, doc_id, e, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "E_AUDIO_SIGN_FAILED", "message": f"Failed to sign audio {aud_req.filename!r}: {e}"},
            )

        # Apply spread-spectrum watermark (Enterprise only)
        watermark_applied = False
        watermark_key_val = None
        if request.options.enable_audio_watermark:
            from app.services.audio_watermark_client import apply_watermark_to_signed_audio

            wm_result = await apply_watermark_to_signed_audio(svc_result.signed_bytes, aud_req.mime_type, audio_id, org_id)
            if wm_result is not None:
                svc_result.signed_bytes, svc_result.signed_hash, watermark_key_val = wm_result
                svc_result.size_bytes = len(svc_result.signed_bytes)
                watermark_applied = True
                logger.info("Audio watermark applied: audio_id=%s doc=%s", audio_id, doc_id)
            else:
                logger.warning("Audio watermark failed for audio_id=%s, continuing without watermark", audio_id)

        db_rows.append(
            ArticleAudio(
                organization_id=org_id,
                document_id=doc_id,
                audio_id=audio_id,
                position=aud_req.position,
                filename=aud_req.filename,
                mime_type=aud_req.mime_type,
                original_hash=svc_result.original_hash,
                signed_hash=svc_result.signed_hash,
                size_bytes=svc_result.size_bytes,
                c2pa_instance_id=svc_result.c2pa_instance_id,
                c2pa_manifest_hash=svc_result.c2pa_manifest_hash,
                watermark_applied=watermark_applied,
                watermark_key=watermark_key_val,
                audio_metadata=aud_req.metadata or {},
            )
        )

        signed_results.append(
            SignedAudioResult(
                audio_id=audio_id,
                filename=aud_req.filename,
                position=aud_req.position,
                signed_audio_b64=base64.b64encode(svc_result.signed_bytes).decode(),
                signed_audio_hash=svc_result.signed_hash,
                c2pa_manifest_instance_id=svc_result.c2pa_instance_id,
                size_bytes=svc_result.size_bytes,
                watermark_applied=watermark_applied,
                mime_type=aud_req.mime_type,
                c2pa_signed=svc_result.c2pa_signed,
            )
        )

        ingredients.append(
            MediaIngredient(
                asset_id=audio_id,
                filename=aud_req.filename,
                mime_type=aud_req.mime_type,
                media_type="audio",
                c2pa_instance_id=svc_result.c2pa_instance_id,
                signed_hash=svc_result.signed_hash,
                position=aud_req.position,
            )
        )

    return signed_results, db_rows, ingredients


async def _sign_videos_for_article(
    *,
    request: RichArticleSignRequest,
    doc_id: str,
    org_id: str,
    signer_private_key_pem: str,
    signer_cert_chain_pem: str,
) -> tuple[List[SignedVideoResult], List[ArticleVideo], List[MediaIngredient]]:
    """Sign all video files in the request and return results, DB rows, and ingredients."""
    from fastapi import HTTPException, status

    from app.services.video_signing_service import sign_video

    signed_results: List[SignedVideoResult] = []
    db_rows: List[ArticleVideo] = []
    ingredients: List[MediaIngredient] = []

    for vid_req in sorted(request.videos, key=lambda x: x.position):
        video_id = f"vid_{uuid.uuid4().hex[:16]}"
        raw_bytes = base64.b64decode(vid_req.data)

        # Add soft-binding assertion when watermarking is enabled
        custom_assertions: list[dict] = []
        if request.options.enable_video_watermark:
            from app.services.video_watermark_client import SOFT_BINDING_ASSERTION_VIDEO

            custom_assertions.append(SOFT_BINDING_ASSERTION_VIDEO)

        try:
            svc_result = await sign_video(
                video_data=raw_bytes,
                mime_type=vid_req.mime_type,
                title=vid_req.filename,
                org_id=org_id,
                document_id=doc_id,
                video_id=video_id,
                custom_assertions=custom_assertions,
                rights_data={},
                signer_private_key_pem=signer_private_key_pem,
                signer_cert_chain_pem=signer_cert_chain_pem,
                action=request.options.action,
            )
        except Exception as e:
            logger.error("Video signing failed for video_id=%s in doc=%s: %s", video_id, doc_id, e, exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "E_VIDEO_SIGN_FAILED", "message": f"Failed to sign video {vid_req.filename!r}: {e}"},
            )

        # Apply spread-spectrum watermark (Enterprise only)
        watermark_applied = False
        watermark_key_val = None
        if request.options.enable_video_watermark:
            from app.services.video_watermark_client import apply_watermark_to_signed_video

            wm_result = await apply_watermark_to_signed_video(svc_result.signed_bytes, vid_req.mime_type, video_id, org_id)
            if wm_result is not None:
                svc_result.signed_bytes, svc_result.signed_hash, watermark_key_val = wm_result
                svc_result.size_bytes = len(svc_result.signed_bytes)
                watermark_applied = True
                logger.info("Video watermark applied: video_id=%s doc=%s", video_id, doc_id)
            else:
                logger.warning("Video watermark failed for video_id=%s, continuing without watermark", video_id)

        db_rows.append(
            ArticleVideo(
                organization_id=org_id,
                document_id=doc_id,
                video_id=video_id,
                position=vid_req.position,
                filename=vid_req.filename,
                mime_type=vid_req.mime_type,
                original_hash=svc_result.original_hash,
                signed_hash=svc_result.signed_hash,
                size_bytes=svc_result.size_bytes,
                c2pa_instance_id=svc_result.c2pa_instance_id,
                c2pa_manifest_hash=svc_result.c2pa_manifest_hash,
                watermark_applied=watermark_applied,
                watermark_key=watermark_key_val,
                video_metadata=vid_req.metadata or {},
            )
        )

        signed_results.append(
            SignedVideoResult(
                video_id=video_id,
                filename=vid_req.filename,
                position=vid_req.position,
                signed_video_b64=base64.b64encode(svc_result.signed_bytes).decode(),
                signed_video_hash=svc_result.signed_hash,
                c2pa_manifest_instance_id=svc_result.c2pa_instance_id,
                size_bytes=svc_result.size_bytes,
                watermark_applied=watermark_applied,
                mime_type=vid_req.mime_type,
                c2pa_signed=svc_result.c2pa_signed,
            )
        )

        ingredients.append(
            MediaIngredient(
                asset_id=video_id,
                filename=vid_req.filename,
                mime_type=vid_req.mime_type,
                media_type="video",
                c2pa_instance_id=svc_result.c2pa_instance_id,
                signed_hash=svc_result.signed_hash,
                position=vid_req.position,
            )
        )

    return signed_results, db_rows, ingredients


async def execute_rich_signing(
    *,
    request: RichArticleSignRequest,
    organization: Dict[str, Any],
    content_db: AsyncSession,
    core_db: AsyncSession,
    correlation_id: str,
) -> Dict[str, Any]:
    """Execute the full rich article signing pipeline.

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

    if request.options.enable_audio_watermark:
        if not features.get("audio_watermark", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "E_TIER_REQUIRED",
                    "message": "enable_audio_watermark requires Enterprise tier",
                    "hint": "Upgrade to Enterprise to use audio watermarking",
                },
            )

    if request.options.enable_video_watermark:
        if not features.get("video_watermark", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "E_TIER_REQUIRED",
                    "message": "enable_video_watermark requires Enterprise tier",
                    "hint": "Upgrade to Enterprise to use video watermarking",
                },
            )

    # Validate image_signing feature is enabled (when images present)
    if request.images and not features.get("image_signing", True):
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

    signer_kwargs = dict(
        request=request,
        doc_id=doc_id,
        org_id=org_id,
        signer_private_key_pem=signer_private_key_pem,
        signer_cert_chain_pem=signer_cert_chain_pem,
    )

    # --- Sign each media type SEQUENTIALLY ---
    # Composite manifest needs all hashes, so we cannot parallelize.
    image_results, image_rows, image_ingredients = await _sign_images_for_article(**signer_kwargs)
    audio_results, audio_rows, audio_ingredients = await _sign_audios_for_article(**signer_kwargs)
    video_results, video_rows, video_ingredients = await _sign_videos_for_article(**signer_kwargs)

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
        images=image_ingredients,
        audios=audio_ingredients,
        videos=video_ingredients,
    )

    # --- Persist to DB ---
    for row in image_rows:
        content_db.add(row)
    for row in audio_rows:
        content_db.add(row)
    for row in video_rows:
        content_db.add(row)

    composite_row = CompositeManifest(
        organization_id=org_id,
        document_id=doc_id,
        instance_id=composite.instance_id,
        manifest_data=composite.manifest_data,
        manifest_hash=composite.manifest_hash,
        text_merkle_root=text_merkle_root,
        ingredient_count=composite.ingredient_count,
        image_count=composite.image_count,
        audio_count=composite.audio_count,
        video_count=composite.video_count,
    )
    content_db.add(composite_row)

    try:
        await content_db.commit()
    except Exception as e:
        logger.error("DB commit failed for rich signing doc=%s: %s", doc_id, e)
        await content_db.rollback()

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
            "images": [img.model_dump() for img in image_results],
            "audios": [aud.model_dump() for aud in audio_results],
            "videos": [vid.model_dump() for vid in video_results],
            "composite_manifest": {
                "instance_id": composite.instance_id,
                "ingredient_count": composite.ingredient_count,
                "manifest_hash": composite.manifest_hash,
            },
            "total_images": len(image_results),
            "total_audios": len(audio_results),
            "total_videos": len(video_results),
            "processing_time_ms": elapsed_ms,
        },
        "error": None,
        "correlation_id": correlation_id,
    }
