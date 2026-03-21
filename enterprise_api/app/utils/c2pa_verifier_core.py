"""Shared C2PA manifest verification via c2pa-python Reader.

Used by both image and audio verification services. Handles all media types
supported by c2pa-python.
"""

import io
import json
import logging
from dataclasses import dataclass
from typing import Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class C2paVerificationResult:
    """Result of C2PA manifest verification for any media type."""

    valid: bool
    c2pa_manifest_valid: bool
    hash_matches: bool
    c2pa_instance_id: Optional[str] = None
    signer: Optional[str] = None
    signed_at: Optional[str] = None
    manifest_data: Optional[dict] = None
    error: Optional[str] = None


def verify_c2pa(
    data: bytes,
    mime_type: str,
    *,
    canonicalize_fn: Optional[Callable[[str], str]] = None,
) -> C2paVerificationResult:
    """Verify a C2PA manifest embedded in media bytes.

    Uses c2pa-python Reader to extract and verify the manifest. Works for
    any format supported by c2pa-python (images, audio, video).

    Args:
        data: Raw media file bytes.
        mime_type: MIME type string.
        canonicalize_fn: Optional function to normalize the MIME type before
            passing to the Reader.

    Returns:
        C2paVerificationResult with manifest details and validation status.
    """
    effective_mime = canonicalize_fn(mime_type) if canonicalize_fn else mime_type

    try:
        import c2pa

        reader = c2pa.Reader(effective_mime, io.BytesIO(data))
        manifest_json = reader.json()
        manifest_data = json.loads(manifest_json) if manifest_json else {}

        active = manifest_data.get("active_manifest", "")
        manifests = manifest_data.get("manifests", {})
        active_manifest = manifests.get(active, {}) if active else {}

        instance_id = active_manifest.get("instance_id")
        claim_generator = active_manifest.get("claim_generator", "")

        # Extract signed_at from actions assertion if present
        signed_at = None
        for assertion in active_manifest.get("assertions", []):
            if assertion.get("label", "").startswith("c2pa.actions"):
                actions = assertion.get("data", {}).get("actions", [])
                if actions:
                    signed_at = actions[0].get("when")
                break

        reader.close()

        return C2paVerificationResult(
            valid=True,
            c2pa_manifest_valid=True,
            hash_matches=True,
            c2pa_instance_id=instance_id,
            signer=claim_generator,
            signed_at=signed_at,
            manifest_data=manifest_data,
        )

    except ImportError:
        return C2paVerificationResult(
            valid=False,
            c2pa_manifest_valid=False,
            hash_matches=False,
            error="c2pa-python not available",
        )
    except Exception as e:
        err_str = str(e)
        no_manifest = any(phrase in err_str.lower() for phrase in ("not found", "no manifest", "missing", "jumbf", "notfound"))
        if no_manifest:
            return C2paVerificationResult(
                valid=False,
                c2pa_manifest_valid=False,
                hash_matches=False,
                error="No C2PA manifest found",
            )
        logger.warning("C2PA verification failed: %s", err_str)
        return C2paVerificationResult(
            valid=False,
            c2pa_manifest_valid=False,
            hash_matches=False,
            error="C2PA verification failed",
        )
