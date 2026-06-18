# Demo Data Audit

This audit reviews `scripts/seed-demo-data.ts` and determines whether the file uses real CSV data or generates synthetic records.

## Summary

- `scripts/seed-demo-data.ts` is a synthetic demo data generator.
- It does not read or import any CSV files.
- It does not write actual data into PostgreSQL.
- It constructs fake student profiles, feature snapshots, predictions, reviews, alerts, drifts, and model versions entirely in code.

## Evidence from the script

- The script defines interfaces such as `StudentProfile`, `FeatureSnapshot`, `PredictionRecord`, `PredictionReview`, `MonitoringAlert`, `DriftSnapshot`, and `ModelVersion`.
- It uses `generateId()` to fabricate IDs and `generateTimestamp()` to fabricate dates.
- Feature values and risk scores are generated with deterministic or random calculations inside `demoData`.
- The script ends by printing a summary instead of inserting rows into a database.

## Conclusion

- The demo data created by `scripts/seed-demo-data.ts` is entirely synthetic.
- It does not import real CSV training datasets.
- It should be treated as a presentation/demo dataset generator rather than a production CSV ingestion tool.
