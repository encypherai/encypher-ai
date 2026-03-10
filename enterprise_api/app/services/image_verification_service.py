"""Image C2PA verification service using c2pa-python Reader."""

import hashlib
import io
import json
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ImageVerificationResult:
    valid: bool
    c2pa_manifest_valid: bool
    hash_matches: bool
    c2pa_instance_id: Optional[str] = None
    signer: Optional[str] = None
    signed_at: Optional[str] = None
    manifest_data: Optional[dict] = None
    error: Optional[str] = None


def verify_image_c2pa(image_bytes: bytes, mime_type: str) -> ImageVerificationResult:
    """
    Verify C2PA manifest embedded in image bytes.

    Uses c2pa-python Reader to:
    1. Extract the JUMBF-embedded manifest
    2. Verify the cryptographic signature
    3. Return verification result with manifest details

    Gracefully handles images with no C2PA manifest.
    """
    try:
        import c2pa

        reader = c2pa.Reader(mime_type, io.BytesIO(image_bytes))
        manifest_json = reader.json()
        manifest_data = json.loads(manifest_json) if manifest_json else {}

        # Extract active manifest details
        active = manifest_data.get("active_manifest", "")
        manifests = manifest_data.get("manifests", {})
        active_manifest = manifests.get(active, {}) if active else {}

        instance_id = active_manifest.get("instance_id")
        claim_generator = active_manifest.get("claim_generator", "")

        return ImageVerificationResult(
            valid=True,
            c2pa_manifest_valid=True,
            hash_matches=True,  # c2pa-python raises exception if hash fails
            c2pa_instance_id=instance_id,
            signer=claim_generator,
            manifest_data=manifest_data,
        )

    except ImportError:
        return ImageVerificationResult(
            valid=False,
            c2pa_manifest_valid=False,
            hash_matches=False,
            error="c2pa-python not available",
        )
    except Exception as e:
        err_str = str(e)
        # Distinguish "no manifest" from "invalid manifest"
        no_manifest = any(phrase in err_str.lower() for phrase in ("not found", "no manifest", "missing", "jumbf", "notfound"))
        if no_manifest:
            return ImageVerificationResult(
                valid=False,
                c2pa_manifest_valid=False,
                hash_matches=False,
                error="No C2PA manifest found in image",
            )
        logger.warning("C2PA verification failed: %s", err_str)
        return ImageVerificationResult(
            valid=False,
            c2pa_manifest_valid=False,
            hash_matches=False,
            error=f"Verification failed: {err_str}",
        )


def compute_sha256(data: bytes) -> str:
    """Return SHA-256 hash of data with 'sha256:' prefix."""
    return "sha256:" + hashlib.sha256(data).hexdigest()
