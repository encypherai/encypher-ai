from typing import Optional, Union

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from .exceptions import EncypherError, PrivateKeyLoadingError, PublicKeyLoadingError
from .logging_config import logger


def generate_ed25519_key_pair() -> tuple[ed25519.Ed25519PrivateKey, ed25519.Ed25519PublicKey]:
    """
    Generates an Ed25519 key pair.

    Returns:
        Tuple containing the private and public keys.
    """
    try:
        logger.debug("Generating new Ed25519 key pair.")
        private_key = ed25519.Ed25519PrivateKey.generate()
        logger.info("Successfully generated Ed25519 private key.")
        public_key = private_key.public_key()
        logger.debug("Successfully generated corresponding Ed25519 public key.")
        return private_key, public_key
    except Exception as e:
        logger.error(f"Failed to generate Ed25519 key pair: {e}", exc_info=True)
        raise


def load_ed25519_private_key(filepath: str) -> ed25519.Ed25519PrivateKey:
    """Loads an Ed25519 private key from a PEM file."""
    logger.debug(f"Attempting to load private key from: {filepath}")
    try:
        with open(filepath, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,  # Assuming keys are not password-protected
            )
        if not isinstance(private_key, ed25519.Ed25519PrivateKey):
            logger.error(f"Key in {filepath} is not an Ed25519 private key.")
            raise PrivateKeyLoadingError(f"Not an Ed25519 private key: {filepath}")
        logger.info(f"Successfully loaded Ed25519 private key from {filepath}.")
        return private_key
    except FileNotFoundError:
        logger.error(f"Private key file not found: {filepath}")
        raise PrivateKeyLoadingError(f"Private key file not found: {filepath}") from None
    except ValueError as e:  # Catches issues from load_pem_private_key like bad format
        logger.error(f"Error loading PEM private key from {filepath}: {e}", exc_info=True)
        raise PrivateKeyLoadingError(f"Invalid PEM format or key type in {filepath}: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error loading private key from {filepath}: {e}", exc_info=True)
        raise PrivateKeyLoadingError(f"Could not load private key from {filepath}: {e}") from e


def load_ed25519_public_key(filepath: str) -> ed25519.Ed25519PublicKey:
    """Loads an Ed25519 public key from a PEM file."""
    logger.debug(f"Attempting to load public key from: {filepath}")
    try:
        with open(filepath, "rb") as key_file:
            public_key = serialization.load_pem_public_key(key_file.read())
        if not isinstance(public_key, ed25519.Ed25519PublicKey):
            logger.error(f"Key in {filepath} is not an Ed25519 public key.")
            raise PublicKeyLoadingError(f"Not an Ed25519 public key: {filepath}")
        logger.info(f"Successfully loaded Ed25519 public key from {filepath}.")
        return public_key
    except FileNotFoundError:
        logger.error(f"Public key file not found: {filepath}")
        raise PublicKeyLoadingError(f"Public key file not found: {filepath}") from None
    except ValueError as e:  # Catches issues from load_pem_public_key
        logger.error(f"Error loading PEM public key from {filepath}: {e}", exc_info=True)
        raise PublicKeyLoadingError(f"Invalid PEM format or key type in {filepath}: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error loading public key from {filepath}: {e}", exc_info=True)
        raise PublicKeyLoadingError(f"Could not load public key from {filepath}: {e}") from e


def save_ed25519_key_pair_to_files(
    private_key: ed25519.Ed25519PrivateKey,
    public_key: ed25519.Ed25519PublicKey,
    private_key_path: str,
    public_key_path: str,
) -> None:
    """Saves the Ed25519 key pair to PEM files."""
    logger.debug(f"Attempting to save private key to: {private_key_path}")
    try:
        with open(private_key_path, "wb") as f:
            f.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )
            )
        logger.info(f"Private key successfully saved to {private_key_path}.")
    except OSError as e:
        logger.error(f"Failed to write private key to {private_key_path}: {e}", exc_info=True)
        raise EncypherError(f"Could not write private key to file: {e}") from e

    logger.debug(f"Attempting to save public key to: {public_key_path}")
    try:
        with open(public_key_path, "wb") as f:
            f.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )
        logger.info(f"Public key successfully saved to {public_key_path}.")
    except OSError as e:
        logger.error(f"Failed to write public key to {public_key_path}: {e}", exc_info=True)
        raise EncypherError(f"Could not write public key to file: {e}") from e


