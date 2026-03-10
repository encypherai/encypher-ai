"""
C2PA Trust List for certificate chain validation.

Trusted CAs from https://github.com/c2pa-org/conformance-public/blob/main/trust-list/C2PA-TRUST-LIST.pem:
- Google (C2PA Root CA G3)
- SSL.com (C2PA RSA/ECC Root CA 2025)
- DigiCert (RSA4096/ECC P384 Root for C2PA G1)
- Adobe, Trufo, vivo, Xiaomi, Irdeto
"""

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional, Tuple

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.asymmetric.ed448 import Ed448PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.x509 import Certificate

logger = logging.getLogger(__name__)

C2PA_TRUST_LIST_URL = "https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TRUST-LIST.pem"
C2PA_TSA_TRUST_LIST_URL = "https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TSA-TRUST-LIST.pem"
C2PA_CLAIM_SIGNING_EKU_OID = "1.3.6.1.4.1.62558.2.1"

_trust_anchors: Optional[List[Certificate]] = None
_trust_anchors_pem: Optional[str] = None
_trust_list_fingerprint: Optional[str] = None
_trust_list_loaded_at: Optional[datetime] = None
_trust_list_source: Optional[str] = None

_tsa_trust_anchors: Optional[List[Certificate]] = None
_tsa_trust_anchors_pem: Optional[str] = None
_tsa_trust_list_fingerprint: Optional[str] = None
_tsa_trust_list_loaded_at: Optional[datetime] = None
_tsa_trust_list_source: Optional[str] = None

_revoked_serial_numbers: set[str] = set()
_revoked_fingerprints: set[str] = set()


async def fetch_trust_list(url: str = C2PA_TRUST_LIST_URL) -> str:
    """Fetch latest C2PA trust list from GitHub."""
    import httpx

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=30.0)
        resp.raise_for_status()
        return resp.text


def compute_trust_list_sha256(pem_data: str) -> str:
    """Return SHA-256 fingerprint for trust list PEM payload."""
    return hashlib.sha256(pem_data.encode("utf-8")).hexdigest()


def _split_pem_chain(pem_data: str) -> List[str]:
    """Split a PEM file containing multiple certificates."""
    certs = []
    current = []
    in_cert = False
    for line in pem_data.split("\n"):
        if "-----BEGIN CERTIFICATE-----" in line:
            in_cert = True
            current = [line]
        elif "-----END CERTIFICATE-----" in line:
            current.append(line)
            certs.append("\n".join(current))
            in_cert = False
        elif in_cert:
            current.append(line)
    return certs


def _normalize_hex_tokens(values: Optional[Iterable[str]]) -> set[str]:
    if values is None:
        return set()
    normalized: set[str] = set()
    for value in values:
        token = value.strip().lower()
        if token:
            normalized.add(token)
    return normalized


def load_trust_anchors_from_pem(pem_data: str) -> List[Certificate]:
    """Parse certificates from PEM data."""
    certs = []
    for pem_block in _split_pem_chain(pem_data):
        try:
            cert = x509.load_pem_x509_certificate(pem_block.encode(), default_backend())
            certs.append(cert)
        except Exception as e:
            logger.warning(f"Failed to parse certificate: {e}")
    return certs


def set_trust_anchors_pem(
    pem_data: str,
    *,
    source: Optional[str] = None,
    expected_sha256: Optional[str] = None,
) -> int:
    """Set trust anchors from PEM data. Returns count loaded."""
    global _trust_anchors, _trust_anchors_pem, _trust_list_fingerprint, _trust_list_loaded_at, _trust_list_source

    fingerprint = compute_trust_list_sha256(pem_data)
    if expected_sha256 and fingerprint.lower() != expected_sha256.lower():
        raise ValueError("C2PA trust list fingerprint mismatch")

    _trust_anchors_pem = pem_data
    _trust_anchors = load_trust_anchors_from_pem(pem_data)
    _trust_list_fingerprint = fingerprint
    _trust_list_loaded_at = datetime.now(timezone.utc)
    _trust_list_source = source
    logger.info(f"Loaded {len(_trust_anchors)} C2PA trust anchors")
    return len(_trust_anchors)


