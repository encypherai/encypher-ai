"""
Asynchronous client for Encypher Enterprise API.
"""
import httpx
from typing import Optional, Dict, Any
from .models import SignRequest, SignResponse, VerifyResponse, LookupResponse, StatsResponse
from .exceptions import (
    AuthenticationError,
    QuotaExceededError,
    SigningError,
    VerificationError,
    APIError
)


class AsyncEncypherClient:
    """
    Asynchronous client for Encypher Enterprise API.

    Example:
        >>> async with AsyncEncypherClient(api_key="encypher_...") as client:
        ...     result = await client.sign("Content to sign")
        ...     print(result.signed_text)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.encypherai.com",
        timeout: float = 30.0,
        max_retries: int = 3,
        transport: Optional[httpx.BaseTransport] = None,
    ):
        """
        Initialize the async Encypher client.

        Args:
            api_key: Your Encypher API key
            base_url: API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"},
            transport=transport,
        )
        self.max_retries = max_retries

    async def sign(
        self,
        text: str,
        title: Optional[str] = None,
        url: Optional[str] = None,
        document_type: str = "article",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SignResponse:
        """
        Async sign content with C2PA manifest.

        Args:
            text: Content to sign
            title: Optional document title
            url: Optional document URL
            document_type: Document type
            metadata: Optional metadata dict to include with the signing request

        Returns:
            SignResponse with signed text

        Raises:
            SigningError: If signing fails
        """
        request = SignRequest(
            text=text,
            document_title=title,
            document_url=url,
            document_type=document_type,
            custom_metadata=metadata
        )

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/sign",
                json=request.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return SignResponse(**response.json())
        except httpx.HTTPStatusError as e:
            self._raise_api_error(e.response)

    async def verify(self, text: str) -> VerifyResponse:
        """
        Async verify C2PA manifest.

        Args:
            text: Signed text to verify

        Returns:
            VerifyResponse with verification results
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/verify",
                json={"text": text}
            )
            self._handle_errors(response)
            return VerifyResponse(**response.json())
        except httpx.HTTPStatusError as e:
            self._raise_api_error(e.response)

    async def lookup(self, sentence: str) -> LookupResponse:
        """
        Async look up sentence provenance.

        Args:
            sentence: Sentence to look up

        Returns:
            LookupResponse with provenance information
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/lookup",
                json={"sentence_text": sentence}
            )
            self._handle_errors(response)
            return LookupResponse(**response.json())
        except httpx.HTTPStatusError as e:
            self._raise_api_error(e.response)

    async def get_stats(self) -> StatsResponse:
        """
        Async get organization statistics.

        Returns:
            StatsResponse with usage stats
        """
        try:
            response = await self.client.get(f"{self.base_url}/stats")
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

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args):
        """Async context manager exit."""
        await self.close()
