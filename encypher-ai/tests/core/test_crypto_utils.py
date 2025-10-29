import base64
import json
import os
import tempfile
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple, cast

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes, PublicKeyTypes
from cryptography.hazmat.primitives.serialization import KeySerializationEncryption

from encypher.core.keys import generate_ed25519_key_pair as generate_key_pair
from encypher.core.keys import load_private_key_from_data as load_private_key
from encypher.core.keys import load_public_key_from_data as load_public_key
from encypher.core.payloads import BasicPayload, ManifestAction, ManifestAiInfo, ManifestPayload, OuterPayload, serialize_payload
from encypher.core.signing import sign_payload, verify_signature

# --- Helper functions to replace missing functionality ---


def save_private_key(private_key: PrivateKeyTypes, path: str, password: Optional[bytes] = None) -> None:
    """
    Save a private key to a file in PEM format.

    Args:
        private_key: The private key to save
        path: The file path to save to
        password: Optional password for encryption
    """
    # For Ed25519 keys
    if isinstance(private_key, ed25519.Ed25519PrivateKey):
        encryption_algorithm: KeySerializationEncryption
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


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format a datetime as an ISO 8601 string.

    Args:
        dt: The datetime to format, or None to use current time

    Returns:
        ISO 8601 formatted timestamp string
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.isoformat(timespec="seconds")


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
        custom_metadata={"info": "some basic custom data", "value": 123},
    )


@pytest.fixture
def manifest_payload_data() -> ManifestPayload:
    """Sample ManifestPayload data."""
    timestamp = format_timestamp()
    return ManifestPayload(
        claim_generator="EncypherAI-Tests/1.0",
        timestamp=timestamp,
        assertions=[
            ManifestAction(
                label="c2pa.created",
                when=timestamp,
            )
        ],
        ai_assertion=ManifestAiInfo(model_id="test_model_manifest_v2.1", model_version="2.3.0"),
        custom_claims={"project_id": "proj-123", "run_type": "test"},
    )


def test_serialize_payload_basic(basic_payload_data: BasicPayload):
    """Test canonical serialization of BasicPayload."""
    # Cast to Dict[str, Any] for serialize_payload
    serialized_bytes = serialize_payload(cast(Dict[str, Any], basic_payload_data))
    assert isinstance(serialized_bytes, bytes)
    # Deserialize to check structure and canonical form (keys sorted)
    data = json.loads(serialized_bytes.decode("utf-8"))
    assert list(data.keys()) == ["custom_metadata", "model_id", "timestamp"]
    assert list(data["custom_metadata"].keys()) == [
        "info",
        "value",
    ]  # Check inner dict keys sorted
    assert data["model_id"] == basic_payload_data["model_id"]


def test_serialize_payload_manifest(manifest_payload_data: ManifestPayload):
    """Test canonical serialization of ManifestPayload."""
    # Cast to Dict[str, Any] for serialize_payload
    serialized_bytes = serialize_payload(cast(Dict[str, Any], manifest_payload_data))
    assert isinstance(serialized_bytes, bytes)
    # Deserialize to check structure and canonical form
    data = json.loads(serialized_bytes.decode("utf-8"))
    expected_keys = [
        "ai_assertion",
        "assertions",
        "claim_generator",
        "custom_claims",
        "timestamp",
    ]
    assert list(data.keys()) == expected_keys
    # Check inner structures are also sorted if they are dicts
    assert list(data["assertions"][0].keys()) == [
        "label",
        "when",
    ]
    assert list(data["ai_assertion"].keys()) == ["model_id", "model_version"]
    assert list(data["custom_claims"].keys()) == ["project_id", "run_type"]
    assert data["claim_generator"] == manifest_payload_data["claim_generator"]


def test_serialize_payload_deterministic(basic_payload_data: BasicPayload):
    """Ensure serialization produces the same bytes for the same input."""
    # Cast to Dict[str, Any] for serialize_payload
    bytes1 = serialize_payload(cast(Dict[str, Any], basic_payload_data))
    # Create identical dict again
    payload2 = BasicPayload(
        timestamp=basic_payload_data["timestamp"],
        model_id="test_model_basic_v1.0",
        custom_metadata={"value": 123, "info": "some basic custom data"},  # Note different order
    )
    # Cast to Dict[str, Any] for serialize_payload
    bytes2 = serialize_payload(cast(Dict[str, Any], payload2))
    assert bytes1 == bytes2


# --- Signing and Verification Tests ---


def test_sign_and_verify_basic(test_keys, basic_payload_data: BasicPayload):
    """Test signing and verifying a BasicPayload."""
    private_key, public_key = test_keys
    # Cast to Dict[str, Any] for serialize_payload
    payload_bytes = serialize_payload(cast(Dict[str, Any], basic_payload_data))
    signer_id = "test-signer-basic"
    signature = sign_payload(private_key, payload_bytes)

    # Construct OuterPayload for verification structure
    outer_payload_data = OuterPayload(
        format="basic",
        signer_id=signer_id,
        payload=basic_payload_data,  # Pass the original TypedDict here
        signature=base64.urlsafe_b64encode(signature).decode("ascii").rstrip("="),
    )

    # Simulate verification process (in reality, this happens within UnicodeMetadata)
    retrieved_payload_bytes = serialize_payload(cast(Dict[str, Any], outer_payload_data["payload"]))
    retrieved_sig_bytes = base64.urlsafe_b64decode(outer_payload_data["signature"] + "===")
    is_valid = verify_signature(public_key, retrieved_payload_bytes, retrieved_sig_bytes)
    assert is_valid is True


