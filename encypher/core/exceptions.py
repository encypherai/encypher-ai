class EncypherError(Exception):
    """Base class for exceptions in the Encypher package."""

    pass


class PrivateKeyLoadingError(EncypherError):
    """Raised when a private key cannot be loaded."""

    pass


class PublicKeyLoadingError(EncypherError):
    """Raised when a public key cannot be loaded."""

    pass


class SigningError(EncypherError):
    """Raised when an error occurs during the signing process."""

    pass


class VerificationError(EncypherError):
    """Raised when an error occurs during the verification process."""

    pass


class PayloadSerializationError(EncypherError):
    """Raised when an error occurs during payload serialization."""

    pass


class MetadataEmbeddingError(EncypherError):
    """Raised when an error occurs during metadata embedding."""

    pass


class MetadataExtractionError(EncypherError):
    """Raised when an error occurs during metadata extraction or verification."""

    pass
