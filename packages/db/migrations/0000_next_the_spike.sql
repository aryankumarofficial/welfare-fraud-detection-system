CREATE TYPE "public"."feature_source" AS ENUM('api_payload', 'csv_ingest', 'profile_snapshot');--> statement-breakpoint
CREATE TYPE "public"."inference_source" AS ENUM('sync_api', 'batch_worker', 'scheduled_job');--> statement-breakpoint
CREATE TYPE "public"."user_role" AS ENUM('admin', 'analyst', 'viewer');--> statement-breakpoint
CREATE TABLE "audit_logs" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"actor_user_id" uuid,
	"action" text NOT NULL,
	"resource_type" text,
	"resource_id" text,
	"metadata" jsonb,
	"ip_address" text,
	"user_agent" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "feature_snapshots" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"student_profile_id" uuid NOT NULL,
	"source" "feature_source" DEFAULT 'api_payload' NOT NULL,
	"features" jsonb NOT NULL,
	"feature_schema_version" text DEFAULT 'v1' NOT NULL,
	"checksum" text,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "model_versions" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"name" text NOT NULL,
	"version" text NOT NULL,
	"description" text,
	"artifact_uri" text,
	"configuration" jsonb,
	"is_active" boolean DEFAULT false NOT NULL,
	"deployed_at" timestamp with time zone,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "prediction_records" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"student_profile_id" uuid NOT NULL,
	"feature_snapshot_id" uuid,
	"model_version_id" uuid,
	"income_risk" real NOT NULL,
	"caste_risk" real NOT NULL,
	"transaction_risk" real NOT NULL,
	"medical_risk" real NOT NULL,
	"final_risk" real NOT NULL,
	"inference_source" "inference_source" DEFAULT 'sync_api' NOT NULL,
	"requested_by_user_id" uuid,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "student_profiles" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"external_id" text,
	"created_by_user_id" uuid,
	"income_in_rs" real,
	"land_owned_acres" real,
	"vehicles_owned" integer,
	"electricity_consumption" real,
	"pending_loans" integer,
	"business_ownership" integer,
	"caste" text,
	"father_caste" text,
	"avg_caste_population_per" real,
	"officer_approvals_per_day" real,
	"weekly_spending" real,
	"monthly_spending" real,
	"transaction_count" integer,
	"avg_transaction_value" real,
	"luxury_items_bought" integer,
	"weekend_spending_ratio" real,
	"hospital_visits_per_year" integer,
	"claim_frequency" integer,
	"medical_claim_amount" real,
	"avg_claim_amount" real,
	"chronic_disease" integer,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "student_profiles_external_id_unique" UNIQUE("external_id")
);
--> statement-breakpoint
CREATE TABLE "users" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"email" text NOT NULL,
	"password_hash" text NOT NULL,
	"role" "user_role" DEFAULT 'analyst' NOT NULL,
	"display_name" text,
	"is_active" boolean DEFAULT true NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL,
	"updated_at" timestamp with time zone DEFAULT now() NOT NULL,
	CONSTRAINT "users_email_unique" UNIQUE("email")
);
--> statement-breakpoint
ALTER TABLE "audit_logs" ADD CONSTRAINT "audit_logs_actor_user_id_users_id_fk" FOREIGN KEY ("actor_user_id") REFERENCES "public"."users"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "feature_snapshots" ADD CONSTRAINT "feature_snapshots_student_profile_id_student_profiles_id_fk" FOREIGN KEY ("student_profile_id") REFERENCES "public"."student_profiles"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "prediction_records" ADD CONSTRAINT "prediction_records_student_profile_id_student_profiles_id_fk" FOREIGN KEY ("student_profile_id") REFERENCES "public"."student_profiles"("id") ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "prediction_records" ADD CONSTRAINT "prediction_records_feature_snapshot_id_feature_snapshots_id_fk" FOREIGN KEY ("feature_snapshot_id") REFERENCES "public"."feature_snapshots"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "prediction_records" ADD CONSTRAINT "prediction_records_model_version_id_model_versions_id_fk" FOREIGN KEY ("model_version_id") REFERENCES "public"."model_versions"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "prediction_records" ADD CONSTRAINT "prediction_records_requested_by_user_id_users_id_fk" FOREIGN KEY ("requested_by_user_id") REFERENCES "public"."users"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
ALTER TABLE "student_profiles" ADD CONSTRAINT "student_profiles_created_by_user_id_users_id_fk" FOREIGN KEY ("created_by_user_id") REFERENCES "public"."users"("id") ON DELETE set null ON UPDATE no action;--> statement-breakpoint
CREATE INDEX "audit_logs_actor_user_id_idx" ON "audit_logs" USING btree ("actor_user_id");--> statement-breakpoint
CREATE INDEX "audit_logs_action_idx" ON "audit_logs" USING btree ("action");--> statement-breakpoint
CREATE INDEX "audit_logs_created_at_idx" ON "audit_logs" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "audit_logs_resource_idx" ON "audit_logs" USING btree ("resource_type","resource_id");--> statement-breakpoint
CREATE INDEX "feature_snapshots_student_profile_id_idx" ON "feature_snapshots" USING btree ("student_profile_id");--> statement-breakpoint
CREATE INDEX "feature_snapshots_checksum_idx" ON "feature_snapshots" USING btree ("checksum");--> statement-breakpoint
CREATE INDEX "feature_snapshots_created_at_idx" ON "feature_snapshots" USING btree ("created_at");--> statement-breakpoint
CREATE UNIQUE INDEX "model_versions_name_version_uidx" ON "model_versions" USING btree ("name","version");--> statement-breakpoint
CREATE INDEX "model_versions_is_active_idx" ON "model_versions" USING btree ("is_active");--> statement-breakpoint
CREATE INDEX "prediction_records_student_profile_id_idx" ON "prediction_records" USING btree ("student_profile_id");--> statement-breakpoint
CREATE INDEX "prediction_records_created_at_idx" ON "prediction_records" USING btree ("created_at");--> statement-breakpoint
CREATE INDEX "prediction_records_final_risk_idx" ON "prediction_records" USING btree ("final_risk");--> statement-breakpoint
CREATE INDEX "prediction_records_model_version_id_idx" ON "prediction_records" USING btree ("model_version_id");--> statement-breakpoint
CREATE INDEX "student_profiles_external_id_idx" ON "student_profiles" USING btree ("external_id");--> statement-breakpoint
CREATE INDEX "student_profiles_created_by_user_id_idx" ON "student_profiles" USING btree ("created_by_user_id");--> statement-breakpoint
CREATE INDEX "users_role_idx" ON "users" USING btree ("role");