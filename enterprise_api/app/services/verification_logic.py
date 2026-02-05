"""
Reusable verification helpers shared by single and batch endpoints.

Encapsulates the low-level `UnicodeMetadata.verify_metadata` call along with
certificate resolution, manifest coercion, and verdict construction so the
logic can be reused by REST controllers and background jobs.

Supports C2PA trust list validation for third-party signed content.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Set

from sqlalchemy.ext.asyncio import AsyncSession

try:
    from encypher import UnicodeMetadata
except ImportError as exc:  # pragma: no cover - import guard
    raise ImportError("encypher-ai package not found. Install the preview version with C2PA verification support.") from exc

from app.models.response_models import VerifyVerdict
from app.services.certificate_service import ResolvedCertificate, certificate_resolver
from app.services.status_service import status_service
from app.utils.c2pa_trust_list import validate_certificate_chain
from app.utils.zw_crypto import (
    verify_minimal_signed_uuid,
    find_all_minimal_signed_uuids,
)

logger = logging.getLogger(__name__)


@dataclass
class VerificationExecution:
    """Result payload returned by `execute_verification`."""

    is_valid: bool
    signer_id: Optional[str]
    manifest: Dict[str, Any]
    missing_signers: Set[str]
    revoked_signers: Set[str]
    resolved_cert: Optional[ResolvedCertificate]
    duration_ms: int
    exception_message: Optional[str]
    # TEAM_002: Document revocation status
    document_revoked: bool = False
    revocation_reason: Optional[str] = None
    revocation_check_status: Optional[str] = None  # "active", "revoked", "unknown"
    revocation_check_error: Optional[str] = None
    revocation_status_list_url: Optional[str] = None
    revocation_bit_index: Optional[int] = None
    # C2PA trust list status
    untrusted_signer: bool = False  # True if signer cert not in C2PA trust list
    trust_status: Optional[str] = None  # "trusted", "untrusted", "unknown"


def _coerce_manifest(raw: Any) -> Dict[str, Any]:
    """Coerce manifest payloads into dictionaries for serialization."""

    if isinstance(raw, dict):
        return raw
    for attr in ("model_dump", "dict"):
        if hasattr(raw, attr):
            try:
                payload = getattr(raw, attr)()
                if isinstance(payload, dict):
                    return payload
            except Exception:  # pragma: no cover - defensive
                if hasattr(raw, "content") and raw.content:
                    return {}
                else:
                    return {}
    return {}


def _find_status_assertion(manifest: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Find the status list assertion in a C2PA manifest.

    TEAM_002: Looks for org.encypher.status assertion containing
    StatusList2021Entry data.
    """
    assertions = manifest.get("assertions", [])
    if isinstance(assertions, list):
        for assertion in assertions:
            if isinstance(assertion, dict):
                label = assertion.get("label", "")
                if label == "org.encypher.status":
                    data = assertion.get("data")
                    if isinstance(data, dict):
                        return data
                    return None

    # Also check custom_metadata for backward compatibility
    custom = manifest.get("custom_metadata", {})
    if isinstance(custom, dict) and "statusListCredential" in custom:
        return custom

    return None


def _extract_rights_signals(manifest: Dict[str, Any]) -> Dict[str, Any]:
    rights_signals: Dict[str, Any] = {}

    candidate_manifest = manifest
    nested_manifest = manifest.get("manifest")
    if isinstance(nested_manifest, dict):
        candidate_manifest = nested_manifest

    assertions = candidate_manifest.get("assertions", [])
    if isinstance(assertions, list):
        for assertion in assertions:
            if not isinstance(assertion, dict):
                continue
            label = assertion.get("label")
            if label == "c2pa.training-mining.v1":
                data = assertion.get("data")
                if isinstance(data, dict):
                    rights_signals["training_mining"] = data
            if label == "com.encypher.rights.v1":
                data = assertion.get("data")
                if isinstance(data, dict):
                    rights_signals["rights"] = data
    return rights_signals


