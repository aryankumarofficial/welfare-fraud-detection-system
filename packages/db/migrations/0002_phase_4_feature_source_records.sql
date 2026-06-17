CREATE TABLE "student_financial_records" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"student_profile_id" uuid NOT NULL,
	"income_in_rs" real NOT NULL,
	"land_owned_acres" real NOT NULL,
	"vehicles_owned" integer NOT NULL,
	"electricity_consumption" real NOT NULL,
	"pending_loans" integer NOT NULL,
	"business_ownership" integer NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "student_social_records" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"student_profile_id" uuid NOT NULL,
	"caste" text NOT NULL,
	"father_caste" text NOT NULL,
	"avg_caste_population_per" real NOT NULL,
	"officer_approvals_per_day" real NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "student_transaction_summaries" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"student_profile_id" uuid NOT NULL,
	"weekly_spending" real NOT NULL,
	"monthly_spending" real NOT NULL,
	"transaction_count" integer NOT NULL,
	"avg_transaction_value" real NOT NULL,
	"luxury_items_bought" integer NOT NULL,
	"weekend_spending_ratio" real NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
CREATE TABLE "student_medical_summaries" (
	"id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
	"student_profile_id" uuid NOT NULL,
	"hospital_visits_per_year" integer NOT NULL,
	"claim_frequency" integer NOT NULL,
	"medical_claim_amount" real NOT NULL,
	"avg_claim_amount" real NOT NULL,
	"chronic_disease" integer NOT NULL,
	"created_at" timestamp with time zone DEFAULT now() NOT NULL
);
--> statement-breakpoint
ALTER TABLE "student_financial_records" ADD CONSTRAINT "student_financial_records_student_profile_id_student_profiles_id_fk" FOREIGN KEY ("student_profile_id") REFERENCES "public"."student_profiles"("id") ON DELETE cascade ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "student_social_records" ADD CONSTRAINT "student_social_records_student_profile_id_student_profiles_id_fk" FOREIGN KEY ("student_profile_id") REFERENCES "public"."student_profiles"("id") ON DELETE cascade ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "student_transaction_summaries" ADD CONSTRAINT "student_transaction_summaries_student_profile_id_student_profiles_id_fk" FOREIGN KEY ("student_profile_id") REFERENCES "public"."student_profiles"("id") ON DELETE cascade ON UPDATE no action;
--> statement-breakpoint
ALTER TABLE "student_medical_summaries" ADD CONSTRAINT "student_medical_summaries_student_profile_id_student_profiles_id_fk" FOREIGN KEY ("student_profile_id") REFERENCES "public"."student_profiles"("id") ON DELETE cascade ON UPDATE no action;
--> statement-breakpoint
CREATE INDEX "student_financial_records_profile_created_at_idx" ON "student_financial_records" USING btree ("student_profile_id","created_at");
--> statement-breakpoint
CREATE INDEX "student_social_records_profile_created_at_idx" ON "student_social_records" USING btree ("student_profile_id","created_at");
--> statement-breakpoint
CREATE INDEX "student_transaction_summaries_profile_created_at_idx" ON "student_transaction_summaries" USING btree ("student_profile_id","created_at");
--> statement-breakpoint
CREATE INDEX "student_medical_summaries_profile_created_at_idx" ON "student_medical_summaries" USING btree ("student_profile_id","created_at");
