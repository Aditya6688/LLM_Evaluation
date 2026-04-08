from unittest.mock import patch

from backend.config import ChunkingStrategy, Settings
from backend.ingestion.chunking import chunk_texts


def _make_settings(**overrides) -> Settings:
    defaults = {
        "openai_api_key": "test-key",
        "chunk_size": 100,
        "chunk_overlap": 20,
        "chunking_strategy": ChunkingStrategy.FIXED,
    }
    defaults.update(overrides)
    return Settings(**defaults)


class TestFixedChunking:
    def test_splits_long_text(self):
        settings = _make_settings(chunk_size=50, chunk_overlap=10)
        texts = [{"text": "word " * 100, "source": "test.pdf", "page": 1}]

        docs = chunk_texts(texts, settings)

        assert len(docs) > 1
        for doc in docs:
            assert doc.metadata["source"] == "test.pdf"
            assert "chunk_index" in doc.metadata

    def test_preserves_metadata(self):
        settings = _make_settings()
        texts = [{"text": "Short text.", "source": "doc.pdf", "page": 3}]

        docs = chunk_texts(texts, settings)

        assert len(docs) == 1
        assert docs[0].metadata["page"] == 3
        assert docs[0].metadata["source"] == "doc.pdf"
        assert docs[0].metadata["chunk_index"] == 0

    def test_empty_input(self):
        settings = _make_settings()
        assert chunk_texts([], settings) == []

    def test_multiple_items(self):
        settings = _make_settings()
        texts = [
            {"text": "First document.", "source": "a.pdf"},
            {"text": "Second document.", "source": "b.pdf"},
        ]

        docs = chunk_texts(texts, settings)

        assert len(docs) == 2
        sources = {doc.metadata["source"] for doc in docs}
        assert sources == {"a.pdf", "b.pdf"}
