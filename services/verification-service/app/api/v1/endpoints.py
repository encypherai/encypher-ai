"""API endpoints for Verification Service v1"""

import hashlib
import html
import os
import re
import time
import unicodedata
from typing import Callable, List, Optional
from uuid import uuid4

import base64
import httpx
import json
from fastapi import APIRouter, Depends, HTTPException, Request, status, Header
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

try:
    import structlog
except ModuleNotFoundError:  # pragma: no cover - fallback for OpenAPI generation
    import logging

    class _StructlogFallback:
        @staticmethod
        def get_logger(name: str | None = None):
            return logging.getLogger(name)

        class contextvars:
            @staticmethod
            def bind_contextvars(**_kwargs):
                return None

    structlog = _StructlogFallback()

from encypher.core.keys import load_public_key_from_data
from cryptography import x509
from encypher.core.payloads import deserialize_jumbf_payload
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.core.signing import extract_certificates_from_cose

try:
    from encypher.interop.c2pa import find_wrapper_info_bytes
except ImportError:  # pragma: no cover

    def find_wrapper_info_bytes(_text: str):
        return None


from ...db.session import get_db
from ...models.enterprise_schemas import (
    ErrorDetail,
    VerifyRequest,
    VerifyResponse,
    VerifyVerdict,
    DocumentInfo,
    C2PAInfo,
    EmbeddingDetail,
    LicensingInfo,
    MerkleProofInfo,
    SegmentLocationInfo,
)
from ...models.schemas import (
    SignatureVerify,
    DocumentVerify,
    VerificationResponse,
    VerificationHistory,
    VerificationStats,
)
from ...services.verification_service import VerificationService
from ...core.config import settings
from ...utils.c2pa_trust_list import (
    fetch_trust_list,
    get_trust_anchors,
    set_trust_anchors_pem,
    validate_certificate_chain,
)

router = APIRouter()

MAX_VERIFY_BYTES = 2 * 1024 * 1024
MAX_MANIFEST_BYTES = 50 * 1024  # 50 KB cap on serialized manifest

# ---------------------------------------------------------------------------
# Template helpers (Task 1.0 - move inline HTML to template files)
# ---------------------------------------------------------------------------

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "templates")


def _load_template(name: str) -> str:
    """Load an HTML template from the templates directory."""
    path = os.path.join(_TEMPLATES_DIR, name)
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _render_portal_not_found(document_id: str, accept: str) -> HTMLResponse | JSONResponse:
    """Return 404 response for missing portal document.

    Returns JSON when the caller prefers it (Accept: application/json),
    otherwise HTML.
    """
    if "application/json" in accept:
        return JSONResponse(
            status_code=404,
            content={
                "error": "NOT_FOUND",
                "message": "Document not found in database.",
                "document_id": html.escape(document_id),
                "hint": ("Demo documents are not stored. Use POST /api/v1/verify with the signed text to verify content directly."),
            },
        )
    safe_id = html.escape(document_id)
    template = _load_template("portal_not_found.html")
    content = template.replace("{document_id}", safe_id)
    return HTMLResponse(content=content, status_code=404)


def _render_portal_result(
    *,
    document_id: str,
    title: str | None,
    org_name: str,
    signer_id: str | None,
    signer_name: str,
    reason_code: str,
    is_valid: bool,
    manifest: dict | None,
    accept: str,
    whitelabel: bool = False,
    org_display_name: str = "",
) -> HTMLResponse | JSONResponse:
    """Render portal result page with all user-controlled values escaped."""
    if "application/json" in accept:
        return JSONResponse(
            status_code=200,
            content={
                "document_id": document_id,
                "valid": is_valid,
                "reason_code": reason_code,
                "signer_id": signer_id,
                "signer_name": signer_name,
                "title": title,
                "org_name": org_name,
                "manifest": manifest or {},
            },
        )

    manifest_json = _render_manifest_json(manifest or {})
    status_color = "#00875A" if is_valid else "#D14343"
    status_text = "Valid" if is_valid else "Invalid"

    if whitelabel and org_display_name:
        branding_footer = f"Verified by {html.escape(org_display_name)}"
    else:
        branding_footer = "Verified by Encypher Verification Service"

    template = _load_template("portal_result.html")
    content = template.format(
        document_id=html.escape(document_id),
        title=html.escape(title or "Untitled"),
        org_name=html.escape(org_name),
        signer_id=html.escape(signer_id or "Unknown"),
        signer_name=html.escape(signer_name),
        reason_code=html.escape(reason_code),
        status_color=status_color,  # static value - safe
        status_text=html.escape(status_text),
        manifest_json=html.escape(manifest_json),
        branding_footer=branding_footer,
    )
    return HTMLResponse(content=content, status_code=200)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _resolve_zw_segment_uuid(segment_uuid: str) -> dict | None:
    """Resolve a ZW segment UUID via the enterprise API's content DB.

    Returns ``{"organization_id": ..., "document_id": ...}`` or ``None``.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.ENTERPRISE_API_URL}/api/v1/public/c2pa/zw/resolve/{segment_uuid}",
                timeout=5.0,
            )
    except httpx.RequestError:
        return None

    if response.status_code != 200:
        return None

    payload = response.json()
    if not isinstance(payload, dict) or "organization_id" not in payload:
        return None

    return payload


async def _bulk_resolve_segment_uuids(segment_uuids: list[str]) -> dict[str, dict]:
    """Resolve multiple segment UUIDs via the enterprise API's bulk endpoint.

    Returns a dict mapping ``segment_uuid -> resolve_payload``.
    Falls back to sequential single-resolve calls if the bulk endpoint fails.
    """
    if not segment_uuids:
        return {}

    # Try bulk endpoint first
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ENTERPRISE_API_URL}/api/v1/public/c2pa/zw/resolve",
                json={"segment_uuids": segment_uuids},
                timeout=10.0,
            )
    except httpx.RequestError:
        response = None

    if response and response.status_code == 200:
        payload = response.json()
        if isinstance(payload, dict) and "results" in payload:
            return {r["segment_uuid"]: r for r in payload["results"] if isinstance(r, dict) and "segment_uuid" in r}

    # Fallback: resolve one-by-one
    results: dict[str, dict] = {}
    for uuid_str in segment_uuids:
        resolved = await _resolve_zw_segment_uuid(uuid_str)
        if resolved:
            results[uuid_str] = resolved
    return results


async def _fetch_trust_anchor(*, signer_id: str) -> tuple[str | None, str | None]:
    """Fetch trust anchor from enterprise API.

    Returns ``(public_key_pem, signer_name)``.
    *signer_name* is the human-readable org name when available.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.ENTERPRISE_API_URL}/api/v1/public/c2pa/trust-anchors/{signer_id}",
                timeout=5.0,
            )
    except httpx.RequestError:
        return None, None

    if response.status_code != 200:
        return None, None

    payload = response.json()
    if not isinstance(payload, dict):
        return None, None

    public_key_pem = payload.get("public_key")
    if not isinstance(public_key_pem, str) or not public_key_pem.strip():
        return None, None

    # TEAM_156: Extract org name for display (fallback to signer_id handled by caller)
    signer_name = payload.get("signer_name")
    if not isinstance(signer_name, str) or not signer_name.strip():
        signer_name = None

    return public_key_pem, signer_name


