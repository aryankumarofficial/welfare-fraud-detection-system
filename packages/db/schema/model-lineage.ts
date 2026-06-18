import {
  index,
  jsonb,
  pgTable,
  text,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core"
import { modelVersions } from "./model-versions"

export const modelLineageEvents = pgTable(
  "model_lineage_events",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    modelVersionId: uuid("model_version_id")
      .notNull()
      .references(() => modelVersions.id, { onDelete: "cascade" }),
    eventType: text("event_type").notNull(),
    fromStatus: text("from_status"),
    toStatus: text("to_status"),
    fromRole: text("from_role"),
    toRole: text("to_role"),
    metadata: jsonb("metadata").$type<Record<string, unknown>>(),
    performedBy: text("performed_by"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("model_lineage_events_model_version_id_idx").on(table.modelVersionId),
    index("model_lineage_events_event_type_idx").on(table.eventType),
    index("model_lineage_events_created_at_idx").on(table.createdAt),
  ],
)