def parse_manifest_timestamp(manifest: Dict[str, Any]) -> Optional[datetime]:
    """Extract ISO8601 timestamp from manifest metadata."""

    timestamp_value = manifest.get("signature_timestamp") or manifest.get("timestamp")
    if isinstance(timestamp_value, datetime):
        return timestamp_value
    if isinstance(timestamp_value, str):
        value = timestamp_value.strip()
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return None


def determine_reason_code(
    *,
    execution: VerificationExecution,
) -> str:
    """Map verification context to a stable reason code."""

    if execution.is_valid:
        if execution.untrusted_signer:
            return "UNTRUSTED_SIGNER"
        return "OK"
    # TEAM_002: Check document revocation before certificate issues
    if execution.document_revoked:
        return "DOC_REVOKED"
    if execution.untrusted_signer:
        return "UNTRUSTED_SIGNER"
    if execution.revoked_signers:
        return "CERT_REVOKED"
    if execution.missing_signers:
        return "CERT_NOT_FOUND"
    if not execution.signer_id:
        return "SIGNER_UNKNOWN"
    if execution.exception_message:
        return "VERIFY_EXCEPTION"
    return "SIGNATURE_INVALID"


@dataclass
class C2PACertificateResult:
    """Result of C2PA certificate extraction and validation."""

    public_key: Optional[Any] = None
    signer_info: Optional[str] = None
    is_trusted: bool = False
    has_certificate: bool = False
    trust_error: Optional[str] = None


def _extract_and_validate_c2pa_certificate(text: str) -> C2PACertificateResult:
    """
    Extract certificate from C2PA manifest in text and validate against trust list.

    Returns C2PACertificateResult with public key and trust status.
    Always returns the public key if found, even if untrusted.
    """
    result = C2PACertificateResult()

    try:
        import base64
        from cryptography.hazmat.primitives import serialization
        from encypher.interop.c2pa.text_wrapper import find_and_decode
        from encypher.interop.c2pa.jumbf import deserialize_jumbf_payload
        from encypher.core.signing import extract_certificates_from_cose

        # Extract manifest from text
        manifest_bytes, _clean_text, _span = find_and_decode(text)
        if manifest_bytes is None:
            return result

        # Deserialize JUMBF to get COSE signature
        manifest_store = deserialize_jumbf_payload(manifest_bytes)
        if not isinstance(manifest_store, dict):
            return result

        cose_sign1_b64 = manifest_store.get("cose_sign1")
        if not cose_sign1_b64:
            return result

        cose_bytes = base64.b64decode(cose_sign1_b64)

        # Extract certificates from COSE x5chain
        try:
            certs = extract_certificates_from_cose(cose_bytes)
        except ValueError:
            # No x5chain in COSE - not an error, just no embedded cert
            return result

        if not certs:
            return result

        # Get the leaf certificate
        leaf_cert = certs[0]
        result.has_certificate = True
        result.public_key = leaf_cert.public_key()

        # Extract signer info from certificate
        from cryptography.x509.oid import NameOID

        try:
            cn = leaf_cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
            result.signer_info = cn[0].value if cn else str(leaf_cert.subject)
        except Exception:
            result.signer_info = str(leaf_cert.subject)

        # Build PEM for validation
        leaf_pem = leaf_cert.public_bytes(serialization.Encoding.PEM).decode()

        chain_pem = None
        if len(certs) > 1:
            chain_pem = "\n".join(cert.public_bytes(serialization.Encoding.PEM).decode() for cert in certs[1:])

        # Validate against C2PA trust list
        is_valid, error_msg, _ = validate_certificate_chain(leaf_pem, chain_pem)

        if is_valid:
            result.is_trusted = True
            logger.info(f"C2PA trust list validation succeeded: {result.signer_info}")
        else:
            result.is_trusted = False
            result.trust_error = error_msg
            logger.info(f"C2PA certificate found but untrusted: {result.signer_info} - {error_msg}")

        return result

    except ValueError:
        # No C2PA wrapper found - not an error
        return result
    except Exception as e:
        logger.debug(f"Could not extract/validate C2PA certificate: {e}")
        return result