def _extract_publisher_name_from_manifest(manifest: dict | None) -> str | None:
    """Extract human-readable publisher name from C2PA manifest assertions.

    Checks ``c2pa.metadata`` assertion for ``publisher.identifier`` (preferred)
    then ``publisher.name``, then falls back to ``author.name``.

    Handles two manifest shapes:
    - Direct: ``{"assertions": [...]}``
    - Wrapped: ``{"manifest": {"custom_metadata": {"assertions": [...]}}}``
      (returned by ``UnicodeMetadata.verify_metadata`` for the "manifest" format)

    Returns ``None`` if nothing useful is found.
    """
    if not isinstance(manifest, dict):
        return None

    # Resolve assertions list from either shape
    assertions = manifest.get("assertions")
    if not isinstance(assertions, list):
        inner = manifest.get("manifest")
        if isinstance(inner, dict):
            custom = inner.get("custom_metadata")
            if isinstance(custom, dict):
                assertions = custom.get("assertions")
    if not isinstance(assertions, list):
        return None
    for assertion in assertions:
        if not isinstance(assertion, dict):
            continue
        if assertion.get("label") != "c2pa.metadata":
            continue
        data = assertion.get("data")
        if not isinstance(data, dict):
            continue
        publisher = data.get("publisher")
        if isinstance(publisher, dict):
            for key in ("identifier", "name"):
                candidate = publisher.get(key)
                if isinstance(candidate, str) and candidate.strip():
                    return candidate.strip()
        author = data.get("author")
        if isinstance(author, dict):
            name = author.get("name")
            if isinstance(name, str) and name.strip():
                return name.strip()
    return None


def _count_variation_selectors(text: str) -> int:
    count = 0
    for ch in text:
        code = ord(ch)
        if 0xFE00 <= code <= 0xFE0F:
            count += 1
        elif 0xE0100 <= code <= 0xE01EF:
            count += 1
    return count


def _render_manifest_json(manifest: dict) -> str:
    """Pretty-print manifest JSON for HTML responses."""
    try:
        return json.dumps(manifest, indent=2) if manifest else "{}"
    except TypeError:
        return "{}"


def _cap_manifest(manifest: dict | None) -> tuple[dict | None, bool]:
    """Cap serialized manifest at MAX_MANIFEST_BYTES.

    Returns ``(manifest_or_none, truncated_flag)``.
    When the serialized form exceeds the cap, returns an empty dict and True.
    """
    if not manifest:
        return manifest, False
    try:
        serialized = json.dumps(manifest)
    except (TypeError, ValueError):
        return {}, True
    if len(serialized.encode("utf-8")) > MAX_MANIFEST_BYTES:
        return {}, True
    return manifest, False


def _error_response(
    status_code: int,
    *,
    correlation_id: str,
    code: str,
    message: str,
    hint: str | None = None,
    duration_ms: int | None = None,
) -> JSONResponse:
    payload = VerifyResponse(
        success=False,
        data=None,
        error=ErrorDetail(code=code, message=message, hint=hint),
        correlation_id=correlation_id,
        duration_ms=duration_ms,
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


async def get_current_user(authorization: str = Header(None)) -> Optional[dict]:
    """Verify user token with auth service (optional)"""
    if not authorization:
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.AUTH_SERVICE_URL}/api/v1/auth/verify", headers={"Authorization": authorization})
            if response.status_code == 200:
                return response.json()
            return None
    except Exception:
        return None


async def get_optional_organization(
    request: Request,
    authorization: str = Header(None),
) -> Optional[dict]:
    # TEAM_065: POST /api/v1/verify is public; only validate API key when provided.
    if not authorization:
        return None
    if not authorization.startswith("Bearer "):
        return None

    api_key = authorization.split(" ", 1)[1].strip()
    if not api_key:
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.KEY_SERVICE_URL}/api/v1/keys/validate",
                json={"key": api_key},
                timeout=5.0,
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Key service unavailable",
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = response.json()
    data = payload.get("data")
    if not payload.get("success") or not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    request.state.organization_id = data.get("organization_id")
    request.state.user_id = data.get("user_id") or data.get("api_key_owner_id")
    request.state.api_key_id = data.get("api_key_id")
    request.state.tier = data.get("tier")
    return data


def _demo_private_key_bytes() -> bytes:
    # TEAM_065: Align demo verification with local docker-compose (32 bytes of 0x00) and allow override.
    for env_name in ("DEMO_PRIVATE_KEY_HEX", "SECRET_KEY"):
        candidate = os.getenv(env_name)
        if candidate:
            try:
                value = bytes.fromhex(candidate.strip())
                if len(value) == 32:
                    return value
            except ValueError:
                pass
    return b"\x00" * 32


def _demo_public_key():
    from cryptography.hazmat.primitives.asymmetric import ed25519

    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(_demo_private_key_bytes())
    return private_key.public_key()


def _extract_embedded_c2pa_public_key(_text: str):
    """Extract leaf public key from embedded C2PA COSE x5chain if present."""
    try:
        info = find_wrapper_info_bytes(_text)
    except Exception:  # pragma: no cover
        info = None
    if not info:
        return None

    manifest_bytes, _wrapper_start, _wrapper_length = info
    try:
        manifest_store = deserialize_jumbf_payload(manifest_bytes)
    except Exception:
        return None
    if not isinstance(manifest_store, dict):
        return None

    cose_sign1_b64 = manifest_store.get("cose_sign1")
    if not isinstance(cose_sign1_b64, str) or not cose_sign1_b64:
        return None

    try:
        cose_bytes = base64.b64decode(cose_sign1_b64)
    except Exception:
        return None

    try:
        certs = extract_certificates_from_cose(cose_bytes)
    except Exception:
        return None

    if not certs:
        return None

    return certs[0].public_key()


async def _ensure_trust_list_loaded() -> None:
    if get_trust_anchors():
        return

    pem = os.getenv("C2PA_TRUST_LIST_PEM")
    if pem:
        set_trust_anchors_pem(pem)
        return

    fetch_enabled = os.getenv("C2PA_TRUST_LIST_FETCH", "").strip().lower() in {"1", "true", "yes"}
    if not fetch_enabled:
        return

    try:
        pem = await fetch_trust_list()
    except Exception:  # pragma: no cover
        return
    set_trust_anchors_pem(pem)


