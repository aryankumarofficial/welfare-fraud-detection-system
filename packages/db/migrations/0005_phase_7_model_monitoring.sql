-- Phase 7: explainability, analyst review, drift snapshots, and alerting.

DO $$ BEGIN
 CREATE TYPE "prediction_review_decision" AS ENUM ('pending', 'confirmed_fraud', 'false_positive', 'under_investigation');
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;--> statement-breakpoint

DO $$ BEGIN
 CREATE TYPE "monitoring_alert_type" AS ENUM ('MODEL_DRIFT', 'HIGH_FAILURE_RATE', 'QUEUE_BACKLOG', 'HIGH_FALSE_POSITIVE_RATE');
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;--> statement-breakpoint

DO $$ BEGIN
 CREATE TYPE "monitoring_alert_severity" AS ENUM ('info', 'warning', 'critical');
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;--> statement-breakpoint

ALTER TABLE "prediction_records" ADD COLUMN IF NOT EXISTS "explanation" jsonb;--> statement-breakpoint

CREATE TABLE IF NOT EXISTS "prediction_reviews" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "prediction_id" uuid NOT NULL,
  "reviewer" text NOT NULL,
  "decision" "prediction_review_decision" DEFAULT 'pending' NOT NULL,
  "notes" text,
  "created_at" timestamp with time zone DEFAULT now() NOT NULL
);--> statement-breakpoint

DO $$ BEGIN
 ALTER TABLE "prediction_reviews" ADD CONSTRAINT "prediction_reviews_prediction_id_prediction_records_id_fk" FOREIGN KEY ("prediction_id") REFERENCES "prediction_records"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;--> statement-breakpoint

CREATE TABLE IF NOT EXISTS "drift_snapshots" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "window" text NOT NULL,
  "feature_distribution_changes" jsonb NOT NULL,
  "risk_distribution_changes" jsonb NOT NULL,
  "prediction_volume_changes" jsonb NOT NULL,
  "drift_score" real DEFAULT 0 NOT NULL,
  "created_at" timestamp with time zone DEFAULT now() NOT NULL
);--> statement-breakpoint

CREATE TABLE IF NOT EXISTS "monitoring_alerts" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "alert_type" "monitoring_alert_type" NOT NULL,
  "severity" "monitoring_alert_severity" DEFAULT 'warning' NOT NULL,
  "message" text NOT NULL,
  "metadata" jsonb,
  "created_at" timestamp with time zone DEFAULT now() NOT NULL
);--> statement-breakpoint

CREATE INDEX IF NOT EXISTS "prediction_reviews_prediction_id_idx" ON "prediction_reviews" USING btree ("prediction_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "prediction_reviews_decision_idx" ON "prediction_reviews" USING btree ("decision");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "prediction_reviews_created_at_idx" ON "prediction_reviews" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "drift_snapshots_created_at_idx" ON "drift_snapshots" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "drift_snapshots_drift_score_idx" ON "drift_snapshots" USING btree ("drift_score");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "monitoring_alerts_alert_type_idx" ON "monitoring_alerts" USING btree ("alert_type");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "monitoring_alerts_severity_idx" ON "monitoring_alerts" USING btree ("severity");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "monitoring_alerts_created_at_idx" ON "monitoring_alerts" USING btree ("created_at");
