import {
  boolean,
  index,
  jsonb,
  pgTable,
  text,
  timestamp,
  uniqueIndex,
  uuid,
} from "drizzle-orm/pg-core"

export const modelVersions = pgTable(
  "model_versions",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    name: text("name").notNull(),
    version: text("version").notNull(),
    description: text("description"),
    artifactUri: text("artifact_uri"),
    configuration: jsonb("configuration").$type<Record<string, unknown>>(),
    isActive: boolean("is_active").notNull().default(false),
    deployedAt: timestamp("deployed_at", { withTimezone: true }),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    uniqueIndex("model_versions_name_version_uidx").on(table.name, table.version),
    index("model_versions_is_active_idx").on(table.isActive),
  ],
)
