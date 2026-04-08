from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.db.models import EvalResult, ReviewItem

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class ScoreTrendPoint(BaseModel):
    date: str
    avg_faithfulness: float
    avg_relevancy: float
    query_count: int


class DashboardStats(BaseModel):
    model_config = {"protected_namespaces": ()}

    total_queries: int
    avg_faithfulness: float
    avg_relevancy: float
    retry_rate: float
    review_queue_pending: int
    model_usage: dict[str, int]
    cost_total_usd: float
    score_trend: list[ScoreTrendPoint]


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get aggregated metrics for the dashboard."""
    # Total queries and averages
    stmt = select(
        func.count(EvalResult.id),
        func.avg(EvalResult.faithfulness),
        func.avg(EvalResult.answer_relevancy),
        func.sum(EvalResult.cost_usd),
    )
    result = await db.execute(stmt)
    row = result.one()
    total_queries = row[0] or 0
    avg_faithfulness = float(row[1] or 0)
    avg_relevancy = float(row[2] or 0)
    cost_total = float(row[3] or 0)

    # Retry rate
    retry_stmt = select(func.count(EvalResult.id)).where(EvalResult.is_retry == True)
    retry_result = await db.execute(retry_stmt)
    retry_count = retry_result.scalar() or 0
    retry_rate = retry_count / total_queries if total_queries > 0 else 0

    # Pending reviews
    pending_stmt = select(func.count(ReviewItem.id)).where(ReviewItem.status == "pending")
    pending_result = await db.execute(pending_stmt)
    pending_count = pending_result.scalar() or 0

    # Model usage breakdown
    model_stmt = select(EvalResult.model_used, func.count(EvalResult.id)).group_by(EvalResult.model_used)
    model_result = await db.execute(model_stmt)
    model_usage = {row[0]: row[1] for row in model_result.all()}

    # Score trend (daily)
    trend_stmt = (
        select(
            func.date(EvalResult.created_at).label("date"),
            func.avg(EvalResult.faithfulness),
            func.avg(EvalResult.answer_relevancy),
            func.count(EvalResult.id),
        )
        .group_by(func.date(EvalResult.created_at))
        .order_by(func.date(EvalResult.created_at))
        .limit(30)
    )
    trend_result = await db.execute(trend_stmt)
    score_trend = [
        ScoreTrendPoint(
            date=str(row[0]),
            avg_faithfulness=float(row[1] or 0),
            avg_relevancy=float(row[2] or 0),
            query_count=row[3],
        )
        for row in trend_result.all()
    ]

    return DashboardStats(
        total_queries=total_queries,
        avg_faithfulness=avg_faithfulness,
        avg_relevancy=avg_relevancy,
        retry_rate=retry_rate,
        review_queue_pending=pending_count,
        model_usage=model_usage,
        cost_total_usd=cost_total,
        score_trend=score_trend,
    )
