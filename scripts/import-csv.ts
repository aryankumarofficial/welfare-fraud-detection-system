import { createPostgresClient } from "@repo/db/client";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, "../services/ml/data");
const CSV_FILES = {
  income: "income.csv",
  caste: "caste.csv",
  transaction: "transaction.csv",
  medical: "medical.csv",
};

function assert(condition: boolean, message: string): asserts condition {
  if (!condition) {
    throw new Error(message);
  }
}

function parseCsv(csvText: string): string[][] {
  const rows: string[][] = [];
  let current = "";
  let row: string[] = [];
  let inQuotes = false;

  for (let i = 0; i < csvText.length; i += 1) {
    const char = csvText[i];
    const next = csvText[i + 1];

    if (inQuotes) {
      if (char === '"') {
        if (next === '"') {
          current += '"';
          i += 1;
        } else {
          inQuotes = false;
        }
      } else {
        current += char;
      }
      continue;
    }

    if (char === '"') {
      inQuotes = true;
      continue;
    }

    if (char === ",") {
      row.push(current);
      current = "";
      continue;
    }

    if (char === "\n") {
      row.push(current);
      rows.push(row);
      current = "";
      row = [];
      continue;
    }

    if (char === "\r") {
      continue;
    }

    current += char;
  }

  if (current !== "" || row.length > 0) {
    row.push(current);
    rows.push(row);
  }

  return rows.filter((r) => r.length > 0 || r.some((cell) => cell !== ""));
}

function parseCsvRows(text: string): Array<Record<string, string>> {
  const rows = parseCsv(text);
  assert(rows.length > 0, "CSV file contains no rows.");

  const header = rows[0].map((cell) => cell.trim());
  assert(header.every(Boolean), "CSV header contains empty column names.");

  return rows.slice(1).map((row, rowIndex) => {
    assert(
      row.length === header.length,
      `CSV row ${rowIndex + 2} does not match header column count. Expected ${header.length}, got ${row.length}.`,
    );

    return Object.fromEntries(
      header.map((key, index) => [key, row[index].trim()]),
    );
  });
}

function parseFloatField(value: string, label: string): number {
  const parsed = Number(value);
  assert(!Number.isNaN(parsed), `Invalid numeric value for ${label}: ${value}`);
  return parsed;
}

function parseIntField(value: string, label: string): number {
  const parsed = Number(value);
  assert(
    Number.isInteger(parsed),
    `Invalid integer value for ${label}: ${value}`,
  );
  return parsed;
}

function profileExternalId(userId: string): string {
  assert(userId !== "", "user_id must not be empty.");
  return userId;
}

async function readCsvFile(
  fileName: string,
): Promise<Array<Record<string, string>>> {
  const filePath = join(DATA_DIR, fileName);
  const text = await Bun.file(filePath).text();
  return parseCsvRows(text);
}

function areRecordsEqual<T extends Record<string, unknown>>(
  existing: T,
  values: T,
): boolean {
  for (const key of Object.keys(values)) {
    const existingValue = existing[key];
    const newValue = values[key];

    if (typeof existingValue === "number" || typeof newValue === "number") {
      if (Number(existingValue) !== Number(newValue)) {
        return false;
      }
      continue;
    }

    if (existingValue !== newValue) {
      return false;
    }
  }

  return true;
}

