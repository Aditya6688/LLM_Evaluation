from backend.config import ChunkingStrategy, Settings


def _split_text_with_overlap(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks by character count."""
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def chunk_texts(texts: list[dict], settings: Settings) -> list[dict]:
    """Chunk texts using the configured strategy.

    Args:
        texts: List of dicts with 'text' key and optional metadata keys.
        settings: App settings with chunking config.

    Returns:
        List of dicts with 'text' and 'metadata' keys.
    """
    documents = []
    for item in texts:
        metadata = {k: v for k, v in item.items() if k != "text"}
        chunks = _split_text_with_overlap(
            item["text"], settings.chunk_size, settings.chunk_overlap
        )
        for i, chunk in enumerate(chunks):
            documents.append({
                "text": chunk,
                "metadata": {**metadata, "chunk_index": i},
            })
    return documents
