import axios from 'axios';
import type {
  DashboardStats,
  EvalResult,
  IngestResponse,
  QueryResponse,
  ReviewItem,
} from '../types';

const api = axios.create({
  baseURL: '/api',
});

export async function queryPipeline(
  question: string,
  reference?: string
): Promise<QueryResponse> {
  const { data } = await api.post<QueryResponse>('/query', {
    question,
    reference: reference || null,
  });
  return data;
}

export async function ingestFile(file: File): Promise<IngestResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post<IngestResponse>('/ingest', formData);
  return data;
}

export async function ingestUrl(url: string): Promise<IngestResponse> {
  const { data } = await api.post<IngestResponse>('/ingest/url', { url });
  return data;
}

export async function getEvaluations(
  params?: Record<string, string | number>
): Promise<EvalResult[]> {
  const { data } = await api.get<EvalResult[]>('/evaluations', { params });
  return data;
}

export async function getReviewQueue(
  status = 'pending'
): Promise<ReviewItem[]> {
  const { data } = await api.get<ReviewItem[]>('/review-queue', {
    params: { status },
  });
  return data;
}

export async function resolveReviewItem(
  id: string,
  status: string,
  resolutionNote?: string
): Promise<ReviewItem> {
  const { data } = await api.patch<ReviewItem>(`/review-queue/${id}`, {
    status,
    resolution_note: resolutionNote || null,
  });
  return data;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await api.get<DashboardStats>('/dashboard/stats');
  return data;
}
