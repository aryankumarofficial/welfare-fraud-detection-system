import {
  index,
  jsonb,
  pgTable,
  text,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core"
import { featureSourceEnum } from "./enums"
import { studentProfiles } from "./student-profiles"

export const featureSnapshots = pgTable(
  "feature_snapshots",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    studentProfileId: uuid("student_profile_id")
      .notNull()
      .references(() => studentProfiles.id, { onDelete: "cascade" }),
    source: featureSourceEnum("source").notNull().default("api_payload"),
    features: jsonb("features").$type<Record<string, unknown>>().notNull(),
    featureSchemaVersion: text("feature_schema_version").notNull().default("v1"),
    checksum: text("checksum"),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("feature_snapshots_student_profile_id_idx").on(table.studentProfileId),
    index("feature_snapshots_checksum_idx").on(table.checksum),
    index("feature_snapshots_created_at_idx").on(table.createdAt),
  ],
)
