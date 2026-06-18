import type {
  AlertsResponse,
  DashboardSummary,
  DriftAnalyticsResponse,
  ModelPerformanceResponse,
  PredictionAnalyticsResponse,
  PredictionDetail,
  PredictionHistoryResponse,
  PredictionJob,
  PredictionReviewsResponse,
  QueueAnalyticsResponse,
} from "@/lib/types";

const API_BASE_URL =
  process.env.ML_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const ANALYST_USERNAME = process.env.ANALYST_USERNAME;
const ANALYST_PASSWORD = process.env.ANALYST_PASSWORD;

interface TokenResponse {
  access_token: string;
  expires_in: number;
  role: string;
}

let cachedToken: string | null = null;
let cachedTokenExpiry = 0;

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
  const now = Date.now() / 1000;

  if (cachedToken && cachedTokenExpiry > now + 5) {
    return cachedToken;
  }

  if (!ANALYST_USERNAME || !ANALYST_PASSWORD) {
    throw new ApiRequestError(
      "Missing ANALYST_USERNAME or ANALYST_PASSWORD environment variables.",
      500
    );
  }

  const response = await fetch(getApiUrl("/auth/token"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username: ANALYST_USERNAME,
      password: ANALYST_PASSWORD,
    }),
    cache: "no-store",
  });

  const body = await response.json().catch(() => null);
  if (!response.ok || body == null || typeof body !== "object") {
    throw new ApiRequestError(
      "Unable to authenticate with the ML backend.",
      response.status,
      body
    );
  }

  if (body.success === false) {
    throw new ApiRequestError(body.error || "Authentication failed.", response.status, body);
  }

  const tokenResponse = body as TokenResponse;
  if (!tokenResponse.access_token) {
    throw new ApiRequestError("Backend did not return an access token.", response.status, body);
  }

  cachedToken = tokenResponse.access_token;
  cachedTokenExpiry = now + Math.max(0, tokenResponse.expires_in - 5);
  return cachedToken;
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

export async function getDriftAnalytics(
  days = 7
): Promise<DriftAnalyticsResponse> {
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

export async function getAlertSeverityLabel(severity: string): Promise<string> {
  return severity;
}