def set_tsa_trust_anchors_pem(
    pem_data: str,
    *,
    source: Optional[str] = None,
    expected_sha256: Optional[str] = None,
) -> int:
    """Set TSA trust anchors from PEM data. Returns count loaded."""
    global _tsa_trust_anchors, _tsa_trust_anchors_pem, _tsa_trust_list_fingerprint, _tsa_trust_list_loaded_at, _tsa_trust_list_source

    fingerprint = compute_trust_list_sha256(pem_data)
    if expected_sha256 and fingerprint.lower() != expected_sha256.lower():
        raise ValueError("C2PA TSA trust list fingerprint mismatch")

    _tsa_trust_anchors_pem = pem_data
    _tsa_trust_anchors = load_trust_anchors_from_pem(pem_data)
    _tsa_trust_list_fingerprint = fingerprint
    _tsa_trust_list_loaded_at = datetime.now(timezone.utc)
    _tsa_trust_list_source = source
    logger.info(f"Loaded {len(_tsa_trust_anchors)} C2PA TSA trust anchors")
    return len(_tsa_trust_anchors)


def set_revocation_denylist(*, serial_numbers: set[str], fingerprints: set[str]) -> None:
    """Set internal revocation denylist for leaf certificates."""
    global _revoked_serial_numbers, _revoked_fingerprints
    _revoked_serial_numbers = _normalize_hex_tokens(serial_numbers)
    _revoked_fingerprints = _normalize_hex_tokens(fingerprints)


def get_trust_anchors() -> List[Certificate]:
    """Get loaded trust anchors."""
    return _trust_anchors or []


def get_tsa_trust_anchors() -> List[Certificate]:
    """Get loaded TSA trust anchors."""
    return _tsa_trust_anchors or []


def get_trust_anchor_subjects() -> List[str]:
    """Get list of trusted CA subject names."""
    subjects = []
    for cert in get_trust_anchors():
        cn = cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
        if cn:
            value = cn[0].value
            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="ignore")
            subjects.append(str(value))
    return subjects


def get_tsa_trust_anchor_subjects() -> List[str]:
    """Get list of trusted TSA CA subject names."""
    subjects = []
    for cert in get_tsa_trust_anchors():
        cn = cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
        if cn:
            value = cn[0].value
            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="ignore")
            subjects.append(str(value))
    return subjects


def get_trust_list_metadata() -> dict[str, Optional[str]]:
    """Return metadata about the loaded trust list."""
    loaded_at = _trust_list_loaded_at.isoformat() if _trust_list_loaded_at else None
    return {
        "fingerprint": _trust_list_fingerprint,
        "loaded_at": loaded_at,
        "source": _trust_list_source,
        "count": str(len(_trust_anchors)) if _trust_anchors is not None else None,
    }


def get_tsa_trust_list_metadata() -> dict[str, Optional[str]]:
    """Return metadata about the loaded TSA trust list."""
    loaded_at = _tsa_trust_list_loaded_at.isoformat() if _tsa_trust_list_loaded_at else None
    return {
        "fingerprint": _tsa_trust_list_fingerprint,
        "loaded_at": loaded_at,
        "source": _tsa_trust_list_source,
        "count": str(len(_tsa_trust_anchors)) if _tsa_trust_anchors is not None else None,
    }


def get_revocation_denylist_metadata() -> dict[str, str]:
    """Return metadata for internal revocation denylist."""
    return {
        "serial_count": str(len(_revoked_serial_numbers)),
        "fingerprint_count": str(len(_revoked_fingerprints)),
    }


def trust_list_needs_refresh(max_age_hours: int) -> bool:
    """Return True when trust list should be refreshed based on age."""
    if max_age_hours <= 0:
        return False
    if _trust_list_loaded_at is None:
        return True
    return datetime.now(timezone.utc) - _trust_list_loaded_at >= timedelta(hours=max_age_hours)


def tsa_trust_list_needs_refresh(max_age_hours: int) -> bool:
    """Return True when TSA trust list should be refreshed based on age."""
    if max_age_hours <= 0:
        return False
    if _tsa_trust_list_loaded_at is None:
        return True
    return datetime.now(timezone.utc) - _tsa_trust_list_loaded_at >= timedelta(hours=max_age_hours)


async def refresh_trust_list(*, url: str, expected_sha256: Optional[str]) -> int:
    """Fetch and load trust list from URL with optional SHA-256 pinning."""
    pem_data = await fetch_trust_list(url)
    return set_trust_anchors_pem(pem_data, source=url, expected_sha256=expected_sha256)


async def refresh_tsa_trust_list(*, url: str, expected_sha256: Optional[str]) -> int:
    """Fetch and load TSA trust list from URL with optional SHA-256 pinning."""
    pem_data = await fetch_trust_list(url)
    return set_tsa_trust_anchors_pem(pem_data, source=url, expected_sha256=expected_sha256)


