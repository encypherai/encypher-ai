"""Video C2PA verification service using c2pa-python Reader."""

from app.utils.c2pa_verifier_core import C2paVerificationResult, verify_c2pa
from app.utils.video_utils import canonicalize_mime_type

# Re-export for callers that import from this module
VideoVerificationResult = C2paVerificationResult


def verify_video_c2pa(video_bytes: bytes, mime_type: str) -> C2paVerificationResult:
    """Verify C2PA manifest embedded in video bytes.

    Delegates to the shared verify_c2pa function with video MIME canonicalization.
    """
    return verify_c2pa(video_bytes, mime_type, canonicalize_fn=canonicalize_mime_type)
