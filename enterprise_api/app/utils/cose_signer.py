"""COSE_Sign1 signing for C2PA claims (RFC 9052 / C2PA spec).

Produces COSE_Sign1_Tagged structures with detached payload mode,
as required by the C2PA specification for claim signatures.

Structure:
  COSE_Sign1_Tagged = #6.18([
    protected,    ; bstr (CBOR-encoded protected headers)
    unprotected,  ; map  (unprotected headers, including cert chain)
    nil,          ; payload is detached
    signature     ; bstr
  ])

Signing input (Sig_structure):
  ["Signature1", protected, b"", payload]
"""

import logging
from dataclasses import dataclass
from typing import Optional

import cbor2

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa, utils
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import load_der_x509_certificate, load_pem_x509_certificate

_log = logging.getLogger(__name__)

# COSE algorithm identifiers (IANA COSE Algorithms registry)
COSE_ALG_ES256 = -7
COSE_ALG_ES384 = -35
COSE_ALG_ES512 = -36
COSE_ALG_PS256 = -37
COSE_ALG_EDDSA = -8

# COSE header keys
COSE_HDR_ALG = 1
COSE_HDR_X5CHAIN = 33  # x5chain - certificate chain

# CBOR tag for COSE_Sign1
COSE_SIGN1_TAG = 18


def _detect_algorithm(key_obj):
    """Detect COSE algorithm from a loaded private key."""
    if isinstance(key_obj, Ed25519PrivateKey):
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


def sign_claim(
    claim_cbor: bytes,
    private_key_pem: str,
    cert_chain_pem: str,
    *,
    pad_size: int = 25000,
) -> bytes:
    """Sign a CBOR-encoded C2PA claim, producing COSE_Sign1_Tagged bytes.

    Args:
        claim_cbor: CBOR-encoded claim payload.
        private_key_pem: PEM-encoded private key.
        cert_chain_pem: PEM-encoded certificate chain (EE cert first).
        pad_size: Reserved padding in unprotected headers (default 25KB).

    Returns:
        CBOR-encoded COSE_Sign1_Tagged bytes.
    """
    key_obj = load_pem_private_key(private_key_pem.encode("utf-8"), password=None)
    alg = _detect_algorithm(key_obj)

    # Protected headers: just the algorithm
    protected_map = {COSE_HDR_ALG: alg}
    protected_bytes = cbor2.dumps(protected_map)

    # Build Sig_structure for signing
    # ["Signature1", protected, external_aad, payload]
    sig_structure = cbor2.dumps(
        [
            "Signature1",
            protected_bytes,
            b"",  # external_aad
            claim_cbor,
        ]
    )

    signature = _sign_bytes(key_obj, sig_structure, alg)

    # Unprotected headers: certificate chain + padding
    # Use string label "x5chain" (not integer 33) because c2pa-rs coset
    # only checks Label::Text("x5chain") in unprotected headers.
    cert_chain_der = _parse_cert_chain_pem(cert_chain_pem)
    unprotected = {
        "x5chain": cert_chain_der if len(cert_chain_der) > 1 else cert_chain_der[0],
    }

    # Add padding to reserve space for the two-pass approach
    # C2PA padding uses integer label 0x43504164 ("CPAd") per c2pa-rs convention
    if pad_size > 0:
        unprotected[0x43504164] = b"\x00" * pad_size

    # COSE_Sign1 = [protected, unprotected, nil, signature]
    cose_array = [protected_bytes, unprotected, None, signature]

    # Wrap in CBOR tag 18 (COSE_Sign1_Tagged)
    return cbor2.dumps(cbor2.CBORTag(COSE_SIGN1_TAG, cose_array))


# ---- Verification ----


@dataclass
class CoseVerifyResult:
    valid: bool
    algorithm: int
    claim_cbor: Optional[bytes] = None
    certificate_der: Optional[bytes] = None
    error: Optional[str] = None


def _verify_signature(public_key, data: bytes, signature: bytes, alg: int) -> None:
    """Verify a signature using the appropriate algorithm. Raises on failure."""
    if alg == COSE_ALG_EDDSA:
        public_key.verify(signature, data)
    elif alg in (COSE_ALG_ES256, COSE_ALG_ES384, COSE_ALG_ES512):
        # Convert raw r||s to DER signature
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


def verify_cose_sign1(cose_bytes: bytes, claim_cbor: bytes) -> CoseVerifyResult:
    """Verify a COSE_Sign1_Tagged signature against the claim payload.

    Args:
        cose_bytes: CBOR-encoded COSE_Sign1_Tagged bytes.
        claim_cbor: The CBOR-encoded claim (detached payload).

    Returns:
        CoseVerifyResult with validation status.
    """
    try:
        decoded = cbor2.loads(cose_bytes)
        if not isinstance(decoded, cbor2.CBORTag) or decoded.tag != COSE_SIGN1_TAG:
            return CoseVerifyResult(valid=False, algorithm=0, error="Not a COSE_Sign1_Tagged structure")

        protected_bytes, unprotected, payload_nil, signature = decoded.value

        # Parse protected headers
        protected = cbor2.loads(protected_bytes)
        alg = protected.get(COSE_HDR_ALG)
        if alg is None:
            return CoseVerifyResult(valid=False, algorithm=0, error="Missing algorithm in protected headers")

        # Extract certificate from unprotected headers
        # Check both string "x5chain" and integer 33 for compatibility
        x5chain = unprotected.get("x5chain") or unprotected.get(COSE_HDR_X5CHAIN)
        if x5chain is None:
            return CoseVerifyResult(valid=False, algorithm=alg, error="Missing x5chain in unprotected headers")

        # x5chain can be a single cert (bytes) or array of certs
        if isinstance(x5chain, list):
            ee_cert_der = x5chain[0]
        else:
            ee_cert_der = x5chain

        # Load public key from EE certificate
        cert = load_der_x509_certificate(ee_cert_der)
        public_key = cert.public_key()

        # Reconstruct Sig_structure
        sig_structure = cbor2.dumps(
            [
                "Signature1",
                protected_bytes,
                b"",  # external_aad
                claim_cbor,
            ]
        )

        # Verify
        _verify_signature(public_key, sig_structure, signature, alg)

        return CoseVerifyResult(
            valid=True,
            algorithm=alg,
            claim_cbor=claim_cbor,
            certificate_der=ee_cert_der,
        )

    except Exception as exc:
        return CoseVerifyResult(valid=False, algorithm=0, error=str(exc))
