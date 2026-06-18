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
import { modelRoleEnum, modelStatusEnum } from "./enums"

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
    status: modelStatusEnum("status").notNull().default("DRAFT"),
    role: modelRoleEnum("role").notNull().default("none"),
    parentModelId: uuid("parent_model_id"),
    artifactHash: text("artifact_hash"),
    trainingMetadata: jsonb("training_metadata").$type<Record<string, unknown>>(),
    featureSchemaVersion: text("feature_schema_version"),
    promotedAt: timestamp("promoted_at", { withTimezone: true }),
    promotedBy: text("promoted_by"),
    rolledBackAt: timestamp("rolled_back_at", { withTimezone: true }),
  },
  (table) => [
    uniqueIndex("model_versions_name_version_uidx").on(table.name, table.version),
    index("model_versions_is_active_idx").on(table.isActive),
    index("model_versions_status_idx").on(table.status),
    index("model_versions_role_idx").on(table.role),
    index("model_versions_parent_model_id_idx").on(table.parentModelId),
  ],
)
