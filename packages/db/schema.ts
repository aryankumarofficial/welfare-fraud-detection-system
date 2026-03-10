import { pgTable, text, uuid } from "drizzle-orm/pg-core"

export const beneficiaries = pgTable("beneficiaries", {
  id: uuid("id").primaryKey(),
  name: text("name"),
})
