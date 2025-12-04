"""
SSL.com API client for certificate provisioning.
"""
from typing import Dict

import httpx

from app.config import settings


class SSLComClient:
    """
    Client for SSL.com certificate issuance API.

    This client handles:
    - Creating code signing certificate orders
    - Checking order status
    - Downloading issued certificates
    """

    def __init__(self):
        """Initialize SSL.com API client."""
        self.api_key = settings.ssl_com_api_key  # maps to SWS secret_key
        self.account_key = getattr(settings, "ssl_com_account_key", None)
        self.base_url = settings.ssl_com_api_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)

    def _is_sws(self) -> bool:
        """Detect if configured to use SWS endpoints (sws-test or production SWS)."""
        u = self.base_url.lower()
        return ("sws" in u) or ("sslpki" in u)

    async def create_code_signing_order(
        self,
        organization: str,
        country: str,
        email: str,
        validity_years: int = 2,
        product_id: str = "106"
    ) -> Dict:
        """
        Create SSL.com code signing certificate order.

        Args:
            organization: Organization name
            country: Country code (e.g., 'US')
            email: Contact email
            validity_years: Certificate validity period

        Returns:
            Order details including validation URL

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        if self._is_sws():
            if not self.account_key:
                raise ValueError("SSL_COM_ACCOUNT_KEY is required for SWS API calls")
            # SWS: POST /certificates with account_key and secret_key in body
            sws_product = getattr(settings, "ssl_com_product_id", None) or product_id
            payload = {
                "account_key": self.account_key,
                "secret_key": self.api_key,
                "product": sws_product,
                # Approximate mapping of our inputs to SWS fields
                "period": str(365 * max(1, int(validity_years))),
                "organization_name": organization,
                "country_name": country,
                "email": email,
                # CSR is typically required for server certs; for workflows that do not
                # supply a CSR via API, the order will remain pending until completed via portal.
            }
            response = await self.client.post(
                f"{self.base_url}/certificates",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
        else:
            # Legacy (Bearer) flow
            response = await self.client.post(
                f"{self.base_url}/orders",
                json={
                    "product": "CODE_SIGNING_CERTIFICATE",
                    "product_subtype": "C2PA_SIGNING",
                    "organization_name": organization,
                    "country": country,
                    "email": email,
                    "validity_period_years": validity_years,
                    "csr_generation": "automatic",
                },
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        response.raise_for_status()
        data = response.json()
        # Normalize SWS response keys to expected fields
        if self._is_sws():
            # SWS returns 'ref' as the order reference and may include 'validation_url'
            return {
                "order_id": data.get("ref") or data.get("order_id"),
                "validation_url": data.get("validation_url"),
                **data,
            }
        return data

    async def get_order_status(self, order_id: str) -> Dict:
        """
        Poll order status.

        Args:
            order_id: SSL.com order ID

        Returns:
            Order status details

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        if self._is_sws():
            if not self.account_key:
                raise ValueError("SSL_COM_ACCOUNT_KEY is required for SWS API calls")
            response = await self.client.get(
                f"{self.base_url}/certificate/{order_id}",
                params={
                    "account_key": self.account_key,
                    "secret_key": self.api_key,
                },
            )
        else:
            response = await self.client.get(
                f"{self.base_url}/orders/{order_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
        response.raise_for_status()
        return response.json()

    async def download_certificate(self, order_id: str) -> Dict:
        """
        Download issued certificate and chain.

        Args:
            order_id: SSL.com order ID

        Returns:
            Dictionary containing:
                - certificate: PEM-encoded certificate
                - chain: List of PEM-encoded chain certificates
                - expires_at: Expiration timestamp

        Raises:
            httpx.HTTPStatusError: If API request fails
        """
        if self._is_sws():
            if not self.account_key:
                raise ValueError("SSL_COM_ACCOUNT_KEY is required for SWS API calls")
            response = await self.client.get(
                f"{self.base_url}/certificate/{order_id}",
                params={
                    "account_key": self.account_key,
                    "secret_key": self.api_key,
                    "response_type": "individually",
                    "response_encoding": "base64",
                },
            )
        else:
            response = await self.client.get(
                f"{self.base_url}/orders/{order_id}/certificate",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
