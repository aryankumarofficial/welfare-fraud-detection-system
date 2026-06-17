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