async def _is_embedded_c2pa_key_trusted(text: str) -> bool:
    await _ensure_trust_list_loaded()

    if not get_trust_anchors():
        return False

    try:
        info = find_wrapper_info_bytes(text)
    except Exception:  # pragma: no cover
        info = None
    if not info:
        return False

    manifest_bytes, _wrapper_start, _wrapper_length = info
    try:
        manifest_store = deserialize_jumbf_payload(manifest_bytes)
    except Exception:
        return False
    if not isinstance(manifest_store, dict):
        return False

    cose_sign1_b64 = manifest_store.get("cose_sign1")
    if not isinstance(cose_sign1_b64, str) or not cose_sign1_b64:
        return False

    try:
        cose_bytes = base64.b64decode(cose_sign1_b64)
    except Exception:
        return False

    try:
        certs = extract_certificates_from_cose(cose_bytes)
    except Exception:
        return False

    if not certs:
        return False

    from cryptography.hazmat.primitives import serialization

    leaf_pem = certs[0].public_bytes(serialization.Encoding.PEM).decode("utf-8")
    chain_pem = None
    if len(certs) > 1:
        chain_pem = "\n".join(cert.public_bytes(serialization.Encoding.PEM).decode("utf-8") for cert in certs[1:])
    ok, _err, _parsed = validate_certificate_chain(leaf_pem, chain_pem)
    return ok


# ---------------------------------------------------------------------------
# Org context and trust anchor resolution helper
# ---------------------------------------------------------------------------


async def _resolve_org_context(
    *,
    organization: dict | None,
    text: str,
    has_c2pa_wrapper: bool,
    wrapper_info,
    db: Session,
    logger,
) -> tuple[
    str | None,  # organization_id
    str | None,  # organization_name
    object | None,  # public_key (loaded from certificate_pem)
    str | None,  # extracted_signer_id
    str | None,  # extracted_manifest_uuid
    object | None,  # trust_anchor_public_key
    str | None,  # trust_anchor_name
]:
    """Extract org credentials and resolve trust anchor for unauthenticated requests.

    Returns a tuple of all org-context fields needed by verify_text.
    """
    organization_id = organization.get("organization_id") if organization else None
    organization_name = organization.get("organization_name") if organization else None
    certificate_pem = organization.get("certificate_pem") if organization else None

    logger.info(
        "verify_org_context",
        organization_id=organization_id,
        has_org_certificate=bool(certificate_pem),
    )

    public_key = None
    if certificate_pem:
        try:
            if isinstance(certificate_pem, str) and "BEGIN CERTIFICATE" in certificate_pem:
                cert = x509.load_pem_x509_certificate(certificate_pem.encode("utf-8"))
                public_key = cert.public_key()
            else:
                public_key = load_public_key_from_data(certificate_pem)
        except Exception:
            public_key = None

    # Extract signer_id and manifest_uuid from embedded metadata
    extracted_metadata = None
    try:
        extracted_metadata = UnicodeMetadata.extract_metadata(text)
    except Exception:
        extracted_metadata = None

    extracted_signer_id = None
    extracted_manifest_uuid = None
    if isinstance(extracted_metadata, dict):
        extracted_signer_id = extracted_metadata.get("signer_id")
        custom_metadata = extracted_metadata.get("custom_metadata")
        if isinstance(custom_metadata, dict):
            extracted_manifest_uuid = custom_metadata.get("manifest_uuid")

    # TEAM_156: For C2PA format, extract_metadata returns the decoded CBOR
    # payload which doesn't include signer_id (it's in the outer/JUMBF layer).
    if not extracted_signer_id and has_c2pa_wrapper and wrapper_info:
        try:
            manifest_bytes = wrapper_info[0]
            manifest_store = deserialize_jumbf_payload(manifest_bytes)
            if isinstance(manifest_store, dict):
                jumbf_signer_id = manifest_store.get("signer_id")
                if isinstance(jumbf_signer_id, str):
                    extracted_signer_id = jumbf_signer_id
        except Exception:
            pass

    # Trust anchor resolution for unauthenticated requests
    trust_anchor_public_key = None
    trust_anchor_name = None
    if not organization_id and not certificate_pem and isinstance(extracted_signer_id, str) and extracted_signer_id.startswith("org_"):
        if isinstance(extracted_manifest_uuid, str) and extracted_manifest_uuid.strip():
            # Soft check: try to confirm manifest_uuid in content_references
            try:
                exists_row = db.execute(
                    text(
                        """
                        SELECT 1
                        FROM content_references
                        WHERE embedding_metadata->>'manifest_uuid' = :manifest_uuid
                        LIMIT 1
                        """
                    ),
                    {"manifest_uuid": extracted_manifest_uuid},
                ).fetchone()
                if not exists_row:
                    logger.warning(
                        "manifest_uuid_not_in_content_references",
                        manifest_uuid=extracted_manifest_uuid,
                        signer_id=extracted_signer_id,
                    )
            except (ProgrammingError, OperationalError) as exc:
                # TEAM_156: Table may not exist (lightweight UUID mode, dev env).
                logger.warning(
                    "content_references_lookup_failed",
                    manifest_uuid=extracted_manifest_uuid,
                    error=str(exc),
                )
                db.rollback()

        trust_anchor_pem, trust_anchor_name = await _fetch_trust_anchor(signer_id=extracted_signer_id)
        if trust_anchor_pem:
            try:
                trust_anchor_public_key = load_public_key_from_data(trust_anchor_pem)
            except Exception:
                trust_anchor_public_key = None

    return (
        organization_id,
        organization_name,
        public_key,
        extracted_signer_id,
        extracted_manifest_uuid,
        trust_anchor_public_key,
        trust_anchor_name,
    )


# ---------------------------------------------------------------------------
# Fallback embedding detection helpers (Task 2.0)
# ---------------------------------------------------------------------------


def _build_embedding_details(uuids: list[str], resolved_map: dict[str, dict]) -> list[EmbeddingDetail]:
    """Build EmbeddingDetail list from resolved UUIDs."""
    details: list[EmbeddingDetail] = []
    for uuid_str in uuids:
        r = resolved_map.get(uuid_str)
        if not r:
            continue
        seg_loc = None
        loc_data = r.get("segment_location")
        if isinstance(loc_data, dict):
            seg_loc = SegmentLocationInfo(
                paragraph_index=loc_data.get("paragraph_index", 0),
                sentence_in_paragraph=loc_data.get("sentence_in_paragraph", 0),
            )
        details.append(
            EmbeddingDetail(
                segment_uuid=uuid_str,
                leaf_index=r.get("leaf_index"),
                segment_location=seg_loc,
                manifest_mode=r.get("manifest_mode"),
            )
        )
    return details


