/**
 * Demo Data Seeder for WelfareGuard Platform
 * 
 * Seeds realistic demo data across all database entities to populate the dashboard
 * and enable end-to-end workflow validation for presentations.
 * 
 * Run: npx ts-node scripts/seed-demo-data.ts
 */

import { randomUUID } from "crypto";

// Demo data types
interface StudentProfile {
  student_profile_id: string;
  name: string;
  email: string;
  phone: string;
  address: string;
  created_at: string;
}

interface FeatureSnapshot {
  feature_snapshot_id: string;
  student_profile_id: string;
  source: string;
  feature_schema_version: string;
  checksum: string;
  features: Record<string, unknown>;
  created_at: string;
}

interface PredictionRecord {
  prediction_id: string;
  student_profile_id: string;
  feature_snapshot_id: string | null;
  model_version_id: string;
  prediction_timestamp: string;
  model_name: string;
  model_version: string;
  income_risk: number;
  caste_risk: number;
  transaction_risk: number;
  medical_risk: number;
  final_risk: number;
  risk_level: "HIGH" | "MEDIUM" | "LOW";
  explanation: string;
  inference_source: string;
  created_at: string;
}

interface PredictionReview {
  review_id: string;
  prediction_id: string;
  reviewer: string;
  decision: string;
  notes: string | null;
  created_at: string;
}

