"""
Cryptographic signing and verification utilities for Encypher.

This module provides functions for signing payloads and verifying signatures
using Ed25519 keys, as well as X.509 certificate validation and trust list
management for C2PA v2.2 compliance.

The C2PA COSE_Sign1 signing functions produce spec-compliant structures:
- CBOR tag 18 (COSE_Sign1_Tagged)
- Detached payload (nil at position [2])
- x5chain in unprotected headers (string key "x5chain")
- Multi-algorithm support: EdDSA, ES256, ES384, ES512, PS256
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Protocol, Union, cast

import cbor2
import requests
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa, utils
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import Certificate, NameOID, load_der_x509_certificate, load_pem_x509_certificate

from .logging_config import logger

# COSE algorithm identifiers (IANA COSE Algorithms registry)
COSE_ALG_EDDSA = -8
COSE_ALG_ES256 = -7
COSE_ALG_ES384 = -35
COSE_ALG_ES512 = -36
COSE_ALG_PS256 = -37

# COSE header keys
COSE_HDR_ALG = 1

# CBOR tag for COSE_Sign1
COSE_SIGN1_TAG = 18

# Legacy aliases (kept for backward compatibility with existing imports)
ALG_HEADER = COSE_HDR_ALG
ALG_EDDSA = COSE_ALG_EDDSA
X5CHAIN_HEADER = 33  # integer form -- only used by extract_certificates_from_cose for compat


class Signer(Protocol):
    """Protocol for abstract signing implementations (e.g., AWS KMS, Azure Key Vault)."""

    def sign(self, data: bytes) -> bytes: ...


SigningKey = Union[ed25519.Ed25519PrivateKey, ec.EllipticCurvePrivateKey, rsa.RSAPrivateKey, Signer]


# ---------------------------------------------------------------------------
# Low-level COSE helpers
# ---------------------------------------------------------------------------


def _encode_protected(headers: dict) -> bytes:
    return cbor2.dumps(headers)


def _sig_structure(protected_bstr: bytes, payload: bytes) -> bytes:
    """Build the COSE Sig_structure for signing/verification.

    ["Signature1", protected, external_aad, payload]
    """
    return cbor2.dumps(["Signature1", protected_bstr, b"", payload])


def _detect_algorithm(key_obj) -> int:
    """Detect COSE algorithm from a loaded private key."""
    if isinstance(key_obj, ed25519.Ed25519PrivateKey):
        return COSE_ALG_EDDSA
    elif isinstance(key_obj, ec.EllipticCurvePrivateKey):
        curve = key_obj.curve
        if isinstance(curve, ec.SECP384R1):
            return COSE_ALG_ES384
        elif isinstance(curve, ec.SECP521R1):
            return COSE_ALG_ES512
        else:
            return COSE_ALG_ES256
    elif isinstance(key_obj, rsa.RSAPrivateKey):
        return COSE_ALG_PS256
    else:
        raise ValueError(f"Unsupported key type: {type(key_obj).__name__}")


def _detect_algorithm_from_public_key(key_obj) -> int:
    """Detect COSE algorithm from a loaded public key."""
    if isinstance(key_obj, ed25519.Ed25519PublicKey):
        return COSE_ALG_EDDSA
    elif isinstance(key_obj, ec.EllipticCurvePublicKey):
        curve = key_obj.curve
        if isinstance(curve, ec.SECP384R1):
            return COSE_ALG_ES384
        elif isinstance(curve, ec.SECP521R1):
            return COSE_ALG_ES512
        else:
            return COSE_ALG_ES256
    elif isinstance(key_obj, rsa.RSAPublicKey):
        return COSE_ALG_PS256
    else:
        raise ValueError(f"Unsupported public key type: {type(key_obj).__name__}")


def _sign_bytes(key_obj, data: bytes, alg: int) -> bytes:
    """Sign data bytes using the appropriate algorithm."""
    if alg == COSE_ALG_EDDSA:
        return key_obj.sign(data)
    elif alg == COSE_ALG_ES256:
        der_sig = key_obj.sign(data, ec.ECDSA(hashes.SHA256()))
        r, s = utils.decode_dss_signature(der_sig)
        return r.to_bytes(32, "big") + s.to_bytes(32, "big")
    elif alg == COSE_ALG_ES384:
        der_sig = key_obj.sign(data, ec.ECDSA(hashes.SHA384()))
        r, s = utils.decode_dss_signature(der_sig)
        return r.to_bytes(48, "big") + s.to_bytes(48, "big")
    elif alg == COSE_ALG_ES512:
        der_sig = key_obj.sign(data, ec.ECDSA(hashes.SHA512()))
        r, s = utils.decode_dss_signature(der_sig)
        return r.to_bytes(66, "big") + s.to_bytes(66, "big")
    elif alg == COSE_ALG_PS256:
        return key_obj.sign(
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32),
            hashes.SHA256(),
        )
    else:
        raise ValueError(f"Unsupported COSE algorithm: {alg}")


def _verify_signature_bytes(public_key, data: bytes, signature: bytes, alg: int) -> None:
    """Verify a signature using the appropriate algorithm. Raises on failure."""
    if alg == COSE_ALG_EDDSA:
        public_key.verify(signature, data)
    elif alg in (COSE_ALG_ES256, COSE_ALG_ES384, COSE_ALG_ES512):
        if alg == COSE_ALG_ES256:
            coord_size, hash_alg = 32, hashes.SHA256()
        elif alg == COSE_ALG_ES384:
            coord_size, hash_alg = 48, hashes.SHA384()
        else:
            coord_size, hash_alg = 66, hashes.SHA512()
        r = int.from_bytes(signature[:coord_size], "big")
        s = int.from_bytes(signature[coord_size : coord_size * 2], "big")
        der_sig = utils.encode_dss_signature(r, s)
        public_key.verify(der_sig, data, ec.ECDSA(hash_alg))
    elif alg == COSE_ALG_PS256:
        public_key.verify(
            signature,
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=32),
            hashes.SHA256(),
        )
    else:
        raise ValueError(f"Unsupported COSE algorithm for verification: {alg}")


def _parse_cert_chain_pem(cert_chain_pem: str) -> list[bytes]:
    """Parse PEM certificate chain into list of DER-encoded certificates."""
    certs = []
    for block in cert_chain_pem.split("-----END CERTIFICATE-----"):
        block = block.strip()
        if "-----BEGIN CERTIFICATE-----" in block:
            pem = block + "\n-----END CERTIFICATE-----\n"
            cert = load_pem_x509_certificate(pem.encode("utf-8"))
            certs.append(cert.public_bytes(serialization.Encoding.DER))
    return certs


def _parse_sign1(cose_bytes: bytes) -> tuple[bytes, dict, Optional[bytes], bytes]:
    """Parse a COSE_Sign1 structure (tagged or untagged)."""
    decoded = cbor2.loads(cose_bytes)

    # Handle CBOR tag 18 (COSE_Sign1_Tagged)
    if isinstance(decoded, cbor2.CBORTag):
        if decoded.tag != COSE_SIGN1_TAG:
            raise ValueError(f"Unexpected CBOR tag: {decoded.tag}, expected {COSE_SIGN1_TAG}")
        arr = decoded.value
    elif isinstance(decoded, list):
        arr = decoded
    else:
        raise ValueError("Invalid COSE_Sign1 structure")

    if len(arr) != 4:
        raise ValueError("Invalid COSE_Sign1 structure: expected 4-element array")

    protected_bstr, unprotected, payload, signature = arr
    if not isinstance(protected_bstr, (bytes, bytearray)):
        raise ValueError("Protected header must be bstr")
    if not isinstance(unprotected, dict):
        raise ValueError("Unprotected header must be map")
    if not isinstance(payload, (bytes, bytearray)) and payload is not None:
        raise ValueError("Payload must be bstr or null")
    if not isinstance(signature, (bytes, bytearray)):
        raise ValueError("Signature must be bstr")
    return bytes(protected_bstr), unprotected, None if payload is None else bytes(payload), bytes(signature)


# ---------------------------------------------------------------------------
# Legacy signing functions (Ed25519-only, used by non-C2PA paths)
# ---------------------------------------------------------------------------


def sign_payload(private_key: SigningKey, payload_bytes: bytes) -> bytes:
    """
    Signs the payload bytes using the private key (Ed25519 or Signer).

    Args:
        private_key: The Ed25519 private key object or Signer implementation.
        payload_bytes: The canonical bytes of the payload to sign.

    Returns:
        The signature bytes.

    Raises:
        TypeError: If the provided key is invalid.
    """
    logger.debug(f"Attempting to sign payload ({len(payload_bytes)} bytes).")

    if hasattr(private_key, "sign") and callable(private_key.sign):
        try:
            signature = private_key.sign(payload_bytes)
            logger.info(f"Successfully signed payload (signature length: {len(signature)} bytes).")
            return cast(bytes, signature)
        except Exception as e:
            logger.error(f"Signing operation failed: {e}", exc_info=True)
            raise RuntimeError(f"Signing failed: {e}") from e

    raise TypeError("Signing requires a key with a .sign() method.")


def verify_signature(public_key: PublicKeyTypes, payload_bytes: bytes, signature: bytes) -> bool:
    """
    Verifies the signature against the payload using the public key (Ed25519).

    Args:
        public_key: The Ed25519 public key object.
        payload_bytes: The canonical bytes of the payload that was signed.
        signature: The signature bytes to verify.

    Returns:
        True if the signature is valid, False otherwise.

    Raises:
        TypeError: If the provided key is not an Ed25519 public key.
    """
    if not isinstance(public_key, ed25519.Ed25519PublicKey):
        logger.error(f"Verification aborted: Incorrect public key type provided ({type(public_key)}). Expected Ed25519PublicKey.")
        raise TypeError("Verification requires an Ed25519PublicKey instance.")

    logger.debug(f"Attempting to verify signature (len={len(signature)}) against payload (len={len(payload_bytes)}) using Ed25519 public key.")
    try:
        public_key.verify(signature, payload_bytes)
        logger.info("Signature verification successful.")
        return True
    except InvalidSignature:
        logger.warning("Signature verification failed: Invalid signature.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during verification: {e}", exc_info=True)
        raise RuntimeError(f"Verification process failed unexpectedly: {e}") from e


# ---------------------------------------------------------------------------
# C2PA COSE_Sign1 signing (spec-compliant)
# ---------------------------------------------------------------------------


def sign_c2pa_cose(
    private_key: SigningKey,
    payload_bytes: bytes,
    timestamp_authority_url: Optional[str] = None,
    certificates: Optional[list[Certificate]] = None,
    cert_chain_pem: Optional[str] = None,
) -> bytes:
    """Sign a C2PA payload producing a COSE_Sign1_Tagged structure.

    Produces a spec-compliant COSE_Sign1_Tagged (#6.18) with:
    - Detached payload (nil at position [2], payload in Sig_structure)
    - x5chain in unprotected headers (string key "x5chain")
    - Multi-algorithm support based on key type

    When neither certificates nor cert_chain_pem is provided, falls back to
    a legacy inline-payload mode (for backward compatibility with the
    non-certificate Ed25519 path used by basic/manifest formats).

    Args:
        private_key: Private key for signing (Ed25519, EC, RSA, or Signer).
        payload_bytes: The CBOR-encoded C2PA manifest/claim to be signed.
        timestamp_authority_url: Optional RFC 3161 TSA URL.
        certificates: Optional list of X.509 Certificate objects.
        cert_chain_pem: Optional PEM-encoded certificate chain string.

    Returns:
        CBOR-encoded COSE_Sign1_Tagged bytes (or untagged for legacy mode).
    """
    has_certs = bool(certificates) or bool(cert_chain_pem)

    if has_certs:
        return _sign_c2pa_cose_spec(private_key, payload_bytes, timestamp_authority_url, certificates, cert_chain_pem)
    else:
        return _sign_c2pa_cose_legacy(private_key, payload_bytes)


def _sign_c2pa_cose_spec(
    private_key: SigningKey,
    payload_bytes: bytes,
    timestamp_authority_url: Optional[str] = None,
    certificates: Optional[list[Certificate]] = None,
    cert_chain_pem: Optional[str] = None,
) -> bytes:
    """Spec-compliant C2PA COSE_Sign1_Tagged signing with certificate chain."""
    try:
        # Resolve key object
        if isinstance(private_key, str):
            key_obj = load_pem_private_key(private_key.encode("utf-8"), password=None)
        elif isinstance(private_key, (ed25519.Ed25519PrivateKey, ec.EllipticCurvePrivateKey, rsa.RSAPrivateKey)):
            key_obj = private_key
        else:
            # Signer protocol -- use Ed25519 algorithm by default
            key_obj = private_key

        alg = _detect_algorithm(key_obj)

        # Protected headers: algorithm
        protected_map = {COSE_HDR_ALG: alg}
        protected_bytes = _encode_protected(protected_map)

        # Build Sig_structure (payload is included here even though detached in the array)
        sig_structure = _sig_structure(protected_bytes, payload_bytes)

        # Sign
        if hasattr(key_obj, "sign") and callable(key_obj.sign):
            signature = _sign_bytes(key_obj, sig_structure, alg)
        else:
            raise ValueError(f"Key object has no sign method: {type(key_obj)}")

        # Build cert chain for unprotected headers
        cert_chain_der: list[bytes] = []
        if cert_chain_pem:
            cert_chain_der = _parse_cert_chain_pem(cert_chain_pem)
        elif certificates:
            cert_chain_der = [cert.public_bytes(serialization.Encoding.DER) for cert in certificates]

        # Unprotected headers: x5chain (string key per c2pa-rs convention)
        unprotected: dict = {}
        if cert_chain_der:
            unprotected["x5chain"] = cert_chain_der if len(cert_chain_der) > 1 else cert_chain_der[0]

        # COSE_Sign1 = [protected, unprotected, nil (detached payload), signature]
        cose_array = [protected_bytes, unprotected, None, signature]

        # Wrap in CBOR tag 18 (COSE_Sign1_Tagged)
        encoded = cbor2.dumps(cbor2.CBORTag(COSE_SIGN1_TAG, cose_array))

        logger.info(f"Successfully created COSE_Sign1 signed message (length: {len(encoded)} bytes).")
        return encoded

    except Exception as e:
        logger.error(f"COSE signing operation failed: {e}", exc_info=True)
        raise RuntimeError(f"COSE signing failed: {e}") from e


def _sign_c2pa_cose_legacy(
    private_key: SigningKey,
    payload_bytes: bytes,
) -> bytes:
    """Legacy COSE signing: inline payload, no tag, no certs.

    Used by the basic/manifest/cbor_manifest formats where no certificate
    chain is available. Produces an untagged COSE_Sign1 with Ed25519.
    """
    try:
        protected_header = {COSE_HDR_ALG: COSE_ALG_EDDSA}
        protected_bstr = _encode_protected(protected_header)
        to_sign = _sig_structure(protected_bstr, payload_bytes)

        if hasattr(private_key, "sign") and callable(private_key.sign):
            signature = private_key.sign(to_sign)
        else:
            raise TypeError("Legacy signing requires a key with a .sign() method")

        # Untagged, inline payload (legacy format)
        encoded = cbor2.dumps([protected_bstr, {}, payload_bytes, cast(bytes, signature)])

        logger.info(f"Successfully created COSE_Sign1 signed message (length: {len(encoded)} bytes).")
        return encoded
    except Exception as e:
        logger.error(f"COSE signing operation failed: {e}", exc_info=True)
        raise RuntimeError(f"COSE signing failed: {e}") from e


# ---------------------------------------------------------------------------
# C2PA COSE_Sign1 verification
# ---------------------------------------------------------------------------


def verify_c2pa_cose(
    public_key: Optional[ed25519.Ed25519PublicKey],
    cose_bytes: bytes,
    payload_override: Optional[bytes] = None,
) -> bytes:
    """Verify a COSE_Sign1 signature and return the payload.

    Handles both tagged (spec-compliant) and untagged (legacy) structures,
    and both detached and inline payloads.

    Args:
        public_key: Ed25519 public key for verification (legacy path).
            If None, the public key is extracted from the embedded x5chain.
        cose_bytes: The CBOR-encoded COSE_Sign1 message.
        payload_override: For detached payloads, the external payload bytes.

    Returns:
        The payload bytes if the signature is valid.

    Raises:
        InvalidSignature: If the signature is invalid.
        ValueError: If the message structure is invalid.
    """
    logger.debug(f"Attempting to verify COSE_Sign1 message ({len(cose_bytes)} bytes).")
    protected_bstr, unprotected, payload, signature = _parse_sign1(cose_bytes)

    # Determine the actual payload (inline or detached)
    actual_payload = payload or payload_override
    if actual_payload is None:
        raise ValueError("COSE_Sign1 has detached payload but no payload_override provided.")

    # Parse protected headers
    protected_map = cbor2.loads(protected_bstr)
    alg = protected_map.get(COSE_HDR_ALG)

    # Determine the public key to use
    effective_key = public_key
    if effective_key is None:
        # Extract from x5chain
        x5chain = unprotected.get("x5chain") or unprotected.get(X5CHAIN_HEADER)
        if x5chain is None:
            raise ValueError("No public key provided and no x5chain in unprotected headers")
        ee_cert_der = x5chain[0] if isinstance(x5chain, list) else x5chain
        cert = load_der_x509_certificate(ee_cert_der)
        effective_key = cert.public_key()

    # Determine algorithm
    if alg is None:
        alg = _detect_algorithm_from_public_key(effective_key)

    # Build Sig_structure and verify
    to_verify = _sig_structure(protected_bstr, actual_payload)
    try:
        _verify_signature_bytes(effective_key, to_verify, signature, alg)
        logger.info("COSE_Sign1 signature verification successful.")
        return bytes(actual_payload)
    except InvalidSignature:
        raise InvalidSignature("COSE signature verification failed.") from None


def extract_payload_from_cose_sign1(cose_bytes: bytes) -> Optional[bytes]:
    """Extract the payload from a COSE_Sign1 structure without verifying.

    Handles both tagged and untagged, inline and detached payloads.

    Args:
        cose_bytes: The CBOR-encoded COSE_Sign1 message.

    Returns:
        The payload bytes if present, None for detached payloads.
    """
    try:
        logger.debug(f"Attempting to extract payload from COSE_Sign1 message ({len(cose_bytes)} bytes).")
        _protected_bstr, _unprotected, payload, _signature = _parse_sign1(cose_bytes)
        if payload is None:
            logger.debug("COSE_Sign1 message has detached payload (nil)")
            return None
        payload = bytes(payload)
        logger.debug(f"Successfully extracted payload ({len(payload)} bytes) from COSE_Sign1 message.")
        return payload
    except Exception as e:
        logger.warning(f"Error extracting payload from COSE_Sign1: {e}")
        return None


def extract_certificates_from_cose(cose_bytes: bytes) -> list[Certificate]:
    """Extract X.509 certificates from a COSE_Sign1 message.

    Checks both string "x5chain" and integer 33 keys for compatibility.

    Args:
        cose_bytes: The CBOR-encoded COSE_Sign1 message.

    Returns:
        List of X.509 certificates found in the COSE message.

    Raises:
        ValueError: If no certificates are found.
    """
    _protected_bstr, unprotected, _payload, _signature = _parse_sign1(cose_bytes)

    # Check both string and integer keys
    x5chain = unprotected.get("x5chain") or unprotected.get(X5CHAIN_HEADER)

    if not x5chain:
        raise ValueError("No X.509 certificates found in COSE message.")

    # Normalize to list
    if isinstance(x5chain, (bytes, bytearray)):
        x5chain = [x5chain]

    certificates = []
    for cert_bytes in x5chain:
        try:
            cert = x509.load_der_x509_certificate(cert_bytes)
            certificates.append(cert)
        except Exception as e:
            logger.warning(f"Failed to parse certificate from COSE message: {e}")

    if not certificates:
        raise ValueError("Failed to extract any valid certificates from COSE message.")

    return certificates


# ---------------------------------------------------------------------------
# Timestamp functions
# ---------------------------------------------------------------------------


def add_timestamp_to_cose(cose_bytes: bytes, tsa_url: str) -> bytes:
    """
    Request a timestamp from an RFC 3161 Time-Stamp Authority and add it to a COSE message.

    Args:
        cose_bytes: The CBOR-encoded COSE_Sign1 message.
        tsa_url: URL of the Time-Stamp Authority.

    Returns:
        Updated COSE_Sign1 message with the timestamp in the unprotected header.
    """
    try:
        protected_bstr, unprotected, payload, signature = _parse_sign1(cose_bytes)

        digest = hashes.Hash(hashes.SHA256())
        digest.update(cose_bytes)
        message_hash = digest.finalize()

        timestamp_request = create_timestamp_request(message_hash)
        timestamp_token = request_timestamp(timestamp_request, tsa_url)

        TIMESTAMP_HEADER_PARAM = 8
        unprotected[TIMESTAMP_HEADER_PARAM] = timestamp_token
        logger.info("Added RFC 3161 timestamp to COSE message")

        # Rebuild with same structure (tagged or untagged based on original)
        cose_array = [protected_bstr, unprotected, payload, signature]
        return cbor2.dumps(cbor2.CBORTag(COSE_SIGN1_TAG, cose_array))
    except Exception as e:
        logger.error(f"Failed to add timestamp to COSE message: {e}", exc_info=True)
        logger.warning("Returning original COSE message without timestamp")
        return cose_bytes


def create_timestamp_request(message_hash: bytes) -> bytes:
    """
    Create an RFC 3161 timestamp request for the given message hash.

    Note: This is a simplified implementation. In production, use a proper
    ASN.1 library for RFC 3161 TimeStampReq construction.
    """
    logger.warning("Using simplified timestamp request implementation. Consider using a proper RFC 3161 library.")
    return message_hash


def request_timestamp(timestamp_request: bytes, tsa_url: str) -> bytes:
    """Send a timestamp request to an RFC 3161 TSA and return the response."""
    try:
        headers = {
            "Content-Type": "application/timestamp-query",
            "Accept": "application/timestamp-reply",
        }

        logger.debug(f"Sending timestamp request to {tsa_url}")
        response = requests.post(tsa_url, data=timestamp_request, headers=headers, timeout=10)

        if response.status_code != 200:
            logger.error(f"Timestamp request failed with status code {response.status_code}")
            raise RuntimeError(f"Timestamp request failed: HTTP {response.status_code}")

        logger.info("Received timestamp response successfully")
        return bytes(response.content)
    except requests.RequestException as e:
        logger.error(f"Timestamp request failed: {e}", exc_info=True)
        raise RuntimeError(f"Timestamp request failed: {e}") from e


# --- X.509 Certificate Validation for C2PA ---


class CertificateValidationError(Exception):
    """Exception raised for certificate validation errors."""

    pass


class TrustStore:
    """Manages a collection of trusted root certificates for C2PA validation."""

    def __init__(self, trust_store_path: Optional[str] = None):
        self.trusted_roots: set[Certificate] = set()
        self.trust_store_path = trust_store_path or self._get_default_trust_store_path()
        self._load_trust_store()

    def _get_default_trust_store_path(self) -> str:
        return os.path.join(str(Path.home()), ".encypher", "trust_store")

    def _load_trust_store(self) -> None:
        if not os.path.exists(self.trust_store_path):
            logger.warning(f"Trust store path does not exist: {self.trust_store_path}")
            return

        for file_path in Path(self.trust_store_path).glob("*.pem"):
            try:
                with open(file_path, "rb") as f:
                    cert_data = f.read()
                    cert = x509.load_pem_x509_certificate(cert_data)
                    self.trusted_roots.add(cert)
                    logger.debug(f"Loaded trusted root certificate: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to load certificate from {file_path}: {e}")

    def add_certificate(self, cert: Certificate) -> None:
        self.trusted_roots.add(cert)

    def remove_certificate(self, cert: Certificate) -> None:
        if cert in self.trusted_roots:
            self.trusted_roots.remove(cert)

    def is_trusted_root(self, cert: Certificate) -> bool:
        return cert in self.trusted_roots

    def save_certificate(self, cert: Certificate, name: Optional[str] = None) -> str:
        if not os.path.exists(self.trust_store_path):
            os.makedirs(self.trust_store_path, exist_ok=True)

        if name is None:
            try:
                common_name = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
                common_name_str = str(common_name)
                serial_str = str(cert.serial_number)
                name = f"{common_name_str}_{serial_str}"
            except (IndexError, ValueError):
                serial_str = str(cert.serial_number)
                name = f"cert_{serial_str}"

        name = "".join(c for c in name if c.isalnum() or c in "_-")
        file_path = os.path.join(self.trust_store_path, f"{name}.pem")

        with open(file_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        logger.info(f"Saved certificate to trust store: {file_path}")
        return file_path


def validate_certificate_chain(cert_chain: list[Certificate], trust_store: TrustStore) -> bool:
    """Validate a certificate chain against a trust store."""
    if not cert_chain:
        raise CertificateValidationError("Empty certificate chain")

    for i in range(len(cert_chain) - 1):
        issuer = cert_chain[i + 1]
        subject = cert_chain[i]
        if subject.issuer != issuer.subject:
            raise CertificateValidationError(f"Certificate chain broken: {subject.subject} is not issued by {issuer.subject}")

    root_cert = cert_chain[-1]
    if not trust_store.is_trusted_root(root_cert):
        if root_cert.issuer == root_cert.subject:
            logger.warning(f"Self-signed root certificate not in trust store: {root_cert.subject}")
            return False
        else:
            raise CertificateValidationError("Root certificate is not self-signed and not in trust store")

    for i in range(len(cert_chain) - 1):
        issuer = cert_chain[i + 1]
        subject = cert_chain[i]

        try:
            now = datetime.now(timezone.utc)
            if now < subject.not_valid_before or now > subject.not_valid_after:
                raise CertificateValidationError(f"Certificate {subject.subject} has expired or is not yet valid")

            issuer_public_key = issuer.public_key()
            if isinstance(issuer_public_key, rsa.RSAPublicKey):
                if subject.signature_hash_algorithm is None:
                    raise CertificateValidationError("Certificate has no signature hash algorithm")
                issuer_public_key.verify(
                    subject.signature,
                    subject.tbs_certificate_bytes,
                    padding.PKCS1v15(),
                    subject.signature_hash_algorithm,
                )
            elif isinstance(issuer_public_key, ec.EllipticCurvePublicKey):
                if subject.signature_hash_algorithm is None:
                    raise CertificateValidationError("Certificate has no signature hash algorithm")
                issuer_public_key.verify(
                    subject.signature,
                    subject.tbs_certificate_bytes,
                    ec.ECDSA(subject.signature_hash_algorithm),
                )
            elif isinstance(issuer_public_key, ed25519.Ed25519PublicKey):
                issuer_public_key.verify(subject.signature, subject.tbs_certificate_bytes)
            else:
                raise CertificateValidationError(f"Unsupported public key type: {type(issuer_public_key)}")

        except InvalidSignature:
            raise CertificateValidationError(f"Invalid signature on certificate: {subject.subject}") from None
        except CertificateValidationError:
            raise
        except Exception as e:
            raise CertificateValidationError(f"Certificate validation error: {e}") from e

    return True
