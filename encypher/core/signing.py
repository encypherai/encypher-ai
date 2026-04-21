"""
Cryptographic signing and verification utilities for Encypher.

This module provides functions for signing payloads and verifying signatures
using Ed25519 keys, as well as X.509 certificate validation and trust list
management for C2PA v2.2 compliance.
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
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from cryptography.x509 import Certificate, NameOID

from .logging_config import logger

ALG_HEADER = 1
ALG_EDDSA = -8
ALG_ES256 = -7
ALG_ES384 = -35
ALG_ES512 = -36
ALG_PS256 = -37
X5CHAIN_HEADER = 33

# Map COSE algorithm IDs to EC curve / hash pairs for verification
_EC_ALG_MAP: dict[int, tuple[type[ec.EllipticCurve], type[hashes.HashAlgorithm]]] = {
    ALG_ES256: (ec.SECP256R1, hashes.SHA256),
    ALG_ES384: (ec.SECP384R1, hashes.SHA384),
    ALG_ES512: (ec.SECP521R1, hashes.SHA512),
}


class Signer(Protocol):
    """Protocol for abstract signing implementations (e.g., AWS KMS, Azure Key Vault)."""

    def sign(self, data: bytes) -> bytes: ...


SigningKey = Union[ed25519.Ed25519PrivateKey, ec.EllipticCurvePrivateKey, rsa.RSAPrivateKey, Signer]


def _cose_alg_for_key(key: SigningKey) -> int:
    """Return the COSE algorithm identifier for a private key."""
    if isinstance(key, ed25519.Ed25519PrivateKey):
        return ALG_EDDSA
    if isinstance(key, ec.EllipticCurvePrivateKey):
        curve = key.curve
        if isinstance(curve, ec.SECP256R1):
            return ALG_ES256
        if isinstance(curve, ec.SECP384R1):
            return ALG_ES384
        if isinstance(curve, ec.SECP521R1):
            return ALG_ES512
        raise ValueError(f"Unsupported EC curve: {curve.name}")
    if isinstance(key, rsa.RSAPrivateKey):
        return ALG_PS256
    # Signer protocol - assume EdDSA (caller should override if needed)
    return ALG_EDDSA


def _sign_with_key(key: SigningKey, data: bytes) -> bytes:
    """Sign data using the correct algorithm for the key type."""
    if isinstance(key, ed25519.Ed25519PrivateKey):
        return key.sign(data)
    if isinstance(key, ec.EllipticCurvePrivateKey):
        curve = key.curve
        if isinstance(curve, ec.SECP256R1):
            hash_alg: hashes.HashAlgorithm = hashes.SHA256()
        elif isinstance(curve, ec.SECP384R1):
            hash_alg = hashes.SHA384()
        elif isinstance(curve, ec.SECP521R1):
            hash_alg = hashes.SHA512()
        else:
            raise ValueError(f"Unsupported EC curve: {curve.name}")
        return key.sign(data, ec.ECDSA(hash_alg))
    if isinstance(key, rsa.RSAPrivateKey):
        return key.sign(
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
    # Signer protocol (e.g. AWS KMS) - handles algorithm internally
    return key.sign(data)


def _verify_with_public_key(pub: PublicKeyTypes, signature: bytes, data: bytes, alg: int) -> None:
    """Verify a signature using the correct algorithm for the key/alg pair.

    Raises InvalidSignature on failure.
    """
    if isinstance(pub, ed25519.Ed25519PublicKey):
        pub.verify(signature, data)
        return
    if isinstance(pub, ec.EllipticCurvePublicKey):
        ec_entry = _EC_ALG_MAP.get(alg)
        if ec_entry is None:
            raise ValueError(f"COSE alg {alg} is not an EC algorithm")
        _, hash_cls = ec_entry
        pub.verify(signature, data, ec.ECDSA(hash_cls()))
        return
    if isinstance(pub, rsa.RSAPublicKey):
        pub.verify(
            signature,
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return
    raise ValueError(f"Unsupported public key type: {type(pub)}")


def _encode_protected(headers: dict) -> bytes:
    return cbor2.dumps(headers)


def _sig_structure(protected_bstr: bytes, payload: bytes) -> bytes:
    return cbor2.dumps(["Signature1", protected_bstr, b"", payload])


def _build_sign1(protected_bstr: bytes, unprotected: dict, payload: bytes, signature: bytes) -> bytes:
    return cbor2.dumps([protected_bstr, unprotected, payload, signature])


def _parse_sign1(cose_bytes: bytes) -> tuple[bytes, dict, Optional[bytes], bytes]:
    arr = cbor2.loads(cose_bytes)
    # COSE_Sign1 may be wrapped in CBOR tag 18 per RFC 9052 §4.1.
    if isinstance(arr, cbor2.CBORTag) and arr.tag == 18:
        arr = arr.value
    if not isinstance(arr, list) or len(arr) != 4:
        raise ValueError("Invalid COSE_Sign1 structure")
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


def sign_payload(private_key: SigningKey, payload_bytes: bytes) -> bytes:
    """
    Signs the payload bytes using the private key.

    Supports Ed25519, EC (P-256/P-384/P-521), RSA, and Signer protocol.

    Args:
        private_key: The private key object or Signer implementation.
        payload_bytes: The canonical bytes of the payload to sign.

    Returns:
        The signature bytes.

    Raises:
        TypeError: If the provided key is invalid.
    """
    logger.debug(f"Attempting to sign payload ({len(payload_bytes)} bytes).")

    try:
        signature = _sign_with_key(private_key, payload_bytes)
        logger.info(f"Successfully signed payload (signature length: {len(signature)} bytes).")
        return cast(bytes, signature)
    except Exception as e:
        logger.error(f"Signing operation failed: {e}", exc_info=True)
        raise RuntimeError(f"Signing failed: {e}") from e


def verify_signature(public_key: PublicKeyTypes, payload_bytes: bytes, signature: bytes) -> bool:
    """
    Verifies the signature against the payload using the public key.

    Supports Ed25519, EC (P-256/P-384/P-521), and RSA public keys.

    Args:
        public_key: The public key object (Ed25519, EC, or RSA).
        payload_bytes: The canonical bytes of the payload that was signed.
        signature: The signature bytes to verify.

    Returns:
        True if the signature is valid, False otherwise.

    Raises:
        TypeError: If the provided key is not a supported public key type.
    """
    supported_types = (ed25519.Ed25519PublicKey, ec.EllipticCurvePublicKey, rsa.RSAPublicKey)
    if not isinstance(public_key, supported_types):
        logger.error(f"Verification aborted: Unsupported public key type ({type(public_key)}).")
        raise TypeError(f"Verification requires Ed25519, EC, or RSA public key, got {type(public_key).__name__}.")

    key_name = type(public_key).__name__
    logger.debug(f"Attempting to verify signature (len={len(signature)}) against payload (len={len(payload_bytes)}) using {key_name}.")
    try:
        if isinstance(public_key, ed25519.Ed25519PublicKey):
            public_key.verify(signature, payload_bytes)
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            curve = public_key.curve
            if isinstance(curve, ec.SECP256R1):
                hash_alg: hashes.HashAlgorithm = hashes.SHA256()
            elif isinstance(curve, ec.SECP384R1):
                hash_alg = hashes.SHA384()
            elif isinstance(curve, ec.SECP521R1):
                hash_alg = hashes.SHA512()
            else:
                raise ValueError(f"Unsupported EC curve: {curve.name}")
            public_key.verify(signature, payload_bytes, ec.ECDSA(hash_alg))
        elif isinstance(public_key, rsa.RSAPublicKey):
            public_key.verify(
                signature,
                payload_bytes,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
        logger.info("Signature verification successful.")
        return True
    except InvalidSignature:
        logger.warning("Signature verification failed: Invalid signature.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during verification: {e}", exc_info=True)
        raise RuntimeError(f"Verification process failed unexpectedly: {e}") from e


def sign_c2pa_cose(
    private_key: SigningKey,
    payload_bytes: bytes,
    timestamp_authority_url: Optional[str] = None,
    certificates: Optional[list[Certificate]] = None,
) -> bytes:
    """
    Signs a C2PA payload using a COSE_Sign1 structure with optional timestamp and certificates.

    This function creates a standard COSE_Sign1 object, which encapsulates the
    payload, signing algorithm, and signature in a single CBOR structure, as
    required for C2PA claim signatures. It can optionally include a timestamp from
    an RFC 3161 Time-Stamp Authority and a certificate chain.

    Args:
        private_key: The signing key (Ed25519, EC, RSA, or Signer protocol).
        payload_bytes: The CBOR-encoded C2PA manifest to be signed.
        timestamp_authority_url: Optional URL of an RFC 3161 Time-Stamp Authority.
        certificates: Optional list of X.509 certificates to include in the signature.

    Returns:
        The COSE_Sign1 structure as a CBOR-encoded byte string.

    Raises:
        RuntimeError: If the COSE signing process fails.
    """
    logger.debug(f"Attempting to sign payload ({len(payload_bytes)} bytes) with COSE_Sign1 structure.")
    try:
        alg = _cose_alg_for_key(private_key)
        protected_header = {ALG_HEADER: alg}
        unprotected_header = {}

        # Add certificates if provided
        if certificates and len(certificates) > 0:
            x5chain = [cert.public_bytes(serialization.Encoding.DER) for cert in certificates]
            unprotected_header[X5CHAIN_HEADER] = x5chain
            logger.debug(f"Added {len(x5chain)} certificates to COSE unprotected header")

        protected_bstr = _encode_protected(protected_header)
        to_sign = _sig_structure(protected_bstr, payload_bytes)

        signature = _sign_with_key(private_key, to_sign)

        encoded_cose = _build_sign1(protected_bstr, unprotected_header, payload_bytes, cast(bytes, signature))

        # If timestamp authority URL is provided, request a timestamp
        if timestamp_authority_url:
            encoded_cose = add_timestamp_to_cose(encoded_cose, timestamp_authority_url)

        logger.info(f"Successfully created COSE_Sign1 signed message (length: {len(encoded_cose)} bytes).")
        return bytes(encoded_cose)
    except Exception as e:
        logger.error(f"COSE signing operation failed: {e}", exc_info=True)
        raise RuntimeError(f"COSE signing failed: {e}") from e


def add_timestamp_to_cose(cose_bytes: bytes, tsa_url: str) -> bytes:
    """
    Request a timestamp from an RFC 3161 Time-Stamp Authority and add it to a COSE message.

    Args:
        cose_bytes: The CBOR-encoded COSE_Sign1 message.
        tsa_url: URL of the Time-Stamp Authority.

    Returns:
        Updated COSE_Sign1 message with the timestamp in the unprotected header.

    Raises:
        RuntimeError: If the timestamp request fails.
    """
    try:
        protected_bstr, unprotected, payload, signature = _parse_sign1(cose_bytes)
        if payload is None:
            raise ValueError("Message is not a COSE_Sign1 structure.")

        # Calculate hash of the COSE message for the timestamp request
        digest = hashes.Hash(hashes.SHA256())
        digest.update(cose_bytes)
        message_hash = digest.finalize()

        # Prepare the timestamp request
        timestamp_request = create_timestamp_request(message_hash)

        # Send the request to the TSA
        timestamp_token = request_timestamp(timestamp_request, tsa_url)

        # Add the timestamp to the unprotected header
        TIMESTAMP_HEADER_PARAM = 8
        unprotected[TIMESTAMP_HEADER_PARAM] = timestamp_token
        logger.info("Added RFC 3161 timestamp to COSE message")
        return _build_sign1(protected_bstr, unprotected, payload, signature)
    except Exception as e:
        logger.error(f"Failed to add timestamp to COSE message: {e}", exc_info=True)
        # Return the original message if timestamping fails
        logger.warning("Returning original COSE message without timestamp")
        return cose_bytes


def create_timestamp_request(message_hash: bytes) -> bytes:
    """
    Create an RFC 3161 timestamp request for the given message hash.

    Args:
        message_hash: The SHA-256 hash of the message to timestamp.

    Returns:
        DER-encoded timestamp request.
    """
    # This is a simplified implementation of an RFC 3161 timestamp request
    # In a production environment, you would use a library like pyasn1 or python-tsp
    # to create a proper ASN.1 TimeStampReq structure

    # For now, we'll create a basic ASN.1 structure manually
    # This is a placeholder implementation and should be replaced with a proper library

    # ASN.1 structure for a basic TimeStampReq (simplified):
    # TimeStampReq ::= SEQUENCE {
    #    version           INTEGER { v1(1) },
    #    messageImprint    MessageImprint,
    #    reqPolicy         OPTIONAL,
    #    nonce             OPTIONAL,
    #    certReq           BOOLEAN DEFAULT FALSE,
    #    extensions        OPTIONAL
    # }

    # MessageImprint ::= SEQUENCE {
    #    hashAlgorithm    AlgorithmIdentifier,
    #    hashedMessage    OCTET STRING
    # }

    # In a real implementation, use a proper ASN.1 library
    logger.warning("Using simplified timestamp request implementation. Consider using a proper RFC 3161 library.")

    # For demonstration purposes, we'll return a placeholder
    # In a real implementation, this would be a proper DER-encoded TimeStampReq
    return message_hash


def request_timestamp(timestamp_request: bytes, tsa_url: str) -> bytes:
    """
    Send a timestamp request to an RFC 3161 Time-Stamp Authority and return the response.

    Args:
        timestamp_request: DER-encoded timestamp request.
        tsa_url: URL of the Time-Stamp Authority.

    Returns:
        DER-encoded timestamp response token.

    Raises:
        RuntimeError: If the timestamp request fails.
    """
    try:
        headers = {
            "Content-Type": "application/timestamp-query",
            "Accept": "application/timestamp-reply",
        }

        logger.debug(f"Sending timestamp request to {tsa_url}")
        response = requests.post(tsa_url, data=timestamp_request, headers=headers, timeout=10)  # 10-second timeout

        if response.status_code != 200:
            logger.error(f"Timestamp request failed with status code {response.status_code}")
            raise RuntimeError(f"Timestamp request failed: HTTP {response.status_code}")

        # In a real implementation, parse and validate the timestamp response
        # For now, we'll just return the raw response content
        logger.info("Received timestamp response successfully")
        return bytes(response.content)
        return bytes(response.content)
    except requests.RequestException as e:
        logger.error(f"Timestamp request failed: {e}", exc_info=True)
        raise RuntimeError(f"Timestamp request failed: {e}") from e


def extract_payload_from_cose_sign1(cose_bytes: bytes) -> Optional[bytes]:
    """
    Extracts the payload from a COSE_Sign1 structure without verifying the signature.

    This function is used for extracting the CBOR payload from a COSE_Sign1 structure
    during metadata extraction, where verification may be performed separately.

    Args:
        cose_bytes: The CBOR-encoded COSE_Sign1 message.

    Returns:
        The payload bytes if extraction is successful, None otherwise.

    Raises:
        ValueError: If the message is not a valid COSE_Sign1 structure.
    """
    try:
        logger.debug(f"Attempting to extract payload from COSE_Sign1 message ({len(cose_bytes)} bytes).")
        _protected_bstr, _unprotected, payload, _signature = _parse_sign1(cose_bytes)
        if payload is None:
            logger.warning("COSE_Sign1 message has no payload")
            return None
        payload = bytes(payload)
        logger.debug(f"Successfully extracted payload ({len(payload)} bytes) from COSE_Sign1 message.")
        return payload
    except Exception as e:
        logger.warning(f"Error extracting payload from COSE_Sign1: {e}")
        return None


_SUPPORTED_COSE_ALGS = {ALG_EDDSA, ALG_ES256, ALG_ES384, ALG_ES512, ALG_PS256}


def verify_c2pa_cose(
    public_key: Optional[PublicKeyTypes],
    cose_bytes: bytes,
    payload_override: Optional[bytes] = None,
) -> bytes:
    """
    Verifies a COSE_Sign1 signature and returns the payload if valid.

    Args:
        public_key: The public key for verification (Ed25519, EC, or RSA).
            If None, the public key is extracted from the x5chain certificates
            embedded in the COSE unprotected header.
        cose_bytes: The CBOR-encoded COSE_Sign1 message.
        payload_override: If provided, use this as the payload for signature
            verification instead of the embedded payload. Used when the COSE
            structure has a detached payload (payload=None in the COSE envelope)
            but the actual payload is known from context (e.g. reconstructed
            from the JUMBF manifest store).

    Returns:
        The original payload bytes if the signature is valid.

    Raises:
        InvalidSignature: If the signature is invalid.
        ValueError: If the message is not a valid COSE_Sign1 structure.
    """
    logger.debug(f"Attempting to verify COSE_Sign1 message ({len(cose_bytes)} bytes).")
    protected_bstr, unprotected, payload, signature = _parse_sign1(cose_bytes)
    if payload is None and payload_override is None:
        raise ValueError("Message is not a COSE_Sign1 structure.")
    effective_payload: bytes = payload_override if payload_override is not None else (payload or b"")
    if not effective_payload:
        raise ValueError("No payload available for verification")
    protected_map = cbor2.loads(protected_bstr)
    alg = protected_map.get(ALG_HEADER)
    if alg not in _SUPPORTED_COSE_ALGS:
        raise ValueError(f"Unsupported or missing alg in protected header: {alg}")
    to_verify = _sig_structure(protected_bstr, effective_payload)

    # Resolve public key: use provided key or extract from x5chain
    verify_key: PublicKeyTypes
    if public_key is not None:
        verify_key = public_key
    else:
        x5chain = unprotected.get(X5CHAIN_HEADER)
        if not x5chain:
            raise ValueError("No public key provided and no x5chain in COSE message")
        # Per RFC 9360, x5chain is a single CBOR bstr for one certificate
        # or a CBOR array of bstr for a chain. Extract the leaf (first) cert.
        leaf_der = x5chain if isinstance(x5chain, bytes) else x5chain[0]
        cert = x509.load_der_x509_certificate(leaf_der)
        verify_key = cert.public_key()

    try:
        _verify_with_public_key(verify_key, signature, to_verify, alg)
        logger.info("COSE_Sign1 signature verification successful.")
        return effective_payload
    except InvalidSignature:
        raise InvalidSignature("COSE signature verification failed.") from None


# --- X.509 Certificate Validation for C2PA ---


class CertificateValidationError(Exception):
    """Exception raised for certificate validation errors."""

    pass


class TrustStore:
    """Manages a collection of trusted root certificates for C2PA validation."""

    def __init__(self, trust_store_path: Optional[str] = None):
        """
        Initialize the trust store with certificates from a directory.

        Args:
            trust_store_path: Path to a directory containing trusted root certificates in PEM format.
                             If None, uses the default trust store path.
        """
        self.trusted_roots: set[Certificate] = set()
        self.trust_store_path = trust_store_path or self._get_default_trust_store_path()
        self._load_trust_store()

    def _get_default_trust_store_path(self) -> str:
        """Returns the default path for the trust store."""
        # Default to a directory in the user's home directory
        return os.path.join(str(Path.home()), ".encypher", "trust_store")

    def _load_trust_store(self) -> None:
        """Load all certificates from the trust store directory."""
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
        """Add a certificate to the trust store."""
        self.trusted_roots.add(cert)

    def remove_certificate(self, cert: Certificate) -> None:
        """Remove a certificate from the trust store."""
        if cert in self.trusted_roots:
            self.trusted_roots.remove(cert)

    def is_trusted_root(self, cert: Certificate) -> bool:
        """Check if a certificate is in the trust store."""
        return cert in self.trusted_roots

    def save_certificate(self, cert: Certificate, name: Optional[str] = None) -> str:
        """Save a certificate to the trust store directory."""
        if not os.path.exists(self.trust_store_path):
            os.makedirs(self.trust_store_path, exist_ok=True)

        # Generate a filename based on the certificate's subject if not provided
        if name is None:
            try:
                common_name = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
                # Ensure both common_name and serial_number are strings
                common_name_str = str(common_name)
                serial_str = str(cert.serial_number)
                name = f"{common_name_str}_{serial_str}"
            except (IndexError, ValueError):
                serial_str = str(cert.serial_number)
                name = f"cert_{serial_str}"

        # Ensure the filename is valid
        name = "".join(c for c in name if c.isalnum() or c in "_-")
        file_path = os.path.join(self.trust_store_path, f"{name}.pem")

        # Save the certificate
        with open(file_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        logger.info(f"Saved certificate to trust store: {file_path}")
        return file_path


def validate_certificate_chain(cert_chain: list[Certificate], trust_store: TrustStore) -> bool:
    """
    Validate a certificate chain against a trust store.

    Args:
        cert_chain: List of certificates, ordered from leaf to root.
        trust_store: TrustStore instance containing trusted root certificates.

    Returns:
        True if the chain is valid and trusted, False otherwise.

    Raises:
        CertificateValidationError: If there's an issue with the certificate chain.
    """
    if not cert_chain:
        raise CertificateValidationError("Empty certificate chain")

    # Check if the chain is properly ordered
    for i in range(len(cert_chain) - 1):
        issuer = cert_chain[i + 1]
        subject = cert_chain[i]

        # Verify issuer-subject relationship
        if subject.issuer != issuer.subject:
            raise CertificateValidationError(f"Certificate chain broken: {subject.subject} is not issued by {issuer.subject}")

    # Check if the root certificate is trusted
    root_cert = cert_chain[-1]
    if not trust_store.is_trusted_root(root_cert):
        # If self-signed but not in trust store
        if root_cert.issuer == root_cert.subject:
            logger.warning(f"Self-signed root certificate not in trust store: {root_cert.subject}")
            return False
        else:
            raise CertificateValidationError("Root certificate is not self-signed and not in trust store")

    # Verify each certificate in the chain
    for i in range(len(cert_chain) - 1):
        issuer = cert_chain[i + 1]
        subject = cert_chain[i]

        try:
            # Check validity period
            now = datetime.now(timezone.utc)
            if now < subject.not_valid_before or now > subject.not_valid_after:
                raise CertificateValidationError(f"Certificate {subject.subject} has expired or is not yet valid")

            # Verify signature
            issuer_public_key = issuer.public_key()
            if isinstance(issuer_public_key, rsa.RSAPublicKey):
                # Ensure we have a valid hash algorithm
                if subject.signature_hash_algorithm is None:
                    raise CertificateValidationError("Certificate has no signature hash algorithm")

                # Ensure we have a valid hash algorithm
                if subject.signature_hash_algorithm is None:
                    raise CertificateValidationError("Certificate has no signature hash algorithm")

                issuer_public_key.verify(
                    subject.signature,
                    subject.tbs_certificate_bytes,
                    padding.PKCS1v15(),
                    subject.signature_hash_algorithm,
                )
            else:
                # Handle other key types if needed
                raise CertificateValidationError(f"Unsupported public key type: {type(issuer_public_key)}")

        except InvalidSignature:
            raise CertificateValidationError(f"Invalid signature on certificate: {subject.subject}") from None
        except Exception as e:
            raise CertificateValidationError(f"Certificate validation error: {e}") from e

    return True


def extract_certificates_from_cose(cose_bytes: bytes) -> list[Certificate]:
    """
    Extract X.509 certificates from a COSE_Sign1 message.

    Args:
        cose_bytes: The CBOR-encoded COSE_Sign1 message.

    Returns:
        List of X.509 certificates found in the COSE message.

    Raises:
        ValueError: If the message is not a valid COSE_Sign1 structure or contains no certificates.
    """
    protected_bstr, unprotected, payload, _signature = _parse_sign1(cose_bytes)

    # Extract certificates from the unprotected header (x5chain).
    # The payload may be None for detached-payload COSE_Sign1 structures
    # (required by C2PA spec); certificates live in the unprotected header
    # regardless of whether the payload is inline or detached.
    certificates = []
    x5chain = unprotected.get(X5CHAIN_HEADER)

    if not x5chain:
        raise ValueError("No X.509 certificates found in COSE message.")

    # Per RFC 9360, x5chain is a single CBOR bstr for one certificate
    # or a CBOR array of bstr for a chain. Normalise to a list.
    if isinstance(x5chain, bytes):
        x5chain = [x5chain]

    for cert_bytes in x5chain:
        try:
            cert = x509.load_der_x509_certificate(cert_bytes)
            certificates.append(cert)
        except Exception as e:
            logger.warning(f"Failed to parse certificate from COSE message: {e}")

    if not certificates:
        raise ValueError("Failed to extract any valid certificates from COSE message.")

    return certificates
