import {
  index,
  integer,
  jsonb,
  pgTable,
  text,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core"
import { featureSnapshots } from "./feature-snapshots"
import { predictionRecords } from "./prediction-records"
import { studentProfiles } from "./student-profiles"

export const predictionJobs = pgTable(
  "prediction_jobs",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    bullmqJobId: text("bullmq_job_id"),
    batchId: uuid("batch_id"),
    studentProfileId: uuid("student_profile_id")
      .notNull()
      .references(() => studentProfiles.id, { onDelete: "cascade" }),
    featureSnapshotId: uuid("feature_snapshot_id").references(
      () => featureSnapshots.id,
      { onDelete: "set null" },
    ),
    predictionRecordId: uuid("prediction_record_id").references(
      () => predictionRecords.id,
      { onDelete: "set null" },
    ),
    status: text("status").notNull().default("pending"),
    attempts: integer("attempts").notNull().default(0),
    maxAttempts: integer("max_attempts").notNull().default(3),
    lastError: text("last_error"),
    result: jsonb("result"),
    metadata: jsonb("metadata"),
    queuedAt: timestamp("queued_at", { withTimezone: true }),
    startedAt: timestamp("started_at", { withTimezone: true }),
    completedAt: timestamp("completed_at", { withTimezone: true }),
    failedAt: timestamp("failed_at", { withTimezone: true }),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index("prediction_jobs_status_idx").on(table.status),
    index("prediction_jobs_batch_id_idx").on(table.batchId),
    index("prediction_jobs_student_profile_id_idx").on(table.studentProfileId),
    index("prediction_jobs_prediction_record_id_idx").on(table.predictionRecordId),
    index("prediction_jobs_created_at_idx").on(table.createdAt),
  ],
)
