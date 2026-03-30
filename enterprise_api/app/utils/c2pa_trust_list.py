"""
C2PA Trust List for certificate chain validation.

Trust anchors sourced from https://github.com/contentauth/verify-site/tree/main/static/trust
(the same trust store used by https://contentcredentials.org/verify):
- anchors.pem: root CA trust anchors (Google, SSL.com, DigiCert, Adobe, Truepic,
  Leica, Microsoft, Canon, Nikon, Sony, Samsung, Fujifilm, and others)
- allowed.pem: explicitly trusted end-entity certificates
- store.cfg: accepted EKU OIDs
"""

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Iterable, List, Optional, Tuple

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives.asymmetric.ed448 import Ed448PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509 import Certificate, ocsp as x509_ocsp

logger = logging.getLogger(__name__)

C2PA_TRUST_LIST_URL = "https://raw.githubusercontent.com/contentauth/verify-site/main/static/trust/anchors.pem"
C2PA_TSA_TRUST_LIST_URL = "https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TSA-TRUST-LIST.pem"
C2PA_ALLOWED_LIST_URL = "https://raw.githubusercontent.com/contentauth/verify-site/main/static/trust/allowed.pem"
C2PA_CLAIM_SIGNING_EKU_OID = "1.3.6.1.4.1.62558.2.1"

# EKU OIDs accepted by the C2PA ecosystem (from verify-site store.cfg)
C2PA_TRUST_CONFIG = "\n".join(
    [
        "1.3.6.1.5.5.7.3.4",  # id-kp-emailProtection
        "1.3.6.1.5.5.7.3.36",  # id-kp-documentSigning
        "1.3.6.1.5.5.7.3.8",  # id-kp-timeStamping
        "1.3.6.1.5.5.7.3.9",  # id-kp-OCSPSigning
        "1.3.6.1.4.1.311.76.59.1.9",  # MS C2PA Signing
        "1.3.6.1.4.1.62558.2.1",  # c2pa-claim_signing OID
    ]
)

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

_allowed_list_pem: Optional[str] = None
_allowed_list_loaded_at: Optional[datetime] = None

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


def get_trust_anchors_pem() -> Optional[str]:
    """Get loaded trust anchors as a PEM string (for passing to c2pa-python)."""
    return _trust_anchors_pem


def set_allowed_list_pem(pem_data: str) -> int:
    """Set the allowed end-entity certificate list. Returns count loaded."""
    global _allowed_list_pem, _allowed_list_loaded_at
    _allowed_list_pem = pem_data
    _allowed_list_loaded_at = datetime.now(timezone.utc)
    count = pem_data.count("-----BEGIN CERTIFICATE-----")
    logger.info("Loaded %d C2PA allowed end-entity certificates", count)
    return count


def get_allowed_list_pem() -> Optional[str]:
    """Get loaded allowed list as a PEM string (for passing to c2pa-python)."""
    return _allowed_list_pem


async def refresh_allowed_list(*, url: str) -> int:
    """Fetch and load the allowed end-entity certificate list."""
    pem_data = await fetch_trust_list(url)
    return set_allowed_list_pem(pem_data)


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


async def check_ocsp_status(
    cert: Certificate,
    issuer_cert: Certificate,
) -> Tuple[str, Optional[str]]:
    """Check certificate revocation status via OCSP.

    Extracts the OCSP responder URL from the certificate's Authority Information
    Access (AIA) extension, builds an OCSP request, sends it via HTTP POST, and
    parses the response.

    Args:
        cert: The leaf certificate to check.
        issuer_cert: The issuer certificate (required to build the OCSP request).

    Returns:
        A (status_code, explanation) tuple where status_code is one of:
          - ``signingCredential.ocsp.notRevoked``
          - ``signingCredential.ocsp.revoked``
          - ``signingCredential.ocsp.inaccessible``
          - ``signingCredential.ocsp.skipped``
    """
    import httpx

    # Locate the OCSP responder URL from the AIA extension.
    ocsp_url: Optional[str] = None
    try:
        aia = cert.extensions.get_extension_for_class(x509.AuthorityInformationAccess).value
        for access_desc in aia:
            if access_desc.access_method == x509.AuthorityInformationAccessOID.OCSP:
                ocsp_url = access_desc.access_location.value
                break
    except x509.ExtensionNotFound:
        return (
            "signingCredential.ocsp.skipped",
            "Certificate has no Authority Information Access extension",
        )
    except Exception as exc:
        logger.debug("Failed to read AIA extension: %s", exc)
        return (
            "signingCredential.ocsp.skipped",
            f"Could not read AIA extension: {exc}",
        )

    if not ocsp_url:
        return (
            "signingCredential.ocsp.skipped",
            "No OCSP responder URL found in AIA extension",
        )

    # Build the OCSP request.
    try:
        builder = x509_ocsp.OCSPRequestBuilder()
        builder = builder.add_certificate(cert, issuer_cert, hashes.SHA256())
        ocsp_request = builder.build()
        request_bytes = ocsp_request.public_bytes(Encoding.DER)
    except Exception as exc:
        logger.debug("Failed to build OCSP request: %s", exc)
        return (
            "signingCredential.ocsp.inaccessible",
            f"Could not build OCSP request: {exc}",
        )

    # Send the request to the OCSP responder.
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                ocsp_url,
                content=request_bytes,
                headers={"Content-Type": "application/ocsp-request"},
                timeout=10.0,
            )
            resp.raise_for_status()
            response_bytes = resp.content
    except httpx.TimeoutException as exc:
        logger.debug("OCSP request timed out for %s: %s", ocsp_url, exc)
        return (
            "signingCredential.ocsp.inaccessible",
            f"OCSP responder timed out: {ocsp_url}",
        )
    except Exception as exc:
        logger.debug("OCSP request failed for %s: %s", ocsp_url, exc)
        return (
            "signingCredential.ocsp.inaccessible",
            f"OCSP responder unreachable: {ocsp_url}",
        )

    # Parse and evaluate the OCSP response.
    try:
        ocsp_response = x509_ocsp.load_der_ocsp_response(response_bytes)
    except Exception as exc:
        logger.debug("Failed to parse OCSP response: %s", exc)
        return (
            "signingCredential.ocsp.inaccessible",
            f"Could not parse OCSP response: {exc}",
        )

    if ocsp_response.response_status != x509_ocsp.OCSPResponseStatus.SUCCESSFUL:
        return (
            "signingCredential.ocsp.inaccessible",
            f"OCSP responder returned non-successful status: {ocsp_response.response_status.name}",
        )

    cert_status = ocsp_response.certificate_status
    if cert_status == x509_ocsp.OCSPCertStatus.GOOD:
        return ("signingCredential.ocsp.notRevoked", None)

    if cert_status == x509_ocsp.OCSPCertStatus.REVOKED:
        revocation_time = ocsp_response.revocation_time
        revocation_reason = ocsp_response.revocation_reason
        explanation = "Certificate revoked"
        if revocation_time:
            explanation += f" at {revocation_time.isoformat()}"
        if revocation_reason:
            explanation += f" (reason: {revocation_reason.name})"
        return ("signingCredential.ocsp.revoked", explanation)

    # OCSPCertStatus.UNKNOWN
    return (
        "signingCredential.ocsp.inaccessible",
        "OCSP responder returned unknown status for certificate",
    )


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
    is_valid, msgs, parsed_cert = validate_certificate_for_upload(cert_pem, chain_pem, required_eku_oids=required_eku_oids)
    if not is_valid:
        # Hard failure -- extract first error message
        return False, msgs[0] if msgs else "Unknown validation error", None
    # Upload validation passed; check for trust warnings (strict mode)
    if msgs:
        return False, msgs[0], parsed_cert
    return True, None, parsed_cert


