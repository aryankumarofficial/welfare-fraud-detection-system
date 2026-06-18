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
import { modelVersions } from "./model-versions"

export const modelEvaluationRuns = pgTable(
  "model_evaluation_runs",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    modelVersionId: uuid("model_version_id")
      .notNull()
      .references(() => modelVersions.id, { onDelete: "cascade" }),
    datasetName: text("dataset_name").notNull(),
    datasetVersion: text("dataset_version"),
    sampleSize: integer("sample_size").notNull(),
    precision: real("precision").notNull(),
    recall: real("recall").notNull(),
    f1Score: real("f1_score").notNull(),
    falsePositiveRate: real("false_positive_rate").notNull(),
    additionalMetrics: jsonb("additional_metrics").$type<Record<string, unknown>>(),
    evaluatedBy: text("evaluated_by"),
    evaluatedAt: timestamp("evaluated_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("model_evaluation_runs_model_version_id_idx").on(table.modelVersionId),
    index("model_evaluation_runs_evaluated_at_idx").on(table.evaluatedAt),
  ],
)
