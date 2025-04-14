import pytest
import os
import tempfile
import json
import datetime
from typing import Tuple, Optional
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from encypher.core.crypto_utils import (
    generate_key_pair,
    load_private_key,
    load_public_key,
    serialize_payload,
    sign_payload,
    verify_signature,
    BasicPayload,
    ManifestPayload,
    PrivateKeyTypes,
    PublicKeyTypes,
    ManifestAction,
    ManifestAiInfo,
)

# --- Helper functions to replace missing functionality ---


def save_private_key(
    private_key: PrivateKeyTypes, path: str, password: Optional[bytes] = None
) -> None:
    """
    Save a private key to a file in PEM format.

    Args:
        private_key: The private key to save
        path: The file path to save to
        password: Optional password for encryption
    """
    # For Ed25519 keys
    if isinstance(private_key, ed25519.Ed25519PrivateKey):
        if password:
            encryption_algorithm = serialization.BestAvailableEncryption(password)
        else:
            encryption_algorithm = serialization.NoEncryption()

        pem_data = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_algorithm,
        )

        with open(path, "wb") as f:
            f.write(pem_data)
    else:
        raise TypeError("Only Ed25519 private keys are supported")


def save_public_key(public_key: PublicKeyTypes, path: str) -> None:
    """
    Save a public key to a file in PEM format.

    Args:
        public_key: The public key to save
        path: The file path to save to
    """
    pem_data = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    with open(path, "wb") as f:
        f.write(pem_data)


def format_timestamp(dt: Optional[datetime.datetime] = None) -> str:
    """
    Format a datetime as an ISO 8601 string.

    Args:
        dt: The datetime to format, or None to use current time

    Returns:
        ISO 8601 formatted timestamp string
    """
    if dt is None:
        dt = datetime.datetime.now(datetime.timezone.utc)
    return dt.isoformat()


# --- Test Fixtures / Setup ---


@pytest.fixture(scope="module")
def test_keys() -> Tuple[PrivateKeyTypes, PublicKeyTypes]:
    """Generate a key pair for tests."""
    return generate_key_pair()


def test_generate_key_pair():
    """Test if key pair generation returns correct types."""
    private_key, public_key = generate_key_pair()
    assert isinstance(private_key, ed25519.Ed25519PrivateKey)
    assert isinstance(public_key, ed25519.Ed25519PublicKey)


def test_load_save_keys(test_keys):
    """Test saving and loading keys using PEM format."""
    private_key, public_key = test_keys
    # Use tempfile for secure handling
    with tempfile.TemporaryDirectory() as tmpdir:
        priv_path = os.path.join(tmpdir, "test_priv.pem")
        pub_path = os.path.join(tmpdir, "test_pub.pem")

        # Save keys (PEM format implicitly)
        save_private_key(private_key, priv_path)
        save_public_key(public_key, pub_path)

        # Read key files
        with open(priv_path, "rb") as f:
            priv_data = f.read()
        with open(pub_path, "rb") as f:
            pub_data = f.read()

        # Load keys from data
        loaded_priv = load_private_key(priv_data)
        loaded_pub = load_public_key(pub_data)

        # Check if loaded keys match original key types
        assert isinstance(loaded_priv, ed25519.Ed25519PrivateKey)
        assert isinstance(loaded_pub, ed25519.Ed25519PublicKey)

        # Instead of comparing raw bytes, we'll sign and verify a test message
        # to confirm the keys are functionally equivalent
        test_message = b"test message for key verification"
        original_signature = private_key.sign(test_message)
        loaded_signature = loaded_priv.sign(test_message)

        # Verify both signatures with both public keys
        public_key.verify(original_signature, test_message)
        public_key.verify(loaded_signature, test_message)
        loaded_pub.verify(original_signature, test_message)
        loaded_pub.verify(loaded_signature, test_message)


