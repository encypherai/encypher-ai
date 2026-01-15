from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from app.api.v1 import endpoints as verify_endpoints
from app.utils.c2pa_trust_list import set_trust_anchors_pem


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
        .not_valid_after(now + timedelta(days=365))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(private_key=issuer_key, algorithm=hashes.SHA256())
    )
    return key, cert


async def test_is_embedded_c2pa_key_trusted_uses_trust_list(monkeypatch) -> None:
    root_key, root = _make_root_ca(cn="C2PA Test Root")
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

    set_trust_anchors_pem("")
    monkeypatch.setenv("C2PA_TRUST_LIST_PEM", _pem(root))

    monkeypatch.setattr(
        verify_endpoints,
        "find_wrapper_info_bytes",
        lambda _text: (b"manifest", 0, 0),
    )
    monkeypatch.setattr(
        verify_endpoints,
        "deserialize_jumbf_payload",
        lambda _b: {"cose_sign1": base64.b64encode(b"fake").decode("ascii")},
    )
    monkeypatch.setattr(
        verify_endpoints,
        "extract_certificates_from_cose",
        lambda _b: [leaf, intermediate, root],
    )

    assert await verify_endpoints._is_embedded_c2pa_key_trusted("hello") is True
