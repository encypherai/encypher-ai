"""
C2PA Trust List for certificate chain validation.

Trusted CAs from https://github.com/c2pa-org/conformance-public/blob/main/trust-list/C2PA-TRUST-LIST.pem:
- Google (C2PA Root CA G3)
- SSL.com (C2PA RSA/ECC Root CA 2025)
- DigiCert (RSA4096/ECC P384 Root for C2PA G1)
- Adobe, Trufo, vivo, Xiaomi, Irdeto
"""
import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed448 import Ed448PublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.x509 import Certificate

logger = logging.getLogger(__name__)

C2PA_TRUST_LIST_URL = "https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TRUST-LIST.pem"

_trust_anchors: Optional[List[Certificate]] = None
_trust_anchors_pem: Optional[str] = None


async def fetch_trust_list() -> str:
    """Fetch latest C2PA trust list from GitHub."""
    import httpx
    async with httpx.AsyncClient() as client:
        resp = await client.get(C2PA_TRUST_LIST_URL, timeout=30.0)
        resp.raise_for_status()
        return resp.text


def _split_pem_chain(pem_data: str) -> List[str]:
    """Split a PEM file containing multiple certificates."""
    certs = []
    current = []
    in_cert = False
    for line in pem_data.split('\n'):
        if '-----BEGIN CERTIFICATE-----' in line:
            in_cert = True
            current = [line]
        elif '-----END CERTIFICATE-----' in line:
            current.append(line)
            certs.append('\n'.join(current))
            in_cert = False
        elif in_cert:
            current.append(line)
    return certs


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


def set_trust_anchors_pem(pem_data: str) -> int:
    """Set trust anchors from PEM data. Returns count loaded."""
    global _trust_anchors, _trust_anchors_pem
    _trust_anchors_pem = pem_data
    _trust_anchors = load_trust_anchors_from_pem(pem_data)
    logger.info(f"Loaded {len(_trust_anchors)} C2PA trust anchors")
    return len(_trust_anchors)


def get_trust_anchors() -> List[Certificate]:
    """Get loaded trust anchors."""
    return _trust_anchors or []


def get_trust_anchor_subjects() -> List[str]:
    """Get list of trusted CA subject names."""
    subjects = []
    for cert in get_trust_anchors():
        cn = cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
        if cn:
            subjects.append(cn[0].value)
    return subjects


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


def validate_certificate_chain(
    cert_pem: str,
    chain_pem: Optional[str] = None,
) -> Tuple[bool, Optional[str], Optional[Certificate]]:
    """
    Validate certificate chains to a C2PA trusted root.
    
    Returns: (is_valid, error_message, parsed_certificate)
    """
    try:
        cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
    except Exception as e:
        return False, f"Invalid certificate format: {e}", None

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
