from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import ReviewItem


class ReviewQueueService:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create_review_item(self, eval_result_id: str, reason: str) -> ReviewItem:
        item = ReviewItem(eval_result_id=eval_result_id, reason=reason)
        self._db.add(item)
        await self._db.commit()
        await self._db.refresh(item)
        return item

    async def list_items(
        self, status: str = "pending", limit: int = 20, offset: int = 0
    ) -> list[ReviewItem]:
        stmt = (
            select(ReviewItem)
            .where(ReviewItem.status == status)
            .order_by(ReviewItem.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def resolve_item(
        self, item_id: str, status: str, resolution_note: str | None = None
    ) -> ReviewItem | None:
        stmt = select(ReviewItem).where(ReviewItem.id == item_id)
        result = await self._db.execute(stmt)
        item = result.scalar_one_or_none()
        if not item:
            return None

        item.status = status
        item.resolution_note = resolution_note
        item.resolved_at = datetime.now(timezone.utc)
        await self._db.commit()
        await self._db.refresh(item)
        return item

    async def get_stats(self) -> dict:
        stmt = select(ReviewItem.status, func.count(ReviewItem.id)).group_by(ReviewItem.status)
        result = await self._db.execute(stmt)
        counts = {row[0]: row[1] for row in result.all()}
        return {
            "pending": counts.get("pending", 0),
            "resolved": counts.get("resolved", 0),
            "dismissed": counts.get("dismissed", 0),
        }