async def _run_embedding_fallback(
    *,
    ids: list[str],
    detect_label: str,
    logger,
) -> tuple[str | None, str | None, list[EmbeddingDetail], dict | None, int | None, bool]:
    """Resolve a list of embedding IDs against the enterprise API.

    Returns ``(org_id, document_id, embedding_details, c2pa_manifest, total_segments, is_valid)``.
    """
    if not ids:
        return None, None, [], None, None, False

    resolved_map = await _bulk_resolve_segment_uuids(ids)
    if not resolved_map:
        return None, None, [], None, None, False

    first_result = resolved_map.get(ids[0]) or next(iter(resolved_map.values()))
    org_id = first_result.get("organization_id")
    document_id = first_result.get("document_id")

    if not org_id:
        return None, document_id, [], None, None, False

    c2pa_manifest = first_result.get("manifest_data") if first_result.get("manifest_data") else None
    total_segments = first_result.get("total_segments")
    embedding_details = _build_embedding_details(ids, resolved_map)

    logger.info(
        f"verify_{detect_label}_resolved",
        first_id=ids[0],
        organization_id=org_id,
        document_id=document_id,
        total_ids=len(ids),
        resolved_count=len(embedding_details),
    )

    return org_id, document_id, embedding_details, c2pa_manifest, total_segments, True


async def _run_zw_fallback(
    text: str,
    logger,
) -> tuple[str | None, str | None, str | None, list[EmbeddingDetail], dict | None, int | None, bool]:
    """ZWC embedding fallback.

    Returns ``(org_id, document_id, uuid_str, embeddings, c2pa_manifest, total_segments, is_valid)``.
    """
    try:
        from ...utils.zw_detect import find_zw_signatures, extract_uuid_from_signature

        zw_sigs = find_zw_signatures(text)
        if not zw_sigs:
            return None, None, None, [], None, None, False

        zw_uuids: list[str] = []
        for _start, _end, sig_str in zw_sigs:
            sig_uuid = extract_uuid_from_signature(sig_str)
            if sig_uuid:
                zw_uuids.append(str(sig_uuid))

        if not zw_uuids:
            return None, None, None, [], None, None, False

        first_uuid = zw_uuids[0]
        org_id, doc_id, embeddings, manifest, total_segs, valid = await _run_embedding_fallback(
            ids=zw_uuids,
            detect_label="zw",
            logger=logger,
        )
        return org_id, doc_id, first_uuid, embeddings, manifest, total_segs, valid

    except Exception as exc:
        logger.debug("verify_zw_detection_error", error=str(exc))
        return None, None, None, [], None, None, False


async def _run_vs256_fallback(
    text: str,
    logger,
) -> tuple[str | None, str | None, str | None, list[EmbeddingDetail], dict | None, int | None, bool]:
    """VS256 embedding fallback.

    Returns ``(org_id, document_id, uuid_str, embeddings, c2pa_manifest, total_segments, is_valid)``.
    """
    try:
        from ...utils.vs256_detect import (
            find_vs256_signatures,
            extract_uuid_from_vs256_signature,
            collect_distributed_vs_chars,
            reassemble_signature_from_distributed,
        )

        vs256_sigs = find_vs256_signatures(text)

        # If no contiguous signatures found, try reassembling from distributed VS chars
        if not vs256_sigs:
            vs_chars = collect_distributed_vs_chars(text)
            reassembled = reassemble_signature_from_distributed(vs_chars)
            if reassembled:
                vs256_sigs = [(0, len(reassembled), reassembled)]
                logger.info(
                    "verify_vs256_reassembled_from_distributed",
                    total_vs_chars=len(vs_chars),
                )

        if not vs256_sigs:
            return None, None, None, [], None, None, False

        vs256_uuids: list[str] = []
        for _start, _end, sig_str in vs256_sigs:
            sig_uuid = extract_uuid_from_vs256_signature(sig_str)
            if sig_uuid:
                vs256_uuids.append(str(sig_uuid))

        if not vs256_uuids:
            return None, None, None, [], None, None, False

        first_uuid = vs256_uuids[0]
        org_id, doc_id, embeddings, manifest, total_segs, valid = await _run_embedding_fallback(
            ids=vs256_uuids,
            detect_label="vs256",
            logger=logger,
        )
        return org_id, doc_id, first_uuid, embeddings, manifest, total_segs, valid

    except Exception as exc:
        logger.debug("verify_vs256_detection_error", error=str(exc))
        return None, None, None, [], None, None, False


async def _run_legacy_safe_fallback(
    text: str,
    logger,
) -> tuple[str | None, str | None, str | None, list[EmbeddingDetail], dict | None, int | None, bool]:
    """Legacy-safe (base-6 ZWC) embedding fallback.

    Returns ``(org_id, document_id, first_log_id, embeddings, c2pa_manifest, total_segments, is_valid)``.
    """
    try:
        from ...utils.legacy_safe_detect import (
            find_legacy_safe_markers,
            extract_log_id_from_marker,
        )

        ls_markers = find_legacy_safe_markers(text)
        if not ls_markers:
            return None, None, None, [], None, None, False

        ls_log_ids: list[str] = []
        for _start, _end, marker_str in ls_markers:
            log_id_hex = extract_log_id_from_marker(marker_str)
            if log_id_hex:
                ls_log_ids.append(log_id_hex)

        if not ls_log_ids:
            return None, None, None, [], None, None, False

        first_log_id = ls_log_ids[0]
        org_id, doc_id, embeddings, manifest, total_segs, valid = await _run_embedding_fallback(
            ids=ls_log_ids,
            detect_label="legacy_safe",
            logger=logger,
        )
        return org_id, doc_id, first_log_id, embeddings, manifest, total_segs, valid

    except Exception as exc:
        logger.debug("verify_legacy_safe_detection_error", error=str(exc))
        return None, None, None, [], None, None, False


# ---------------------------------------------------------------------------
# Verdict builder (Task 2.4)
# ---------------------------------------------------------------------------


