"""Shared C2PA manifest verification via c2pa-python Reader.

Used by both image and audio verification services. Handles all media types
supported by c2pa-python.
"""

import io
import json
import logging
from dataclasses import dataclass, field
from typing import Callable, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ValidationStatus:
    """A single C2PA spec validation status entry.

    Mirrors the ValidationStatus object defined in the C2PA specification.
    See: https://c2pa.org/specifications/specifications/2.1/specs/C2PA_Specification.html#_validation_status_codes
    """

    code: str
    success: Optional[bool] = None
    url: Optional[str] = None
    explanation: Optional[str] = None


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
    validation_status: List[ValidationStatus] = field(default_factory=list)


def _extract_validation_statuses(manifest_data: dict) -> List[ValidationStatus]:
    """Extract structured ValidationStatus entries from c2pa-python Reader JSON output.

    The Reader JSON contains a top-level ``validation_results`` key with the shape::

        {
          "activeManifest": {
            "success": [{"code": "...", "url": "..."}, ...],
            "failure": [{"code": "...", "url": "...", "explanation": "..."}, ...]
          }
        }

    Each entry is mapped to a ValidationStatus with ``success=True`` for entries in
    the success list and ``success=False`` for entries in the failure list.
    """
    statuses: List[ValidationStatus] = []
    validation_results = manifest_data.get("validation_results", {})
    active = validation_results.get("activeManifest", {})

    for entry in active.get("success", []):
        if not isinstance(entry, dict):
            continue
        statuses.append(
            ValidationStatus(
                code=str(entry.get("code", "")),
                success=True,
                url=entry.get("url") or None,
                explanation=entry.get("explanation") or None,
            )
        )

    for entry in active.get("failure", []):
        if not isinstance(entry, dict):
            continue
        statuses.append(
            ValidationStatus(
                code=str(entry.get("code", "")),
                success=False,
                url=entry.get("url") or None,
                explanation=entry.get("explanation") or None,
            )
        )

    return statuses


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

        from app.utils.c2pa_trust_list import (
            C2PA_TRUST_CONFIG,
            get_allowed_list_pem,
            get_trust_anchors_pem,
        )

        context = None
        trust_pem = get_trust_anchors_pem()
        if trust_pem:
            trust_settings: dict = {
                "trust_anchors": trust_pem,
                "trust_config": C2PA_TRUST_CONFIG,
            }
            allowed_pem = get_allowed_list_pem()
            if allowed_pem:
                trust_settings["allowed_list"] = allowed_pem

            settings = c2pa.Settings.from_dict(
                {
                    "trust": trust_settings,
                    "verify": {
                        "verify_trust": True,
                    },
                }
            )
            context = c2pa.Context(settings=settings)

        reader = c2pa.Reader(effective_mime, io.BytesIO(data), context=context)
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

        validation_statuses = _extract_validation_statuses(manifest_data)

        return C2paVerificationResult(
            valid=True,
            c2pa_manifest_valid=True,
            hash_matches=True,
            c2pa_instance_id=instance_id,
            signer=claim_generator,
            signed_at=signed_at,
            manifest_data=manifest_data,
            validation_status=validation_statuses,
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
