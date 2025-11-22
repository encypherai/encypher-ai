"""
Custom exceptions for Encypher Enterprise SDK.
"""
from typing import Optional, Dict, Any


class EncypherError(Exception):
    """Base exception for all Encypher SDK errors."""
    pass


class AuthenticationError(EncypherError):
    """Raised when API key authentication fails."""
    pass


class QuotaExceededError(EncypherError):
    """Raised when monthly API quota is exceeded."""
    pass


class SigningError(EncypherError):
    """Raised when content signing fails."""
    pass


class VerificationError(EncypherError):
    """Raised when content verification fails."""
    pass


class LookupError(EncypherError):
    """Raised when sentence lookup fails."""
    pass


class APIError(EncypherError):
    """
    Raised for general API errors.

    Attributes:
        status_code: HTTP status code
        message: Error message
        details: Additional error details from API
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        detail_str = str(self.details.get("detail", "")) or str(self.details)
        super().__init__(f"HTTP {status_code}: {message} | Detail: {detail_str}")


class ConfigurationError(EncypherError):
    """Raised when SDK configuration is invalid."""
    pass


class StreamingError(EncypherError):
    """Raised when streaming operations fail."""
    pass
