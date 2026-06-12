import {
  index,
  integer,
  pgTable,
  real,
  text,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core"
import { users } from "./users"

export const studentProfiles = pgTable(
  "student_profiles",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    externalId: text("external_id").unique(),
    createdByUserId: uuid("created_by_user_id").references(() => users.id, {
      onDelete: "set null",
    }),

    incomeInRs: real("income_in_rs"),
    landOwnedAcres: real("land_owned_acres"),
    vehiclesOwned: integer("vehicles_owned"),
    electricityConsumption: real("electricity_consumption"),
    pendingLoans: integer("pending_loans"),
    businessOwnership: integer("business_ownership"),

    caste: text("caste"),
    fatherCaste: text("father_caste"),
    avgCastePopulationPer: real("avg_caste_population_per"),
    officerApprovalsPerDay: real("officer_approvals_per_day"),

    weeklySpending: real("weekly_spending"),
    monthlySpending: real("monthly_spending"),
    transactionCount: integer("transaction_count"),
    avgTransactionValue: real("avg_transaction_value"),
    luxuryItemsBought: integer("luxury_items_bought"),
    weekendSpendingRatio: real("weekend_spending_ratio"),

    hospitalVisitsPerYear: integer("hospital_visits_per_year"),
    claimFrequency: integer("claim_frequency"),
    medicalClaimAmount: real("medical_claim_amount"),
    avgClaimAmount: real("avg_claim_amount"),
    chronicDisease: integer("chronic_disease"),

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
