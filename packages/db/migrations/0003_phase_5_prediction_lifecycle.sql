-- Phase 5: prediction lifecycle metadata, risk levels, and observability support.

ALTER TABLE "prediction_records" ADD COLUMN IF NOT EXISTS "prediction_timestamp" timestamp with time zone;--> statement-breakpoint
ALTER TABLE "prediction_records" ADD COLUMN IF NOT EXISTS "model_name" text;--> statement-breakpoint
ALTER TABLE "prediction_records" ADD COLUMN IF NOT EXISTS "model_version" text;--> statement-breakpoint
ALTER TABLE "prediction_records" ADD COLUMN IF NOT EXISTS "snapshot_checksum" text;--> statement-breakpoint
ALTER TABLE "prediction_records" ADD COLUMN IF NOT EXISTS "prediction_duration_ms" integer;--> statement-breakpoint
ALTER TABLE "prediction_records" ADD COLUMN IF NOT EXISTS "risk_level" text;--> statement-breakpoint

UPDATE "prediction_records" AS prediction
SET
  "prediction_timestamp" = COALESCE(prediction."prediction_timestamp", prediction."created_at"),
  "model_name" = COALESCE(prediction."model_name", model_version."name"),
  "model_version" = COALESCE(prediction."model_version", model_version."version"),
  "snapshot_checksum" = COALESCE(prediction."snapshot_checksum", feature_snapshot."checksum"),
  "risk_level" = COALESCE(
    prediction."risk_level",
    CASE
      WHEN prediction."final_risk" <= 0.30 THEN 'LOW'
      WHEN prediction."final_risk" <= 0.60 THEN 'MEDIUM'
      ELSE 'HIGH'
    END
  )
FROM "model_versions" AS model_version, "feature_snapshots" AS feature_snapshot
WHERE prediction."model_version_id" = model_version."id"
  AND prediction."feature_snapshot_id" = feature_snapshot."id";--> statement-breakpoint

UPDATE "prediction_records"
SET
  "prediction_timestamp" = COALESCE("prediction_timestamp", "created_at"),
  "risk_level" = COALESCE(
    "risk_level",
    CASE
      WHEN "final_risk" <= 0.30 THEN 'LOW'
      WHEN "final_risk" <= 0.60 THEN 'MEDIUM'
      ELSE 'HIGH'
    END
  );--> statement-breakpoint

CREATE INDEX IF NOT EXISTS "prediction_records_prediction_timestamp_idx" ON "prediction_records" USING btree ("prediction_timestamp");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "prediction_records_risk_level_idx" ON "prediction_records" USING btree ("risk_level");
