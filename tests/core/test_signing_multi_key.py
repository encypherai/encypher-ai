"""Tests for multi-key-type C2PA COSE signing and verification.

Covers EC (P-256, P-384, P-521) and RSA-PSS key types in sign_c2pa_cose,
verify_c2pa_cose, and verify_signature (basic payload path), in addition
to the existing Ed25519 path.
"""

import cbor2
import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa

from encypher.core.signing import (
    ALG_EDDSA,
    SigningKey,
    sign_c2pa_cose,
    sign_payload,
    verify_c2pa_cose,
    verify_signature,
)

# COSE algorithm identifiers (RFC 9053 / C2PA)
ALG_ES256 = -7
ALG_ES384 = -35
ALG_ES512 = -36
ALG_PS256 = -37


# --- Key generation fixtures ---


@pytest.fixture
def ed25519_keypair():
    priv = ed25519.Ed25519PrivateKey.generate()
    return priv, priv.public_key()


@pytest.fixture
def ec_p256_keypair():
    priv = ec.generate_private_key(ec.SECP256R1())
    return priv, priv.public_key()


@pytest.fixture
def ec_p384_keypair():
    priv = ec.generate_private_key(ec.SECP384R1())
    return priv, priv.public_key()


@pytest.fixture
def ec_p521_keypair():
    priv = ec.generate_private_key(ec.SECP521R1())
    return priv, priv.public_key()


@pytest.fixture
def rsa_keypair():
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return priv, priv.public_key()


SAMPLE_PAYLOAD = cbor2.dumps({"test": "c2pa-payload", "version": 1})


# --- Helper to extract COSE alg from signed output ---


def _extract_cose_alg(cose_bytes: bytes) -> int:
    arr = cbor2.loads(cose_bytes)
    protected_map = cbor2.loads(arr[0])
    return protected_map[1]  # ALG_HEADER = 1


# --- sign_c2pa_cose tests ---


class TestSignC2paCoseEdDSA:
    """Existing Ed25519 path should continue to work."""

    def test_sign_and_verify_roundtrip(self, ed25519_keypair):
        priv, pub = ed25519_keypair
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD)
        assert _extract_cose_alg(cose) == ALG_EDDSA
        result = verify_c2pa_cose(pub, cose)
        assert result == SAMPLE_PAYLOAD

    def test_wrong_key_fails_verification(self, ed25519_keypair):
        priv, _ = ed25519_keypair
        wrong_priv = ed25519.Ed25519PrivateKey.generate()
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD)
        with pytest.raises(InvalidSignature):
            verify_c2pa_cose(wrong_priv.public_key(), cose)


class TestSignC2paCoseEC:
    """EC key types: P-256, P-384, P-521."""

    def test_ec_p256_sign_and_verify(self, ec_p256_keypair):
        priv, pub = ec_p256_keypair
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD)
        assert _extract_cose_alg(cose) == ALG_ES256
        result = verify_c2pa_cose(pub, cose)
        assert result == SAMPLE_PAYLOAD

    def test_ec_p384_sign_and_verify(self, ec_p384_keypair):
        priv, pub = ec_p384_keypair
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD)
        assert _extract_cose_alg(cose) == ALG_ES384
        result = verify_c2pa_cose(pub, cose)
        assert result == SAMPLE_PAYLOAD

    def test_ec_p521_sign_and_verify(self, ec_p521_keypair):
        priv, pub = ec_p521_keypair
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD)
        assert _extract_cose_alg(cose) == ALG_ES512
        result = verify_c2pa_cose(pub, cose)
        assert result == SAMPLE_PAYLOAD

    def test_ec_wrong_key_fails(self, ec_p256_keypair):
        priv, _ = ec_p256_keypair
        wrong_priv = ec.generate_private_key(ec.SECP256R1())
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD)
        with pytest.raises(InvalidSignature):
            verify_c2pa_cose(wrong_priv.public_key(), cose)

    def test_ec_cross_curve_fails(self, ec_p256_keypair, ec_p384_keypair):
        """Signing with P-256 and verifying with P-384 key must fail."""
        priv_256, _ = ec_p256_keypair
        _, pub_384 = ec_p384_keypair
        cose = sign_c2pa_cose(priv_256, SAMPLE_PAYLOAD)
        with pytest.raises((InvalidSignature, ValueError)):
            verify_c2pa_cose(pub_384, cose)


class TestSignC2paCoseRSA:
    """RSA-PSS key type."""

    def test_rsa_sign_and_verify(self, rsa_keypair):
        priv, pub = rsa_keypair
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD)
        assert _extract_cose_alg(cose) == ALG_PS256
        result = verify_c2pa_cose(pub, cose)
        assert result == SAMPLE_PAYLOAD

    def test_rsa_wrong_key_fails(self, rsa_keypair):
        priv, _ = rsa_keypair
        wrong_priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD)
        with pytest.raises(InvalidSignature):
            verify_c2pa_cose(wrong_priv.public_key(), cose)


class TestSignC2paCosePayloadOverride:
    """verify_c2pa_cose with payload_override for all key types."""

    @pytest.mark.parametrize(
        "keypair_fixture",
        ["ed25519_keypair", "ec_p256_keypair", "rsa_keypair"],
    )
    def test_payload_override(self, keypair_fixture, request):
        priv, pub = request.getfixturevalue(keypair_fixture)
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD)
        # Verify with correct payload override
        result = verify_c2pa_cose(pub, cose, payload_override=SAMPLE_PAYLOAD)
        assert result == SAMPLE_PAYLOAD


class TestSignC2paCoseTampering:
    """Tampered payloads must fail verification for all key types."""

    @pytest.mark.parametrize(
        "keypair_fixture",
        ["ed25519_keypair", "ec_p256_keypair", "ec_p384_keypair", "rsa_keypair"],
    )
    def test_tampered_payload_fails(self, keypair_fixture, request):
        priv, pub = request.getfixturevalue(keypair_fixture)
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD)
        tampered = cbor2.dumps({"test": "TAMPERED", "version": 999})
        with pytest.raises(InvalidSignature):
            verify_c2pa_cose(pub, cose, payload_override=tampered)


class TestVerifySignatureMultiKey:
    """verify_signature must accept EC and RSA keys (not just Ed25519)."""

    def test_ec_p256_sign_verify(self, ec_p256_keypair):
        priv, pub = ec_p256_keypair
        sig = sign_payload(priv, SAMPLE_PAYLOAD)
        assert verify_signature(pub, SAMPLE_PAYLOAD, sig) is True

    def test_ec_p384_sign_verify(self, ec_p384_keypair):
        priv, pub = ec_p384_keypair
        sig = sign_payload(priv, SAMPLE_PAYLOAD)
        assert verify_signature(pub, SAMPLE_PAYLOAD, sig) is True

    def test_rsa_sign_verify(self, rsa_keypair):
        priv, pub = rsa_keypair
        sig = sign_payload(priv, SAMPLE_PAYLOAD)
        assert verify_signature(pub, SAMPLE_PAYLOAD, sig) is True

    def test_ed25519_sign_verify(self, ed25519_keypair):
        priv, pub = ed25519_keypair
        sig = sign_payload(priv, SAMPLE_PAYLOAD)
        assert verify_signature(pub, SAMPLE_PAYLOAD, sig) is True

    def test_ec_wrong_key_fails(self, ec_p256_keypair):
        priv, _ = ec_p256_keypair
        other_priv = ec.generate_private_key(ec.SECP256R1())
        sig = sign_payload(priv, SAMPLE_PAYLOAD)
        assert verify_signature(other_priv.public_key(), SAMPLE_PAYLOAD, sig) is False
