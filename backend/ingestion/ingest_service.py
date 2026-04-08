import uuid

from fastapi import UploadFile

from backend.config import Settings
from backend.ingestion.chunking import chunk_texts
from backend.ingestion.pdf_loader import extract_text_from_pdf
from backend.ingestion.web_scraper import scrape_url
from backend.vectorstore.chroma_store import ChromaStore


class IngestResult:
    def __init__(self, document_id: str, chunks_stored: int, source: str, doc_type: str):
        self.document_id = document_id
        self.chunks_stored = chunks_stored
        self.source = source
        self.doc_type = doc_type


class IngestService:
    def __init__(self, chroma_store: ChromaStore, settings: Settings):
        self._store = chroma_store
        self._settings = settings

    async def ingest_file(self, file: UploadFile) -> IngestResult:
        """Ingest an uploaded PDF file."""
        file_bytes = await file.read()
        pages = extract_text_from_pdf(file_bytes)

        doc_id = str(uuid.uuid4())
        text_items = [
            {"text": p["text"], "page": p["page"], "source": file.filename, "doc_type": "pdf", "document_id": doc_id}
            for p in pages
        ]

        chunks = chunk_texts(text_items, self._settings)
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        self._store.add_documents(texts, metadatas)

        return IngestResult(
            document_id=doc_id,
            chunks_stored=len(chunks),
            source=file.filename,
            doc_type="pdf",
        )

    async def ingest_url(self, url: str) -> IngestResult:
        """Ingest a web page by URL."""
        data = scrape_url(url)

        doc_id = str(uuid.uuid4())
        text_items = [
            {"text": data["text"], "source": url, "title": data["title"], "doc_type": "web", "document_id": doc_id}
        ]

        chunks = chunk_texts(text_items, self._settings)
        texts = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]
        self._store.add_documents(texts, metadatas)

        return IngestResult(
            document_id=doc_id,
            chunks_stored=len(chunks),
            source=url,
            doc_type="web",
        )