def test_load_save_keys_encrypted(test_keys):
    """Test saving and loading keys with encryption."""
    private_key, public_key = test_keys
    password = b"supersecretpassword"

    with tempfile.TemporaryDirectory() as tmpdir:
        priv_path_enc = os.path.join(tmpdir, "test_priv_enc.pem")

        # Save encrypted private key
        save_private_key(private_key, priv_path_enc, password=password)

        # Read encrypted key file
        with open(priv_path_enc, "rb") as f:
            priv_data_enc = f.read()

        # Load encrypted private key
        loaded_priv_enc = load_private_key(priv_data_enc, password=password)
        assert isinstance(loaded_priv_enc, ed25519.Ed25519PrivateKey)

        # Verify the loaded key is functionally equivalent
        test_message = b"test message for encrypted key verification"
        original_signature = private_key.sign(test_message)
        loaded_signature = loaded_priv_enc.sign(test_message)

        public_key.verify(original_signature, test_message)
        public_key.verify(loaded_signature, test_message)

        # Test loading with wrong password
        with pytest.raises(ValueError):
            load_private_key(priv_data_enc, password=b"wrongpassword")

        # Test loading without password
        with pytest.raises(ValueError):
            load_private_key(priv_data_enc)


# --- Serialization Tests ---


@pytest.fixture
def basic_payload_data() -> BasicPayload:
    """Sample BasicPayload data."""
    return BasicPayload(
        timestamp=format_timestamp(),
        model_id="test_model_basic_v1.0",
        target="Some basic text.",
        custom={"info": "some basic custom data", "value": 123},
    )


@pytest.fixture
def manifest_payload_data() -> ManifestPayload:
    """Sample ManifestPayload data."""
    timestamp = format_timestamp()
    return ManifestPayload(
        manifest_id="urn:uuid:123e4567-e89b-12d3-a456-426614174000",
        timestamp=timestamp,
        actions=[
            ManifestAction(
                action_id="urn:uuid:action-1",
                action_type="generated",
                timestamp=timestamp,
                actor="Test Generator",
                details={"prompt": "Create an example manifest"},
            )
        ],
        ai_info=ManifestAiInfo(
            model_id="test_model_manifest_v2.1",
            provider="Test Provider Inc.",
            parameters={"temperature": 0.7, "max_tokens": 50},
        ),
        target="Text relevant to the manifest.",
        custom={"extra_field": "manifest custom data", "flag": True},
    )


def test_serialize_payload_basic(basic_payload_data):
    """Test canonical serialization of BasicPayload."""
    serialized_bytes = serialize_payload(basic_payload_data)
    assert isinstance(serialized_bytes, bytes)
    # Deserialize to check structure and canonical form (keys sorted)
    data = json.loads(serialized_bytes.decode("utf-8"))
    assert list(data.keys()) == ["custom", "model_id", "target", "timestamp"]
    assert list(data["custom"].keys()) == [
        "info",
        "value",
    ]  # Check inner dict keys sorted
    assert data["model_id"] == basic_payload_data["model_id"]


def test_serialize_payload_manifest(manifest_payload_data):
    """Test canonical serialization of ManifestPayload."""
    serialized_bytes = serialize_payload(manifest_payload_data)
    assert isinstance(serialized_bytes, bytes)
    # Deserialize to check structure and canonical form
    data = json.loads(serialized_bytes.decode("utf-8"))
    expected_keys = [
        "actions",
        "ai_info",
        "custom",
        "manifest_id",
        "target",
        "timestamp",
    ]
    assert list(data.keys()) == expected_keys
    # Check inner structures are also sorted if they are dicts
    assert list(data["actions"][0].keys()) == [
        "action_id",
        "action_type",
        "actor",
        "details",
        "timestamp",
    ]
    assert list(data["actions"][0]["details"].keys()) == ["prompt"]
    assert list(data["ai_info"].keys()) == ["model_id", "parameters", "provider"]
    assert list(data["ai_info"]["parameters"].keys()) == ["max_tokens", "temperature"]
    assert list(data["custom"].keys()) == ["extra_field", "flag"]
    assert data["manifest_id"] == manifest_payload_data["manifest_id"]


