# Ingestion Audit

This audit inspects whether repository data is ingested into PostgreSQL and documents the current ingestion status.

## Search evidence

### Relevant findings

- `services/ml/src/train.py` reads raw CSV files with `pandas.read_csv()`.
- The CSV files are located in `services/ml/data/`.
- There is no `COPY`, `copy_expert`, `csv.DictReader`, or explicit `.copy_from()` import path anywhere else in the repository.
- `packages/db/migrate.ts` runs migrations only and does not load CSV data.
- `scripts/seed-demo-data.ts` is a demo data generator and does not import CSV files into the database.

### Confirmed files and code paths

- `services/ml/src/train.py`
  - `pd.read_csv("data/income.csv")`
  - `pd.read_csv("data/caste.csv")`
  - `pd.read_csv("data/transaction.csv")`
  - `pd.read_csv("data/medical.csv")`
- `docker-compose.yml`
  - `migrate` service runs `bun run db:migrate`
- `packages/db/migrate.ts`
  - Only executes Drizzle DB migrations

## Automation status

- There is no automation for CSV ingestion into PostgreSQL.
- The only automated DB action in startup is schema migration.
- No repository service performs CSV-to-DB ingest on `docker compose up --build`.

## Can a fresh database be populated from repository data?

**NO**

### Justification

- A fresh deployment provisions PostgreSQL and applies migrations.
- No code writes the CSV rows into PostgreSQL tables.
- The raw CSV files remain unused by the runtime ingestion pipeline.

## Summary

| Item | Present | Notes |
|---|---|---|
| CSV import code | ❌ | No importer, no loader, no COPY path found |
| CSV ingestion automation | ❌ | Startup only runs migrations |
| Runtime source table writer | ❌ | Source tables exist but are not populated from CSV |
| Training data reader | ✅ | `services/ml/src/train.py` reads CSVs for model training |
