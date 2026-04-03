"""
Encypher SDK - Python client for the Encypher Enterprise API.

This is an auto-generated SDK. For the source, see:
https://github.com/encypherai/encypherai-commercial/tree/main/sdk

Usage:
    from encypher.client import EncypherClient

    client = EncypherClient(api_key="your_api_key")
    result = client.sign(text="Hello, world!")
    print(result.signed_text)
"""

__all__ = [
    "EncypherClient",
]


class EncypherClient:
    """
    High-level client for the Encypher Enterprise API.

    This wraps the auto-generated API clients with a more ergonomic interface.

    Example:
        >>> client = EncypherClient(api_key="ency_...")
        >>> result = client.sign("Content to sign")
        >>> print(result.signed_text)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.encypher.com",
    ):
        """
        Initialize the Encypher client.

        Args:
            api_key: Your Encypher API key
            base_url: API base URL (default: production)
        """
        from encypher.api_client import ApiClient
        from encypher.configuration import Configuration
        from encypher.api.signing_api import SigningApi
        from encypher.api.verification_api import VerificationApi

        self.config = Configuration(
            host=base_url,
            access_token=api_key,
        )
        self.api_client = ApiClient(self.config)

        # Initialize API instances
        self._signing = SigningApi(self.api_client)
        self._verification = VerificationApi(self.api_client)

    def sign(self, text: str, **kwargs):
        """Sign content with C2PA manifest."""
        from encypher.models import SignRequest
        request = SignRequest(text=text, **kwargs)
        return self._signing.sign_content_api_v1_sign_post(request)

    def verify(self, text: str):
        """Verify signed content."""
        from encypher.models import VerifyRequest
        request = VerifyRequest(text=text)
        return self._verification.verify_content_api_v1_verify_post(request)

    def close(self):
        """Close the client."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
