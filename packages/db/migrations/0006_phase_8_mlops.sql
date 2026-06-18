-- Phase 8: MLOps & Model Lifecycle Management

DO $$ BEGIN
 CREATE TYPE "model_status" AS ENUM ('DRAFT', 'VALIDATED', 'STAGING', 'PRODUCTION', 'ARCHIVED', 'ROLLED_BACK');
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;--> statement-breakpoint

DO $$ BEGIN
 CREATE TYPE "model_role" AS ENUM ('champion', 'challenger', 'none');
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;--> statement-breakpoint

ALTER TABLE "model_versions" ADD COLUMN IF NOT EXISTS "status" "model_status" DEFAULT 'DRAFT' NOT NULL;--> statement-breakpoint
ALTER TABLE "model_versions" ADD COLUMN IF NOT EXISTS "role" "model_role" DEFAULT 'none' NOT NULL;--> statement-breakpoint
ALTER TABLE "model_versions" ADD COLUMN IF NOT EXISTS "parent_model_id" uuid;--> statement-breakpoint
ALTER TABLE "model_versions" ADD COLUMN IF NOT EXISTS "artifact_hash" text;--> statement-breakpoint
ALTER TABLE "model_versions" ADD COLUMN IF NOT EXISTS "training_metadata" jsonb;--> statement-breakpoint
ALTER TABLE "model_versions" ADD COLUMN IF NOT EXISTS "feature_schema_version" text;--> statement-breakpoint
ALTER TABLE "model_versions" ADD COLUMN IF NOT EXISTS "promoted_at" timestamp with time zone;--> statement-breakpoint
ALTER TABLE "model_versions" ADD COLUMN IF NOT EXISTS "promoted_by" text;--> statement-breakpoint
ALTER TABLE "model_versions" ADD COLUMN IF NOT EXISTS "rolled_back_at" timestamp with time zone;--> statement-breakpoint

CREATE TABLE IF NOT EXISTS "model_evaluation_runs" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "model_version_id" uuid NOT NULL,
  "dataset_name" text NOT NULL,
  "dataset_version" text,
  "sample_size" integer NOT NULL,
  "precision" real NOT NULL,
  "recall" real NOT NULL,
  "f1_score" real NOT NULL,
  "false_positive_rate" real NOT NULL,
  "additional_metrics" jsonb,
  "evaluated_by" text,
  "evaluated_at" timestamp with time zone DEFAULT now() NOT NULL,
  "created_at" timestamp with time zone DEFAULT now() NOT NULL
);--> statement-breakpoint

DO $$ BEGIN
 ALTER TABLE "model_evaluation_runs" ADD CONSTRAINT "model_evaluation_runs_model_version_id_model_versions_id_fk" FOREIGN KEY ("model_version_id") REFERENCES "model_versions"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;--> statement-breakpoint

CREATE TABLE IF NOT EXISTS "model_lineage_events" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "model_version_id" uuid NOT NULL,
  "event_type" text NOT NULL,
  "from_status" text,
  "to_status" text,
  "from_role" text,
  "to_role" text,
  "metadata" jsonb,
  "performed_by" text,
  "created_at" timestamp with time zone DEFAULT now() NOT NULL
);--> statement-breakpoint

DO $$ BEGIN
 ALTER TABLE "model_lineage_events" ADD CONSTRAINT "model_lineage_events_model_version_id_model_versions_id_fk" FOREIGN KEY ("model_version_id") REFERENCES "model_versions"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;--> statement-breakpoint

CREATE INDEX IF NOT EXISTS "model_versions_status_idx" ON "model_versions" USING btree ("status");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "model_versions_role_idx" ON "model_versions" USING btree ("role");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "model_versions_parent_model_id_idx" ON "model_versions" USING btree ("parent_model_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "model_evaluation_runs_model_version_id_idx" ON "model_evaluation_runs" USING btree ("model_version_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "model_evaluation_runs_evaluated_at_idx" ON "model_evaluation_runs" USING btree ("evaluated_at");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "model_lineage_events_model_version_id_idx" ON "model_lineage_events" USING btree ("model_version_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "model_lineage_events_event_type_idx" ON "model_lineage_events" USING btree ("event_type");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "model_lineage_events_created_at_idx" ON "model_lineage_events" USING btree ("created_at");
