"""
Reusable verification helpers shared by single and batch endpoints.

Encapsulates the low-level `UnicodeMetadata.verify_metadata` call along with
certificate resolution, manifest coercion, and verdict construction so the
logic can be reused by REST controllers and background jobs.

Supports C2PA trust list validation for third-party signed content.
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
import unicodedata
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


def _resolve_signer_name(execution: VerificationExecution) -> Optional[str]:
    """Resolve a human-readable signer label from certificate/manifest context."""

    if execution.resolved_cert and execution.resolved_cert.organization_name:
        return execution.resolved_cert.organization_name

    manifest = execution.manifest if isinstance(execution.manifest, dict) else {}
    nested_manifest = manifest.get("manifest") if isinstance(manifest.get("manifest"), dict) else None
    manifest_data = manifest.get("manifest_data") if isinstance(manifest.get("manifest_data"), dict) else None

    for candidate_manifest in (nested_manifest, manifest_data, manifest):
        if not isinstance(candidate_manifest, dict):
            continue

        custom_metadata = candidate_manifest.get("custom_metadata")
        if isinstance(custom_metadata, dict):
            for key in ("publisher_name", "organization_name", "display_name"):
                value = custom_metadata.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()

        publisher = candidate_manifest.get("publisher")
        if isinstance(publisher, dict):
            for key in ("name", "identifier"):
                value = publisher.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()

        for key in ("publisher_name", "organization_name", "display_name"):
            value = candidate_manifest.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return execution.signer_id or None


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
            if label == "com.encypher.rights.v2":
                data = assertion.get("data")
                if isinstance(data, dict):
                    rights_signals["segment_rights"] = data.get("segment_rights_map")
                    if data.get("default_rights"):
                        rights_signals.setdefault("rights", data["default_rights"])
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
        from encypher.core.signing import extract_certificates_from_cose
        from encypher.interop.c2pa.jumbf import deserialize_jumbf_payload
        from encypher.interop.c2pa.text_wrapper import find_and_decode

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


def detect_vs256_embeddings(text: str) -> bool:
    """Check if text contains VS256 embeddings using magic prefix detection."""
    from app.utils.vs256_crypto import find_all_markers as vs256_find_all

    return len(vs256_find_all(text)) > 0


_RESOLVE_UUID_SQL = """
    SELECT organization_id, document_id, leaf_index,
           embedding_metadata->>'manifest_mode' AS manifest_mode,
           embedding_metadata->'segment_location' AS segment_location,
           (embedding_metadata->>'total_segments')::int AS total_segments,
           manifest_data,
           leaf_hash
    FROM content_references
    WHERE embedding_metadata->>'log_id' = :log_id
       OR embedding_metadata->>'segment_uuid' = :legacy_uuid
    LIMIT 1
