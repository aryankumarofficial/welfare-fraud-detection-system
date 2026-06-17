import { date, index, pgTable, text, timestamp, uuid } from "drizzle-orm/pg-core"
import { users } from "./users"

export const studentProfiles = pgTable(
  "student_profiles",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    externalId: text("external_id").unique(),
    name: text("name"),
    dateOfBirth: date("date_of_birth"),
    gender: text("gender"),
    region: text("region"),
    createdByUserId: uuid("created_by_user_id").references(() => users.id, {
      onDelete: "set null",
    }),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true })
      .notNull()
      .defaultNow()
      .$onUpdate(() => new Date()),
  },
  (table) => [
    index("student_profiles_external_id_idx").on(table.externalId),
    index("student_profiles_created_by_user_id_idx").on(table.createdByUserId),
  ],
)