async function main() {
  const client = createPostgresClient();

  const incomeRows = await readCsvFile(CSV_FILES.income);
  const casteRows = await readCsvFile(CSV_FILES.caste);
  const transactionRows = await readCsvFile(CSV_FILES.transaction);
  const medicalRows = await readCsvFile(CSV_FILES.medical);

  const profiles = new Map<string, { id: string; region?: string }>();
  let financialInserted = 0;
  let socialInserted = 0;
  let transactionInserted = 0;
  let medicalInserted = 0;

  await client.begin(async (tx) => {
    for (const row of [
      ...incomeRows,
      ...casteRows,
      ...transactionRows,
      ...medicalRows,
    ]) {
      const externalId = profileExternalId(row.user_id);
      if (!profiles.has(externalId)) {
        const region = row.state ?? null;
        const result = await tx`
          INSERT INTO student_profiles (external_id, region)
          VALUES (${externalId}, ${region})
          ON CONFLICT (external_id)
          DO UPDATE SET region = COALESCE(student_profiles.region, EXCLUDED.region)
          RETURNING id;
        `;
        const profileId = result[0]?.id;
        assert(
          profileId,
          `Failed to create or load student_profiles for external_id=${externalId}`,
        );
        profiles.set(externalId, { id: profileId, region });
      }
    }

    for (const row of incomeRows) {
      const externalId = profileExternalId(row.user_id);
      const profile = profiles.get(externalId);
      assert(profile, `Profile missing for income user_id=${externalId}`);
      const studentProfileId = profile.id;

      const values = {
        income_in_rs: parseFloatField(row.income_in_rs, "income_in_rs"),
        land_owned_acres: parseFloatField(
          row.land_owned_acres,
          "land_owned_acres",
        ),
        vehicles_owned: parseIntField(row.vehicles_owned, "vehicles_owned"),
        electricity_consumption: parseFloatField(
          row.electricity_consumption,
          "electricity_consumption",
        ),
        pending_loans: parseIntField(row.pending_loans, "pending_loans"),
        business_ownership: parseIntField(
          row.business_ownership,
          "business_ownership",
        ),
      };

      const existing = await tx`
        SELECT income_in_rs, land_owned_acres, vehicles_owned, electricity_consumption, pending_loans, business_ownership
        FROM student_financial_records
        WHERE student_profile_id = ${studentProfileId}
        ORDER BY created_at DESC
        LIMIT 1;
      `;

      if (existing.length === 0 || !areRecordsEqual(existing[0], values)) {
        await tx`
          INSERT INTO student_financial_records (
            student_profile_id,
            income_in_rs,
            land_owned_acres,
            vehicles_owned,
            electricity_consumption,
            pending_loans,
            business_ownership
          ) VALUES (
            ${studentProfileId},
            ${values.income_in_rs},
            ${values.land_owned_acres},
            ${values.vehicles_owned},
            ${values.electricity_consumption},
            ${values.pending_loans},
            ${values.business_ownership}
          );
        `;
        financialInserted += 1;
      }
    }

    for (const row of casteRows) {
      const externalId = profileExternalId(row.user_id);
      const profile = profiles.get(externalId);
      assert(profile, `Profile missing for caste user_id=${externalId}`);
      const studentProfileId = profile.id;
      const values = {
        caste: row.caste,
        father_caste: row.father_caste,
        avg_caste_population_per: parseFloatField(
          row.avg_caste_population_per,
          "avg_caste_population_per",
        ),
        officer_approvals_per_day: parseFloatField(
          row.officer_approvals_per_day,
          "officer_approvals_per_day",
        ),
      };

      const existing = await tx`
        SELECT caste, father_caste, avg_caste_population_per, officer_approvals_per_day
        FROM student_social_records
        WHERE student_profile_id = ${studentProfileId}
        ORDER BY created_at DESC
        LIMIT 1;
      `;

      if (existing.length === 0 || !areRecordsEqual(existing[0], values)) {
        await tx`
          INSERT INTO student_social_records (
            student_profile_id,
            caste,
            father_caste,
            avg_caste_population_per,
            officer_approvals_per_day
          ) VALUES (
            ${studentProfileId},
            ${values.caste},
            ${values.father_caste},
            ${values.avg_caste_population_per},
            ${values.officer_approvals_per_day}
          );
        `;
        socialInserted += 1;
      }
    }

    for (const row of transactionRows) {
      const externalId = profileExternalId(row.user_id);
      const profile = profiles.get(externalId);
      assert(profile, `Profile missing for transaction user_id=${externalId}`);
      const studentProfileId = profile.id;
      const values = {
        weekly_spending: parseFloatField(
          row.weekly_spending,
          "weekly_spending",
        ),
        monthly_spending: parseFloatField(
          row.monthly_spending,
          "monthly_spending",
        ),
        transaction_count: parseIntField(
          row.transaction_count,
          "transaction_count",
        ),
        avg_transaction_value: parseFloatField(
          row.avg_transaction_value,
          "avg_transaction_value",
        ),
        luxury_items_bought: parseIntField(
          row.luxury_items_bought,
          "luxury_items_bought",
        ),
        weekend_spending_ratio: parseFloatField(
          row.weekend_spending_ratio,
          "weekend_spending_ratio",
        ),
      };

      const existing = await tx`
        SELECT weekly_spending, monthly_spending, transaction_count, avg_transaction_value, luxury_items_bought, weekend_spending_ratio
        FROM student_transaction_summaries
        WHERE student_profile_id = ${studentProfileId}
        ORDER BY created_at DESC
        LIMIT 1;
      `;

      if (existing.length === 0 || !areRecordsEqual(existing[0], values)) {
        await tx`
          INSERT INTO student_transaction_summaries (
            student_profile_id,
            weekly_spending,
            monthly_spending,
            transaction_count,
            avg_transaction_value,
            luxury_items_bought,
            weekend_spending_ratio
          ) VALUES (
            ${studentProfileId},
            ${values.weekly_spending},
            ${values.monthly_spending},
            ${values.transaction_count},
            ${values.avg_transaction_value},
            ${values.luxury_items_bought},
            ${values.weekend_spending_ratio}
          );
        `;
        transactionInserted += 1;
      }
    }

    for (const row of medicalRows) {
      const externalId = profileExternalId(row.user_id);
      const profile = profiles.get(externalId);
      assert(profile, `Profile missing for medical user_id=${externalId}`);
      const studentProfileId = profile.id;
      const values = {
        hospital_visits_per_year: parseIntField(
          row.hospital_visits_per_year,
          "hospital_visits_per_year",
        ),
        claim_frequency: parseIntField(row.claim_frequency, "claim_frequency"),
        medical_claim_amount: parseFloatField(
          row.medical_claim_amount,
          "medical_claim_amount",
        ),
        avg_claim_amount: parseFloatField(
          row.avg_claim_amount,
          "avg_claim_amount",
        ),
        chronic_disease: parseIntField(row.chronic_disease, "chronic_disease"),
      };

      const existing = await tx`
        SELECT hospital_visits_per_year, claim_frequency, medical_claim_amount, avg_claim_amount, chronic_disease
        FROM student_medical_summaries
        WHERE student_profile_id = ${studentProfileId}
        ORDER BY created_at DESC
        LIMIT 1;
      `;

      if (existing.length === 0 || !areRecordsEqual(existing[0], values)) {
        await tx`
          INSERT INTO student_medical_summaries (
            student_profile_id,
            hospital_visits_per_year,
            claim_frequency,
            medical_claim_amount,
            avg_claim_amount,
            chronic_disease
          ) VALUES (
            ${studentProfileId},
            ${values.hospital_visits_per_year},
            ${values.claim_frequency},
            ${values.medical_claim_amount},
            ${values.avg_claim_amount},
            ${values.chronic_disease}
          );
        `;
        medicalInserted += 1;
      }
    }
  });

  const totals = await client`
    SELECT
      (SELECT COUNT(*) FROM student_profiles) AS profiles,
      (SELECT COUNT(*) FROM student_financial_records) AS financial_records,
      (SELECT COUNT(*) FROM student_social_records) AS social_records,
      (SELECT COUNT(*) FROM student_transaction_summaries) AS transaction_records,
      (SELECT COUNT(*) FROM student_medical_summaries) AS medical_records,
      (SELECT MAX(created_at) FROM student_profiles) AS imported_at;
  `;

  const summary = totals[0];
  console.log("CSV import completed successfully.");
  console.log(
    JSON.stringify(
      {
        profiles: Number(summary.profiles),
        financial_records: Number(summary.financial_records),
        social_records: Number(summary.social_records),
        transaction_records: Number(summary.transaction_records),
        medical_records: Number(summary.medical_records),
        imported_at: summary.imported_at?.toISOString?.() ?? null,
        status: "completed",
        inserted: {
          financialInserted,
          socialInserted,
          transactionInserted,
          medicalInserted,
        },
      },
      null,
      2,
    ),
  );
}

main().catch((error) => {
  console.error("CSV import failed:", error);
  process.exit(1);
});
