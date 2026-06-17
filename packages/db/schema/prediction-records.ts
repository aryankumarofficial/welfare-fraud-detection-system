import {
  index,
  integer,
  jsonb,
  pgTable,
  real,
  text,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core"
import { inferenceSourceEnum } from "./enums"
import { featureSnapshots } from "./feature-snapshots"
import { modelVersions } from "./model-versions"
import { studentProfiles } from "./student-profiles"
import { users } from "./users"

export const predictionRecords = pgTable(
  "prediction_records",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    studentProfileId: uuid("student_profile_id")
      .notNull()
      .references(() => studentProfiles.id, { onDelete: "cascade" }),
    featureSnapshotId: uuid("feature_snapshot_id").references(
      () => featureSnapshots.id,
      { onDelete: "set null" },
    ),
    modelVersionId: uuid("model_version_id").references(() => modelVersions.id, {
      onDelete: "set null",
    }),
    jobId: uuid("job_id"),
    predictionTimestamp: timestamp("prediction_timestamp", { withTimezone: true }),
    modelName: text("model_name"),
    modelVersion: text("model_version"),
    snapshotChecksum: text("snapshot_checksum"),
    predictionDurationMs: integer("prediction_duration_ms"),
    incomeRisk: real("income_risk").notNull(),
    casteRisk: real("caste_risk").notNull(),
    transactionRisk: real("transaction_risk").notNull(),
    medicalRisk: real("medical_risk").notNull(),
    finalRisk: real("final_risk").notNull(),
    riskLevel: text("risk_level"),
    explanation: jsonb("explanation").$type<Record<string, unknown>>(),
    inferenceSource: inferenceSourceEnum("inference_source")
      .notNull()
      .default("sync"),
    requestedByUserId: uuid("requested_by_user_id").references(() => users.id, {
      onDelete: "set null",
    }),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("prediction_records_student_profile_id_idx").on(table.studentProfileId),
    index("prediction_records_created_at_idx").on(table.createdAt),
    index("prediction_records_final_risk_idx").on(table.finalRisk),
    index("prediction_records_model_version_id_idx").on(table.modelVersionId),
    index("prediction_records_job_id_idx").on(table.jobId),
    index("prediction_records_prediction_timestamp_idx").on(table.predictionTimestamp),
    index("prediction_records_risk_level_idx").on(table.riskLevel),
  ],
)
