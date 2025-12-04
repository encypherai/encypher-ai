"""
Service for handling statistical updates in the background.
Separated to ensure non-blocking operations and proper session management.
"""
import logging
from datetime import datetime

from sqlalchemy import text

from app.database import async_session_factory

logger = logging.getLogger(__name__)


class StatService:
    """Service for background statistical updates."""

    async def update_api_key_last_used(self, api_key: str):
        """
        Update the last_used_at timestamp for an API key.
        
        This runs in a background task with its own database session
        to avoid blocking the main request or using a closed session.
        
        Args:
            api_key: The API key to update
        """
        try:
            async with async_session_factory() as session:
                await session.execute(
                    text("UPDATE api_keys SET last_used_at = :last_used_at WHERE api_key = :api_key"),
                    {"api_key": api_key, "last_used_at": datetime.utcnow()},
                )
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to update API key stats for {api_key[:8]}...: {e}")


stat_service = StatService()
