"""
Encypher Enterprise SDK - Python client for C2PA content signing.
"""
__version__ = "1.0.0"

from .client import EncypherClient
from .async_client import AsyncEncypherClient
from .streaming import StreamingSigner, AsyncStreamingSigner, sign_stream, async_sign_stream
from .models import (
    SignResponse,
    VerifyResponse,
    LookupResponse,
    StatsResponse,
)
from .exceptions import (
    EncypherError,
    AuthenticationError,
    QuotaExceededError,
    SigningError,
    VerificationError,
    APIError,
    ConfigurationError,
    StreamingError,
)

__all__ = [
    # Clients
    "EncypherClient",
    "AsyncEncypherClient",
    # Streaming
    "StreamingSigner",
    "AsyncStreamingSigner",
    "sign_stream",
    "async_sign_stream",
    # Models
    "SignResponse",
    "VerifyResponse",
    "LookupResponse",
    "StatsResponse",
    # Exceptions
    "EncypherError",
    "AuthenticationError",
    "QuotaExceededError",
    "SigningError",
    "VerificationError",
    "APIError",
    "ConfigurationError",
    "StreamingError",
]
