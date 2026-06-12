import { pgEnum } from "drizzle-orm/pg-core"

export const userRoleEnum = pgEnum("user_role", ["admin", "analyst", "viewer"])

export const inferenceSourceEnum = pgEnum("inference_source", [
  "sync_api",
  "batch_worker",
  "scheduled_job",
])

export const featureSourceEnum = pgEnum("feature_source", [
  "api_payload",
  "csv_ingest",
  "profile_snapshot",
])
