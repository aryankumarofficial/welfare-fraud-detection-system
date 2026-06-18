# CSV Import Design

This document captures design requirements for an ingestion path that is currently missing from the repository.

## Existing gap

- `services/ml/data/*.csv` exist as raw training datasets.
- `services/ml/src/train.py` consumes these CSV files for model training only.
- There is no repository code to import CSV rows into PostgreSQL source tables.
- Startup automation does not include CSV ingestion.

## Proposed import design

### Goals

- Load CSV rows into database tables for runtime feature building.
- Keep training CSV usage separate from runtime ingestion.
- Provide an idempotent startup path for fresh deployments.
- Enable repeatable seeding for development and demo environments.

### Recommended components

1. `scripts/import-csv.ts` or `packages/db/src/importCsv.ts`
   - Reads CSV files from `services/ml/data/`
   - Maps CSV columns to source table columns
   - Inserts rows into PostgreSQL with upsert semantics or transaction-based batch inserts

2. `docker-compose.yml` entry
   - Add a service or init container that runs after `migrate`
   - Example: `csv-importer` depends on `postgres:healthy` and `migrate`
   - Runs `bun run import:csv` or equivalent

3. Source table mapping
   - `income.csv` → `student_financial_records`
   - `caste.csv` → `student_social_records`
   - `transaction.csv` → `student_transaction_summaries`
   - `medical.csv` → `student_medical_summaries`

4. Validation and idempotence
   - Skip duplicate rows by unique key or composite index
   - Validate column types before insert
   - Use transactions to avoid partial loads

5. Runtime population check
   - After import, `services/ml/src/services/feature_builder.py` can generate feature snapshots from populated source tables
   - Prediction flows can then be executed against real data rather than synthetic demo data

## Short-term alternative

- Use a manual import script for development only.
- Keep `scripts/seed-demo-data.ts` for demo generation while building the importer.

## Notes

- This design is not implemented in the current repository.
- It is a recommended future improvement to make repository data usable for runtime predictions.
