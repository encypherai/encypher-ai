"""Client for communicating with the Auth Service (internal endpoints)."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, cast

import httpx

from app.config import settings
from app.middleware.request_id_middleware import request_id_ctx

logger = logging.getLogger(__name__)


class AuthServiceClient:
    def __init__(self) -> None:
        self.base_url = settings.auth_service_url

    @staticmethod
    def _build_internal_headers(*, audience: str) -> Dict[str, str]:
        token = (getattr(settings, "internal_service_token", None) or "").strip()
        headers = {
            "x-request-id": request_id_ctx.get(),
            "X-Internal-Service": "enterprise_api",
            "X-Internal-Audience": audience,
            "X-Internal-Timestamp": datetime.now(timezone.utc).isoformat(),
        }
        if token:
            headers["X-Internal-Token"] = token
        return headers

    async def get_organization_context(self, organization_id: str) -> Optional[Dict[str, Any]]:
        token = (getattr(settings, "internal_service_token", None) or "").strip()
        if not token:
            logger.warning("internal_service_token_missing")
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/organizations/internal/{organization_id}/context",
                    headers=self._build_internal_headers(audience="auth_service.organization_context"),
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

    async def create_user_internal(
        self,
        email: str,
        name: str,
        password: str,
    ) -> dict:
        """Create a new user account via the auth-service internal endpoint.

        Used by the team invite accept-new flow to create accounts for invited
        users without requiring a separate email verification step.

        Raises RuntimeError on non-200 responses (caller checks for '409' in
        the message to detect duplicate-email conflicts).
        """
        token = (getattr(settings, "internal_service_token", None) or "").strip()
        if not token:
            raise RuntimeError("internal_service_token_missing")
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/internal/users/create",
                    headers=self._build_internal_headers(audience="auth_service.user_create"),
                    json={"email": email, "name": name, "password": password},
                )
        except httpx.RequestError as exc:
            logger.warning("create_user_internal_request_failed error=%s", str(exc))
            raise RuntimeError(f"create_user_internal request failed: {exc}") from exc

        if response.status_code != 200:
            raise RuntimeError(f"create_user_internal failed: {response.status_code} {response.text}")

        payload = response.json()
        if not (isinstance(payload, dict) and payload.get("success") and isinstance(payload.get("data"), dict)):
            raise RuntimeError(f"create_user_internal unexpected response: {payload}")

        return dict(payload["data"])

    async def set_default_organization(
        self,
        user_id: str,
        organization_id: str,
    ) -> None:
        """Set a user's default organization via the auth-service internal endpoint.

        Called after team invite acceptance so the setup wizard can complete.
        Best-effort: logs a warning on failure rather than raising, since the
        membership row is already committed and the admin can fix it manually.
        """
        token = (getattr(settings, "internal_service_token", None) or "").strip()
        if not token:
            logger.warning("set_default_organization skipped: internal_service_token_missing")
            return
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/internal/users/set-default-org",
                    headers=self._build_internal_headers(audience="auth_service.set_default_org"),
                    json={"user_id": user_id, "organization_id": organization_id},
                )
            if response.status_code != 200:
                logger.warning(
                    "set_default_organization_failed status=%s body=%s",
                    response.status_code,
                    response.text,
                )
        except httpx.RequestError as exc:
            logger.warning("set_default_organization_request_failed error=%s", str(exc))

    async def bulk_provision_publishers(
        self,
        publishers: List[Dict[str, Any]],
        partner_org_id: str,
        partner_name: str,
        send_claim_email: bool = False,
    ) -> Dict[str, Any]:
        """Bulk-provision publisher orgs via the auth-service internal endpoint.

        send_claim_email is False by default because enterprise_api sends the
        partner-branded claim email after rights profiles are set up.
        """
        token = (getattr(settings, "internal_service_token", None) or "").strip()
        if not token:
            raise RuntimeError("internal_service_token_missing")
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/organizations/internal/bulk-provision",
                    headers=self._build_internal_headers(audience="auth_service.bulk_provision"),
                    json={
                        "publishers": publishers,
                        "partner_org_id": partner_org_id,
                        "partner_name": partner_name,
                        "send_claim_email": send_claim_email,
                    },
                )
        except httpx.RequestError as exc:
            logger.warning("bulk_provision_request_failed error=%s", str(exc))
            raise
        if response.status_code != 200:
            raise RuntimeError(f"bulk-provision failed: {response.status_code} {response.text}")
        return cast(Dict[str, Any], response.json())


auth_service_client = AuthServiceClient()