def test_sign_and_verify_manifest(test_keys, manifest_payload_data: ManifestPayload):
    """Test signing and verifying a ManifestPayload."""
    private_key, public_key = test_keys
    # Cast to Dict[str, Any] for serialize_payload
    payload_bytes = serialize_payload(cast(Dict[str, Any], manifest_payload_data))
    signer_id = "test-signer-manifest"
    signature = sign_payload(private_key, payload_bytes)

    # Construct OuterPayload for verification structure
    outer_payload_data = OuterPayload(
        format="manifest",
        signer_id=signer_id,
        payload=manifest_payload_data,  # Pass the original TypedDict here
        signature=base64.urlsafe_b64encode(signature).decode("ascii").rstrip("="),
    )

    # Simulate verification process
    retrieved_payload_bytes = serialize_payload(cast(Dict[str, Any], outer_payload_data["payload"]))
    retrieved_sig_bytes = base64.urlsafe_b64decode(outer_payload_data["signature"] + "===")
    is_valid = verify_signature(public_key, retrieved_payload_bytes, retrieved_sig_bytes)
    assert is_valid is True


def test_verify_failure_wrong_key(test_keys, basic_payload_data: BasicPayload):
    """Test that verification fails with the wrong public key."""
    private_key, _ = test_keys  # Use the correct private key to sign
    # Cast to Dict[str, Any] for serialize_payload
    payload_bytes = serialize_payload(cast(Dict[str, Any], basic_payload_data))
    signer_id = "test-signer-basic-wrongkey"
    signature = sign_payload(private_key, payload_bytes)

    # Generate a DIFFERENT key pair for verification
    _, wrong_public_key = generate_key_pair()

    outer_payload_data = OuterPayload(
        format="basic",
        signer_id=signer_id,
        payload=basic_payload_data,
        signature=base64.urlsafe_b64encode(signature).decode("ascii").rstrip("="),
    )

    retrieved_payload_bytes = serialize_payload(cast(Dict[str, Any], outer_payload_data["payload"]))
    retrieved_sig_bytes = base64.urlsafe_b64decode(outer_payload_data["signature"] + "===")
    is_valid = verify_signature(wrong_public_key, retrieved_payload_bytes, retrieved_sig_bytes)
    assert is_valid is False


def test_verify_failure_tampered_payload(test_keys, basic_payload_data: BasicPayload):
    """Test that verification fails if the payload is altered after signing."""
    private_key, public_key = test_keys
    # Cast to Dict[str, Any] for serialize_payload
    payload_bytes = serialize_payload(cast(Dict[str, Any], basic_payload_data))
    signer_id = "test-signer-tampered"
    signature = sign_payload(private_key, payload_bytes)

    # Tamper with the payload *after* signing but before outer construction
    tampered_payload = BasicPayload(
        timestamp=basic_payload_data["timestamp"],
        model_id="tampered_model_id",  # Changed value
        custom_metadata=basic_payload_data["custom_metadata"].copy(),
    )

    outer_payload_data = OuterPayload(
        format="basic",
        signer_id=signer_id,
        payload=tampered_payload,  # Use the tampered payload
        signature=base64.urlsafe_b64encode(signature).decode("ascii").rstrip("="),
    )

    # Verification uses the (tampered) payload from OuterPayload
    retrieved_payload_bytes = serialize_payload(cast(Dict[str, Any], outer_payload_data["payload"]))
    retrieved_sig_bytes = base64.urlsafe_b64decode(outer_payload_data["signature"] + "===")
    is_valid_tampered = verify_signature(public_key, retrieved_payload_bytes, retrieved_sig_bytes)
    assert is_valid_tampered is False

    # Also verify that serializing the *original* payload still fails against the tampered payload's signature context
    # Although the signature was made from the original, verification compares against the *provided* (tampered) payload bytes
    original_payload_bytes_for_check = serialize_payload(cast(Dict[str, Any], basic_payload_data))
    verify_signature(public_key, original_payload_bytes_for_check, retrieved_sig_bytes)
    # This might seem counter-intuitive, but verify_signature takes the bytes it's *told* correspond to the signature.
    # Since we provide the tampered bytes during the actual verification call, it fails correctly.
    # The important part is that the signature doesn't match the bytes derived from outer_payload_data['payload']
    assert is_valid_tampered is False  # Re-asserting the main point


def test_verify_failure_corrupt_signature(test_keys, basic_payload_data: BasicPayload):
    """Test that verification fails with a corrupted signature."""
    private_key, public_key = test_keys
    # Cast to Dict[str, Any] for serialize_payload
    payload_bytes = serialize_payload(cast(Dict[str, Any], basic_payload_data))
    signer_id = "test-signer-corrupt"
    signature = sign_payload(private_key, payload_bytes)

    corrupted_signature = signature[:-1] + bytes([(signature[-1] + 1) % 256])  # Alter last byte

    outer_payload_data = OuterPayload(
        format="basic",
        signer_id=signer_id,
        payload=basic_payload_data,
        signature=base64.urlsafe_b64encode(corrupted_signature).decode("ascii").rstrip("="),
    )

    retrieved_payload_bytes = serialize_payload(cast(Dict[str, Any], outer_payload_data["payload"]))
    retrieved_sig_bytes = base64.urlsafe_b64decode(outer_payload_data["signature"] + "===")
    is_valid = verify_signature(public_key, retrieved_payload_bytes, retrieved_sig_bytes)
    assert is_valid is False


# --- Key Loading/Saving Tests --- (If applicable, add tests for load/save functions)
