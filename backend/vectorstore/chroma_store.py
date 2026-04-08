import uuid

import chromadb

from backend.vectorstore.embedding import embed_texts, embed_query


class ChromaStore:
    """Wrapper around ChromaDB for document storage and retrieval."""

    def __init__(self, persist_directory: str):
        self._client = chromadb.PersistentClient(path=persist_directory)
        self._collection = self._client.get_or_create_collection(
            name="llm_eval_docs",
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(
        self, texts: list[str], metadatas: list[dict] | None = None
    ) -> list[str]:
        """Add documents to the store. Returns list of IDs."""
        ids = [str(uuid.uuid4()) for _ in texts]
        embeddings = embed_texts(texts)
        self._collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        return ids

    def search(
        self, query: str, k: int = 5, where: dict | None = None
    ) -> list[dict]:
        """Search for similar documents. Returns list of {text, metadata, distance}."""
        query_embedding = embed_query(query)
        kwargs = {"query_embeddings": [query_embedding], "n_results": k}
        if where:
            kwargs["where"] = where

        results = self._collection.query(**kwargs)

        docs = []
        for i in range(len(results["documents"][0])):
            docs.append({
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 0,
            })
        return docs

    def get_all_texts(self) -> list[str]:
        """Get all document texts for BM25 index building."""
        result = self._collection.get()
        return result["documents"] if result["documents"] else []

    @property
    def count(self) -> int:
        return self._collection.count()
