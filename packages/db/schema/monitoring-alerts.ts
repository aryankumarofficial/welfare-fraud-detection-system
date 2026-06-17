import {
  index,
  jsonb,
  pgTable,
  text,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core"
import { monitoringAlertSeverityEnum, monitoringAlertTypeEnum } from "./enums"

export const monitoringAlerts = pgTable(
  "monitoring_alerts",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    alertType: monitoringAlertTypeEnum("alert_type").notNull(),
    severity: monitoringAlertSeverityEnum("severity").notNull().default("warning"),
    message: text("message").notNull(),
    metadata: jsonb("metadata").$type<Record<string, unknown>>(),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (table) => [
    index("monitoring_alerts_alert_type_idx").on(table.alertType),
    index("monitoring_alerts_severity_idx").on(table.severity),
    index("monitoring_alerts_created_at_idx").on(table.createdAt),
  ],
)