def test_serialize_payload_deterministic(basic_payload_data):
    """Ensure serialization produces the same bytes for the same input."""
    bytes1 = serialize_payload(basic_payload_data)
    # Create identical dict again
    payload2 = BasicPayload(
        timestamp=basic_payload_data["timestamp"],
        model_id="test_model_basic_v1.0",
        target="Some basic text.",
        custom={"value": 123, "info": "some basic custom data"},  # Note different order
    )
    bytes2 = serialize_payload(payload2)
    assert bytes1 == bytes2


# --- Signing and Verification Tests ---


def test_sign_and_verify_basic(test_keys, basic_payload_data):
    """Test signing and verifying a BasicPayload."""
    private_key, public_key = test_keys
    payload_bytes = serialize_payload(basic_payload_data)

    # Sign the payload
    signature_bytes = sign_payload(private_key, payload_bytes)
    assert isinstance(signature_bytes, bytes)
    assert len(signature_bytes) == 64  # Ed25519 signatures are 64 bytes

    # Verify the signature - should be valid
    is_valid = verify_signature(public_key, payload_bytes, signature_bytes)
    assert is_valid is True


def test_sign_and_verify_manifest(test_keys, manifest_payload_data):
    """Test signing and verifying a ManifestPayload."""
    private_key, public_key = test_keys
    payload_bytes = serialize_payload(manifest_payload_data)

    # Sign
    signature_bytes = sign_payload(private_key, payload_bytes)
    assert isinstance(signature_bytes, bytes)
    assert len(signature_bytes) == 64

    # Verify - should be valid
    is_valid = verify_signature(public_key, payload_bytes, signature_bytes)
    assert is_valid is True


def test_verify_failure_wrong_key(test_keys, basic_payload_data):
    """Test that verification fails with the wrong public key."""
    private_key, _ = test_keys  # Use the correct private key to sign
    payload_bytes = serialize_payload(basic_payload_data)
    signature_bytes = sign_payload(private_key, payload_bytes)

    # Generate a *different* key pair for verification
    _, wrong_public_key = generate_key_pair()

    # Verify with the wrong key - should be invalid
    is_valid = verify_signature(wrong_public_key, payload_bytes, signature_bytes)
    assert is_valid is False


def test_verify_failure_tampered_payload(test_keys, basic_payload_data):
    """Test that verification fails if the payload is altered after signing."""
    private_key, public_key = test_keys
    payload_bytes = serialize_payload(basic_payload_data)
    signature_bytes = sign_payload(private_key, payload_bytes)

    # Tamper with the original payload bytes
    tampered_payload_bytes = payload_bytes + b"extra_data"

    # Verify with the tampered payload - should be invalid
    is_valid = verify_signature(public_key, tampered_payload_bytes, signature_bytes)
    assert is_valid is False

    # Also test tampering by deserializing, changing, and reserializing
    tampered_data = basic_payload_data.copy()
    tampered_data["model_id"] = "hacked_model"
    tampered_payload_bytes_reserialized = serialize_payload(tampered_data)

    is_valid_reserialized = verify_signature(
        public_key, tampered_payload_bytes_reserialized, signature_bytes
    )
    assert is_valid_reserialized is False


def test_verify_failure_corrupt_signature(test_keys, basic_payload_data):
    """Test that verification fails with a corrupted signature."""
    private_key, public_key = test_keys
    payload_bytes = serialize_payload(basic_payload_data)
    signature_bytes = sign_payload(private_key, payload_bytes)

    # Corrupt the signature (e.g., flip a bit or change a byte)
    corrupt_signature_list = list(signature_bytes)
    corrupt_signature_list[0] = (corrupt_signature_list[0] + 1) % 256
    corrupt_signature_bytes = bytes(corrupt_signature_list)

    assert corrupt_signature_bytes != signature_bytes  # Ensure corruption happened

    # Verify with the corrupt signature - should be invalid
    is_valid = verify_signature(public_key, payload_bytes, corrupt_signature_bytes)
    assert is_valid is False


# --- End of Tests for crypto_utils.py ---
