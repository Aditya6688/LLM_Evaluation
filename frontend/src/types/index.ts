export interface EvalScores {
  faithfulness: number;
  answer_relevancy: number;
  context_precision: number;
  context_recall: number | null;
}

export interface QueryResponse {
  answer: string;
  contexts: string[];
  eval_scores: EvalScores;
  model_used: string;
  is_retry: boolean;
  trace_id: string | null;
}

export interface EvalResult {
  id: string;
  query: string;
  response: string;
  contexts: string[];
  faithfulness: number;
  answer_relevancy: number;
  context_precision: number;
  context_recall: number | null;
  model_used: string;
  is_retry: boolean;
  latency_ms: number;
  token_count: number;
  cost_usd: number;
  trace_id: string | null;
  created_at: string;
}

export interface ReviewItem {
  id: string;
  eval_result_id: string;
  reason: string;
  status: string;
  resolution_note: string | null;
  created_at: string;
  resolved_at: string | null;
}

export interface ScoreTrendPoint {
  date: string;
  avg_faithfulness: number;
  avg_relevancy: number;
  query_count: number;
}

export interface DashboardStats {
  total_queries: number;
  avg_faithfulness: number;
  avg_relevancy: number;
  retry_rate: number;
  review_queue_pending: number;
  model_usage: Record<string, number>;
  cost_total_usd: number;
  score_trend: ScoreTrendPoint[];
}

export interface IngestResponse {
  document_id: string;
  chunks_stored: number;
  source: string;
  doc_type: string;
}
