"""Audio signing service: C2PA manifest embedding for audio files.

Supports WAV, MP3, and M4A/AAC formats. Uses c2pa-python to embed a JUMBF
manifest store into the audio container. The library handles all
container-specific logic (RIFF C2PA chunk, ID3 GEOB frame, BMFF uuid box).
"""

import logging
import uuid
from dataclasses import dataclass
from io import BytesIO
from typing import List

logger = logging.getLogger(__name__)


@dataclass
class SignedAudioResult:
    """Result of signing an audio file with c2pa-python."""

    audio_id: str
    signed_bytes: bytes
    original_hash: str  # sha256: hex of original bytes
    signed_hash: str  # sha256: hex of signed bytes
    c2pa_instance_id: str  # "urn:uuid:..."
    c2pa_manifest_hash: str  # sha256 of manifest bytes
    size_bytes: int
    mime_type: str
    c2pa_signed: bool = True


async def sign_audio(
    *,
    audio_data: bytes,
    mime_type: str,
    title: str,
    org_id: str,
    document_id: str,
    audio_id: str,
    custom_assertions: List[dict],
    rights_data: dict,
    signer_private_key_pem: str,
    signer_cert_chain_pem: str,
    action: str = "c2pa.created",
) -> SignedAudioResult:
    """Sign an audio file with a C2PA manifest.

    Pipeline:
    1. Validate audio (size, format, MIME type)
    2. Compute original_hash
    3. Build C2PA manifest dict
    4. Create c2pa Signer from PEM keys
    5. Use c2pa.Builder to sign -> get signed_bytes
    6. Compute signed_hash and manifest_hash
    7. Return SignedAudioResult
    """
    from app.utils.audio_utils import canonicalize_mime_type, validate_audio
    from app.utils.hashing import compute_sha256

    canonical_mime, file_size = validate_audio(audio_data, mime_type)
    logger.info(
        "Signing audio: id=%s mime=%s size=%d",
        audio_id,
        canonical_mime,
        file_size,
    )

    original_hash = compute_sha256(audio_data)

    from app.config import settings

    passthrough = settings.signing_passthrough or not (signer_private_key_pem and signer_cert_chain_pem)
    if passthrough:
        logger.debug("Audio signing passthrough: no C2PA embed for audio_id=%s", audio_id)
        return SignedAudioResult(
            audio_id=audio_id,
            signed_bytes=audio_data,
            original_hash=original_hash,
            signed_hash=original_hash,
            c2pa_instance_id="urn:uuid:" + str(uuid.uuid4()),
            c2pa_manifest_hash="sha256:" + "0" * 64,
            size_bytes=file_size,
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
        asset_id=audio_id,
        asset_id_key="audio_id",
        action=action,
        custom_assertions=custom_assertions,
        rights_data=rights_data,
    )
    c2pa_instance_id = manifest_dict["instance_id"]

    signer = create_signer_from_pem(signer_private_key_pem, signer_cert_chain_pem)

    try:
        builder = c2pa.Builder(manifest_dict)
        dest = BytesIO()
        manifest_bytes = builder.sign(
            signer,
            canonical_mime,
            BytesIO(audio_data),
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
        "Audio signed: id=%s original=%d signed=%d overhead=%d",
        audio_id,
        len(audio_data),
        len(signed_bytes),
        len(signed_bytes) - len(audio_data),
    )

    return SignedAudioResult(
        audio_id=audio_id,
        signed_bytes=signed_bytes,
        original_hash=original_hash,
        signed_hash=signed_hash,
        c2pa_instance_id=c2pa_instance_id,
        c2pa_manifest_hash=c2pa_manifest_hash,
        size_bytes=len(signed_bytes),
        mime_type=canonical_mime,
        c2pa_signed=True,
    )