def _build_verdict(
    *,
    is_valid: bool,
    signer_id: str | None,
    manifest: dict | None,
    duration_ms: int,
    payload_bytes: int,
    organization_id: str | None,
    organization_name: str | None,
    extracted_signer_id: str | None,
    trust_anchor_name: str | None,
    embedded_public_key,
    embedded_trusted: bool,
    public_key_resolver: Callable[[str], object | None],
    resolved_embeddings: list[EmbeddingDetail],
    resolved_c2pa_manifest: dict | None,
    resolved_total_segments: int | None,
    zw_org_id: str | None,
    vs256_org_id: str | None,
    legacy_safe_org_id: str | None,
    include_merkle: bool,
) -> VerifyVerdict:
    """Assemble VerifyVerdict from all verification state."""
    # Determine reason_code
    reason_code = "OK" if is_valid else "SIGNATURE_INVALID"
    if not signer_id:
        reason_code = "SIGNER_UNKNOWN"
    elif zw_org_id and signer_id == zw_org_id:
        # TEAM_156: ZW DB-resolved - skip public_key_resolver check
        reason_code = "OK"
    elif vs256_org_id and signer_id == vs256_org_id:
        # TEAM_158: VS256 DB-resolved - skip public_key_resolver check
        reason_code = "OK"
    elif legacy_safe_org_id and signer_id == legacy_safe_org_id:
        # Legacy-safe DB-resolved - skip public_key_resolver check
        reason_code = "OK"
    elif public_key_resolver(signer_id) is None:
        reason_code = "CERT_NOT_FOUND"
    elif is_valid and embedded_public_key is not None and not embedded_trusted and not (organization_id and signer_id == organization_id):
        # TEAM_065: Valid signature, but signer cannot be validated to a trusted root.
        reason_code = "UNTRUSTED_SIGNER"

    # Attach navigation hints for non-OK reason codes
    _REASON_HINTS: dict[str, str] = {
        "SIGNER_UNKNOWN": (
            "No signer identity could be extracted from the content. "
            "Ensure the text is copied without modification from the original signed document."
        ),
        "CERT_NOT_FOUND": (
            "The signer's public key could not be resolved. "
            "The signing organization may not be registered, or use POST /api/v1/verify "
            "with an API key to supply the certificate directly."
        ),
        "UNTRUSTED_SIGNER": (
            "The signature is cryptographically valid but the signer certificate is not "
            "anchored to a trusted root. Contact the publisher for their trust anchor PEM."
        ),
    }
    hint = _REASON_HINTS.get(reason_code)

    # Build document_info
    document_info = None
    licensing_info = None
    if isinstance(manifest, dict):
        custom_metadata = manifest.get("custom_metadata", {})
        if isinstance(custom_metadata, dict):
            document_info = DocumentInfo(
                document_id=custom_metadata.get("document_id") or custom_metadata.get("manifest_uuid"),
                title=custom_metadata.get("title"),
                author=custom_metadata.get("author"),
                document_type=custom_metadata.get("document_type"),
            )
            if custom_metadata.get("license_type") or custom_metadata.get("license_url"):
                licensing_info = LicensingInfo(
                    license_type=custom_metadata.get("license_type"),
                    license_url=custom_metadata.get("license_url"),
                    usage_terms=custom_metadata.get("usage_terms"),
                    attribution_required=custom_metadata.get("attribution_required", False),
                )

    # Build c2pa_info
    c2pa_info = None
    if resolved_c2pa_manifest and isinstance(resolved_c2pa_manifest, dict):
        c2pa_info = C2PAInfo(
            validated=is_valid,
            validation_type="db_backed_manifest",
            manifest_hash=resolved_c2pa_manifest.get("manifest_hash"),
        )
        if resolved_c2pa_manifest.get("assertions"):
            c2pa_info.assertions = resolved_c2pa_manifest["assertions"]
    elif isinstance(manifest, dict) and manifest.get("cose_sign1") or (isinstance(manifest, dict) and manifest.get("manifest_hash")):
        c2pa_info = C2PAInfo(
            validated=is_valid,
            validation_type="cryptographic" if is_valid else None,
            manifest_hash=manifest.get("manifest_hash") if isinstance(manifest, dict) else None,
        )
        if isinstance(manifest, dict) and manifest.get("assertions"):
            c2pa_info.assertions = manifest.get("assertions")

    # Merkle proof (paid feature)
    merkle_proof_info = None
    if include_merkle and isinstance(manifest, dict):
        custom_metadata = manifest.get("custom_metadata", {})
        if isinstance(custom_metadata, dict) and custom_metadata.get("merkle_root"):
            merkle_proof_info = MerkleProofInfo(
                root_hash=custom_metadata.get("merkle_root"),
                leaf_hash=custom_metadata.get("leaf_hash"),
                leaf_index=custom_metadata.get("leaf_index"),
                verified=is_valid,
            )

    # Publisher name
    manifest_for_publisher = resolved_c2pa_manifest if resolved_c2pa_manifest else (manifest if isinstance(manifest, dict) else None)
    publisher_name = _extract_publisher_name_from_manifest(manifest_for_publisher)

    # Cap manifest before including in details
    raw_manifest_for_details = manifest or {}
    capped_manifest, manifest_truncated = _cap_manifest(raw_manifest_for_details if isinstance(raw_manifest_for_details, dict) else {})

    details: dict = {
        "manifest": capped_manifest or {},
        "duration_ms": duration_ms,
        "payload_bytes": payload_bytes,
    }
    if manifest_truncated:
        details["manifest_truncated"] = True
    if hint:
        details["hint"] = hint

    return VerifyVerdict(
        valid=is_valid,
        tampered=(not is_valid and reason_code == "SIGNATURE_INVALID"),
        reason_code=reason_code,
        signer_id=signer_id,
        publisher_name=publisher_name,
        # TEAM_210: Prefer publisher name from signed manifest, then org name from
        # authenticated context, then trust anchor name, then signer_id.
        signer_name=(
            publisher_name
            if publisher_name
            else organization_name
            if (signer_id and signer_id == organization_id and organization_name)
            else trust_anchor_name
            if trust_anchor_name
            else signer_id
        ),
        organization_id=organization_id if signer_id == organization_id else (extracted_signer_id if extracted_signer_id else None),
        organization_name=organization_name or trust_anchor_name,
        timestamp=None,
        document=document_info,
        c2pa=c2pa_info,
        licensing=licensing_info,
        embeddings=resolved_embeddings if resolved_embeddings else None,
        total_embeddings=len(resolved_embeddings) if resolved_embeddings else None,
        total_segments_in_document=resolved_total_segments,
        merkle_proof=merkle_proof_info,
        details=details,
    )


# ---------------------------------------------------------------------------
# C2PA fallback verification helper
# ---------------------------------------------------------------------------


def _try_c2pa_fallback(
    text: str,
    public_key_resolver: Callable[[str], object | None],
) -> tuple[bool, str | None, dict | None]:
    """Attempt C2PA wrapper-only verification when primary fails.

    Returns ``(is_valid, signer_id, manifest)``.
    """
    try:
        info = find_wrapper_info_bytes(text)
    except Exception:  # pragma: no cover - defensive
        info = None

    if not info:
        return False, None, None

    manifest_bytes, wrapper_start_byte, wrapper_length_byte = info
    try:
        manifest_store = deserialize_jumbf_payload(manifest_bytes)
        if isinstance(manifest_store, dict):
            fallback_signer_id = manifest_store.get("signer_id")
            cose_sign1 = manifest_store.get("cose_sign1")
        else:
            fallback_signer_id = None
            cose_sign1 = None

        if isinstance(fallback_signer_id, str) and isinstance(cose_sign1, str):
            outer_payload = {
                "format": "c2pa",
                "signer_id": fallback_signer_id,
                "cose_sign1": cose_sign1,
            }
            is_valid, signer_id, manifest = UnicodeMetadata._verify_c2pa(
                original_text=text,
                outer_payload=outer_payload,
                public_key_resolver=public_key_resolver,
                return_payload_on_failure=True,
                require_hard_binding=True,
                wrapper_exclusion=(wrapper_start_byte, wrapper_length_byte),
            )
            return is_valid, signer_id, manifest
    except Exception:  # pragma: no cover - defensive
        pass

    return False, None, None