def detect_zw_embeddings(text: str) -> bool:
    """Check if text contains ZW (zero-width) embeddings using contiguous sequence detection."""
    # Use find_all_minimal_signed_uuids which detects 128 contiguous base-4 characters
    return len(find_all_minimal_signed_uuids(text)) > 0


async def execute_verification(*, payload_text: str, db: AsyncSession) -> VerificationExecution:
    """Run UnicodeMetadata verification with cached certificate resolution.

    Resolution order:
    1. Demo organization key (for testing)
    2. User-level orgs (free tier, use demo key)
    3. Registered organization certificates/BYOK keys
    4. C2PA trust list (for third-party signed content with embedded x5chain)
    5. ZW embeddings (Word-compatible, requires signing key from DB)
    """

    await certificate_resolver.refresh_cache(db)
    missing_signers: Set[str] = set()
    revoked_signers: Set[str] = set()

    # Pre-extract C2PA certificate for trust list validation
    c2pa_cert_result = _extract_and_validate_c2pa_certificate(payload_text)
    used_untrusted_cert = False  # Track if we used an untrusted certificate

    def resolve_public_key(signer_id: str):
        nonlocal used_untrusted_cert
        from app.config import settings
        from app.utils.crypto_utils import get_demo_private_key

        # Handle demo organization
        if signer_id == settings.demo_organization_id:
            return get_demo_private_key().public_key()

        # Handle user-level orgs (free tier) - they use the demo key
        if signer_id.startswith("user_"):
            logger.info(f"Using demo key for user org {signer_id}")
            return get_demo_private_key().public_key()

        cert = certificate_resolver.get(signer_id)
        if cert:
            if not cert.is_active():
                revoked_signers.add(signer_id)
            return cert.public_key

        # Fallback: Use embedded certificate from COSE x5chain
        # Even if untrusted, we can verify signature and show manifest
        if c2pa_cert_result.public_key is not None:
            if c2pa_cert_result.is_trusted:
                logger.info(f"Using C2PA trusted certificate for signer: {signer_id}")
            else:
                logger.info(f"Using untrusted certificate for signer: {signer_id} (will mark as untrusted)")
                used_untrusted_cert = True
            return c2pa_cert_result.public_key

        missing_signers.add(signer_id)
        return None

    start = time.perf_counter()
    try:
        is_valid, signer_id, manifest = UnicodeMetadata.verify_metadata(
            text=payload_text,
            public_key_resolver=resolve_public_key,
        )
        exception_message = None
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Verification runtime error: %s", exc, exc_info=True)
        is_valid = False
        signer_id = None
        manifest = {}
        exception_message = str(exc)

    duration_ms = int((time.perf_counter() - start) * 1000)
    manifest_dict = _coerce_manifest(manifest)
    resolved_cert = certificate_resolver.get(signer_id) if signer_id else None

    # TEAM_002: Check document revocation status via bitstring status list
    document_revoked = False
    revocation_reason = None
    revocation_check_status = None
    revocation_check_error = None
    revocation_status_list_url = None
    revocation_bit_index = None

    if is_valid and signer_id and manifest_dict:
        # Try to check revocation status from manifest assertions
        try:
            status_assertion = _find_status_assertion(manifest_dict)
            if status_assertion:
                status_list_url = status_assertion.get("statusListCredential")
                bit_index_str = status_assertion.get("statusListIndex")

                if status_list_url and bit_index_str:
                    bit_index = int(bit_index_str)
                    revocation_status_list_url = status_list_url
                    revocation_bit_index = bit_index
                    is_revoked, error = await status_service.check_revocation(
                        status_list_url=status_list_url,
                        bit_index=bit_index,
                    )

                    if is_revoked is None:
                        revocation_check_status = "unknown"
                        revocation_check_error = error
                    elif is_revoked:
                        revocation_check_status = "revoked"
                        document_revoked = True
                        is_valid = False
                        revocation_reason = "Document has been revoked by publisher"
                        logger.info(f"Document revoked: signer={signer_id}, list={status_list_url}, bit={bit_index}")
                    else:
                        revocation_check_status = "active"
        except Exception as e:
            logger.warning(f"Failed to check document revocation: {e}")
            # Continue without revocation check - fail open
            revocation_check_status = "unknown"
            revocation_check_error = str(e)

    # Determine trust status
    untrusted_signer = used_untrusted_cert
    if used_untrusted_cert:
        trust_status = "untrusted"
    elif c2pa_cert_result.is_trusted:
        trust_status = "trusted"
    elif resolved_cert is not None:
        trust_status = "trusted"  # Our registered certs are trusted
    else:
        trust_status = "unknown"

    return VerificationExecution(
        is_valid=is_valid,
        signer_id=signer_id,
        manifest=manifest_dict,
        missing_signers=missing_signers,
        revoked_signers=revoked_signers,
        resolved_cert=resolved_cert,
        duration_ms=duration_ms,
        exception_message=exception_message,
        document_revoked=document_revoked,
        revocation_reason=revocation_reason,
        revocation_check_status=revocation_check_status,
        revocation_check_error=revocation_check_error,
        revocation_status_list_url=revocation_status_list_url,
        revocation_bit_index=revocation_bit_index,
        untrusted_signer=untrusted_signer,
        trust_status=trust_status,
    )


