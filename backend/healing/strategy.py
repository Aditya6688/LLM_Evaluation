from dataclasses import dataclass

from backend.evaluation.models import EvalScores


@dataclass
class HealingDecision:
    action: str  # "accept" | "retry" | "flag_for_review"
    model: str | None = None
    reason: str | None = None


class HealingStrategy:
    """Decide whether to accept, retry with a stronger model, or flag for human review."""

    def __init__(self, threshold: float, fallback_model: str):
        self.threshold = threshold
        self.fallback_model = fallback_model

    def decide(self, eval_scores: EvalScores, attempt: int) -> HealingDecision:
        if eval_scores.faithfulness >= self.threshold:
            return HealingDecision(action="accept")

        if attempt == 0:
            return HealingDecision(
                action="retry",
                model=self.fallback_model,
                reason=f"Faithfulness {eval_scores.faithfulness:.2f} below threshold {self.threshold}",
            )

        return HealingDecision(
            action="flag_for_review",
            reason=f"Faithfulness {eval_scores.faithfulness:.2f} still below threshold after retry with {self.fallback_model}",
        )