def load_private_key_from_data(key_data: Union[bytes, str], password: Optional[bytes] = None) -> ed25519.Ed25519PrivateKey:
    """
    Loads an Ed25519 private key from PEM-encoded bytes or string,
    or from raw bytes (32 bytes).

    Args:
        key_data: PEM string/bytes or raw private key bytes.
        password: Optional password for encrypted PEM keys.

    Returns:
        Ed25519 private key object.

    Raises:
        ValueError: If the key format is invalid or unsupported.
        TypeError: If key_data has an invalid type.
    """
    input_was_string = isinstance(key_data, str)
    key_data_bytes: bytes

    if input_was_string:
        logger.debug("Received private key as string, encoding to ASCII for PEM processing.")
        try:
            key_data_bytes = key_data.encode("ascii")  # type: ignore
        except UnicodeEncodeError:
            logger.error("Failed to encode private key string to ASCII.")
            raise ValueError("Private key string contains non-ASCII characters, expected PEM format.") from None
    elif isinstance(key_data, bytes):
        key_data_bytes = key_data
    else:
        logger.error(f"Invalid type for key_data: {type(key_data)}.")
        raise TypeError("key_data must be bytes or a PEM string")

    # --- Process key_data_bytes ---
    logger.debug(f"Processing private key data ({len(key_data_bytes)} bytes).")

    # Check for PEM formats first
    if b"-----BEGIN PRIVATE KEY-----" in key_data_bytes:  # Unencrypted PKCS8
        logger.debug("Detected unencrypted PKCS8 PEM format.")
        try:
            loaded_key = serialization.load_pem_private_key(
                key_data_bytes,
                password=None,  # Explicitly None for unencrypted
            )
            if isinstance(loaded_key, ed25519.Ed25519PrivateKey):
                logger.info("Successfully loaded Ed25519 private key from unencrypted PEM.")
                return loaded_key
            else:
                logger.warning(f"PEM data yielded unexpected key type: {type(loaded_key)}.")
                raise ValueError("PEM data did not yield an Ed25519 private key")
        except Exception as e:
            logger.error(f"Failed to load unencrypted PEM private key: {e}", exc_info=True)
            raise ValueError(f"Failed to load unencrypted PEM private key: {e}") from e

    elif b"-----BEGIN ENCRYPTED PRIVATE KEY-----" in key_data_bytes:
        logger.debug("Detected encrypted PKCS8 PEM format.")
        if password is None:
            logger.error("Password required for encrypted private key, but none provided.")
            raise ValueError("Password required for encrypted private key")
        try:
            loaded_key = serialization.load_pem_private_key(
                key_data_bytes,
                password=password,
            )
            if isinstance(loaded_key, ed25519.Ed25519PrivateKey):
                logger.info("Successfully loaded Ed25519 private key from encrypted PEM.")
                return loaded_key
            else:
                logger.warning(f"Encrypted PEM data yielded unexpected key type: {type(loaded_key)}.")
                raise ValueError("Encrypted PEM data did not yield an Ed25519 private key")
        except Exception as e:
            logger.error(f"Failed to load encrypted PEM private key: {e}", exc_info=True)
            raise ValueError(f"Failed to load encrypted PEM private key: {e}") from e

    # Check for raw bytes (only if input wasn't a string)
    elif not input_was_string and len(key_data_bytes) == 32:
        logger.debug("Detected potential raw Ed25519 private key (32 bytes).")
        try:
            key = ed25519.Ed25519PrivateKey.from_private_bytes(key_data_bytes)
            logger.info("Successfully loaded Ed25519 private key from raw bytes.")
            return key
        except Exception as e:
            logger.error(f"Failed to load raw private key bytes: {e}", exc_info=True)
            raise ValueError(f"Failed to load raw private key bytes: {e}") from e

    # If none of the above matched
    logger.error("Private key data does not match expected PEM formats or raw byte length.")
    if input_was_string:
        raise ValueError("Invalid PEM format in string key_data")
    else:  # Input was bytes, but not PEM or correct raw length
        raise ValueError("Invalid private key byte length or format (expected PEM or 32 raw bytes)")


def load_public_key_from_data(key_data: Union[bytes, str]) -> ed25519.Ed25519PublicKey:
    """
    Loads an Ed25519 public key from PEM-encoded bytes or string,
    or from raw bytes (32 bytes).

    Args:
        key_data: PEM string/bytes or raw public key bytes.

    Returns:
        Ed25519 public key object.

    Raises:
        ValueError: If the key format is invalid or unsupported.
        TypeError: If key_data has an invalid type.
    """
    if isinstance(key_data, str):
        key_data_bytes = key_data.encode("utf-8")  # Assume PEM if string
        logger.debug("Received public key as string, encoded to UTF-8 for PEM processing.")
    elif isinstance(key_data, bytes):
        key_data_bytes = key_data
        logger.debug(f"Processing public key data ({len(key_data_bytes)} bytes).")
    else:
        logger.error(f"Invalid type for key_data: {type(key_data)}.")
        raise TypeError("key_data must be bytes or a PEM string")

    if b"-----BEGIN PUBLIC KEY-----" in key_data_bytes:  # Check for PEM format (SPKI)
        logger.debug("Detected SPKI PEM format for public key.")
        try:
            loaded_key = serialization.load_pem_public_key(key_data_bytes)
            if isinstance(loaded_key, ed25519.Ed25519PublicKey):
                logger.info("Successfully loaded Ed25519 public key from PEM.")
                return loaded_key
            else:
                logger.warning(f"PEM data yielded unexpected key type: {type(loaded_key)}.")
                raise ValueError("PEM data is not an Ed25519 public key")
        except Exception as e:
            logger.error(f"Failed to load PEM public key: {e}", exc_info=True)
            raise ValueError(f"Failed to load PEM public key: {e}") from e
    elif len(key_data_bytes) == 32:  # Ed25519 public key is 32 bytes
        logger.debug("Detected potential raw Ed25519 public key (32 bytes).")
        try:
            key = ed25519.Ed25519PublicKey.from_public_bytes(key_data_bytes)
            logger.info("Successfully loaded Ed25519 public key from raw bytes.")
            return key
        except Exception as e:
            logger.error(f"Failed to load raw public key bytes: {e}", exc_info=True)
            raise ValueError(f"Failed to load raw public key bytes: {e}") from e
    else:
        logger.error(f"Invalid public key byte length or format: {len(key_data_bytes)} bytes.")
        raise ValueError("Invalid public key byte length or format")
