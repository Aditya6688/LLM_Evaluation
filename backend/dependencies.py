from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import Settings, settings
from backend.db.database import get_db
from backend.ingestion.ingest_service import IngestService
from backend.rag.query_service import QueryService
from backend.rag.retriever import HybridRetriever
from backend.vectorstore.chroma_store import ChromaStore


@lru_cache
def get_settings() -> Settings:
    return settings


@lru_cache
def get_chroma_store() -> ChromaStore:
    return ChromaStore(persist_directory=settings.chroma_persist_dir)


@lru_cache
def get_retriever() -> HybridRetriever:
    return HybridRetriever(chroma_store=get_chroma_store())


def get_ingest_service(
    store: ChromaStore = Depends(get_chroma_store),
    s: Settings = Depends(get_settings),
) -> IngestService:
    return IngestService(chroma_store=store, settings=s)


def get_query_service(
    retriever: HybridRetriever = Depends(get_retriever),
    s: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
) -> QueryService:
    return QueryService(retriever=retriever, settings=s, db=db)
