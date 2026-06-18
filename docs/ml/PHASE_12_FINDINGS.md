# Phase 12 Findings

This document summarizes the audit findings for CSV ingestion, data lineage, startup bootstrap, and demo data reality.

## Key findings

1. `services/ml/data/*.csv` are training-only datasets.
   - Confirmed by `services/ml/src/train.py` reading all 4 CSV files.
   - No other repository file references `pd.read_csv` or loads these CSVs.

2. There is no CSV ingestion into PostgreSQL.
   - `packages/db/migrate.ts` only applies schema migrations.
   - Startup automation in `docker-compose.yml` does not include CSV import.
   - No import path exists in `apps/api`, `services/ml`, `workers`, or `packages/db`.

3. Runtime prediction depends on source tables that are not populated from CSV in repo startup.
   - `services/ml/src/services/feature_builder.py` and snapshot generation expect source records.
   - Those source tables remain empty after `bun run db:migrate`.

4. Demo seeder is synthetic and separate from CSV data.
   - `scripts/seed-demo-data.ts` generates fake records instead of loading repository CSVs.
   - It is a presentation/demo generator, not a CSV ingestion tool.

## Verdict

- A fresh environment started with `docker compose up --build` will have schema only.
- The repository does not currently provide a working CSV-to-PostgreSQL data ingestion pipeline.
- Data lineage from `services/ml/data/*.csv` to runtime database tables is missing.
- For demo correctness, the project relies on synthetic/demo data rather than ingesting the raw CSV datasets.

## Recommendations

- Add an import script or service for the CSV files.
- Wire that script into `docker-compose.yml` after migrations.
- Document the source table schema mappings.
- Reserve `scripts/seed-demo-data.ts` for synthetic demo scenarios.
