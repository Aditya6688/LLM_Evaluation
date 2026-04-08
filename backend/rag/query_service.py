import logging
import time
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import Settings
from backend.db.models import EvalResult
from backend.evaluation.models import QueryResponse
from backend.evaluation.ragas_evaluator import RagasEvaluator
from backend.healing.review_queue import ReviewQueueService
from backend.healing.strategy import HealingStrategy
from backend.rag.chain import generate_answer
from backend.rag.retriever import HybridRetriever

logger = logging.getLogger(__name__)

# Approximate cost per 1K tokens (input/output averaged)
MODEL_COSTS = {
    "gpt-4o-mini": 0.00015,
    "gpt-4o": 0.0025,
}


class QueryService:
    """Central orchestrator: retrieve -> generate -> evaluate -> heal -> log."""

    def __init__(
        self,
        retriever: HybridRetriever,
        settings: Settings,
        db: AsyncSession,
    ):
        self._retriever = retriever
        self._settings = settings
        self._db = db
        self._evaluator = RagasEvaluator(
            judge_model=settings.judge_model,
            api_key=settings.openai_api_key,
        )
        self._healer = HealingStrategy(
            threshold=settings.faithfulness_threshold,
            fallback_model=settings.judge_model,
        )

    async def execute_query(
        self,
        question: str,
        reference: str | None = None,
        filters: dict | None = None,
    ) -> QueryResponse:
        """Execute the full RAG pipeline with eval and self-healing."""
        model = self._settings.generation_model
        attempt = 0
        final_response: QueryResponse | None = None

        while attempt < 2:
            start = time.perf_counter()

            # 1. Retrieve
            contexts = self._retriever.search(question)

            # 2. Generate
            result = generate_answer(
                question=question,
                contexts=contexts,
                model=model,
                api_key=self._settings.openai_api_key,
            )
            answer = result["answer"]
            token_count = result["token_count"]

            elapsed_ms = int((time.perf_counter() - start) * 1000)

            # 3. Evaluate
            eval_scores = self._evaluator.evaluate(
                question=question,
                answer=answer,
                contexts=contexts,
                reference=reference,
            )

            # Cost estimate
            cost_per_1k = MODEL_COSTS.get(model, 0.001)
            cost_usd = (token_count / 1000) * cost_per_1k

            # 4. Persist eval result
            eval_result = EvalResult(
                id=str(uuid.uuid4()),
                query=question,
                response=answer,
                contexts=contexts,
                reference=reference,
                faithfulness=eval_scores.faithfulness,
                answer_relevancy=eval_scores.answer_relevancy,
                context_precision=eval_scores.context_precision,
                context_recall=eval_scores.context_recall,
                model_used=model,
                is_retry=attempt > 0,
                latency_ms=elapsed_ms,
                token_count=token_count,
                cost_usd=cost_usd,
            )
            self._db.add(eval_result)
            await self._db.commit()

            final_response = QueryResponse(
                answer=answer,
                contexts=contexts,
                eval_scores=eval_scores,
                model_used=model,
                is_retry=attempt > 0,
            )

            # 5. Self-healing decision
            decision = self._healer.decide(eval_scores, attempt)

            if decision.action == "accept":
                logger.info("Query accepted (faithfulness=%.2f)", eval_scores.faithfulness)
                break

            if decision.action == "retry":
                logger.warning("Retrying with %s: %s", decision.model, decision.reason)
                model = decision.model
                attempt += 1
                continue

            if decision.action == "flag_for_review":
                logger.warning("Flagging for review: %s", decision.reason)
                review_svc = ReviewQueueService(self._db)
                await review_svc.create_review_item(
                    eval_result_id=eval_result.id,
                    reason=decision.reason,
                )
                break

        return final_response
