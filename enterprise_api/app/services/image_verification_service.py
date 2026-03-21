"""Image C2PA verification service using c2pa-python Reader."""

from app.utils.c2pa_verifier_core import C2paVerificationResult, verify_c2pa
from app.utils.hashing import compute_sha256

# Re-export for callers that import from this module
ImageVerificationResult = C2paVerificationResult


def verify_image_c2pa(image_bytes: bytes, mime_type: str) -> C2paVerificationResult:
    """Verify C2PA manifest embedded in image bytes.

    Delegates to the shared verify_c2pa function.
    """
    return verify_c2pa(image_bytes, mime_type)


__all__ = ["ImageVerificationResult", "compute_sha256", "verify_image_c2pa"]
