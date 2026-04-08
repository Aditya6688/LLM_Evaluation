"""Seed the vector store with sample data for development."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import settings
from backend.ingestion.ingest_service import IngestService
from backend.vectorstore.chroma_store import ChromaStore
from backend.vectorstore.embedding import get_embedding_function


async def main():
    store = ChromaStore(
        persist_directory=settings.chroma_persist_dir,
        embedding_function=get_embedding_function(),
    )
    service = IngestService(chroma_store=store, settings=settings)

    # Ingest sample PDFs from data/ directory
    data_dir = Path(__file__).parent.parent / "data"
    pdf_files = list(data_dir.glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found in data/ directory.")
        print("Place sample PDFs in data/ and re-run this script.")
        return

    for pdf_path in pdf_files:
        print(f"Ingesting {pdf_path.name}...")

        class FakeUploadFile:
            def __init__(self, path: Path):
                self.filename = path.name
                self._data = path.read_bytes()

            async def read(self) -> bytes:
                return self._data

        result = await service.ingest_file(FakeUploadFile(pdf_path))
        print(f"  -> {result.chunks_stored} chunks stored (doc_id: {result.document_id})")

    print(f"\nTotal documents in store: {store.count}")


if __name__ == "__main__":
    asyncio.run(main())
