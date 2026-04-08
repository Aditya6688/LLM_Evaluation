from rank_bm25 import BM25Okapi

from backend.vectorstore.chroma_store import ChromaStore


class HybridRetriever:
    """Combines dense (ChromaDB) and sparse (BM25) retrieval."""

    def __init__(self, chroma_store: ChromaStore, k: int = 5, dense_weight: float = 0.5):
        self._store = chroma_store
        self._k = k
        self._dense_weight = dense_weight
        self._bm25 = None
        self._corpus_texts: list[str] = []
        self._refresh_bm25()

    def _refresh_bm25(self):
        texts = self._store.get_all_texts()
        if texts:
            self._corpus_texts = texts
            tokenized = [t.lower().split() for t in texts]
            self._bm25 = BM25Okapi(tokenized)

    def search(self, query: str) -> list[str]:
        """Return top-k relevant text chunks using hybrid search."""
        # Dense search via ChromaDB
        dense_results = self._store.search(query, k=self._k)

        if self._bm25 is None:
            return [r["text"] for r in dense_results]

        # Sparse search via BM25
        tokenized_query = query.lower().split()
        bm25_scores = self._bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:self._k]
        sparse_results = [self._corpus_texts[i] for i in top_indices]

        # Reciprocal rank fusion
        doc_scores: dict[str, float] = {}
        sparse_weight = 1.0 - self._dense_weight

        for rank, result in enumerate(dense_results):
            key = result["text"][:200]
            doc_scores[key] = doc_scores.get(key, 0) + self._dense_weight / (rank + 1)

        for rank, text in enumerate(sparse_results):
            key = text[:200]
            doc_scores[key] = doc_scores.get(key, 0) + sparse_weight / (rank + 1)

        # Build final results — map keys back to full texts
        all_texts = {r["text"][:200]: r["text"] for r in dense_results}
        for text in sparse_results:
            all_texts[text[:200]] = text

        sorted_keys = sorted(doc_scores, key=doc_scores.get, reverse=True)
        return [all_texts[k] for k in sorted_keys[:self._k]]
