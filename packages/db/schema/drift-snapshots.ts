import {
  index,
  jsonb,
  pgTable,
  real,
  text,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core"

export const driftSnapshots = pgTable(
  "drift_snapshots",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    window: text("window").notNull(),
    featureDistributionChanges: jsonb("feature_distribution_changes")
      .$type<Record<string, unknown>>()
      .notNull(),
    riskDistributionChanges: jsonb("risk_distribution_changes")
      .$type<Record<string, unknown>>()
      .notNull(),
    predictionVolumeChanges: jsonb("prediction_volume_changes")
      .$type<Record<string, unknown>>()
      .notNull(),
    driftScore: real("drift_score").notNull().default(0),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index("drift_snapshots_created_at_idx").on(table.createdAt),
    index("drift_snapshots_drift_score_idx").on(table.driftScore),
  ],
)
