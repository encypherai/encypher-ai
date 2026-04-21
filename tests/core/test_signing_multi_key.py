"""Tests for multi-key-type C2PA COSE signing and verification.

Covers EC (P-256, P-384, P-521) and RSA-PSS key types in sign_c2pa_cose,
verify_c2pa_cose, and verify_signature (basic payload path), in addition
to the existing Ed25519 path.
"""

import cbor2
import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa

from encypher.core.signing import (
    ALG_EDDSA,
    SigningKey,
    extract_certificates_from_cose,
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


# --- Helper: self-signed X.509 certificate ---


def _self_signed_cert(private_key, public_key):
    """Create a self-signed X.509 certificate for testing."""
    from cryptography import x509 as x509_mod
    from cryptography.x509.oid import NameOID
    import datetime

    subject = issuer = x509_mod.Name([
        x509_mod.NameAttribute(NameOID.COMMON_NAME, "test-c2pa-signer"),
    ])
    cert = (
        x509_mod.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(x509_mod.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
        .sign(private_key, hashes.SHA256())
    )
    return cert


def _make_detached_cose(cose_bytes: bytes) -> bytes:
    """Replace the inline payload in a COSE_Sign1 with None (detached)."""
    arr = cbor2.loads(cose_bytes)
    arr[2] = None  # payload = null
    return cbor2.dumps(arr)


class TestExtractCertificatesFromCose:
    """extract_certificates_from_cose must handle detached and inline payloads."""

    def test_inline_payload_with_x5chain(self, ec_p256_keypair):
        priv, pub = ec_p256_keypair
        cert = _self_signed_cert(priv, pub)
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD, certificates=[cert])
        certs = extract_certificates_from_cose(cose)
        assert len(certs) == 1
        assert certs[0].public_key().public_numbers() == pub.public_numbers()

    def test_detached_payload_with_x5chain(self, ec_p256_keypair):
        """Detached payload (None) must not prevent x5chain extraction."""
        priv, pub = ec_p256_keypair
        cert = _self_signed_cert(priv, pub)
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD, certificates=[cert])
        detached = _make_detached_cose(cose)
        certs = extract_certificates_from_cose(detached)
        assert len(certs) == 1
        assert certs[0].public_key().public_numbers() == pub.public_numbers()

    def test_single_bstr_x5chain(self, ec_p256_keypair):
        """x5chain as a single CBOR bstr (not array) per RFC 9360."""
        from cryptography.hazmat.primitives import serialization as ser
        priv, pub = ec_p256_keypair
        cert = _self_signed_cert(priv, pub)
        cert_der = cert.public_bytes(ser.Encoding.DER)
        # Build COSE manually with x5chain as single bstr (not list)
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD, certificates=[cert])
        arr = cbor2.loads(cose)
        arr[1] = {33: cert_der}  # single bstr, not [cert_der]
        patched = cbor2.dumps(arr)
        certs = extract_certificates_from_cose(patched)
        assert len(certs) == 1

    def test_no_x5chain_raises(self, ec_p256_keypair):
        priv, _ = ec_p256_keypair
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD)  # no certificates
        with pytest.raises(ValueError, match="No X.509 certificates"):
            extract_certificates_from_cose(cose)


class TestVerifyCoseWithX5chain:
    """verify_c2pa_cose extracts key from x5chain when public_key=None."""

    def test_verify_inline_x5chain(self, ec_p256_keypair):
        priv, pub = ec_p256_keypair
        cert = _self_signed_cert(priv, pub)
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD, certificates=[cert])
        result = verify_c2pa_cose(None, cose)
        assert result == SAMPLE_PAYLOAD

    def test_verify_detached_x5chain(self, ec_p256_keypair):
        """Detached payload + x5chain: verify with payload_override."""
        priv, pub = ec_p256_keypair
        cert = _self_signed_cert(priv, pub)
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD, certificates=[cert])
        detached = _make_detached_cose(cose)
        result = verify_c2pa_cose(None, detached, payload_override=SAMPLE_PAYLOAD)
        assert result == SAMPLE_PAYLOAD

    def test_verify_single_bstr_x5chain(self, ec_p256_keypair):
        """verify_c2pa_cose handles x5chain as single bstr per RFC 9360."""
        from cryptography.hazmat.primitives import serialization as ser
        priv, pub = ec_p256_keypair
        cert = _self_signed_cert(priv, pub)
        cert_der = cert.public_bytes(ser.Encoding.DER)
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD, certificates=[cert])
        arr = cbor2.loads(cose)
        arr[1] = {33: cert_der}  # single bstr, not [cert_der]
        patched = cbor2.dumps(arr)
        result = verify_c2pa_cose(None, patched)
        assert result == SAMPLE_PAYLOAD

    def test_verify_cbor_tag18_wrapped(self, ec_p256_keypair):
        """COSE_Sign1 wrapped in CBOR tag 18 per RFC 9052 section 4.1."""
        priv, pub = ec_p256_keypair
        cert = _self_signed_cert(priv, pub)
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD, certificates=[cert])
        # Wrap in CBOR tag 18 (as WordPress C2PA plugin does)
        tagged = cbor2.dumps(cbor2.CBORTag(18, cbor2.loads(cose)))
        result = verify_c2pa_cose(None, tagged)
        assert result == SAMPLE_PAYLOAD

    def test_extract_certs_cbor_tag18(self, ec_p256_keypair):
        """extract_certificates_from_cose handles CBOR tag 18 wrapping."""
        priv, pub = ec_p256_keypair
        cert = _self_signed_cert(priv, pub)
        cose = sign_c2pa_cose(priv, SAMPLE_PAYLOAD, certificates=[cert])
        tagged = cbor2.dumps(cbor2.CBORTag(18, cbor2.loads(cose)))
        certs = extract_certificates_from_cose(tagged)
        assert len(certs) == 1
        assert certs[0].public_key().public_numbers() == pub.public_numbers()
