from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.dependencies import get_query_service
from backend.evaluation.models import QueryResponse
from backend.rag.query_service import QueryService

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str
    reference: str | None = None
    filters: dict | None = None


@router.post("", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    service: QueryService = Depends(get_query_service),
):
    """Execute a RAG query with automatic evaluation and self-healing."""
    return await service.execute_query(
        question=request.question,
        reference=request.reference,
        filters=request.filters,
    )
