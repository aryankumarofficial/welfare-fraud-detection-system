import { pgEnum } from "drizzle-orm/pg-core"

export const inferenceSourceEnum = pgEnum("inference_source", [
  "manual",
  "sync",
  "async",
  "scheduled",
  "system",
])

export const featureSourceEnum = pgEnum("feature_source", [
  "api_payload",
  "csv_ingest",
  "profile_snapshot",
])

export const predictionReviewDecisionEnum = pgEnum("prediction_review_decision", [
  "pending",
  "confirmed_fraud",
  "false_positive",
  "under_investigation",
])

export const monitoringAlertTypeEnum = pgEnum("monitoring_alert_type", [
  "MODEL_DRIFT",
  "HIGH_FAILURE_RATE",
  "QUEUE_BACKLOG",
  "HIGH_FALSE_POSITIVE_RATE",
])

export const monitoringAlertSeverityEnum = pgEnum("monitoring_alert_severity", [
  "info",
  "warning",
  "critical",
])

export const modelStatusEnum = pgEnum("model_status", [
  "DRAFT",
  "VALIDATED",
  "STAGING",
  "PRODUCTION",
  "ARCHIVED",
  "ROLLED_BACK",
])

export const modelRoleEnum = pgEnum("model_role", [
  "champion",
  "challenger",
  "none",
])
