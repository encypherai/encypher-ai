"""Shared C2PA signer creation from PEM-encoded credentials.

Used by both image and audio signing pipelines. Supports Ed25519, EC
(P-256/P-384/P-521), and RSA (PS256) private keys.
"""

from typing import Any


def create_signer_from_pem(
    private_key_pem: str,
    cert_chain_pem: str,
) -> Any:
    """Create a c2pa.Signer from PEM-encoded private key and certificate chain.

    Uses C2paSignerInfo with NULL ta_url (no timestamp authority).
    The private key must be PKCS8-encoded EC/RSA/Ed25519.
    The cert_chain_pem should be EE cert + intermediate(s) + root CA.

    Args:
        private_key_pem: PKCS8 PEM-encoded private key string.
        cert_chain_pem: PEM-encoded certificate chain (EE first).

    Returns:
        c2pa.Signer instance. Caller must call .close() when done.
    """
    import c2pa
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import load_pem_private_key

    key_bytes = private_key_pem.encode("utf-8")
    key_obj = load_pem_private_key(key_bytes, password=None)

    if isinstance(key_obj, Ed25519PrivateKey):
        alg = c2pa.C2paSigningAlg.ED25519

        def sign_callback(data: bytes) -> bytes:
            return key_obj.sign(data)

    elif isinstance(key_obj, ec.EllipticCurvePrivateKey):
        curve = key_obj.curve
        if isinstance(curve, ec.SECP384R1):
            alg = c2pa.C2paSigningAlg.ES384
            hash_alg = hashes.SHA384()
        elif isinstance(curve, ec.SECP521R1):
            alg = c2pa.C2paSigningAlg.ES512
            hash_alg = hashes.SHA512()
        else:
            alg = c2pa.C2paSigningAlg.ES256
            hash_alg = hashes.SHA256()

        def sign_callback(data: bytes) -> bytes:
            return key_obj.sign(data, ec.ECDSA(hash_alg))

    elif isinstance(key_obj, rsa.RSAPrivateKey):
        alg = c2pa.C2paSigningAlg.PS256

        def sign_callback(data: bytes) -> bytes:
            return key_obj.sign(
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=32,
                ),
                hashes.SHA256(),
            )

    else:
        raise ValueError(f"Unsupported private key type: {type(key_obj).__name__}")

    return c2pa.Signer.from_callback(
        callback=sign_callback,
        alg=alg,
        certs=cert_chain_pem,
        tsa_url=None,
    )
