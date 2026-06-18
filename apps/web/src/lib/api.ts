import type {
  AlertsResponse,
  DashboardSummary,
  DriftAnalyticsResponse,
  ModelDetail,
  ModelHealthResponse,
  ModelPerformanceResponse,
  ModelSummary,
  PredictionAnalyticsResponse,
  PredictionDetail,
  PredictionGenerationResult,
  PredictionHistoryResponse,
  PredictionJob,
  PredictionReviewsResponse,
  QueueAnalyticsResponse,
  SnapshotGenerationResult,
} from "@/lib/types";
import { getStoredAccessToken } from "@/lib/auth";

const API_BASE_URL =
  process.env.ML_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiRequestError extends Error {
  public status: number;
  public details: unknown;

  constructor(message: string, status = 500, details?: unknown) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.details = details;
  }
}

function getApiUrl(path: string) {
  return `${API_BASE_URL}${path}`;
}

async function getAuthToken(): Promise<string> {
  const browserToken = getStoredAccessToken();
  if (!browserToken) {
    throw new ApiRequestError("No access token found. Please log in.", 401);
  }

  return browserToken;
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const token = await getAuthToken();
  const response = await fetch(getApiUrl(path), {
    ...init,
    headers: {
      Accept: "application/json",
      Authorization: `Bearer ${token}`,
      ...(init?.headers as Record<string, string>),
    },
    cache: "no-store",
  });

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const message = body?.error || response.statusText || "API request failed.";
    throw new ApiRequestError(message, response.status, body);
  }

  if (body && typeof body === "object" && "success" in body && body.success === false) {
    throw new ApiRequestError(body.error || "API request returned an error.", response.status, body);
  }

  return body?.data as T;
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return fetchJson<DashboardSummary>("/dashboard/summary");
}

export async function getPredictionHistory(
  studentProfileId: string
): Promise<PredictionHistoryResponse> {
  return fetchJson<PredictionHistoryResponse>(`/predictions/${studentProfileId}`);
}

export async function getPredictionDetail(
  predictionId: string
): Promise<PredictionDetail> {
  return fetchJson<PredictionDetail>(`/predictions/detail/${predictionId}`);
}

export async function getPredictionAnalytics(): Promise<PredictionAnalyticsResponse> {
  return fetchJson<PredictionAnalyticsResponse>("/analytics/predictions");
}

export async function getModelPerformance(): Promise<ModelPerformanceResponse> {
  return fetchJson<ModelPerformanceResponse>("/analytics/model-performance");
}

export async function getModelHealth(): Promise<ModelHealthResponse> {
  return fetchJson<ModelHealthResponse>("/analytics/model-health");
}

export async function getDriftAnalytics(days = 7): Promise<DriftAnalyticsResponse> {
  return fetchJson<DriftAnalyticsResponse>(`/analytics/drift?days=${days}`);
}

export async function getAlerts(): Promise<AlertsResponse> {
  return fetchJson<AlertsResponse>("/analytics/alerts");
}

export async function getQueueAnalytics(): Promise<QueueAnalyticsResponse> {
  return fetchJson<QueueAnalyticsResponse>("/analytics/queue");
}

export async function getPredictionJob(jobId: string): Promise<PredictionJob> {
  return fetchJson<PredictionJob>(`/predictions/jobs/${jobId}`);
}

export async function getPredictionReviews(
  decision?: string
): Promise<PredictionReviewsResponse[]> {
  const query = decision ? `?decision=${encodeURIComponent(decision)}` : "";
  return fetchJson<PredictionReviewsResponse[]>(`/predictions/reviews${query}`);
}

export async function generateSnapshot(
  studentProfileId: string
): Promise<SnapshotGenerationResult> {
  return fetchJson<SnapshotGenerationResult>("/snapshot/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_profile_id: studentProfileId }),
  });
}

export async function generatePrediction(
  studentProfileId: string
): Promise<PredictionGenerationResult> {
  return fetchJson<PredictionGenerationResult>("/predict/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_profile_id: studentProfileId }),
  });
}

export async function queuePrediction(
  studentProfileId: string
): Promise<PredictionJob> {
  return fetchJson<PredictionJob>("/predictions/queue", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_profile_id: studentProfileId }),
  });
}

export async function createPredictionReview(
  predictionId: string,
  reviewer: string,
  decision: string,
  notes?: string
): Promise<PredictionReviewsResponse> {
  return fetchJson<PredictionReviewsResponse>(`/predictions/${predictionId}/review`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reviewer, decision, notes }),
  });
}

export async function getModels(): Promise<ModelSummary[]> {
  return fetchJson<ModelSummary[]>("/models");
}

export async function getModelDetail(modelId: string): Promise<ModelDetail> {
  return fetchJson<ModelDetail>(`/models/${modelId}`);
}

export async function compareModels(ids: string): Promise<ModelDetail[]> {
  return fetchJson<ModelDetail[]>(`/models/compare?ids=${encodeURIComponent(ids)}`);
}

export async function promoteModel(modelId: string): Promise<ModelDetail> {
  return fetchJson<ModelDetail>(`/models/${modelId}/promote`, {
    method: "POST",
  });
}

export async function rollbackModel(modelId: string): Promise<ModelDetail> {
  return fetchJson<ModelDetail>(`/models/${modelId}/rollback`, {
    method: "POST",
  });
}

export async function archiveModel(modelId: string): Promise<ModelDetail> {
  return fetchJson<ModelDetail>(`/models/${modelId}/archive`, {
    method: "POST",
  });
}

export async function getAlertSeverityLabel(severity: string): Promise<string> {
  return severity;
}
