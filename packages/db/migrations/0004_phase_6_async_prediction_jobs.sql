-- Phase 6: asynchronous prediction job lifecycle support.

CREATE TABLE IF NOT EXISTS "prediction_jobs" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "bullmq_job_id" text,
  "batch_id" uuid,
  "student_profile_id" uuid NOT NULL,
  "feature_snapshot_id" uuid,
  "prediction_record_id" uuid,
  "status" text DEFAULT 'pending' NOT NULL,
  "attempts" integer DEFAULT 0 NOT NULL,
  "max_attempts" integer DEFAULT 3 NOT NULL,
  "last_error" text,
  "result" jsonb,
  "metadata" jsonb,
  "queued_at" timestamp with time zone,
  "started_at" timestamp with time zone,
  "completed_at" timestamp with time zone,
  "failed_at" timestamp with time zone,
  "created_at" timestamp with time zone DEFAULT now() NOT NULL,
  "updated_at" timestamp with time zone DEFAULT now() NOT NULL
);--> statement-breakpoint

DO $$ BEGIN
 ALTER TABLE "prediction_jobs" ADD CONSTRAINT "prediction_jobs_student_profile_id_student_profiles_id_fk" FOREIGN KEY ("student_profile_id") REFERENCES "student_profiles"("id") ON DELETE cascade ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;--> statement-breakpoint

DO $$ BEGIN
 ALTER TABLE "prediction_jobs" ADD CONSTRAINT "prediction_jobs_feature_snapshot_id_feature_snapshots_id_fk" FOREIGN KEY ("feature_snapshot_id") REFERENCES "feature_snapshots"("id") ON DELETE set null ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;--> statement-breakpoint

DO $$ BEGIN
 ALTER TABLE "prediction_jobs" ADD CONSTRAINT "prediction_jobs_prediction_record_id_prediction_records_id_fk" FOREIGN KEY ("prediction_record_id") REFERENCES "prediction_records"("id") ON DELETE set null ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;--> statement-breakpoint

CREATE INDEX IF NOT EXISTS "prediction_jobs_status_idx" ON "prediction_jobs" USING btree ("status");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "prediction_jobs_batch_id_idx" ON "prediction_jobs" USING btree ("batch_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "prediction_jobs_student_profile_id_idx" ON "prediction_jobs" USING btree ("student_profile_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "prediction_jobs_prediction_record_id_idx" ON "prediction_jobs" USING btree ("prediction_record_id");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "prediction_jobs_created_at_idx" ON "prediction_jobs" USING btree ("created_at");
