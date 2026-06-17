import {
  index,
  integer,
  pgTable,
  real,
  text,
  timestamp,
  uuid,
} from "drizzle-orm/pg-core"
import { studentProfiles } from "./student-profiles"

export const studentFinancialRecords = pgTable(
  "student_financial_records",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    studentProfileId: uuid("student_profile_id")
      .notNull()
      .references(() => studentProfiles.id, { onDelete: "cascade" }),
    incomeInRs: real("income_in_rs").notNull(),
    landOwnedAcres: real("land_owned_acres").notNull(),
    vehiclesOwned: integer("vehicles_owned").notNull(),
    electricityConsumption: real("electricity_consumption").notNull(),
    pendingLoans: integer("pending_loans").notNull(),
    businessOwnership: integer("business_ownership").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("student_financial_records_profile_created_at_idx").on(
      table.studentProfileId,
      table.createdAt,
    ),
  ],
)

export const studentSocialRecords = pgTable(
  "student_social_records",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    studentProfileId: uuid("student_profile_id")
      .notNull()
      .references(() => studentProfiles.id, { onDelete: "cascade" }),
    caste: text("caste").notNull(),
    fatherCaste: text("father_caste").notNull(),
    avgCastePopulationPer: real("avg_caste_population_per").notNull(),
    officerApprovalsPerDay: real("officer_approvals_per_day").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("student_social_records_profile_created_at_idx").on(
      table.studentProfileId,
      table.createdAt,
    ),
  ],
)

export const studentTransactionSummaries = pgTable(
  "student_transaction_summaries",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    studentProfileId: uuid("student_profile_id")
      .notNull()
      .references(() => studentProfiles.id, { onDelete: "cascade" }),
    weeklySpending: real("weekly_spending").notNull(),
    monthlySpending: real("monthly_spending").notNull(),
    transactionCount: integer("transaction_count").notNull(),
    avgTransactionValue: real("avg_transaction_value").notNull(),
    luxuryItemsBought: integer("luxury_items_bought").notNull(),
    weekendSpendingRatio: real("weekend_spending_ratio").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("student_transaction_summaries_profile_created_at_idx").on(
      table.studentProfileId,
      table.createdAt,
    ),
  ],
)

export const studentMedicalSummaries = pgTable(
  "student_medical_summaries",
  {
    id: uuid("id").defaultRandom().primaryKey(),
    studentProfileId: uuid("student_profile_id")
      .notNull()
      .references(() => studentProfiles.id, { onDelete: "cascade" }),
    hospitalVisitsPerYear: integer("hospital_visits_per_year").notNull(),
    claimFrequency: integer("claim_frequency").notNull(),
    medicalClaimAmount: real("medical_claim_amount").notNull(),
    avgClaimAmount: real("avg_claim_amount").notNull(),
    chronicDisease: integer("chronic_disease").notNull(),
    createdAt: timestamp("created_at", { withTimezone: true })
      .notNull()
      .defaultNow(),
  },
  (table) => [
    index("student_medical_summaries_profile_created_at_idx").on(
      table.studentProfileId,
      table.createdAt,
    ),
  ],
)
