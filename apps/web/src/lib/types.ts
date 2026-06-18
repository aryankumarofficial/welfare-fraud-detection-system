export type RiskLevel = "HIGH" | "MEDIUM" | "LOW" | string | null;

export interface DashboardSummary {
  profiles: number;
  snapshots: number;
  predictions: number;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
}

export interface PredictionSnapshot {
  feature_snapshot_id: string;
  student_profile_id: string;
  source: string | null;
  feature_schema_version: string | null;
  checksum: string | null;
  features: Record<string, unknown> | null;
  created_at: string;
}

export interface SnapshotGenerationResult {
  feature_snapshot_id: string;
  student_profile_id: string;
  feature_schema_version: string | null;
  source: string | null;
  checksum: string | null;
  features: Record<string, unknown> | null;
}

export interface PredictionGenerationResult {
  prediction_id: string;
  student_profile_id: string;
  feature_snapshot_id: string | null;
  model_version_id: string | null;
  risk_level: RiskLevel;
  prediction_duration_ms: number | null;
  explanation: string | null;
  [key: string]: unknown;
}

export interface PredictionDetail {
  prediction_id: string;
  student_profile_id: string;
  feature_snapshot_id: string | null;
  model_version_id: string | null;
  prediction_timestamp: string | null;
  model_name: string | null;
  model_version: string | null;
  snapshot_checksum: string | null;
  prediction_duration_ms: number | null;
  income_risk: number | null;
  caste_risk: number | null;
  transaction_risk: number | null;
  medical_risk: number | null;
  final_risk: number | null;
  risk_level: RiskLevel;
  explanation: string | null;
  inference_source: string | null;
  created_at: string;
  snapshot: PredictionSnapshot | null;
  model_version_metadata?: Record<string, unknown> | null;
}

export interface PredictionHistoryResponse {
  student_profile_id: string;
  latest_prediction: PredictionDetail;
  prediction_history: PredictionDetail[];
  associated_snapshots: PredictionSnapshot[];
}

export interface PredictionAnalyticsResponse {
  total_predictions: number;
  average_risk: number;
  high_risk_count: number;
  low_risk_count: number;
  average_latency_ms: number;
  predictions_by_model_version: Array<{
    model_name: string;
    model_version: string;
    count: number;
  }>;
  predictions_by_date: Array<{
    date: string;
    count: number;
  }>;
}

export interface ModelPerformanceResponse {
  reviewed_predictions: number;
  confirmed_fraud_count: number;
  false_positives: number;
  pending_reviews: number;
  under_investigation: number;
  precision: number;
  review_agreement_rate: number;
  decision_counts: Record<string, number>;
}

export interface DriftSnapshot {
  drift_snapshot_id: string;
  window: string;
  feature_distribution_changes: Record<string, { baseline_mean: number; current_mean: number; change_percentage: number }>;
  risk_distribution_changes: {
    baseline_average_risk: number;
    current_average_risk: number;
    average_risk_change_percentage: number;
    baseline_risk_levels: Record<string, number>;
    current_risk_levels: Record<string, number>;
  };
  prediction_volume_changes: {
    baseline_count: number;
    current_count: number;
    change_percentage: number;
  };
  drift_score: number;
  created_at: string;
}

export interface DriftAnalyticsResponse {
  latest_snapshot: DriftSnapshot;
  recent_snapshots: DriftSnapshot[];
}

export interface QueueAnalyticsResponse {
  total_jobs: number;
  pending: number;
  processing: number;
  completed: number;
  failed: number;
  retrying: number;
  success_rate: number;
  failure_rate: number;
  prediction_metrics: {
    total_predictions: number;
    failed_predictions: number;
    average_latency: number;
    latest_model_version: { name: string; version: string } | null;
    high_risk_percentage: number;
  };
  recent_jobs: PredictionJob[];
}

export interface PredictionJob {
  job_id: string;
  bullmq_job_id: string | null;
  batch_id: string | null;
  student_profile_id: string;
  feature_snapshot_id: string | null;
  prediction_record_id: string | null;
  status: string;
  attempts: number;
  max_attempts: number;
  last_error: string | null;
  result: Record<string, unknown> | null;
  metadata: Record<string, unknown> | null;
  queued_at: string | null;
  started_at: string | null;
  completed_at: string | null;
  failed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AlertItem {
  alert_id: string;
  alert_type: string;
  severity: string;
  message: string;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

export interface AlertsResponse {
  generated: AlertItem[];
  recent_alerts: AlertItem[];
}

export interface PredictionReviewsResponse {
  review_id: string;
  prediction_id: string;
  reviewer: string;
  decision: string;
  notes: string | null;
  created_at: string;
}