# ---------------------------------------------------------------------------
# Whitespace-normalization retry
# ---------------------------------------------------------------------------


def _try_ws_normalized_retry(
    text: str,
    manifest: dict | None,
    public_key_resolver: Callable[[str], object | None],
    logger,
) -> tuple[bool, str | None, dict | None]:
    """Retry verification on whitespace-normalized text.

    Called when COSE identified a signer but the content hash failed
    (browser copy-paste may introduce extra newlines).

    Returns updated ``(is_valid, signer_id, manifest)``.
    """
    _ws_text = re.sub(r"\s+", " ", text).strip()
    if _ws_text == text:
        return False, None, manifest

    # Step 1: full re-verification with ws-normalized text
    try:
        _is_valid_ws, _signer_id_ws, _manifest_ws = UnicodeMetadata.verify_metadata(
            text=_ws_text,
            public_key_resolver=public_key_resolver,
        )
        if _is_valid_ws:
            logger.info("verify_ws_normalized_success", payload_bytes=len(text.encode("utf-8")))
            return _is_valid_ws, _signer_id_ws, _manifest_ws
    except Exception as _ws_exc:
        logger.warning("verify_ws_normalized_exception", error=str(_ws_exc))

    # Step 2: manual content-hash check.
    # COSE is already trusted (signer_id resolved above). Compute the
    # SHA-256 of the ws-normalized text with stored exclusions applied and
    # compare against the hash committed in the COSE payload.
    if not isinstance(manifest, dict):
        return False, None, manifest

    try:
        _assertions = manifest.get("assertions", [])
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
                        logger.info("verify_ws_manual_hash_success", payload_bytes=len(text.encode("utf-8")))
                        return True, None, manifest  # signer_id unchanged by caller
    except Exception as _mh_exc:
        logger.warning("verify_ws_manual_hash_exception", error=str(_mh_exc))

    return False, None, manifest


# ---------------------------------------------------------------------------
# Primary verify endpoint
# ---------------------------------------------------------------------------


