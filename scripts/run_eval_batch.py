"""Run batch evaluation on a set of questions."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.config import settings
from backend.db.models import Base
from backend.rag.query_service import QueryService
from backend.vectorstore.chroma_store import ChromaStore
from backend.vectorstore.embedding import get_embedding_function

SAMPLE_QUESTIONS = [
    "What is the main topic of the document?",
    "Summarize the key findings.",
    "What methodology was used?",
    "What are the conclusions?",
]


async def main():
    # Initialize components
    engine = create_async_engine(settings.sqlite_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    store = ChromaStore(
        persist_directory=settings.chroma_persist_dir,
        embedding_function=get_embedding_function(),
    )

    if store.count == 0:
        print("No documents in store. Run seed_data.py first.")
        return

    questions = SAMPLE_QUESTIONS
    # Or load from a JSON file if provided
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            questions = json.load(f)

    print(f"Running evaluation on {len(questions)} questions...\n")

    async with session_factory() as session:
        service = QueryService(chroma_store=store, settings=settings, db=session)

        for i, question in enumerate(questions, 1):
            print(f"[{i}/{len(questions)}] {question}")
            result = await service.execute_query(question)
            scores = result.eval_scores
            print(f"  Model: {result.model_used} | Retry: {result.is_retry}")
            print(f"  Faithfulness: {scores.faithfulness:.3f}")
            print(f"  Relevancy:    {scores.answer_relevancy:.3f}")
            print(f"  Precision:    {scores.context_precision:.3f}")
            print()

    await engine.dispose()
    print("Batch evaluation complete.")


if __name__ == "__main__":
    asyncio.run(main())
