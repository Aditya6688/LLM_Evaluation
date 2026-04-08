import json
import logging

from openai import OpenAI

from backend.evaluation.models import EvalScores

logger = logging.getLogger(__name__)

EVAL_PROMPT = """You are an evaluation judge. Score the following RAG (Retrieval-Augmented Generation) response on these metrics:

1. **faithfulness** (0.0 to 1.0): Is the answer factually supported by the provided contexts? 1.0 means every claim is grounded in the context.
2. **answer_relevancy** (0.0 to 1.0): Does the answer address the question directly and completely? 1.0 means perfectly relevant.
3. **context_precision** (0.0 to 1.0): Are the retrieved contexts relevant to the question? 1.0 means all contexts are useful.

**Question:** {question}

**Retrieved Contexts:**
{contexts}

**Generated Answer:** {answer}

Respond with ONLY a JSON object (no markdown, no explanation):
{{"faithfulness": <float>, "answer_relevancy": <float>, "context_precision": <float>}}"""


class RagasEvaluator:
    """Evaluate RAG responses using an LLM-as-judge pattern."""

    def __init__(self, judge_model: str, api_key: str):
        self._client = OpenAI(api_key=api_key)
        self._model = judge_model

    def evaluate(
        self,
        question: str,
        answer: str,
        contexts: list[str],
        reference: str | None = None,
    ) -> EvalScores:
        """Compute evaluation metrics for a single Q&A pair."""
        contexts_text = "\n---\n".join(f"[{i+1}] {c}" for i, c in enumerate(contexts))

        prompt = EVAL_PROMPT.format(
            question=question,
            contexts=contexts_text,
            answer=answer,
        )

        try:
            logger.info("Running LLM-as-judge with model=%s", self._model)
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content
            logger.info("Judge raw response: %s", raw)
            scores = json.loads(raw)

            result = EvalScores(
                faithfulness=float(scores.get("faithfulness", 0.0)),
                answer_relevancy=float(scores.get("answer_relevancy", 0.0)),
                context_precision=float(scores.get("context_precision", 0.0)),
                context_recall=None,
            )
            logger.info("Eval scores: faith=%.2f relev=%.2f prec=%.2f",
                        result.faithfulness, result.answer_relevancy, result.context_precision)
            return result
        except Exception as e:
            logger.error("LLM-as-judge evaluation failed: %s", e, exc_info=True)
            return EvalScores(
                faithfulness=0.0,
                answer_relevancy=0.0,
                context_precision=0.0,
                context_recall=None,
            )
