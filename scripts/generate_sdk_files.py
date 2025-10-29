#!/usr/bin/env python3
"""
Script to generate all Encypher Enterprise SDK files.
"""
from pathlib import Path

SDK_ROOT = Path(__file__).parent.parent / "enterprise_sdk"

# File contents as dictionary
FILES = {
    "encypher_enterprise/config.py": '''"""
Configuration for Encypher Enterprise SDK.
"""
from typing import Optional
from pydantic_settings import BaseSettings


class EncypherConfig(BaseSettings):
    """SDK configuration from environment variables."""

    encypher_api_key: Optional[str] = None
    encypher_base_url: str = "https://api.encypherai.com"
    encypher_timeout: float = 30.0
    encypher_max_retries: int = 3

    class Config:
        env_prefix = "ENCYPHER_"
        case_sensitive = False


def get_config() -> EncypherConfig:
    """Get SDK configuration."""
    return EncypherConfig()
''',

    "encypher_enterprise/client.py": '''"""
Synchronous client for Encypher Enterprise API.
"""
import httpx
from typing import Optional
from .models import SignRequest, SignResponse, VerifyResponse, LookupResponse, StatsResponse
from .exceptions import (
    AuthenticationError,
    QuotaExceededError,
    SigningError,
    VerificationError,
    APIError
)


class EncypherClient:
    """
    Synchronous client for Encypher Enterprise API.

    Example:
        >>> client = EncypherClient(api_key="encypher_...")
        >>> result = client.sign("Content to sign", title="My Document")
        >>> print(result.signed_text)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.encypherai.com",
        timeout: float = 30.0,
        max_retries: int = 3
    ):
        """
        Initialize the Encypher client.

        Args:
            api_key: Your Encypher API key
            base_url: API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"}
        )
        self.max_retries = max_retries

    def sign(
        self,
        text: str,
        title: Optional[str] = None,
        url: Optional[str] = None,
        document_type: str = "article"
    ) -> SignResponse:
        """
        Sign content with C2PA manifest.

        Args:
            text: Content to sign
            title: Optional document title
            url: Optional document URL
            document_type: Document type (article, legal_brief, contract, ai_output)

        Returns:
            SignResponse with signed text and metadata

        Raises:
            SigningError: If signing fails
            AuthenticationError: If API key is invalid
            QuotaExceededError: If quota is exceeded
        """
        request = SignRequest(
            text=text,
            document_title=title,
            document_url=url,
            document_type=document_type
        )

        try:
            response = self.client.post(
                f"{self.base_url}/api/v1/sign",
                json=request.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return SignResponse(**response.json())
        except httpx.HTTPStatusError as e:
            self._raise_api_error(e.response)

    def verify(self, text: str) -> VerifyResponse:
        """
        Verify C2PA manifest in signed content.

        Args:
            text: Signed text to verify

        Returns:
            VerifyResponse with verification results

        Raises:
            VerificationError: If verification fails
        """
        try:
            response = self.client.post(
                f"{self.base_url}/api/v1/verify",
                json={"text": text}
            )
            self._handle_errors(response)
            return VerifyResponse(**response.json())
        except httpx.HTTPStatusError as e:
            self._raise_api_error(e.response)

    def lookup(self, sentence: str) -> LookupResponse:
        """
        Look up sentence provenance.

        Args:
            sentence: Sentence to look up

        Returns:
            LookupResponse with provenance information
        """
        try:
            response = self.client.post(
                f"{self.base_url}/api/v1/lookup",
                json={"sentence_text": sentence}
            )
            self._handle_errors(response)
            return LookupResponse(**response.json())
        except httpx.HTTPStatusError as e:
            self._raise_api_error(e.response)

    def get_stats(self) -> StatsResponse:
        """
        Get organization usage statistics.

        Returns:
            StatsResponse with usage stats
        """
        try:
            response = self.client.get(f"{self.base_url}/stats")
            self._handle_errors(response)
            return StatsResponse(**response.json())
        except httpx.HTTPStatusError as e:
            self._raise_api_error(e.response)

    def _handle_errors(self, response: httpx.Response) -> None:
        """Handle HTTP errors."""
        if response.status_code >= 400:
            response.raise_for_status()

    def _raise_api_error(self, response: httpx.Response) -> None:
        """Raise appropriate exception based on response."""
        try:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", "Unknown error")
            error_code = error_data.get("error", {}).get("code", "UNKNOWN")
        except:
            error_msg = response.text
            error_code = "UNKNOWN"

        if response.status_code == 401:
            raise AuthenticationError(error_msg)
        elif response.status_code == 429:
            raise QuotaExceededError(error_msg)
        elif "sign" in response.url.path.lower():
            raise SigningError(error_msg)
        elif "verify" in response.url.path.lower():
            raise VerificationError(error_msg)
        else:
            raise APIError(response.status_code, error_msg, {"code": error_code})

    def close(self) -> None:
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, *args):
        """Context manager exit."""
        self.close()
''',

    "encypher_enterprise/__init__.py": '''"""
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
''',
}

def main():
    """Generate all SDK files."""
    for file_path, content in FILES.items():
        full_path = SDK_ROOT / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        print(f"✅ Created: {file_path}")

    print(f"\n✅ Generated {len(FILES)} SDK files")

if __name__ == "__main__":
    main()
