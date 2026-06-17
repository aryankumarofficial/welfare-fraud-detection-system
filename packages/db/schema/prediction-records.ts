import {
  index,
  pgTable,
  real,
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
    incomeRisk: real("income_risk").notNull(),
    casteRisk: real("caste_risk").notNull(),
    transactionRisk: real("transaction_risk").notNull(),
    medicalRisk: real("medical_risk").notNull(),
    finalRisk: real("final_risk").notNull(),
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
  ],
)
