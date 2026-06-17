import {
  index,
  pgTable,
  text,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core"
import { predictionReviewDecisionEnum } from "./enums"
import { predictionRecords } from "./prediction-records"

export const predictionReviews = pgTable(
  "prediction_reviews",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    predictionId: uuid("prediction_id")
      .notNull()
      .references(() => predictionRecords.id, { onDelete: "cascade" }),
    reviewer: text("reviewer").notNull(),
    decision: predictionReviewDecisionEnum("decision").notNull().default("pending"),
    notes: text("notes"),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index("prediction_reviews_prediction_id_idx").on(table.predictionId),
    index("prediction_reviews_decision_idx").on(table.decision),
    index("prediction_reviews_created_at_idx").on(table.createdAt),
  ],
)
