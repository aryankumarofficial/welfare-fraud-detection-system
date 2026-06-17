import { relations } from "drizzle-orm"
import { auditLogs } from "./audit-logs"
import { featureSnapshots } from "./feature-snapshots"
import { modelVersions } from "./model-versions"
import { predictionRecords } from "./prediction-records"
import { predictionJobs } from "./prediction-jobs"
import {
  studentFinancialRecords,
  studentMedicalSummaries,
  studentSocialRecords,
  studentTransactionSummaries,
} from "./source-records"
import { studentProfiles } from "./student-profiles"
import { users } from "./users"

export const usersRelations = relations(users, ({ many }) => ({
  studentProfiles: many(studentProfiles),
  predictionRecords: many(predictionRecords),
  auditLogs: many(auditLogs),
}))

export const studentProfilesRelations = relations(
  studentProfiles,
  ({ one, many }) => ({
    createdByUser: one(users, {
      fields: [studentProfiles.createdByUserId],
      references: [users.id],
    }),
    featureSnapshots: many(featureSnapshots),
    financialRecords: many(studentFinancialRecords),
    medicalSummaries: many(studentMedicalSummaries),
    predictionRecords: many(predictionRecords),
    predictionJobs: many(predictionJobs),
    socialRecords: many(studentSocialRecords),
    transactionSummaries: many(studentTransactionSummaries),
  }),
)

export const modelVersionsRelations = relations(modelVersions, ({ many }) => ({
  predictionRecords: many(predictionRecords),
}))

export const featureSnapshotsRelations = relations(
  featureSnapshots,
  ({ one, many }) => ({
    studentProfile: one(studentProfiles, {
      fields: [featureSnapshots.studentProfileId],
      references: [studentProfiles.id],
    }),
    predictionRecords: many(predictionRecords),
    predictionJobs: many(predictionJobs),
  }),
)

export const predictionRecordsRelations = relations(
  predictionRecords,
  ({ one }) => ({
    studentProfile: one(studentProfiles, {
      fields: [predictionRecords.studentProfileId],
      references: [studentProfiles.id],
    }),
    featureSnapshot: one(featureSnapshots, {
      fields: [predictionRecords.featureSnapshotId],
      references: [featureSnapshots.id],
    }),
    modelVersion: one(modelVersions, {
      fields: [predictionRecords.modelVersionId],
      references: [modelVersions.id],
    }),
    requestedByUser: one(users, {
      fields: [predictionRecords.requestedByUserId],
      references: [users.id],
    }),
  }),
)

export const predictionJobsRelations = relations(predictionJobs, ({ one }) => ({
  studentProfile: one(studentProfiles, {
    fields: [predictionJobs.studentProfileId],
    references: [studentProfiles.id],
  }),
  featureSnapshot: one(featureSnapshots, {
    fields: [predictionJobs.featureSnapshotId],
    references: [featureSnapshots.id],
  }),
  predictionRecord: one(predictionRecords, {
    fields: [predictionJobs.predictionRecordId],
    references: [predictionRecords.id],
  }),
}))

export const studentFinancialRecordsRelations = relations(
  studentFinancialRecords,
  ({ one }) => ({
    studentProfile: one(studentProfiles, {
      fields: [studentFinancialRecords.studentProfileId],
      references: [studentProfiles.id],
    }),
  }),
)

export const studentSocialRecordsRelations = relations(
  studentSocialRecords,
  ({ one }) => ({
    studentProfile: one(studentProfiles, {
      fields: [studentSocialRecords.studentProfileId],
      references: [studentProfiles.id],
    }),
  }),
)

export const studentTransactionSummariesRelations = relations(
  studentTransactionSummaries,
  ({ one }) => ({
    studentProfile: one(studentProfiles, {
      fields: [studentTransactionSummaries.studentProfileId],
      references: [studentProfiles.id],
    }),
  }),
)

export const studentMedicalSummariesRelations = relations(
  studentMedicalSummaries,
  ({ one }) => ({
    studentProfile: one(studentProfiles, {
      fields: [studentMedicalSummaries.studentProfileId],
      references: [studentProfiles.id],
    }),
  }),
)

export const auditLogsRelations = relations(auditLogs, ({ one }) => ({
  actorUser: one(users, {
    fields: [auditLogs.actorUserId],
    references: [users.id],
  }),
}))
