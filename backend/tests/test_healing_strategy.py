from backend.evaluation.models import EvalScores
from backend.healing.strategy import HealingStrategy


def _make_scores(faithfulness: float = 0.9) -> EvalScores:
    return EvalScores(
        faithfulness=faithfulness,
        answer_relevancy=0.8,
        context_precision=0.7,
    )


class TestHealingStrategy:
    def setup_method(self):
        self.strategy = HealingStrategy(threshold=0.7, fallback_model="gpt-4o")

    def test_accept_when_above_threshold(self):
        decision = self.strategy.decide(_make_scores(0.85), attempt=0)
        assert decision.action == "accept"

    def test_accept_exactly_at_threshold(self):
        decision = self.strategy.decide(_make_scores(0.7), attempt=0)
        assert decision.action == "accept"

    def test_retry_on_first_failure(self):
        decision = self.strategy.decide(_make_scores(0.5), attempt=0)
        assert decision.action == "retry"
        assert decision.model == "gpt-4o"

    def test_flag_for_review_on_second_failure(self):
        decision = self.strategy.decide(_make_scores(0.3), attempt=1)
        assert decision.action == "flag_for_review"
        assert "still below threshold" in decision.reason

    def test_accept_on_second_attempt_if_passes(self):
        decision = self.strategy.decide(_make_scores(0.8), attempt=1)
        assert decision.action == "accept"
