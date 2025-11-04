"""
Coalition Service Client for Enterprise API
"""
import httpx
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CoalitionClient:
    """Client for calling Coalition Service"""

    def __init__(self, coalition_service_url: str, timeout: float = 10.0):
        self.base_url = coalition_service_url.rstrip("/")
        self.timeout = timeout

    async def get_member_by_user_id(self, user_id: str) -> Optional[dict]:
        """
        Get coalition member by user_id
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/coalition/status/{user_id}"
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        return data.get("data")

                logger.warning(
                    f"Coalition member not found for user {user_id}: "
                    f"status={response.status_code}"
                )
                return None

        except httpx.TimeoutException:
            logger.error(f"Coalition service timeout for user {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching coalition member: {e}")
            return None

    async def index_content(
        self,
        member_id: str,
        document_id: str,
        content_hash: str,
        content_type: Optional[str] = None,
        word_count: Optional[int] = None,
        signed_at: Optional[datetime] = None,
    ) -> bool:
        """
        Index signed content in coalition
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/coalition/content",
                    json={
                        "member_id": member_id,
                        "document_id": document_id,
                        "content_hash": content_hash,
                        "content_type": content_type,
                        "word_count": word_count,
                        "signed_at": signed_at.isoformat() if signed_at else None,
                    },
                )

                if response.status_code == 201:
                    logger.info(
                        f"Successfully indexed content in coalition: "
                        f"document={document_id}, member={member_id}"
                    )
                    return True
                else:
                    logger.warning(
                        f"Failed to index content in coalition: "
                        f"status={response.status_code}, response={response.text}"
                    )
                    return False

        except httpx.TimeoutException:
            logger.error(f"Coalition service timeout indexing document {document_id}")
            return False
        except Exception as e:
            logger.error(f"Error indexing content in coalition: {e}")
            return False

    async def get_member_stats(self, user_id: str) -> Optional[dict]:
        """
        Get coalition statistics for a member
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/coalition/stats/{user_id}"
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        return data.get("data")

                return None

        except Exception as e:
            logger.error(f"Error fetching coalition stats: {e}")
            return None
