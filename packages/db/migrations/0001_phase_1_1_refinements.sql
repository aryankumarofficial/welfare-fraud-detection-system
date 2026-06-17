-- Phase 1.1: decouple auth, domain identity, and ML features

-- users: identity anchor only (auth strategy deferred)
DROP INDEX IF EXISTS "users_role_idx";--> statement-breakpoint
ALTER TABLE "users" DROP CONSTRAINT IF EXISTS "users_email_unique";--> statement-breakpoint
ALTER TABLE "users" DROP COLUMN IF EXISTS "email";--> statement-breakpoint
ALTER TABLE "users" DROP COLUMN IF EXISTS "password_hash";--> statement-breakpoint
ALTER TABLE "users" DROP COLUMN IF EXISTS "role";--> statement-breakpoint
ALTER TABLE "users" DROP COLUMN IF EXISTS "display_name";--> statement-breakpoint
ALTER TABLE "users" DROP COLUMN IF EXISTS "is_active";--> statement-breakpoint
DROP TYPE IF EXISTS "public"."user_role";--> statement-breakpoint
ALTER TABLE "users" ADD COLUMN IF NOT EXISTS "external_auth_id" text;--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "users_external_auth_id_idx" ON "users" USING btree ("external_auth_id");--> statement-breakpoint

-- student_profiles: domain identity only; ML features belong in feature_snapshots
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "income_in_rs";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "land_owned_acres";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "vehicles_owned";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "electricity_consumption";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "pending_loans";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "business_ownership";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "caste";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "father_caste";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "avg_caste_population_per";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "officer_approvals_per_day";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "weekly_spending";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "monthly_spending";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "transaction_count";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "avg_transaction_value";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "luxury_items_bought";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "weekend_spending_ratio";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "hospital_visits_per_year";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "claim_frequency";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "medical_claim_amount";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "avg_claim_amount";--> statement-breakpoint
ALTER TABLE "student_profiles" DROP COLUMN IF EXISTS "chronic_disease";--> statement-breakpoint
ALTER TABLE "student_profiles" ADD COLUMN IF NOT EXISTS "name" text;--> statement-breakpoint
ALTER TABLE "student_profiles" ADD COLUMN IF NOT EXISTS "date_of_birth" date;--> statement-breakpoint
ALTER TABLE "student_profiles" ADD COLUMN IF NOT EXISTS "gender" text;--> statement-breakpoint
ALTER TABLE "student_profiles" ADD COLUMN IF NOT EXISTS "region" text;--> statement-breakpoint

-- prediction_records: reserved job correlation + provider-agnostic inference source
ALTER TABLE "prediction_records" ADD COLUMN IF NOT EXISTS "job_id" uuid;--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "prediction_records_job_id_idx" ON "prediction_records" USING btree ("job_id");--> statement-breakpoint
ALTER TABLE "prediction_records" ALTER COLUMN "inference_source" DROP DEFAULT;--> statement-breakpoint
ALTER TABLE "prediction_records" ALTER COLUMN "inference_source" SET DATA TYPE text;--> statement-breakpoint
UPDATE "prediction_records" SET "inference_source" = CASE
  WHEN "inference_source" = 'sync_api' THEN 'sync'
  WHEN "inference_source" = 'batch_worker' THEN 'async'
  WHEN "inference_source" = 'scheduled_job' THEN 'scheduled'
  ELSE 'sync'
END;--> statement-breakpoint
DROP TYPE "public"."inference_source";--> statement-breakpoint
CREATE TYPE "public"."inference_source" AS ENUM('manual', 'sync', 'async', 'scheduled', 'system');--> statement-breakpoint
ALTER TABLE "prediction_records" ALTER COLUMN "inference_source" SET DATA TYPE "public"."inference_source" USING "inference_source"::"public"."inference_source";--> statement-breakpoint
ALTER TABLE "prediction_records" ALTER COLUMN "inference_source" SET DEFAULT 'sync';