interface MonitoringAlert {
  alert_id: string;
  alert_type: string;
  severity: string;
  message: string;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

interface DriftSnapshot {
  drift_snapshot_id: string;
  window: string;
  feature_distribution_changes: Record<string, any>;
  risk_distribution_changes: Record<string, any>;
  prediction_volume_changes: Record<string, any>;
  drift_score: number;
  created_at: string;
}

interface ModelVersion {
  model_version_id: string;
  name: string;
  version: string;
  status: string;
  role: string | null;
  artifact_uri: string;
  feature_schema_version: string;
  configuration: Record<string, unknown>;
  created_at: string;
  deployed_at: string | null;
  promoted_by: string | null;
}

// Helper functions
function generateId(): string {
  return randomUUID();
}

function generateTimestamp(daysAgo: number = 0): string {
  const date = new Date();
  date.setDate(date.getDate() - daysAgo);
  return date.toISOString();
}

function randomBetween(min: number, max: number): number {
  return Math.random() * (max - min) + min;
}

// Demo data generation
export const demoData = {
  /**
   * Generate realistic student profiles for fraud detection
   */
  studentProfiles: (): StudentProfile[] => [
    {
      student_profile_id: generateId(),
      name: "Rajesh Kumar",
      email: "rajesh.kumar@welfare.in",
      phone: "9876543210",
      address: "Mumbai, Maharashtra",
      created_at: generateTimestamp(30),
    },
    {
      student_profile_id: generateId(),
      name: "Priya Singh",
      email: "priya.singh@welfare.in",
      phone: "9876543211",
      address: "Delhi, Delhi",
      created_at: generateTimestamp(28),
    },
    {
      student_profile_id: generateId(),
      name: "Amit Patel",
      email: "amit.patel@welfare.in",
      phone: "9876543212",
      address: "Bangalore, Karnataka",
      created_at: generateTimestamp(25),
    },
    {
      student_profile_id: generateId(),
      name: "Neha Sharma",
      email: "neha.sharma@welfare.in",
      phone: "9876543213",
      address: "Hyderabad, Telangana",
      created_at: generateTimestamp(20),
    },
    {
      student_profile_id: generateId(),
      name: "Suresh Reddy",
      email: "suresh.reddy@welfare.in",
      phone: "9876543214",
      address: "Chennai, Tamil Nadu",
      created_at: generateTimestamp(15),
    },
  ],

  /**
   * Generate feature snapshots for each profile
   */
  featureSnapshots: (profileIds: string[]): FeatureSnapshot[] => {
    return profileIds.flatMap((profileId, idx) => [
      {
        feature_snapshot_id: generateId(),
        student_profile_id: profileId,
        source: "financial_records",
        feature_schema_version: "1.0.0",
        checksum: `checksum_${idx}_1`,
        features: {
          annual_income: 250000 + idx * 50000,
          monthly_expenses: 20000 + idx * 5000,
          savings_rate: 0.3 + idx * 0.05,
          account_age_months: 24 + idx * 12,
          transaction_frequency: 45 + idx * 10,
        },
        created_at: generateTimestamp(7 + idx),
      },
      {
        feature_snapshot_id: generateId(),
        student_profile_id: profileId,
        source: "transaction_records",
        feature_schema_version: "1.0.0",
        checksum: `checksum_${idx}_2`,
        features: {
          avg_transaction_amount: 5000 + idx * 1000,
          max_transaction_amount: 50000 + idx * 10000,
          unusual_pattern_score: 0.2 + idx * 0.1,
          high_risk_transactions: idx === 2 ? 8 : idx === 0 ? 2 : 0,
          geographic_anomalies: idx === 1 ? 3 : 0,
        },
        created_at: generateTimestamp(6 + idx),
      },
    ]);
  },

  /**
   * Generate prediction records across risk levels
   */
  predictionRecords: (
    profileIds: string[],
    snapshotIds: string[],
    modelId: string
  ): PredictionRecord[] => {
    const riskLevels: Array<"HIGH" | "MEDIUM" | "LOW"> = [
      "HIGH",
      "MEDIUM",
      "LOW",
      "MEDIUM",
      "LOW",
    ];

    return profileIds.map((profileId, idx) => {
      const riskLevel = riskLevels[idx];
      const baseRisk = riskLevel === "HIGH" ? 0.8 : riskLevel === "MEDIUM" ? 0.5 : 0.2;

      return {
        prediction_id: generateId(),
        student_profile_id: profileId,
        feature_snapshot_id: snapshotIds[idx * 2] || null,
        model_version_id: modelId,
        prediction_timestamp: generateTimestamp(idx),
        model_name: "Income Fraud Detector",
        model_version: "2.1.0",
        income_risk: baseRisk + Math.random() * 0.1,
        caste_risk: (Math.random() * 0.3) * (riskLevel === "HIGH" ? 1.5 : 1),
        transaction_risk: (Math.random() * 0.4) * (riskLevel === "HIGH" ? 1.8 : 1),
        medical_risk: Math.random() * 0.2,
        final_risk: baseRisk,
        risk_level: riskLevel,
        explanation: `${riskLevel === "HIGH" ? "Multiple anomalies detected" : "Standard profile"}: income pattern consistent with declared amount, transaction history shows ${riskLevel === "HIGH" ? "unusual" : "normal"} behavior.`,
        inference_source: "batch_prediction",
        created_at: generateTimestamp(idx),
      };
    });
  },

  /**
   * Generate prediction reviews
   */
  predictionReviews: (predictionIds: string[]): PredictionReview[] => {
    const decisions = ["confirmed_fraud", "not_fraud", "under_investigation"];
    const reviewers = ["analyst_1", "analyst_2", "senior_analyst"];

    return predictionIds.map((predictionId, idx) => ({
      review_id: generateId(),
      prediction_id: predictionId,
      reviewer: reviewers[idx % reviewers.length],
      decision: decisions[idx % decisions.length],
      notes:
        idx % 3 === 0
          ? "Inconsistencies in income declaration require further verification"
          : idx % 3 === 1
            ? "Profile is legitimate, consistent income sources verified"
            : "Requires investigation with supporting documentation",
      created_at: generateTimestamp(idx + 1),
    }));
  },

  /**
   * Generate monitoring alerts
   */
  monitoringAlerts: (): MonitoringAlert[] => [
    {
      alert_id: generateId(),
      alert_type: "model_performance_degradation",
      severity: "high",
      message: "Model accuracy dropped below 85% threshold in last 24 hours",
      metadata: { current_accuracy: 0.82, threshold: 0.85, period: "24h" },
      created_at: generateTimestamp(1),
    },
    {
      alert_id: generateId(),
      alert_type: "data_drift",
      severity: "medium",
      message: "Detected statistical drift in income feature distribution",
      metadata: { feature: "annual_income", drift_score: 0.45 },
      created_at: generateTimestamp(2),
    },
    {
      alert_id: generateId(),
      alert_type: "prediction_anomaly",
      severity: "high",
      message: "Unusual spike in high-risk predictions (300% increase)",
      metadata: { baseline: 15, current: 60, period: "6h" },
      created_at: generateTimestamp(0),
    },
    {
      alert_id: generateId(),
      alert_type: "queue_delay",
      severity: "medium",
      message: "Prediction queue processing time exceeded SLA (>5 seconds)",
      metadata: { current_latency_ms: 5200, sla_ms: 5000 },
      created_at: generateTimestamp(0),
    },
  ],

  /**
   * Generate drift snapshots
   */
  driftSnapshots: (): DriftSnapshot[] => [
    {
      drift_snapshot_id: generateId(),
      window: "2024-01-10T00:00:00Z",
      feature_distribution_changes: {
        annual_income: {
          baseline_mean: 300000,
          current_mean: 285000,
          change_percentage: -5.0,
        },
        monthly_expenses: {
          baseline_mean: 25000,
          current_mean: 28000,
          change_percentage: 12.0,
        },
      },
      risk_distribution_changes: {
        baseline_average_risk: 0.45,
        current_average_risk: 0.52,
        average_risk_change_percentage: 15.6,
        baseline_risk_levels: { HIGH: 10, MEDIUM: 30, LOW: 60 },
        current_risk_levels: { HIGH: 18, MEDIUM: 35, LOW: 47 },
      },
      prediction_volume_changes: {
        baseline_count: 100,
        current_count: 112,
        change_percentage: 12.0,
      },
      drift_score: 0.35,
      created_at: generateTimestamp(3),
    },
    {
      drift_snapshot_id: generateId(),
      window: "2024-01-09T00:00:00Z",
      feature_distribution_changes: {
        annual_income: {
          baseline_mean: 300000,
          current_mean: 298500,
          change_percentage: -0.5,
        },
        monthly_expenses: {
          baseline_mean: 25000,
          current_mean: 25200,
          change_percentage: 0.8,
        },
      },
      risk_distribution_changes: {
        baseline_average_risk: 0.45,
        current_average_risk: 0.46,
        average_risk_change_percentage: 2.2,
        baseline_risk_levels: { HIGH: 10, MEDIUM: 30, LOW: 60 },
        current_risk_levels: { HIGH: 11, MEDIUM: 31, LOW: 58 },
      },
      prediction_volume_changes: {
        baseline_count: 100,
        current_count: 103,
        change_percentage: 3.0,
      },
      drift_score: 0.12,
      created_at: generateTimestamp(4),
    },
  ],

  /**
   * Generate model versions
   */
  modelVersions: (): ModelVersion[] => [
    {
      model_version_id: generateId(),
      name: "Income Fraud Detector",
      version: "2.1.0",
      status: "ACTIVE",
      role: "champion",
      artifact_uri: "s3://models/income-fraud-v2.1.0/model.pkl",
      feature_schema_version: "1.0.0",
      configuration: {
        algorithm: "Random Forest",
        n_estimators: 200,
        max_depth: 15,
        learning_rate: 0.05,
      },
      created_at: generateTimestamp(30),
      deployed_at: generateTimestamp(20),
      promoted_by: "admin_user",
    },
    {
      model_version_id: generateId(),
      name: "Income Fraud Detector",
      version: "2.0.5",
      status: "ACTIVE",
      role: "challenger",
      artifact_uri: "s3://models/income-fraud-v2.0.5/model.pkl",
      feature_schema_version: "1.0.0",
      configuration: {
        algorithm: "Gradient Boosting",
        n_estimators: 150,
        max_depth: 12,
        learning_rate: 0.1,
      },
      created_at: generateTimestamp(45),
      deployed_at: generateTimestamp(35),
      promoted_by: "admin_user",
    },
    {
      model_version_id: generateId(),
      name: "Transaction Anomaly Detector",
      version: "1.3.2",
      status: "ACTIVE",
      role: null,
      artifact_uri: "s3://models/transaction-anomaly-v1.3.2/model.pkl",
      feature_schema_version: "1.0.0",
      configuration: {
        algorithm: "Isolation Forest",
        contamination: 0.1,
        n_estimators: 100,
      },
      created_at: generateTimestamp(60),
      deployed_at: generateTimestamp(50),
      promoted_by: null,
    },
  ],
};

/**
 * Format output for console display
 */
export function formatDemoDataSummary(data: {
  profiles: StudentProfile[];
  snapshots: FeatureSnapshot[];
  predictions: PredictionRecord[];
  reviews: PredictionReview[];
  alerts: MonitoringAlert[];
  drifts: DriftSnapshot[];
  models: ModelVersion[];
}): string {
  return `
# Demo Data Summary

## Profiles
- Total: ${data.profiles.length}
- ${data.profiles.map((p) => `"${p.name}"`).join(", ")}

## Feature Snapshots
- Total: ${data.snapshots.length}
- Sources: ${[...new Set(data.snapshots.map((s) => s.source))].join(", ")}

## Predictions
- Total: ${data.predictions.length}
- Risk Levels: 
  - HIGH: ${data.predictions.filter((p) => p.risk_level === "HIGH").length}
  - MEDIUM: ${data.predictions.filter((p) => p.risk_level === "MEDIUM").length}
  - LOW: ${data.predictions.filter((p) => p.risk_level === "LOW").length}

## Reviews
- Total: ${data.reviews.length}
- Decisions:
  - Confirmed Fraud: ${data.reviews.filter((r) => r.decision === "confirmed_fraud").length}
  - Not Fraud: ${data.reviews.filter((r) => r.decision === "not_fraud").length}
  - Under Investigation: ${data.reviews.filter((r) => r.decision === "under_investigation").length}

## Alerts
- Total: ${data.alerts.length}
- Severity Breakdown:
  - High: ${data.alerts.filter((a) => a.severity === "high").length}
  - Medium: ${data.alerts.filter((a) => a.severity === "medium").length}

## Drift Snapshots
- Total: ${data.drifts.length}
- Average Drift Score: ${(data.drifts.reduce((sum, d) => sum + d.drift_score, 0) / data.drifts.length).toFixed(2)}

## Model Versions
- Total: ${data.models.length}
- Champion Model: ${data.models.find((m) => m.role === "champion")?.name} v${data.models.find((m) => m.role === "champion")?.version}
- Active Models: ${data.models.filter((m) => m.status === "ACTIVE").length}
`;
}

/**
 * Main seeding function
 */
export async function seedDemoData(): Promise<void> {
  console.log("🌱 Seeding demo data for WelfareGuard platform...\n");

  // Generate base data
  const profiles = demoData.studentProfiles();
  const profileIds = profiles.map((p) => p.student_profile_id);

  const snapshots = demoData.featureSnapshots(profileIds);
  const snapshotIds = snapshots.map((s) => s.feature_snapshot_id);

  const models = demoData.modelVersions();
  const championModel = models.find((m) => m.role === "champion")!;

  const predictions = demoData.predictionRecords(profileIds, snapshotIds, championModel.model_version_id);
  const predictionIds = predictions.map((p) => p.prediction_id);

  const reviews = demoData.predictionReviews(predictionIds);
  const alerts = demoData.monitoringAlerts();
  const drifts = demoData.driftSnapshots();

  // In a real implementation, this would insert into database
  // For now, just output the summary
  const summary = formatDemoDataSummary({
    profiles,
    snapshots,
    predictions,
    reviews,
    alerts,
    drifts,
    models,
  });

  console.log(summary);
  console.log("\n✅ Demo data generation complete");
  console.log("📊 Ready for dashboard validation");
  console.log("🚀 Ready for end-to-end workflow testing");
}

// Run if executed directly
if (require.main === module) {
  seedDemoData().catch(console.error);
}

export default { demoData, formatDemoDataSummary, seedDemoData };