@router.post(
    "",
    response_model=VerifyResponse,
    description="Verify signed content and return a structured verdict.",
)
async def verify_text(
    verify_request: VerifyRequest,
    organization: Optional[dict] = Depends(get_optional_organization),
    db: Session = Depends(get_db),
):
    logger = structlog.get_logger(__name__)
    correlation_id = f"req-{uuid4().hex}"
    structlog.contextvars.bind_contextvars(correlation_id=correlation_id)
    start = time.perf_counter()

    # Task 5.0: Binary content guard
    if "\x00" in verify_request.text or any(ord(c) < 9 for c in verify_request.text):
        duration_ms = int((time.perf_counter() - start) * 1000)
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            correlation_id=correlation_id,
            code="ERR_BINARY_INPUT",
            message="Input contains null bytes or binary control characters.",
            hint="Submit plain text content. Binary or binary-encoded data is not supported.",
            duration_ms=duration_ms,
        )

    payload_bytes = len(verify_request.text.encode("utf-8"))
    vs_count = _count_variation_selectors(verify_request.text)
    try:
        wrapper_info = find_wrapper_info_bytes(verify_request.text)
    except Exception:  # pragma: no cover
        wrapper_info = None
    has_c2pa_wrapper = bool(wrapper_info)

    logger.info(
        "verify_received",
        payload_bytes=payload_bytes,
        variation_selectors=vs_count,
        has_c2pa_wrapper=has_c2pa_wrapper,
        has_auth_context=bool(organization),
    )
    if payload_bytes > MAX_VERIFY_BYTES:
        duration_ms = int((time.perf_counter() - start) * 1000)
        return _error_response(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            correlation_id=correlation_id,
            code="ERR_VERIFY_PAYLOAD_TOO_LARGE",
            message="Verification payload exceeds the 2 MB limit.",
            hint="Submit smaller payloads.",
            duration_ms=duration_ms,
        )

    (
        organization_id,
        organization_name,
        public_key,
        extracted_signer_id,
        _extracted_manifest_uuid,
        trust_anchor_public_key,
        trust_anchor_name,
    ) = await _resolve_org_context(
        organization=organization,
        text=verify_request.text,
        has_c2pa_wrapper=has_c2pa_wrapper,
        wrapper_info=wrapper_info,
        db=db,
        logger=logger,
    )

    embedded_public_key = _extract_embedded_c2pa_public_key(verify_request.text)
    embedded_trusted = await _is_embedded_c2pa_key_trusted(verify_request.text)

    logger.info(
        "verify_embedded_key_context",
        has_embedded_public_key=embedded_public_key is not None,
        embedded_trusted=embedded_trusted,
    )

    def public_key_resolver(signer_id: str):
        # TEAM_065: Support demo/user signers without requiring org auth.
        # TEAM_066: Also support org_encypher* signers (e.g., org_encypher_marketing) which use demo key.
        if signer_id == "org_demo" or signer_id.startswith("user_") or signer_id.startswith("org_encypher"):
            return _demo_public_key()
        if organization_id and signer_id == organization_id:
            return public_key
        if trust_anchor_public_key is not None and signer_id == extracted_signer_id:
            return trust_anchor_public_key
        if embedded_public_key is not None:
            return embedded_public_key
        return None

    try:
        is_valid, signer_id, manifest = UnicodeMetadata.verify_metadata(
            text=verify_request.text,
            public_key_resolver=public_key_resolver,
        )
        logger.info(
            "verify_unicode_metadata_result",
            is_valid=is_valid,
            signer_id=signer_id,
            manifest_type=type(manifest).__name__,
            manifest_keys=list(manifest.keys()) if isinstance(manifest, dict) else None,
        )
    except Exception as exc:
        logger.warning(
            "verify_unicode_metadata_exception",
            exception_type=type(exc).__name__,
            exception=str(exc),
            has_c2pa_wrapper=has_c2pa_wrapper,
        )
        # Fallback: Attempt C2PA wrapper-only verification.
        is_valid, signer_id, manifest = _try_c2pa_fallback(verify_request.text, public_key_resolver)

        logger.info(
            "verify_c2pa_fallback_result",
            is_valid=is_valid,
            signer_id=signer_id,
            manifest_type=type(manifest).__name__ if manifest is not None else None,
        )

        if not is_valid and not signer_id:
            # No C2PA wrapper found at all - return early
            duration_ms = int((time.perf_counter() - start) * 1000)
            verdict = VerifyVerdict(
                valid=False,
                tampered=False,
                reason_code="VERIFY_EXCEPTION",
                signer_id=None,
                signer_name=None,
                timestamp=None,
                details={
                    "manifest": {},
                    "duration_ms": duration_ms,
                    "payload_bytes": payload_bytes,
                    "exception": str(exc),
                },
            )
            return VerifyResponse(success=True, data=verdict, error=None, correlation_id=correlation_id, duration_ms=duration_ms)

    # Whitespace-normalization retry.
    if not is_valid and signer_id is not None and manifest is not None:
        _ws_valid, _ws_signer, _ws_manifest = _try_ws_normalized_retry(verify_request.text, manifest, public_key_resolver, logger)
        if _ws_valid:
            is_valid = True
            if _ws_signer:
                signer_id = _ws_signer
            if _ws_manifest:
                manifest = _ws_manifest

    # Fallback: no exception, but no signer_id extracted.
    if not signer_id:
        logger.info(
            "verify_missing_signer_id_primary",
            has_c2pa_wrapper=has_c2pa_wrapper,
            is_valid=is_valid,
        )
        _fb_valid, _fb_signer, _fb_manifest = _try_c2pa_fallback(verify_request.text, public_key_resolver)
        if _fb_signer:
            is_valid = _fb_valid
            signer_id = _fb_signer
            manifest = _fb_manifest

        logger.info(
            "verify_missing_signer_id_fallback_result",
            is_valid=is_valid,
            signer_id=signer_id,
            manifest_type=type(manifest).__name__ if manifest is not None else None,
        )

    # TEAM_156 / TEAM_170: ZW embedding fallback
    # TEAM_158 / TEAM_170: VS256 embedding fallback
    # Legacy-safe (base-6 ZWC) embedding fallback
    zw_org_id = None
    zw_document_id = None
    zw_uuid_str = None
    resolved_embeddings: list[EmbeddingDetail] = []
    resolved_c2pa_manifest: dict | None = None
    resolved_total_segments: int | None = None

    vs256_org_id = None
    vs256_document_id = None
    vs256_uuid_str = None

    legacy_safe_org_id = None
    legacy_safe_document_id = None

    if not signer_id or not is_valid:
        # ZWC fallback
        zw_org_id, zw_document_id, zw_uuid_str, zw_embeddings, zw_manifest, zw_total_segs, zw_valid = await _run_zw_fallback(
            verify_request.text, logger
        )
        if zw_valid and zw_org_id:
            signer_id = zw_org_id
            is_valid = True
            resolved_embeddings = zw_embeddings
            resolved_c2pa_manifest = zw_manifest
            resolved_total_segments = zw_total_segs
            manifest = {"segment_uuid": zw_uuid_str, "total_signatures": len(zw_embeddings)}

    if not signer_id or not is_valid:
        # VS256 fallback
        vs256_org_id, vs256_document_id, vs256_uuid_str, vs256_embeddings, vs256_manifest, vs256_total_segs, vs256_valid = await _run_vs256_fallback(
            verify_request.text, logger
        )
        if vs256_valid and vs256_org_id:
            signer_id = vs256_org_id
            is_valid = True
            resolved_embeddings = vs256_embeddings
            if vs256_manifest and not resolved_c2pa_manifest:
                resolved_c2pa_manifest = vs256_manifest
            if vs256_total_segs and not resolved_total_segments:
                resolved_total_segments = vs256_total_segs
            manifest = {"segment_uuid": vs256_uuid_str, "total_signatures": len(vs256_embeddings)}

    if not signer_id or not is_valid:
        # Legacy-safe fallback
        (
            legacy_safe_org_id,
            legacy_safe_document_id,
            ls_first_id,
            ls_embeddings,
            ls_manifest,
            ls_total_segs,
            ls_valid,
        ) = await _run_legacy_safe_fallback(verify_request.text, logger)
        if ls_valid and legacy_safe_org_id:
            signer_id = legacy_safe_org_id
            is_valid = True
            resolved_embeddings = ls_embeddings
            if ls_manifest and not resolved_c2pa_manifest:
                resolved_c2pa_manifest = ls_manifest
            if ls_total_segs and not resolved_total_segments:
                resolved_total_segments = ls_total_segs
            manifest = {"segment_uuid": ls_first_id, "total_signatures": len(ls_embeddings)}

    duration_ms = int((time.perf_counter() - start) * 1000)

    logger.info(
        "verify_verdict",
        is_valid=is_valid,
        signer_id=signer_id,
        payload_bytes=payload_bytes,
        duration_ms=duration_ms,
        has_c2pa_wrapper=has_c2pa_wrapper,
        variation_selectors=vs_count,
    )

    include_merkle = bool(verify_request.options and verify_request.options.include_merkle_proof and organization_id)

    verdict = _build_verdict(
        is_valid=is_valid,
        signer_id=signer_id,
        manifest=manifest,
        duration_ms=duration_ms,
        payload_bytes=payload_bytes,
        organization_id=organization_id,
        organization_name=organization_name,
        extracted_signer_id=extracted_signer_id,
        trust_anchor_name=trust_anchor_name,
        embedded_public_key=embedded_public_key,
        embedded_trusted=embedded_trusted,
        public_key_resolver=public_key_resolver,
        resolved_embeddings=resolved_embeddings,
        resolved_c2pa_manifest=resolved_c2pa_manifest,
        resolved_total_segments=resolved_total_segments,
        zw_org_id=zw_org_id,
        vs256_org_id=vs256_org_id,
        legacy_safe_org_id=legacy_safe_org_id,
        include_merkle=include_merkle,
    )

    return VerifyResponse(success=True, data=verdict, error=None, correlation_id=correlation_id, duration_ms=duration_ms)


# ---------------------------------------------------------------------------
# Advanced verify proxy
# ---------------------------------------------------------------------------


@router.post(
    "/advanced",
    summary="Advanced verification (proxy)",
    description=(
        "Proxy to enterprise API for advanced verification features: "
        "Merkle tamper localization, attribution, plagiarism detection, "
        "and fuzzy fingerprint search. Requires API key authentication."
    ),
)
async def verify_advanced_proxy(request: Request):
    """Forward /verify/advanced requests to the enterprise API.

    The enterprise API owns the Merkle tree, attribution, and plagiarism
    logic.  This proxy keeps the verification-service as the single
    entry-point for all ``/verify/*`` traffic so it can be scaled
    independently via Traefik.
    """
    logger = structlog.get_logger(__name__)
    body = await request.body()

    forward_headers = {}
    for key in ("authorization", "x-api-key", "content-type", "x-request-id"):
        value = request.headers.get(key)
        if value:
            forward_headers[key] = value

    enterprise_url = f"{settings.ENTERPRISE_API_URL}/api/v1/verify/advanced"
    logger.info("verify_advanced_proxy", target=enterprise_url)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(enterprise_url, content=body, headers=forward_headers)
        return JSONResponse(status_code=resp.status_code, content=resp.json())
    except httpx.RequestError as exc:
        logger.error("verify_advanced_proxy_error", error=str(exc))
        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "error": {
                    "code": "PROXY_ERROR",
                    "message": "Failed to reach enterprise API for advanced verification.",
                    "error_detail": str(exc),
                },
            },
        )


