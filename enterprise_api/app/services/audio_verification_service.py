"""Audio C2PA verification service using c2pa-python Reader."""

from app.utils.audio_utils import canonicalize_mime_type
from app.utils.c2pa_verifier_core import C2paVerificationResult, verify_c2pa

# Re-export for callers that import from this module
AudioVerificationResult = C2paVerificationResult


def verify_audio_c2pa(audio_bytes: bytes, mime_type: str) -> C2paVerificationResult:
    """Verify C2PA manifest embedded in audio bytes.

    Delegates to the shared verify_c2pa function with audio MIME canonicalization.
    """
    return verify_c2pa(audio_bytes, mime_type, canonicalize_fn=canonicalize_mime_type)
