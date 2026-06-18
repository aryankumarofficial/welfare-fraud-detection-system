# CSV Ingestion Pipeline

This document describes how the new CSV ingestion path moves raw `services/ml/data/*.csv` records into the runtime database and exposes import status for analytics and dashboard flows.

## What was added

- `scripts/import-csv.ts`
  - Reads `services/ml/data/income.csv`, `caste.csv`, `transaction.csv`, and `medical.csv`
  - Creates or updates `student_profiles` by `user_id` / `external_id`
  - Inserts new rows into the source tables:
    - `student_financial_records`
    - `student_social_records`
    - `student_transaction_summaries`
    - `student_medical_summaries`
  - Is idempotent for repeated runs by comparing the latest existing record and only inserting when source values change.

- `services/ml/src/app.py`
  - Added `GET /admin/import/status`
  - Returns counts for imported profiles and each source table plus the latest profile import timestamp.

- `services/ml/src/validate_end_to_end.py`
  - Validates imported profiles can generate feature snapshots and predictions.
  - Supports a `--limit` argument for sample validation.

- `docker-compose.yml`
  - Added a one-shot `csv-importer` service to run the CSV importer after DB migrations complete.
  - `ml-service` now depends on `csv-importer` so the runtime service starts after ingestion.

## How to run the importer

From the workspace root:

```bash
bun run import:csv
```

Or with Docker Compose:

```bash
docker compose up --build csv-importer
```

## Runtime status endpoint

Call the ML service admin endpoint:

```bash
curl http://localhost:8000/admin/import/status
```

Response shape:

```json
{
  "success": true,
  "data": {
    "profiles": 100,
    "financial_records": 100,
    "social_records": 100,
    "transaction_records": 100,
    "medical_records": 100,
    "imported_at": "2026-06-18T13:45:12.345678",
    "status": "completed"
  }
}
```

## Validate end-to-end snapshot and prediction path

Use the Python validation helper from `services/ml`:

```bash
cd services/ml
python src/validate_end_to_end.py --limit 20
```

This script loads profile IDs from the database, generates feature snapshots for each profile, and then creates a prediction record for the generated snapshot.

## Generate snapshots and predictions manually

The ML service already exposes runtime operators for per-profile generation if you want to drive the pipeline via API:

```bash
curl -X POST http://localhost:8000/snapshot/generate \
  -H "Authorization: Bearer <operator-token>" \
  -H "Content-Type: application/json" \
  -d '{"student_profile_id":"<profile-uuid>"}'

curl -X POST http://localhost:8000/predict/generate \
  -H "Authorization: Bearer <operator-token>" \
  -H "Content-Type: application/json" \
  -d '{"student_profile_id":"<profile-uuid>"}'
```

After generation, the imported data will be available through the dashboard analytics path.

## Notes

- This path does not retrain or replace any existing models.
- It only populates runtime source data and confirms the runtime feature/prediction pipeline is operational.
