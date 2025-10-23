"""
Cryptographic signing and verification utilities for EncypherAI.

This module provides functions for signing payloads and verifying signatures
using Ed25519 keys, as well as X.509 certificate validation and trust list
management for C2PA v2.2 compliance.
"""

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Set, cast

import requests
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
from cryptography.x509 import Certificate, NameOID
from pycose.algorithms import EdDSA
from pycose.headers import X5chain
from pycose.keys import OKPKey
from pycose.messages import CoseMessage, Sign1Message

from .logging_config import logger


def sign_payload(private_key: PrivateKeyTypes, payload_bytes: bytes) -> bytes:
    """
    Signs the payload bytes using the private key (Ed25519).

    Args:
        private_key: The Ed25519 private key object.
        payload_bytes: The canonical bytes of the payload to sign.

    Returns:
        The signature bytes.

    Raises:
        TypeError: If the provided key is not an Ed25519 private key.
    """
    if not isinstance(private_key, ed25519.Ed25519PrivateKey):
        logger.error(f"Signing aborted: Incorrect private key type provided " f"({type(private_key)}). Expected Ed25519PrivateKey.")
        raise TypeError("Signing requires an Ed25519PrivateKey instance.")

    logger.debug(f"Attempting to sign payload ({len(payload_bytes)} bytes) with Ed25519 key.")
    try:
        signature = private_key.sign(payload_bytes)
        logger.info(f"Successfully signed payload (signature length: {len(signature)} bytes).")
        return cast(bytes, signature)
    except Exception as e:
        logger.error(f"Signing operation failed: {e}", exc_info=True)
        raise RuntimeError(f"Signing failed: {e}")


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
        logger.error(f"Verification aborted: Incorrect public key type provided " f"({type(public_key)}). Expected Ed25519PublicKey.")
        raise TypeError("Verification requires an Ed25519PublicKey instance.")

    logger.debug(f"Attempting to verify signature (len={len(signature)}) against payload (len={len(payload_bytes)}) " f"using Ed25519 public key.")
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


