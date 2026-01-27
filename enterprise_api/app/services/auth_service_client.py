"""Client for communicating with the Auth Service (internal endpoints)."""

import logging
from typing import Any, Dict, Optional, cast

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class AuthServiceClient:
    def __init__(self) -> None:
        self.base_url = settings.auth_service_url

    async def get_organization_context(self, organization_id: str) -> Optional[Dict[str, Any]]:
        token = (getattr(settings, "internal_service_token", None) or "").strip()
        if not token:
            logger.warning("internal_service_token_missing")
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/organizations/internal/{organization_id}/context",
                    headers={"X-Internal-Token": token},
                    timeout=5.0,
                )
        except httpx.RequestError as exc:
            logger.warning("auth_service_request_failed", extra={"error": str(exc)})
            return None

        if response.status_code != 200:
            logger.warning(
                "auth_service_unexpected_status",
                extra={"status": response.status_code, "body": response.text},
            )
            return None

        payload = cast(Dict[str, Any], response.json())
        if not (isinstance(payload, dict) and payload.get("success") and isinstance(payload.get("data"), dict)):
            return None

        return cast(Dict[str, Any], payload["data"])


auth_service_client = AuthServiceClient()