# ---------------------------------------------------------------------------
# Portal endpoint (GET by document_id)
# ---------------------------------------------------------------------------


@router.get("/{document_id}")
async def verify_by_document_id(
    document_id: str,
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Verify a document by its ID (for clickable verification links).

    Returns HTML or JSON depending on the Accept header.
    """
    accept = (request.headers.get("accept", "") if request else "") or ""

    result = db.execute(
        text("SELECT signed_text, title, organization_id FROM documents WHERE id = :doc_id"),
        {"doc_id": document_id},
    )
    row = result.fetchone()

    if not row:
        return _render_portal_not_found(document_id, accept)

    mapping = getattr(row, "_mapping", None)
    signed_text = mapping["signed_text"] if mapping else row[0]
    title = mapping["title"] if mapping else row[1]
    org_id = mapping["organization_id"] if mapping else row[2]

    try:
        is_valid, signer_id, manifest = UnicodeMetadata.verify_metadata(
            text=signed_text,
            public_key_resolver=lambda _: None,  # No key resolver for HTML portal
        )
    except Exception:
        is_valid = False
        signer_id = None
        manifest = None

    reason_code = "OK" if is_valid else "SIGNATURE_INVALID"
    if not signer_id:
        reason_code = "SIGNER_UNKNOWN"

    org_name = org_id or "Unknown"
    signer_name = signer_id or "Unknown"

    # TEAM_255: Fetch org context for whitelabel branding
    whitelabel = False
    org_display_name = ""
    if org_id:
        try:
            headers = {}
            if settings.INTERNAL_SERVICE_TOKEN:
                headers["X-Internal-Token"] = settings.INTERNAL_SERVICE_TOKEN
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(
                    f"{settings.AUTH_SERVICE_URL}/api/v1/organizations/internal/{org_id}/context",
                    headers=headers,
                )
            if resp.status_code == 200:
                ctx = resp.json()
                data = ctx.get("data", {}) if isinstance(ctx, dict) else {}
                features = data.get("features", {})
                whitelabel = bool(features.get("whitelabel"))
                org_display_name = data.get("display_name") or data.get("name") or ""
        except Exception:
            pass  # Fail-open: default to showing Encypher branding

    return _render_portal_result(
        document_id=document_id,
        title=title,
        org_name=org_name,
        signer_id=signer_id,
        signer_name=signer_name,
        reason_code=reason_code,
        is_valid=is_valid,
        manifest=manifest if isinstance(manifest, dict) else None,
        accept=accept,
        whitelabel=whitelabel,
        org_display_name=org_display_name,
    )


# ---------------------------------------------------------------------------
# Legacy endpoints (deprecated) - Tasks 4.1 and 4.2
# ---------------------------------------------------------------------------

_LEGACY_DEPRECATION_HINT = (
    "This endpoint is deprecated. Use POST /api/v1/verify with a VerifyRequest body instead. "
    "See https://docs.encypherai.com/api/verify for migration guide."
)


@router.post(
    "/signature",
    response_model=VerificationResponse,
    deprecated=True,
    summary="[DEPRECATED] Verify a signature",
    description=("**Deprecated.** Use `POST /api/v1/verify` instead. This endpoint will be removed in a future release."),
)
async def verify_signature(
    verify_data: SignatureVerify,
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Verify a signature (deprecated endpoint).

    - **content**: Original content
    - **signature**: Hex-encoded signature
    - **public_key_pem**: PEM-encoded public key

    Migrate to: ``POST /api/v1/verify``
    """
    try:
        result, processing_time = VerificationService.verify_signature_only(
            db=db,
            user_id=current_user["id"] if current_user else None,
            verify_data=verify_data,
            ip_address=x_forwarded_for,
            user_agent=user_agent,
        )

        return VerificationResponse(
            is_valid=result.is_valid,
            is_tampered=result.is_tampered,
            signature_valid=result.signature_valid,
            hash_valid=result.hash_valid,
            confidence_score=result.confidence_score,
            similarity_score=result.similarity_score,
            signer_id=result.signer_id,
            warnings=result.warnings,
            verification_time_ms=result.verification_time_ms,
            created_at=result.created_at,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Verification failed",
                "hint": _LEGACY_DEPRECATION_HINT,
            },
        )


@router.post(
    "/document",
    response_model=VerificationResponse,
    deprecated=True,
    summary="[DEPRECATED] Verify a document",
    description=("**Deprecated.** Use `POST /api/v1/verify` instead. This endpoint will be removed in a future release."),
)
async def verify_document(
    verify_data: DocumentVerify,
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """
    Complete document verification (deprecated endpoint).

    - **document_id**: Document ID from encoding service
    - **content**: Current content to verify

    Migrate to: ``POST /api/v1/verify``
    """
    try:
        result, processing_time = await VerificationService.verify_document_complete(
            db=db,
            user_id=current_user["id"] if current_user else None,
            verify_data=verify_data,
            ip_address=x_forwarded_for,
            user_agent=user_agent,
        )

        return VerificationResponse(
            is_valid=result.is_valid,
            is_tampered=result.is_tampered,
            signature_valid=result.signature_valid,
            hash_valid=result.hash_valid,
            confidence_score=result.confidence_score,
            similarity_score=result.similarity_score,
            signer_id=result.signer_id,
            warnings=result.warnings,
            verification_time_ms=result.verification_time_ms,
            created_at=result.created_at,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Verification failed",
                "hint": _LEGACY_DEPRECATION_HINT,
            },
        )


# ---------------------------------------------------------------------------
# History, stats, health
# ---------------------------------------------------------------------------


@router.get("/history/{document_id}", response_model=List[VerificationHistory])
async def get_verification_history(
    document_id: str,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Get verification history for a document (public endpoint)

    - **document_id**: Document ID
    - **limit**: Maximum number of results
    """
    history = VerificationService.get_verification_history(db, document_id, limit)
    return history


@router.get("/stats", response_model=VerificationStats)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: Optional[dict] = Depends(get_current_user),
):
    """Get verification statistics"""
    user_id = current_user["id"] if current_user else None
    stats = VerificationService.get_verification_stats(db, user_id)
    return VerificationStats(**stats)


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "verification-service"}
