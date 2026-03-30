"""Video signing service: C2PA manifest embedding for video files.

Supports MP4, MOV, M4V, and AVI formats. Uses c2pa-python to embed a JUMBF
manifest store into the video container. The library handles all
container-specific logic (ISO BMFF uuid box, RIFF C2PA chunk).
"""

import logging
import uuid
from dataclasses import dataclass
from io import BytesIO
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SignedVideoResult:
    """Result of signing a video file with c2pa-python."""

    video_id: str
    signed_bytes: bytes
    original_hash: str  # sha256: hex of original bytes
    signed_hash: str  # sha256: hex of signed bytes
    c2pa_instance_id: str  # "urn:uuid:..."
    c2pa_manifest_hash: str  # sha256 of manifest bytes
    size_bytes: int
    mime_type: str
    c2pa_signed: bool = True


async def sign_video(
    *,
    video_data: bytes,
    mime_type: str,
    title: str,
    org_id: str,
    document_id: str,
    video_id: str,
    custom_assertions: List[dict],
    rights_data: dict,
    signer_private_key_pem: str,
    signer_cert_chain_pem: str,
    action: str = "c2pa.created",
    digital_source_type: Optional[str] = None,
    ingredient_data: Optional[bytes] = None,
    ingredient_mime: Optional[str] = None,
) -> SignedVideoResult:
    """Sign a video file with a C2PA manifest.

    Pipeline:
    1. Validate video (size, format, MIME type)
    2. Compute original_hash
    3. Build C2PA manifest dict
    4. Create c2pa Signer from PEM keys
    5. Use c2pa.Builder to sign -> get signed_bytes
    6. Compute signed_hash and manifest_hash
    7. Return SignedVideoResult
    """
    from app.utils.hashing import compute_sha256
    from app.utils.video_utils import canonicalize_mime_type, validate_video

    canonical_mime, file_size = validate_video(video_data, mime_type)
    logger.info(
        "Signing video: id=%s mime=%s size=%d",
        video_id,
        canonical_mime,
        file_size,
    )

    original_hash = compute_sha256(video_data)

    from app.config import settings

    passthrough = settings.signing_passthrough or settings.video_signing_passthrough or not (signer_private_key_pem and signer_cert_chain_pem)
    if passthrough:
        logger.debug("Video signing passthrough: metadata embed for video_id=%s", video_id)
        from app.utils.video_metadata import inject_encypher_video_metadata

        instance_id = "urn:uuid:" + str(uuid.uuid4())
        embedded_bytes = inject_encypher_video_metadata(
            video_bytes=video_data,
            mime_type=canonical_mime,
            instance_id=instance_id,
            org_id=org_id,
            document_id=document_id,
            content_hash=original_hash,
        )
        signed_hash = compute_sha256(embedded_bytes)
        return SignedVideoResult(
            video_id=video_id,
            signed_bytes=embedded_bytes,
            original_hash=original_hash,
            signed_hash=signed_hash,
            c2pa_instance_id=instance_id,
            c2pa_manifest_hash="sha256:" + "0" * 64,
            size_bytes=len(embedded_bytes),
            mime_type=canonical_mime,
            c2pa_signed=False,
        )

    import c2pa

    from app.utils.c2pa_manifest import build_c2pa_manifest_dict
    from app.utils.c2pa_signer import create_signer_from_pem

    manifest_dict = build_c2pa_manifest_dict(
        title=title,
        org_id=org_id,
        document_id=document_id,
        asset_id=video_id,
        asset_id_key="video_id",
        action=action,
        custom_assertions=custom_assertions,
        rights_data=rights_data,
        digital_source_type=digital_source_type,
    )
    c2pa_instance_id = manifest_dict["instance_id"]

    signer = create_signer_from_pem(signer_private_key_pem, signer_cert_chain_pem)

    try:
        builder = c2pa.Builder(manifest_dict)

        if ingredient_data and ingredient_mime:
            from app.utils.c2pa_manifest import INGREDIENT_PARENT_LABEL

            ingredient_json = {"title": title, "relationship": "parentOf", "label": INGREDIENT_PARENT_LABEL}
            builder.add_ingredient(ingredient_json, ingredient_mime, BytesIO(ingredient_data))
            logger.info("Added ingredient to video manifest: mime=%s size=%d", ingredient_mime, len(ingredient_data))

        dest = BytesIO()
        manifest_bytes = builder.sign(
            signer,
            canonical_mime,
            BytesIO(video_data),
            dest,
        )
        dest.seek(0)
        signed_bytes = dest.read()
        del dest  # release buffer before hash computations
    finally:
        signer.close()

    signed_hash = compute_sha256(signed_bytes)
    c2pa_manifest_hash = compute_sha256(manifest_bytes)

    logger.info(
        "Video signed: id=%s original=%d signed=%d overhead=%d",
        video_id,
        len(video_data),
        len(signed_bytes),
        len(signed_bytes) - len(video_data),
    )

    return SignedVideoResult(
        video_id=video_id,
        signed_bytes=signed_bytes,
        original_hash=original_hash,
        signed_hash=signed_hash,
        c2pa_instance_id=c2pa_instance_id,
        c2pa_manifest_hash=c2pa_manifest_hash,
        size_bytes=len(signed_bytes),
        mime_type=canonical_mime,
        c2pa_signed=True,
    )
