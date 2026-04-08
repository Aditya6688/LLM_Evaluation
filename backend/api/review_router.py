from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.healing.review_queue import ReviewQueueService

router = APIRouter(prefix="/review-queue", tags=["review"])


class ReviewItemOut(BaseModel):
    id: str
    eval_result_id: str
    reason: str
    status: str
    resolution_note: str | None
    created_at: str
    resolved_at: str | None

    model_config = {"from_attributes": True}


class ResolveRequest(BaseModel):
    status: str  # "resolved" | "dismissed"
    resolution_note: str | None = None


@router.get("", response_model=list[ReviewItemOut])
async def list_review_items(
    status: str = Query(default="pending"),
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List review queue items by status."""
    service = ReviewQueueService(db)
    items = await service.list_items(status=status, limit=limit, offset=offset)
    return [
        ReviewItemOut(
            id=item.id,
            eval_result_id=item.eval_result_id,
            reason=item.reason,
            status=item.status,
            resolution_note=item.resolution_note,
            created_at=item.created_at.isoformat(),
            resolved_at=item.resolved_at.isoformat() if item.resolved_at else None,
        )
        for item in items
    ]


@router.patch("/{item_id}", response_model=ReviewItemOut)
async def resolve_review_item(
    item_id: str,
    request: ResolveRequest,
    db: AsyncSession = Depends(get_db),
):
    """Resolve or dismiss a review queue item."""
    service = ReviewQueueService(db)
    item = await service.resolve_item(item_id, request.status, request.resolution_note)
    if not item:
        raise HTTPException(status_code=404, detail="Review item not found")
    return ReviewItemOut(
        id=item.id,
        eval_result_id=item.eval_result_id,
        reason=item.reason,
        status=item.status,
        resolution_note=item.resolution_note,
        created_at=item.created_at.isoformat(),
        resolved_at=item.resolved_at.isoformat() if item.resolved_at else None,
    )