def validate_certificate_for_upload(
    cert_pem: str,
    chain_pem: Optional[str] = None,
    *,
    required_eku_oids: Optional[list[str]] = None,
) -> Tuple[bool, Optional[list[str]], Optional[Certificate]]:
    """
    Validate a certificate for upload (structural + optional trust check).

    Hard failures (return is_valid=False):
    - Invalid PEM format
    - Missing required EKU
    - Revoked by internal denylist
    - Expired or not yet valid
    - Broken chain signatures

    Soft warnings (return is_valid=True with warnings list):
    - Does not chain to a C2PA trust list root

    Returns: (is_valid, warnings_or_error, parsed_certificate)
      - On hard failure: (False, [error_message], None)
      - On success: (True, [warnings] or None, parsed_certificate)
    """
    try:
        cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
    except Exception as e:
        return False, [f"Invalid certificate format: {e}"], None

    effective_eku_oids = required_eku_oids if required_eku_oids is not None else [C2PA_CLAIM_SIGNING_EKU_OID]
    if not _certificate_has_required_eku(cert, effective_eku_oids):
        return False, ["Certificate missing required EKU"], None

    if _is_revoked_by_internal_denylist(cert):
        return False, ["Certificate revoked by internal denylist"], None

    if not _is_certificate_valid_now(cert):
        return False, ["Certificate is expired or not yet valid"], None

    chain_certs: list[Certificate] = []
    if chain_pem:
        chain_certs = load_trust_anchors_from_pem(chain_pem)

    # Validate chain signatures (structural integrity)
    # Include trust anchors as candidates so chains can walk up to a trusted root
    trust_anchors = get_trust_anchors() or []
    current = cert
    seen: set[bytes] = set()
    candidates = list(chain_certs) + list(trust_anchors)

    for _ in range(20):
        fp = _fingerprint_sha256(current)
        if fp in seen:
            break  # Reached a self-signed root or loop -- stop walking
        seen.add(fp)

        # Self-signed root -- verify its own signature and stop
        if current.subject == current.issuer:
            if not _verify_cert_signature(subject=current, issuer=current):
                return False, ["Chain root certificate signature invalid"], None
            break

        issuer_subject = current.issuer
        issuer_cert = next((c for c in candidates if c.subject == issuer_subject), None)
        if issuer_cert is None:
            break  # Can't walk further -- trust check below will handle this

        if not _is_ca_certificate(issuer_cert):
            return False, ["Issuer certificate is not a CA"], None

        if not _verify_cert_signature(subject=current, issuer=issuer_cert):
            return False, ["Certificate signature verification failed"], None

        if not _is_certificate_valid_now(issuer_cert):
            return False, ["Intermediate certificate is expired or not yet valid"], None

        current = issuer_cert

    # Trust list check (soft -- produces warning, not failure)
    if trust_anchors:
        trust_fps = {_fingerprint_sha256(a) for a in trust_anchors}
        all_chain_fps = seen
        # Also check chain certs provided by the user
        for c in chain_certs:
            all_chain_fps.add(_fingerprint_sha256(c))

        trusted = bool(all_chain_fps & trust_fps)
        if not trusted:
            root_cn = current.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
            root_name = root_cn[0].value if root_cn else str(current.subject)
            warnings = [
                f"Certificate does not chain to a C2PA-trusted root CA. "
                f"Chain root: {root_name}. Signatures made with this certificate "
                f"may not be verifiable by C2PA validators. "
                f"See GET /byok/trusted-cas for the list of trusted CAs."
            ]
            return True, warnings, cert
    else:
        return True, ["C2PA trust list not loaded; trust status unknown"], cert

    return True, None, cert
