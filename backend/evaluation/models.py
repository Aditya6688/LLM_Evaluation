from pydantic import BaseModel


class EvalScores(BaseModel):
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float | None = None


class QueryResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    answer: str
    contexts: list[str]
    eval_scores: EvalScores
    model_used: str
    is_retry: bool
    trace_id: str | None = None


class EvalResultOut(BaseModel):
    id: str
    query: str
    response: str
    contexts: list[str]
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float | None
    model_used: str
    is_retry: bool
    latency_ms: int
    token_count: int
    cost_usd: float
    trace_id: str | None
    created_at: str

    model_config = {"from_attributes": True, "protected_namespaces": ()}
