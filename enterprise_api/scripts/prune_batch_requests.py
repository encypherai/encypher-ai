"""
Cleanup utility for batch request retention.
"""
import asyncio
from datetime import datetime, timezone

from sqlalchemy import delete, select
from app.database import async_session_factory
from app.models.batch import BatchItem, BatchRequest


async def prune() -> None:
    async with async_session_factory() as session:
        cutoff = datetime.now(timezone.utc)
        batch_ids = select(BatchRequest.id).where(BatchRequest.expires_at < cutoff)
        item_result = await session.execute(
            delete(BatchItem).where(BatchItem.batch_request_id.in_(batch_ids))
        )
        request_result = await session.execute(
            delete(BatchRequest).where(BatchRequest.expires_at < cutoff)
        )
        await session.commit()

        items_deleted = item_result.rowcount or 0
        requests_deleted = request_result.rowcount or 0
        print(f"Removed {requests_deleted} batch requests and {items_deleted} batch items.")


if __name__ == "__main__":
    asyncio.run(prune())
