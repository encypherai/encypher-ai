from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from app.utils.c2pa_trust_list import set_trust_anchors_pem, validate_certificate_chain


def _new_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _name(common_name: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])


def _pem(cert: x509.Certificate) -> str:
    return cert.public_bytes(serialization.Encoding.PEM).decode("utf-8")


def _make_root_ca(*, cn: str) -> tuple[rsa.RSAPrivateKey, x509.Certificate]:
    key = _new_key()
    subject = _name(cn)
    now = datetime.now(timezone.utc)

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .sign(private_key=key, algorithm=hashes.SHA256())
    )
    return key, cert


def _make_intermediate_ca(
    *,
    cn: str,
    issuer_key: rsa.RSAPrivateKey,
    issuer_cert: x509.Certificate,
    ca: bool = True,
) -> tuple[rsa.RSAPrivateKey, x509.Certificate]:
    key = _new_key()
    subject = _name(cn)
    now = datetime.now(timezone.utc)

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True)
        .sign(private_key=issuer_key, algorithm=hashes.SHA256())
    )
    return key, cert


def _make_leaf(
    *,
    cn: str,
    issuer_key: rsa.RSAPrivateKey,
    issuer_cert: x509.Certificate,
    expires_in_days: int = 365,
    signer_key: rsa.RSAPrivateKey | None = None,
) -> tuple[rsa.RSAPrivateKey, x509.Certificate]:
    key = signer_key or _new_key()
    subject = _name(cn)
    now = datetime.now(timezone.utc)

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=expires_in_days))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(private_key=issuer_key, algorithm=hashes.SHA256())
    )
    return key, cert


def test_validate_certificate_chain_valid_chain_passes() -> None:
    root_key, root = _make_root_ca(cn="C2PA Test Root")
    _ = set_trust_anchors_pem(_pem(root))

    int_key, intermediate = _make_intermediate_ca(
        cn="C2PA Test Intermediate",
        issuer_key=root_key,
        issuer_cert=root,
        ca=True,
    )
    _leaf_key, leaf = _make_leaf(
        cn="C2PA Test Leaf",
        issuer_key=int_key,
        issuer_cert=intermediate,
    )

    ok, err, _parsed = validate_certificate_chain(_pem(leaf), _pem(intermediate))
    assert ok is True
    assert err is None


def test_validate_certificate_chain_signature_mismatch_fails() -> None:
    root_key, root = _make_root_ca(cn="C2PA Test Root")
    _ = set_trust_anchors_pem(_pem(root))

    int_key, intermediate = _make_intermediate_ca(
        cn="C2PA Test Intermediate",
        issuer_key=root_key,
        issuer_cert=root,
        ca=True,
    )

    rogue_key = _new_key()
    _leaf_key, leaf = _make_leaf(
        cn="C2PA Test Leaf",
        issuer_key=rogue_key,
        issuer_cert=intermediate,
    )

    ok, err, _parsed = validate_certificate_chain(_pem(leaf), _pem(intermediate))
    assert ok is False
    assert err


def test_validate_certificate_chain_expired_leaf_fails() -> None:
    root_key, root = _make_root_ca(cn="C2PA Test Root")
    _ = set_trust_anchors_pem(_pem(root))

    int_key, intermediate = _make_intermediate_ca(
        cn="C2PA Test Intermediate",
        issuer_key=root_key,
        issuer_cert=root,
        ca=True,
    )
    _leaf_key, leaf = _make_leaf(
        cn="C2PA Test Leaf",
        issuer_key=int_key,
        issuer_cert=intermediate,
        expires_in_days=-1,
    )

    ok, err, _parsed = validate_certificate_chain(_pem(leaf), _pem(intermediate))
    assert ok is False
    assert err


def test_validate_certificate_chain_intermediate_not_ca_fails() -> None:
    root_key, root = _make_root_ca(cn="C2PA Test Root")
    _ = set_trust_anchors_pem(_pem(root))

    int_key, intermediate = _make_intermediate_ca(
        cn="C2PA Test Intermediate",
        issuer_key=root_key,
        issuer_cert=root,
        ca=False,
    )
    _leaf_key, leaf = _make_leaf(
        cn="C2PA Test Leaf",
        issuer_key=int_key,
        issuer_cert=intermediate,
    )

    ok, err, _parsed = validate_certificate_chain(_pem(leaf), _pem(intermediate))
    assert ok is False
    assert err
