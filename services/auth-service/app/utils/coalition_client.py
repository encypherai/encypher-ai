"""
Coalition Service Client
"""

import httpx
from typing import Optional
import structlog
from uuid import UUID

logger = structlog.get_logger()


class CoalitionClient:
    """Client for calling Coalition Service"""

    def __init__(self, coalition_service_url: str):
        self.base_url = coalition_service_url.rstrip("/")
        self.timeout = 10.0

    async def auto_enroll_member(
        self,
        user_id: UUID,
        tier: str,
        organization_id: Optional[UUID] = None,
    ) -> bool:
        """
        Auto-enroll a user in the coalition
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/coalition/join",
                    json={
                        "user_id": str(user_id),
                        "organization_id": str(organization_id) if organization_id else None,
                        "tier": tier,
                        "accept_terms": True,
                    },
                )

                if response.status_code == 201:
                    logger.info(
                        "coalition_auto_enrollment_success",
                        user_id=str(user_id),
                        tier=tier,
                    )
                    return True
                else:
                    upstream_detail = response.text[:500] if response.text else "(empty response)"
                    logger.warning(
                        "coalition_auto_enrollment_failed",
                        user_id=str(user_id),
                        status_code=response.status_code,
                        upstream_detail=upstream_detail,
                    )
                    raise RuntimeError(f"Coalition enrollment rejected (HTTP {response.status_code}): {upstream_detail}")

        except httpx.TimeoutException as exc:
            logger.error(
                "coalition_auto_enrollment_timeout",
                user_id=str(user_id),
            )
            raise RuntimeError("Coalition service timed out during enrollment") from exc
        except RuntimeError:
            raise
        except Exception as exc:
            logger.error(
                "coalition_auto_enrollment_error",
                user_id=str(user_id),
                error=str(exc),
            )
            raise RuntimeError(f"Coalition enrollment error: {exc}") from exc
