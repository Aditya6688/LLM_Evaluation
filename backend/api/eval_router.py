from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.database import get_db
from backend.db.models import EvalResult
from backend.evaluation.models import EvalResultOut

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get("", response_model=list[EvalResultOut])
async def list_evaluations(
    model_used: str | None = None,
    min_faithfulness: float | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List evaluation results with optional filtering."""
    stmt = select(EvalResult).order_by(EvalResult.created_at.desc())

    if model_used:
        stmt = stmt.where(EvalResult.model_used == model_used)
    if min_faithfulness is not None:
        stmt = stmt.where(EvalResult.faithfulness >= min_faithfulness)

    stmt = stmt.offset(offset).limit(limit)
    result = await db.execute(stmt)
    rows = result.scalars().all()

    return [
        EvalResultOut(
            id=r.id,
            query=r.query,
            response=r.response,
            contexts=r.contexts,
            faithfulness=r.faithfulness,
            answer_relevancy=r.answer_relevancy,
            context_precision=r.context_precision,
            context_recall=r.context_recall,
            model_used=r.model_used,
            is_retry=r.is_retry,
            latency_ms=r.latency_ms,
            token_count=r.token_count,
            cost_usd=r.cost_usd,
            trace_id=r.trace_id,
            created_at=r.created_at.isoformat(),
        )
        for r in rows
    ]
