"""
Reusable verification helpers shared by single and batch endpoints.

Encapsulates the low-level `UnicodeMetadata.verify_metadata` call along with
certificate resolution, manifest coercion, and verdict construction so the
logic can be reused by REST controllers and background jobs.
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
    raise ImportError(
        "encypher-ai package not found. "
        "Install the preview version with C2PA verification support."
    ) from exc

from app.models.response_models import VerifyVerdict
from app.services.certificate_service import ResolvedCertificate, certificate_resolver
from app.services.status_service import status_service

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


def _coerce_manifest(raw: Any) -> Dict[str, Any]:
    """Coerce manifest payloads into dictionaries for serialization."""

    if isinstance(raw, dict):
        return raw
    for attr in ("model_dump", "dict"):
        if hasattr(raw, attr):
            try:
                return getattr(raw, attr)()
            except Exception:  # pragma: no cover - defensive
                if hasattr(raw, 'content') and raw.content:
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
                    return assertion.get("data", {})
    
    # Also check custom_metadata for backward compatibility
    custom = manifest.get("custom_metadata", {})
    if isinstance(custom, dict) and "statusListCredential" in custom:
        return custom
    
    return None


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
        return "OK"
    # TEAM_002: Check document revocation before certificate issues
    if execution.document_revoked:
        return "DOC_REVOKED"
    if execution.revoked_signers:
        return "CERT_REVOKED"
    if execution.missing_signers:
        return "CERT_NOT_FOUND"
    if not execution.signer_id:
        return "SIGNER_UNKNOWN"
    if execution.exception_message:
        return "VERIFY_EXCEPTION"
    return "SIGNATURE_INVALID"


async def execute_verification(*, payload_text: str, db: AsyncSession) -> VerificationExecution:
    """Run UnicodeMetadata verification with cached certificate resolution."""

    await certificate_resolver.refresh_cache(db)
    missing_signers: Set[str] = set()
    revoked_signers: Set[str] = set()

    def resolve_public_key(signer_id: str):
        from app.config import settings
        from app.utils.crypto_utils import get_demo_private_key
        
        if signer_id == settings.demo_organization_id:
            return get_demo_private_key().public_key()

        cert = certificate_resolver.get(signer_id)
        if not cert:
            missing_signers.add(signer_id)
            return None
        if not cert.is_active():
            revoked_signers.add(signer_id)
        return cert.public_key

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
    
    if is_valid and signer_id and manifest_dict:
        # Try to check revocation status from manifest assertions
        try:
            status_assertion = _find_status_assertion(manifest_dict)
            if status_assertion:
                status_list_url = status_assertion.get("statusListCredential")
                bit_index_str = status_assertion.get("statusListIndex")
                
                if status_list_url and bit_index_str:
                    bit_index = int(bit_index_str)
                    document_revoked = await status_service.check_revocation(
                        status_list_url=status_list_url,
                        bit_index=bit_index,
                    )
                    
                    if document_revoked:
                        is_valid = False
                        revocation_reason = "Document has been revoked by publisher"
                        logger.info(
                            f"Document revoked: signer={signer_id}, "
                            f"list={status_list_url}, bit={bit_index}"
                        )
        except Exception as e:
            logger.warning(f"Failed to check document revocation: {e}")
            # Continue without revocation check - fail open

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
    if execution.resolved_cert:
        details["certificate_status"] = execution.resolved_cert.status.value
        if execution.resolved_cert.certificate_rotated_at:
            details["certificate_rotated_at"] = execution.resolved_cert.certificate_rotated_at.isoformat()

    timestamp = parse_manifest_timestamp(execution.manifest)
    signer_name = (
        execution.resolved_cert.organization_name
        if execution.resolved_cert
        else (execution.signer_id or None)
    )

    return VerifyVerdict(
        valid=execution.is_valid,
        tampered=not execution.is_valid,
        reason_code=reason_code,
        signer_id=execution.signer_id,
        signer_name=signer_name,
        timestamp=timestamp,
        details=details,
    )