"""


def _extract_log_id_from_vs256_signature(signature: str) -> Optional[tuple[str, str]]:
    """Extract log_id from a VS256 signature without HMAC verification.

    Decodes the payload bytes and interprets the first 16 bytes as a log_id.
    Returns (hex_str, uuid_str) to support both new (log_id) and legacy
    (segment_uuid) DB record formats.
    """
    from uuid import UUID as _UUID

    from app.utils.vs256_crypto import (
        MAGIC_PREFIX_LEN,
        PAYLOAD_BYTES,
        SIGNATURE_CHARS,
        decode_bytes_vs256,
    )

    if len(signature) != SIGNATURE_CHARS:
        return None
    try:
        payload = decode_bytes_vs256(signature[MAGIC_PREFIX_LEN:])
        if len(payload) != PAYLOAD_BYTES:
            return None
        raw = payload[:16]
        return raw.hex(), str(_UUID(bytes=raw))
    except Exception:
        return None


def _extract_sentence_for_signature(payload_text: str, sig_start: int, sig_end: int) -> Optional[str]:
    """Extract the sentence containing a signature and remove that signature span.

    Returns None when no containing sentence can be determined.
    """
    try:
        from app.utils.segmentation import segment_sentences

        current_pos = 0
        for sentence in segment_sentences(payload_text):
            sent_start = payload_text.find(sentence, current_pos)
            if sent_start == -1:
                continue
            sent_end = sent_start + len(sentence)
            current_pos = sent_end

            if sent_start <= sig_start and sig_end <= sent_end:
                rel_start = sig_start - sent_start
                rel_end = sig_end - sent_start
                return sentence[:rel_start] + sentence[rel_end:]
    except Exception:
        return None

    return None


async def _resolve_uuids_from_db(
    *,
    payload_text: str,
    content_db: Optional[AsyncSession],
    core_db: Optional[AsyncSession] = None,
) -> Optional[Dict[str, Any]]:
    """Resolve VS256/ZW segment UUIDs via the content DB.

    Extracts UUIDs from embedded signatures and looks them up in
    ``content_references``.  When ``core_db`` is provided, the org's
    signing key is loaded and the HMAC is verified so that tampered
    content is correctly rejected.
    """
    from sqlalchemy import text as sql_text

    # Obtain a content DB session
    session = content_db
    owns_session = False
    if session is None:
        from app.database import content_session_factory

        session = content_session_factory()
        owns_session = True

    try:
        # Try VS256 signatures
        from app.utils.vs256_crypto import (
            find_all_markers as vs256_find_all,
        )

        vs256_sigs = vs256_find_all(payload_text)
        log_ids: list[tuple[str, str]] = []  # (hex_str, legacy_uuid_str)

        if vs256_sigs:
            for _start, _end, sig_str in vs256_sigs:
                ids = _extract_log_id_from_vs256_signature(sig_str)
                if ids:
                    log_ids.append(ids)

        if not log_ids:
            return None

        # Resolve the first ID to get org/document info (try new log_id then legacy UUID)
        first_hex, first_uuid = log_ids[0]
        result = await session.execute(sql_text(_RESOLVE_UUID_SQL), {"log_id": first_hex, "legacy_uuid": first_uuid})
        row = result.fetchone()

        if not row or not row.organization_id:
            return None

        manifest_data = None
        if hasattr(row, "manifest_data") and row.manifest_data:
            manifest_data = row.manifest_data if isinstance(row.manifest_data, dict) else None

        # Verify HMAC with the org's actual signing key when possible.
        # Without this, the DB fallback would claim is_valid=True for any
        # text containing a known UUID -- even if the visible content was
        # tampered with after signing.
        hmac_verified = False
        if core_db and vs256_sigs:
            try:
                from app.utils.crypto_utils import load_organization_private_key
                from app.utils.vs256_crypto import (
                    derive_signing_key_from_private_key,
                    verify_signed_marker,
                )

                private_key = await load_organization_private_key(
                    row.organization_id,
                    core_db,
                )
                signing_key = derive_signing_key_from_private_key(private_key)

                _start, _end, sig_str = vs256_sigs[0]
                clean_sentence = _extract_sentence_for_signature(
                    payload_text,
                    _start,
                    _end,
                )
                sig_valid, _sig_log_id = verify_signed_marker(
                    sig_str,
                    signing_key,
                    sentence_text=clean_sentence,
                )
                hmac_verified = sig_valid
                if not sig_valid:
                    logger.info(
                        "DB UUID fallback HMAC check failed (content tampered): org=%s, log_id=%s",
                        row.organization_id,
                        first_hex,
                    )
                else:
                    logger.info(
                        "DB UUID fallback HMAC check passed: org=%s, log_id=%s",
                        row.organization_id,
                        first_hex,
                    )
            except Exception as e:
                logger.warning(
                    "DB UUID fallback: could not verify HMAC for org %s: %s",
                    row.organization_id,
                    e,
                )

        # --- Leaf hash verification (TEAM_272) ---
        # When the DB row stores a per-sentence leaf_hash, verify that the
        # submitted text actually matches.  This catches cases where the HMAC
        # passes (UUID present) but the visible sentence content was altered.
        leaf_hash_verified: Optional[bool] = None
        stored_leaf_hash = getattr(row, "leaf_hash", None)
        if stored_leaf_hash and hmac_verified and vs256_sigs:
            try:
                from app.utils.merkle.hashing import compute_leaf_hash

                _start, _end, _sig_str = vs256_sigs[0]
                clean_sentence = _extract_sentence_for_signature(payload_text, _start, _end)
                if clean_sentence is not None:
                    recomputed = compute_leaf_hash(clean_sentence)
                    leaf_hash_verified = recomputed == stored_leaf_hash
                    if not leaf_hash_verified:
                        hmac_verified = False
                        logger.info(
                            "Leaf hash mismatch: org=%s, log_id=%s",
                            row.organization_id,
                            first_hex,
                        )
            except Exception as e:
                logger.warning(
                    "Leaf hash check failed for org %s: %s",
                    row.organization_id,
                    e,
                )

        manifest_dict: Dict[str, Any] = {
            "manifest_mode": row.manifest_mode or "micro",
            "log_id": first_hex,
            "document_id": row.document_id,
            "total_signatures": len(log_ids),
            "total_segments": row.total_segments,
            **({"manifest_data": manifest_data} if manifest_data else {}),
        }
        if leaf_hash_verified is not None:
            manifest_dict["leaf_hash_verified"] = leaf_hash_verified

        return {
            "is_valid": hmac_verified,
            "signer_id": row.organization_id,
            "manifest": manifest_dict,
            "total_signatures": len(log_ids),
        }
    finally:
        if owns_session:
            await session.close()


async def execute_verification(
    *,
    payload_text: str,
    db: AsyncSession,
    content_db: Optional[AsyncSession] = None,
) -> VerificationExecution:
    """Run UnicodeMetadata verification with cached certificate resolution.

    Resolution order:
    1. Demo organization key (for testing)
    2. User-level orgs (free tier, use demo key)
    3. Registered organization certificates/BYOK keys
    4. C2PA trust list (for third-party signed content with embedded x5chain)
    5. ZW embeddings (Word-compatible, requires signing key from DB)
    6. VS256 embeddings (max density, requires signing key from DB)
    7. DB-based UUID resolution (resolves segment UUIDs without signing key)
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

    # Whitespace-normalization retry.
    # Browser copy-paste of rendered HTML produces \n\n between paragraphs
    # while the signed text was built with single spaces (WordPress extract_text
    # joins paragraphs via implode(' ', ...)).  When COSE verifies (signer_id is
    # set) but the content hash fails (is_valid=False), collapse all whitespace
    # runs to single spaces and retry before giving up.
    #
    # Two-step approach:
    # 1. Call verify_metadata() on the ws-normalized text (handles most cases).
    # 2. If that still fails (e.g. stored byte-offset exclusions land differently),
    #    manually re-compute the content hash from the manifest's stored
    #    c2pa.hash.data.v1 assertion.  COSE already verified, so we only need
    #    to confirm the content hash matches.
    if not is_valid and signer_id is not None and manifest:
        _ws_text = re.sub(r"\s+", " ", payload_text).strip()
        if _ws_text != payload_text:
            # Step 1: full re-verification with ws-normalized text
            try:
                _is_valid_ws, _signer_id_ws, _manifest_ws = UnicodeMetadata.verify_metadata(
                    text=_ws_text,
                    public_key_resolver=resolve_public_key,
                )
                if _is_valid_ws:
                    is_valid = _is_valid_ws
                    signer_id = _signer_id_ws
                    manifest = _manifest_ws
                    exception_message = None
                    logger.info("Whitespace-normalized verification succeeded: signer=%s", signer_id)
            except Exception as _ws_exc:
                logger.warning("Whitespace-normalized verification exception: %s", _ws_exc)

            # Step 2: manual content-hash check.
            # COSE is already trusted (signer_id resolved above).  Compute the
            # SHA-256 of the ws-normalized text with stored exclusions applied and
            # compare against the hash committed in the COSE payload.
            if not is_valid:
                try:
                    _assertions = manifest.get("assertions", []) if isinstance(manifest, dict) else []
                    _ch_assertion = next(
                        (a for a in _assertions if isinstance(a, dict) and a.get("label") == "c2pa.hash.data.v1"),
                        None,
                    )
                    if _ch_assertion:
                        _ch_data = _ch_assertion.get("data", {})
                        _stored_hash = _ch_data.get("hash", "")
                        _raw_excls = _ch_data.get("exclusions", [])
                        _excls = [(e["start"], e["length"]) for e in _raw_excls if isinstance(e, dict) and "start" in e and "length" in e]
                        if _stored_hash and _excls:
                            _norm = unicodedata.normalize("NFC", _ws_text)
                            _buf = bytearray(_norm.encode("utf-8"))
                            _ok = True
                            for _s, _l in sorted(_excls, key=lambda x: x[0], reverse=True):
                                if _s + _l > len(_buf):
                                    _ok = False
                                    break
                                del _buf[_s : _s + _l]
                            if _ok:
                                _actual_hash = hashlib.sha256(bytes(_buf)).hexdigest()
                                if _actual_hash == _stored_hash:
                                    is_valid = True
                                    exception_message = None
                                    logger.info("Whitespace-normalized manual hash check succeeded: signer=%s", signer_id)
                except Exception as _mh_exc:
                    logger.warning("Whitespace-normalized manual hash exception: %s", _mh_exc)

    # TEAM_158: Fallback to micro / ZW embedding verification
    # when C2PA finds no signer.  Micro mode embeds a signed UUID per
    # sentence (not a full C2PA manifest), so UnicodeMetadata won't detect
    # them.  Try ECC first (error-correcting), then plain HMAC, then ZW.
    if not is_valid and not signer_id:
        try:
            from app.utils.crypto_utils import get_demo_private_key
            from app.utils.vs256_crypto import (
                find_all_markers as vs256_find_all,
            )

            vs256_sigs = vs256_find_all(payload_text)
            if vs256_sigs:
                demo_key = get_demo_private_key()
                _start, _end, sig_str = vs256_sigs[0]
                clean_sentence = _extract_sentence_for_signature(payload_text, _start, _end)

                # Try VS256-RS first (error-correcting variant)
                try:
                    from app.utils.vs256_rs_crypto import (
                        derive_signing_key_from_private_key as vs256rs_derive_key,
                    )
                    from app.utils.vs256_rs_crypto import (
                        verify_signed_marker as vs256rs_verify,
                    )

                    rs_signing_key = vs256rs_derive_key(demo_key)
                    sig_valid, sig_log_id = vs256rs_verify(
                        sig_str,
                        rs_signing_key,
                        sentence_text=clean_sentence,
                    )
                    if sig_valid and sig_log_id:
                        from app.config import settings

                        is_valid = True
                        signer_id = settings.demo_organization_id
                        manifest = {
                            "manifest_mode": "micro",
                            "ecc": True,
                            "log_id": sig_log_id.hex(),
                            "micro_signatures_found": len(vs256_sigs),
                        }
                        logger.info(
                            "micro (ecc) fallback verification succeeded: log_id=%s, sigs=%d",
                            sig_log_id.hex(),
                            len(vs256_sigs),
                        )
                except Exception:
                    pass

                # Fall back to plain VS256 if RS didn't match
                if not is_valid:
                    from app.utils.vs256_crypto import (
                        derive_signing_key_from_private_key as vs256_derive_key,
                    )
                    from app.utils.vs256_crypto import (
                        verify_signed_marker as vs256_verify,
                    )

                    signing_key = vs256_derive_key(demo_key)
                    sig_valid, sig_log_id = vs256_verify(
                        sig_str,
                        signing_key,
                        sentence_text=clean_sentence,
                    )
                    if sig_valid and sig_log_id:
                        from app.config import settings

                        is_valid = True
                        signer_id = settings.demo_organization_id
                        manifest = {
                            "manifest_mode": "micro",
                            "log_id": sig_log_id.hex(),
                            "micro_signatures_found": len(vs256_sigs),
                        }
                        logger.info(
                            "micro fallback verification succeeded: log_id=%s, sigs=%d",
                            sig_log_id.hex(),
                            len(vs256_sigs),
                        )

        except Exception as e:
            logger.debug("VS256 fallback verification failed: %s", e)

    # TEAM_175: DB-based UUID resolution fallback.
    # When demo-key verification fails (e.g. content signed with an org key),
    # extract log_ids from VS256 signatures and resolve them via the content DB.
    if not is_valid and not signer_id:
        try:
            resolved = await _resolve_uuids_from_db(
                payload_text=payload_text,
                content_db=content_db,
                core_db=db,
            )
            if resolved:
                is_valid = resolved["is_valid"]
                signer_id = resolved["signer_id"]
                manifest = resolved["manifest"]
                logger.info(
                    "DB UUID resolution succeeded: signer=%s, sigs=%d",
                    signer_id,
                    resolved.get("total_signatures", 0),
                )
        except Exception as e:
            logger.debug("DB UUID resolution fallback failed: %s", e)

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
    signer_name = _resolve_signer_name(execution)

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
