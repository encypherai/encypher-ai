"""
SSL.com API client for certificate provisioning.
"""
import httpx
from typing import Dict, Optional
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
        self.api_key = settings.ssl_com_api_key
        self.base_url = settings.ssl_com_api_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def create_code_signing_order(
        self,
        organization: str,
        country: str,
        email: str,
        validity_years: int = 2
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
        response = await self.client.post(
            f"{self.base_url}/orders",
            json={
                "product": "CODE_SIGNING_CERTIFICATE",
                "product_subtype": "C2PA_SIGNING",
                "organization_name": organization,
                "country": country,
                "email": email,
                "validity_period_years": validity_years,
                "csr_generation": "automatic"  # SSL.com generates keypair
            },
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        return response.json()

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
        response = await self.client.get(
            f"{self.base_url}/orders/{order_id}",
            headers={"Authorization": f"Bearer {self.api_key}"}
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
        response = await self.client.get(
            f"{self.base_url}/orders/{order_id}/certificate",
            headers={"Authorization": f"Bearer {self.api_key}"}
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