def _is_certificate_valid_now(cert: Certificate) -> bool:
    now = datetime.now(timezone.utc)
    not_before = getattr(cert, "not_valid_before_utc", None) or cert.not_valid_before
    not_after = getattr(cert, "not_valid_after_utc", None) or cert.not_valid_after
    if not_before.tzinfo is None:
        not_before = not_before.replace(tzinfo=timezone.utc)
    if not_after.tzinfo is None:
        not_after = not_after.replace(tzinfo=timezone.utc)
    return not_before <= now <= not_after


def _is_ca_certificate(cert: Certificate) -> bool:
    try:
        bc = cert.extensions.get_extension_for_class(x509.BasicConstraints).value
    except x509.ExtensionNotFound:
        return False
    return bool(getattr(bc, "ca", False))


def _verify_cert_signature(*, subject: Certificate, issuer: Certificate) -> bool:
    issuer_pk = issuer.public_key()
    try:
        if isinstance(issuer_pk, RSAPublicKey):
            algo = subject.signature_hash_algorithm
            if algo is None:
                return False
            issuer_pk.verify(
                subject.signature,
                subject.tbs_certificate_bytes,
                padding.PKCS1v15(),
                algo,
            )
            return True
        if isinstance(issuer_pk, EllipticCurvePublicKey):
            algo = subject.signature_hash_algorithm
            if algo is None:
                return False
            issuer_pk.verify(
                subject.signature,
                subject.tbs_certificate_bytes,
                ec.ECDSA(algo),
            )
            return True
        if isinstance(issuer_pk, (Ed25519PublicKey, Ed448PublicKey)):
            issuer_pk.verify(subject.signature, subject.tbs_certificate_bytes)
            return True
    except Exception:
        return False
    return False


def _fingerprint_sha256(cert: Certificate) -> bytes:
    return cert.fingerprint(hashes.SHA256())


def _certificate_has_required_eku(cert: Certificate, required_eku_oids: list[str]) -> bool:
    if not required_eku_oids:
        return True
    try:
        eku = cert.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value
    except x509.ExtensionNotFound:
        return False
    cert_eku_oids = {oid.dotted_string for oid in eku}
    return any(required_oid in cert_eku_oids for required_oid in required_eku_oids)


def _is_revoked_by_internal_denylist(cert: Certificate) -> bool:
    serial_hex = format(cert.serial_number, "x").lower()
    if serial_hex in _revoked_serial_numbers:
        return True

    fingerprint_hex = cert.fingerprint(hashes.SHA256()).hex().lower()
    return fingerprint_hex in _revoked_fingerprints


def validate_certificate_chain(
    cert_pem: str,
    chain_pem: Optional[str] = None,
    *,
    required_eku_oids: Optional[list[str]] = None,
) -> Tuple[bool, Optional[str], Optional[Certificate]]:
    """
    Validate certificate chains to a C2PA trusted root.

    Returns: (is_valid, error_message, parsed_certificate)
    """
    try:
        cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
    except Exception as e:
        return False, f"Invalid certificate format: {e}", None

    effective_eku_oids = required_eku_oids if required_eku_oids is not None else [C2PA_CLAIM_SIGNING_EKU_OID]
    if not _certificate_has_required_eku(cert, effective_eku_oids):
        return False, "Certificate missing required EKU", None

    if _is_revoked_by_internal_denylist(cert):
        return False, "Certificate revoked by internal denylist", None

    chain_certs = []
    if chain_pem:
        chain_certs = load_trust_anchors_from_pem(chain_pem)

    trust_anchors = get_trust_anchors()
    if not trust_anchors:
        return False, "C2PA trust list not loaded", None

    candidates = chain_certs + trust_anchors
    trust_fps = {_fingerprint_sha256(a) for a in trust_anchors}

    current = cert
    seen: set[bytes] = set()

    for _ in range(20):
        fp = _fingerprint_sha256(current)
        if fp in seen:
            return False, "Certificate chain loop detected", None
        seen.add(fp)

        if not _is_certificate_valid_now(current):
            return False, "Certificate is expired or not yet valid", None

        if fp in trust_fps:
            if current.subject == current.issuer and not _verify_cert_signature(subject=current, issuer=current):
                return False, "Trust anchor certificate signature invalid", None
            if not _is_ca_certificate(current):
                return False, "Trust anchor is not a CA certificate", None
            return True, None, cert

        issuer_subject = current.issuer
        issuer_cert = next((c for c in candidates if c.subject == issuer_subject), None)
        if issuer_cert is None:
            return False, f"Cannot find issuer: {issuer_subject}", None

        if not _is_ca_certificate(issuer_cert):
            return False, "Issuer certificate is not a CA", None

        if not _verify_cert_signature(subject=current, issuer=issuer_cert):
            return False, "Certificate signature verification failed", None

        current = issuer_cert

    return False, "Certificate chain too long", None
