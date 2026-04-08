from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel

from backend.dependencies import get_ingest_service
from backend.ingestion.ingest_service import IngestService

router = APIRouter(prefix="/ingest", tags=["ingestion"])


class UrlIngestRequest(BaseModel):
    url: str


class IngestResponse(BaseModel):
    document_id: str
    chunks_stored: int
    source: str
    doc_type: str


@router.post("", response_model=IngestResponse)
async def ingest_file(
    file: UploadFile = File(...),
    service: IngestService = Depends(get_ingest_service),
):
    """Ingest a PDF file into the vector store."""
    result = await service.ingest_file(file)
    return IngestResponse(
        document_id=result.document_id,
        chunks_stored=result.chunks_stored,
        source=result.source,
        doc_type=result.doc_type,
    )


@router.post("/url", response_model=IngestResponse)
async def ingest_url(
    request: UrlIngestRequest,
    service: IngestService = Depends(get_ingest_service),
):
    """Ingest a web page by URL."""
    result = await service.ingest_url(request.url)
    return IngestResponse(
        document_id=result.document_id,
        chunks_stored=result.chunks_stored,
        source=result.source,
        doc_type=result.doc_type,
    )