def sign_c2pa_cose(
    private_key: ed25519.Ed25519PrivateKey,
    payload_bytes: bytes,
    timestamp_authority_url: Optional[str] = None,
    certificates: Optional[List[Certificate]] = None,
) -> bytes:
    """
    Signs a C2PA payload using a COSE_Sign1 structure with optional timestamp and certificates.

    This function creates a standard COSE_Sign1 object, which encapsulates the
    payload, signing algorithm, and signature in a single CBOR structure, as
    required for C2PA claim signatures. It can optionally include a timestamp from
    an RFC 3161 Time-Stamp Authority and a certificate chain.

    Args:
        private_key: The Ed25519 private key for signing.
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
        # Create protected header
        # Use integer 1 for ALG header parameter as per COSE spec
        protected_header = {1: EdDSA}

        # Create unprotected header
        unprotected_header = {}

        # Add certificates if provided
        if certificates and len(certificates) > 0:
            # Convert certificates to DER format for x5chain
            x5chain = [cert.public_bytes(serialization.Encoding.DER) for cert in certificates]
            # Use the integer header label 33 for X5CHAIN as per COSE spec
            unprotected_header[33] = x5chain
            logger.debug(f"Added {len(x5chain)} certificates to COSE unprotected header")

        # Create and prepare the COSE message
        # Extract raw private key bytes from the cryptography Ed25519PrivateKey
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw, format=serialization.PrivateFormat.Raw, encryption_algorithm=serialization.NoEncryption()
        )

        # Create OKPKey for Ed25519
        cose_key = OKPKey(crv="ED25519", d=private_bytes, optional_params={"ALG": "EDDSA"})

        # Create the COSE message
        msg = Sign1Message(phdr=protected_header, uhdr=unprotected_header, payload=payload_bytes)
        msg.key = cose_key

        # Sign the message
        encoded_cose = msg.encode()

        # If timestamp authority URL is provided, request a timestamp
        if timestamp_authority_url:
            encoded_cose = add_timestamp_to_cose(encoded_cose, timestamp_authority_url)

        logger.info(f"Successfully created COSE_Sign1 signed message (length: {len(encoded_cose)} bytes).")
        return bytes(encoded_cose)
    except Exception as e:
        logger.error(f"COSE signing operation failed: {e}", exc_info=True)
        raise RuntimeError(f"COSE signing failed: {e}")


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
        # Decode the COSE message
        msg = CoseMessage.decode(cose_bytes)
        if not isinstance(msg, Sign1Message):
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
        if not msg.uhdr:
            msg.uhdr = {}

        # Store the timestamp token in the unprotected header using a custom header
        # C2PA uses a custom header for timestamps
        # Use a custom header parameter ID for timestamps (8 is typically used for timestamps)
        # This avoids using Reserved.value which is not a valid attribute
        TIMESTAMP_HEADER_PARAM = 8
        msg.uhdr[TIMESTAMP_HEADER_PARAM] = timestamp_token
        # Use a custom header parameter ID for timestamps (8 is typically used for timestamps)
        # This avoids using Reserved.value which is not a valid attribute
        TIMESTAMP_HEADER_PARAM = 8
        msg.uhdr[TIMESTAMP_HEADER_PARAM] = timestamp_token

        # Re-encode the message with the timestamp
        logger.info("Added RFC 3161 timestamp to COSE message")
        return bytes(msg.encode())
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
        raise RuntimeError(f"Timestamp request failed: {e}")


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
        decoded_msg = CoseMessage.decode(cose_bytes)

        if not isinstance(decoded_msg, Sign1Message):
            logger.warning("Message is not a COSE_Sign1 structure.")
            return None

        # Extract payload without verification
        if decoded_msg.payload is None:
            logger.warning("COSE_Sign1 message has no payload")
            return None

        if decoded_msg.payload is None:
            logger.warning("COSE_Sign1 message has no payload")
            return None

        payload = bytes(decoded_msg.payload)
        logger.debug(f"Successfully extracted payload ({len(payload)} bytes) from COSE_Sign1 message.")
        return payload
    except Exception as e:
        logger.warning(f"Error extracting payload from COSE_Sign1: {e}")
        return None


def verify_c2pa_cose(public_key: ed25519.Ed25519PublicKey, cose_bytes: bytes) -> bytes:
    """
    Verifies a COSE_Sign1 signature and returns the payload if valid.

    Args:
        public_key: The Ed25519 public key for verification.
        cose_bytes: The CBOR-encoded COSE_Sign1 message.

    Returns:
        The original payload bytes if the signature is valid.

    Raises:
        InvalidSignature: If the signature is invalid.
        ValueError: If the message is not a valid COSE_Sign1 structure.
    """
    logger.debug(f"Attempting to verify COSE_Sign1 message ({len(cose_bytes)} bytes).")
    decoded_msg = CoseMessage.decode(cose_bytes)
    if not isinstance(decoded_msg, Sign1Message):
        raise ValueError("Message is not a COSE_Sign1 structure.")

    # Extract raw public key bytes from the cryptography Ed25519PublicKey
    public_bytes = public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)

    # Create OKPKey for Ed25519 verification
    cose_key = OKPKey(crv="ED25519", x=public_bytes, optional_params={"ALG": "EDDSA"})
    decoded_msg.key = cose_key

    if decoded_msg.verify_signature():
        logger.info("COSE_Sign1 signature verification successful.")
        if decoded_msg.payload is None:
            raise ValueError("COSE_Sign1 message has no payload after verification")
        if decoded_msg.payload is None:
            raise ValueError("COSE_Sign1 message has no payload after verification")
        return bytes(decoded_msg.payload)
    else:
        # This path is often not hit as verify_signature raises on failure,
        # but it's here for completeness.
        raise InvalidSignature("COSE signature verification failed.")


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
        self.trusted_roots: Set[Certificate] = set()
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


def validate_certificate_chain(cert_chain: List[Certificate], trust_store: TrustStore) -> bool:
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
            raise CertificateValidationError(f"Invalid signature on certificate: {subject.subject}")
        except Exception as e:
            raise CertificateValidationError(f"Certificate validation error: {e}")

    return True


def extract_certificates_from_cose(cose_bytes: bytes) -> List[Certificate]:
    """
    Extract X.509 certificates from a COSE_Sign1 message.

    Args:
        cose_bytes: The CBOR-encoded COSE_Sign1 message.

    Returns:
        List of X.509 certificates found in the COSE message.

    Raises:
        ValueError: If the message is not a valid COSE_Sign1 structure or contains no certificates.
    """
    decoded_msg = CoseMessage.decode(cose_bytes)
    if not isinstance(decoded_msg, Sign1Message):
        raise ValueError("Message is not a COSE_Sign1 structure.")

    # Extract certificates from the unprotected header (x5chain)
    certificates = []
    x5chain = decoded_msg.uhdr.get(X5chain.identifier)

    if not x5chain:
        raise ValueError("No X.509 certificates found in COSE message.")

    # Parse each certificate in the chain
    for cert_bytes in x5chain:
        try:
            cert = x509.load_der_x509_certificate(cert_bytes)
            certificates.append(cert)
        except Exception as e:
            logger.warning(f"Failed to parse certificate from COSE message: {e}")

    if not certificates:
        raise ValueError("Failed to extract any valid certificates from COSE message.")

    return certificates