def build_verdict(
    *,
    execution: VerificationExecution,
    reason_code: str,
    payload_bytes: int,
) -> VerifyVerdict:
    """Construct a VerifyVerdict payload from execution context."""

    details: Dict[str, Any] = {
        "manifest": execution.manifest,
        "duration_ms": execution.duration_ms,
        "payload_bytes": payload_bytes,
    }

    rights_signals = _extract_rights_signals(execution.manifest)
    if rights_signals:
        details["rights_signals"] = rights_signals
    if execution.missing_signers:
        details["missing_signers"] = sorted(execution.missing_signers)
    if execution.revoked_signers:
        details["revoked_signers"] = sorted(execution.revoked_signers)
    if execution.exception_message:
        details["exception"] = execution.exception_message
    # TEAM_002: Include document revocation info
    if execution.document_revoked:
        details["document_revoked"] = True
        if execution.revocation_reason:
            details["revocation_reason"] = execution.revocation_reason
    if execution.revocation_check_status:
        details["revocation_check"] = {
            "status": execution.revocation_check_status,
            "error": execution.revocation_check_error,
            "status_list_url": execution.revocation_status_list_url,
            "bit_index": execution.revocation_bit_index,
        }
    if execution.resolved_cert:
        details["certificate_status"] = execution.resolved_cert.status.value
        if execution.resolved_cert.certificate_rotated_at:
            details["certificate_rotated_at"] = execution.resolved_cert.certificate_rotated_at.isoformat()
    # C2PA trust status
    if execution.trust_status:
        details["trust_status"] = execution.trust_status
    if execution.untrusted_signer:
        details["untrusted_signer"] = True
        details["trust_warning"] = (
            "Certificate not in C2PA trust list. Signature is cryptographically valid but signer identity is not verified by a trusted CA."
        )

    timestamp = parse_manifest_timestamp(execution.manifest)
    signer_name = execution.resolved_cert.organization_name if execution.resolved_cert else (execution.signer_id or None)

    tampered = False
    if not execution.is_valid and reason_code == "SIGNATURE_INVALID":
        tampered = True

    return VerifyVerdict(
        valid=execution.is_valid,
        tampered=tampered,
        reason_code=reason_code,
        signer_id=execution.signer_id,
        signer_name=signer_name,
        timestamp=timestamp,
        details=details,
    )
