"""Image signing service: C2PA JUMBF embedding for individual images.

This service signs images using c2pa-python, embeds a C2PA manifest as JUMBF
data, strips EXIF metadata before signing, and returns the signed image bytes
plus metadata for storage.
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from typing import Any, List

logger = logging.getLogger(__name__)

# ISO 8601 timestamp format for C2PA assertions
_TS_FMT = "%Y-%m-%dT%H:%M:%SZ"


@dataclass
class SignedImageResult:
    """Result of signing an individual image with c2pa-python."""

    image_id: str
    signed_bytes: bytes
    original_hash: str  # sha256: hex of pre-sign (post-EXIF-strip) bytes
    signed_hash: str  # sha256: hex of post-sign bytes
    c2pa_instance_id: str  # "urn:uuid:..."
    c2pa_manifest_hash: str  # sha256 of manifest bytes
    size_bytes: int
    mime_type: str
    c2pa_signed: bool = True  # False in passthrough mode (no cert configured)


def _build_manifest_dict(
    *,
    title: str,
    org_id: str,
    document_id: str,
    image_id: str,
    action: str,
    custom_assertions: List[dict],
    rights_data: dict,
) -> dict:
    """Build the c2pa manifest definition dict for signing."""
    now_iso = datetime.now(timezone.utc).strftime(_TS_FMT)
    instance_id = "urn:uuid:" + str(uuid.uuid4())

    assertions = [
        {
            "label": "c2pa.actions",
            "data": {
                "actions": [
                    {
                        "action": action,
                        "when": now_iso,
                    }
                ]
            },
        },
    ]

    # Add org/rights assertion
    if rights_data:
        assertions.append(
            {
                "label": "com.encypher.rights.v1",
                "data": rights_data,
            }
        )

    # Add custom assertions
    for ca in custom_assertions:
        assertions.append(ca)

    # Add encypher provenance assertion
    assertions.append(
        {
            "label": "com.encypher.provenance.v1",
            "data": {
                "organization_id": org_id,
                "document_id": document_id,
                "image_id": image_id,
                "signed_at": now_iso,
            },
        }
    )

    return {
        "claim_generator": "encypher-ai/1.0",
        "claim_generator_info": [{"name": "Encypher", "version": "1.0"}],
        "title": title,
        "instance_id": instance_id,
        "assertions": assertions,
    }


def _create_signer_from_pem(
    private_key_pem: str,
    cert_chain_pem: str,
) -> Any:
    """
    Create a c2pa.Signer from PEM-encoded private key and certificate chain.

    Uses C2paSignerInfo with ctypes NULL ta_url (no timestamp authority).
    The private key must be PKCS8-encoded EC/RSA/Ed25519.
    The cert_chain_pem should be EE cert + intermediate(s) + root CA.

    Args:
        private_key_pem: PKCS8 PEM-encoded private key string.
        cert_chain_pem: PEM-encoded certificate chain (EE first).

    Returns:
        c2pa.Signer instance. Caller must call .close() when done.
    """
    import c2pa
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    # Detect algorithm from the key type
    from cryptography.hazmat.primitives.serialization import load_pem_private_key

    key_bytes = private_key_pem.encode("utf-8")
    key_obj = load_pem_private_key(key_bytes, password=None)

    if isinstance(key_obj, Ed25519PrivateKey):
        alg = c2pa.C2paSigningAlg.ED25519

        def sign_callback(data: bytes) -> bytes:
            return key_obj.sign(data)

    elif isinstance(key_obj, ec.EllipticCurvePrivateKey):
        curve = key_obj.curve
        if isinstance(curve, ec.SECP256R1):
            alg = c2pa.C2paSigningAlg.ES256
        elif isinstance(curve, ec.SECP384R1):
            alg = c2pa.C2paSigningAlg.ES384
        elif isinstance(curve, ec.SECP521R1):
            alg = c2pa.C2paSigningAlg.ES512
        else:
            alg = c2pa.C2paSigningAlg.ES256

        def sign_callback(data: bytes) -> bytes:
            return key_obj.sign(data, ec.ECDSA(hashes.SHA256()))

    elif isinstance(key_obj, rsa.RSAPrivateKey):
        alg = c2pa.C2paSigningAlg.PS256

        def sign_callback(data: bytes) -> bytes:
            return key_obj.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=32,
                ),
                hashes.SHA256(),
            )

    else:
        raise ValueError(f"Unsupported private key type: {type(key_obj).__name__}")

    # Try from_info first (uses native signing, proper x5chain embedding)
    try:
        si = c2pa.C2paSignerInfo.__new__(c2pa.C2paSignerInfo)
        si.alg = alg.value if hasattr(alg, "value") else alg
        si.sign_cert = cert_chain_pem.encode("utf-8")
        si.private_key = key_bytes
        si.ta_url = None  # ctypes c_char_p: None = NULL = no TSA
        return c2pa.Signer.from_info(si)
    except Exception:
        # Fallback: from_callback (cert chain embedded via certs param)
        return c2pa.Signer.from_callback(
            callback=sign_callback,
            alg=alg,
            certs=cert_chain_pem,
            tsa_url=None,
        )


async def sign_image(
    *,
    image_data: bytes,
    mime_type: str,
    title: str,
    org_id: str,
    document_id: str,
    image_id: str,
    custom_assertions: List[dict],
    rights_data: dict,
    signer_private_key_pem: str,
    signer_cert_chain_pem: str,
    action: str = "c2pa.created",
    image_quality: int = 95,
) -> SignedImageResult:
    """
    Sign an image with a C2PA manifest (JUMBF embedding).

    Pipeline:
    1. Validate image (size, format)
    2. Strip EXIF (GPS / device serial removal)
    3. Compute original_hash (pre-sign, post-EXIF-strip)
    4. Build C2PA manifest dict
    5. Create c2pa Signer from PEM keys
    6. Use c2pa.Builder to sign -> get signed_bytes
    7. Compute signed_hash and manifest_hash
    8. Return SignedImageResult

    Args:
        image_data: Raw image bytes.
        mime_type: MIME type (e.g. "image/jpeg").
        title: Image title for C2PA manifest.
        org_id: Organization identifier.
        document_id: Parent document identifier.
        image_id: Unique image identifier (e.g. "img_aabbccdd").
        custom_assertions: Additional C2PA assertions to embed.
        rights_data: Rights metadata dict for com.encypher.rights.v1 assertion.
        signer_private_key_pem: PKCS8 PEM-encoded private key.
        signer_cert_chain_pem: PEM-encoded cert chain (EE cert + CA chain).
        action: C2PA action string (default "c2pa.created").
        image_quality: JPEG/WebP re-encode quality (1-100).

    Returns:
        SignedImageResult with signed image bytes and metadata.

    Raises:
        ValueError: If image validation fails.
        Exception: If C2PA signing fails.
    """
    from app.config import settings
    from app.utils.image_utils import (
        compute_sha256,
        strip_exif,
        validate_image,
    )

    # Step 1: Validate
    validate_image(image_data, mime_type)

    # Step 2: Strip EXIF (must happen before signing)
    clean_bytes = strip_exif(image_data, mime_type=mime_type, quality=image_quality)

    # Step 3: Compute original_hash (after EXIF strip, before C2PA signing)
    original_hash = compute_sha256(clean_bytes)

    # Passthrough mode: skip JUMBF embedding when no cert is configured or the
    # IMAGE_SIGNING_PASSTHROUGH flag is set. EXIF is still stripped, all hashes
    # and metadata are still computed and stored. Use for local dev / CI.
    # Never enable in production -- the returned image will have no C2PA manifest.
    passthrough = settings.image_signing_passthrough or not (signer_private_key_pem and signer_cert_chain_pem)
    if passthrough:
        logger.debug("Image signing passthrough: XMP embedding for image_id=%s", image_id)
        from app.utils.image_utils import inject_encypher_xmp

        instance_id = "urn:uuid:" + str(uuid.uuid4())
        embedded_bytes = inject_encypher_xmp(
            image_bytes=clean_bytes,
            mime_type=mime_type,
            instance_id=instance_id,
            org_id=org_id,
            document_id=document_id,
            image_hash=original_hash,
        )
        signed_hash = compute_sha256(embedded_bytes)
        return SignedImageResult(
            image_id=image_id,
            signed_bytes=embedded_bytes,
            original_hash=original_hash,
            signed_hash=signed_hash,
            c2pa_instance_id=instance_id,
            c2pa_manifest_hash="sha256:" + "0" * 64,  # sentinel for passthrough
            size_bytes=len(embedded_bytes),
            mime_type=mime_type,
            c2pa_signed=False,
        )

    import c2pa

    # Step 4: Build manifest
    manifest_dict = _build_manifest_dict(
        title=title,
        org_id=org_id,
        document_id=document_id,
        image_id=image_id,
        action=action,
        custom_assertions=custom_assertions,
        rights_data=rights_data,
    )
    c2pa_instance_id = manifest_dict["instance_id"]

    # Step 5: Create signer
    signer = _create_signer_from_pem(signer_private_key_pem, signer_cert_chain_pem)

    try:
        # Step 6: Build and sign
        builder = c2pa.Builder(manifest_dict)
        dest = BytesIO()
        manifest_bytes = builder.sign(
            signer=signer,
            format=mime_type,
            source=BytesIO(clean_bytes),
            dest=dest,
        )
        dest.seek(0)
        signed_bytes = dest.read()
    finally:
        signer.close()

    # Step 7: Compute hashes
    signed_hash = compute_sha256(signed_bytes)
    c2pa_manifest_hash = compute_sha256(manifest_bytes)

    return SignedImageResult(
        image_id=image_id,
        signed_bytes=signed_bytes,
        original_hash=original_hash,
        signed_hash=signed_hash,
        c2pa_instance_id=c2pa_instance_id,
        c2pa_manifest_hash=c2pa_manifest_hash,
        size_bytes=len(signed_bytes),
        mime_type=mime_type,
        c2pa_signed=True,
    )
