"""
Asynchronous client for Encypher Enterprise API.
"""
import httpx
from datetime import datetime
from typing import Optional, Dict, Any, List, AsyncIterator
from .models import (
    SignRequest,
    SignResponse,
    VerifyResponse,
    LookupResponse,
    StatsResponse,
    EncodeWithEmbeddingsRequest,
    EncodeWithEmbeddingsResponse,
    EmbeddingOptions,
    LicenseInfo,
    MerkleTreeDetails,
    MerkleProof,
    ExtractAndVerifyResponse,
    StreamEvent,
)
from .exceptions import (
    AuthenticationError,
    QuotaExceededError,
    SigningError,
    VerificationError,
    APIError
)
from ._sse import aiter_sse_events


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

    async def sign_with_embeddings(
        self,
        *,
        text: Optional[str] = None,
        document_id: Optional[str] = None,
        segmentation_level: str = "sentence",
        action: str = "c2pa.created",
        previous_instance_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        c2pa_manifest_url: Optional[str] = None,
        c2pa_manifest_hash: Optional[str] = None,
        custom_assertions: Optional[List[Dict[str, Any]]] = None,
        validate_assertions: bool = True,
        digital_source_type: Optional[str] = None,
        license: Optional[LicenseInfo] = None,
        embedding_options: Optional[EmbeddingOptions] = None,
        expires_at: Optional[datetime] = None,
        request: Optional[EncodeWithEmbeddingsRequest] = None,
    ) -> EncodeWithEmbeddingsResponse:
        """
        Async variant of the enterprise embeddings endpoint.
        """
        if request and any(
            value is not None
            for value in (
                text,
                document_id,
                metadata,
                previous_instance_id,
                c2pa_manifest_url,
                c2pa_manifest_hash,
                custom_assertions,
                digital_source_type,
                license,
                embedding_options,
                expires_at,
            )
        ):
            raise ValueError("Provide either `request` or keyword arguments, not both.")

        payload_model = request
        if payload_model is None:
            if text is None or document_id is None:
                raise ValueError("`text` and `document_id` are required when request is not provided.")
            payload_model = EncodeWithEmbeddingsRequest(
                text=text,
                document_id=document_id,
                segmentation_level=segmentation_level,
                action=action,
                previous_instance_id=previous_instance_id,
                metadata=metadata,
                c2pa_manifest_url=c2pa_manifest_url,
                c2pa_manifest_hash=c2pa_manifest_hash,
                custom_assertions=custom_assertions,
                validate_assertions=validate_assertions,
                digital_source_type=digital_source_type,
                license=license,
                embedding_options=embedding_options or EmbeddingOptions(),
                expires_at=expires_at,
            )

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/enterprise/embeddings/encode-with-embeddings",
                json=payload_model.model_dump(exclude_none=True)
            )
            self._handle_errors(response)
            return EncodeWithEmbeddingsResponse(**response.json())
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

    async def get_merkle_tree(self, root_id: str) -> MerkleTreeDetails:
        """
        Retrieve the stored Merkle tree for a given root identifier.
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/enterprise/merkle/tree/{root_id}"
            )
            self._handle_errors(response)
            return MerkleTreeDetails(**response.json())
        except httpx.HTTPStatusError as e:
            self._raise_api_error(e.response)

    async def get_merkle_proof(
        self,
        root_id: str,
        *,
        leaf_index: Optional[int] = None,
        leaf_hash: Optional[str] = None,
    ) -> MerkleProof:
        """
        Retrieve a Merkle proof for a specific leaf in a stored tree.
        """
        if leaf_index is None and leaf_hash is None:
            raise ValueError("Provide either leaf_index or leaf_hash.")

        params: Dict[str, Any] = {}
        if leaf_index is not None:
            params["leaf_index"] = leaf_index
        if leaf_hash is not None:
            params["leaf_hash"] = leaf_hash

        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/enterprise/merkle/tree/{root_id}/proof",
                params=params or None,
            )
            self._handle_errors(response)
            return MerkleProof(**response.json())
        except httpx.HTTPStatusError as e:
            self._raise_api_error(e.response)

    async def verify_sentence(self, text: str) -> ExtractAndVerifyResponse:
        """
        Verify text containing invisible embeddings via the public extract endpoint.
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/public/extract-and-verify",
                json={"text": text},
            )
            self._handle_errors(response)
            return ExtractAndVerifyResponse(**response.json())
        except httpx.HTTPStatusError as e:
            self._raise_api_error(e.response)

    async def stream_sign(
        self,
        text: str,
        *,
        document_title: Optional[str] = None,
        document_type: str = "article",
        document_id: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> AsyncIterator[StreamEvent]:
        """
        Stream signing progress/events via SSE from the Enterprise API.
        """
        payload = {
            "text": text,
            "document_title": document_title,
            "document_type": document_type,
            "document_id": document_id,
            "run_id": run_id,
        }
        body = {k: v for k, v in payload.items() if v is not None}

        headers = {"Accept": "text/event-stream"}
        async with self.client.stream(
            "POST",
            f"{self.base_url}/api/v1/stream/sign",
            json=body,
            headers=headers,
        ) as response:
            if response.status_code >= 400:
                response.raise_for_status()
            async for event in aiter_sse_events(response.aiter_lines()):
                yield event

    async def get_stream_run(self, run_id: str) -> Dict[str, Any]:
        """
        Retrieve persisted state for a streaming run (used for retries/resume).
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/stream/runs/{run_id}")
            self._handle_errors(response)
            return response.json()
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
