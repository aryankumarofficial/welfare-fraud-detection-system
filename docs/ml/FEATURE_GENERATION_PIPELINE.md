# Automated Feature Generation Pipeline

Phase 4 removes the need to manually create `feature_snapshots` JSON before running
profile-based inference. The ML service now generates a validated snapshot from
domain source records, persists it, and can immediately run prediction against
that exact snapshot.

## Source Tables

Generated snapshots are assembled from the latest record for each student profile
in these tables:

- `student_financial_records`
- `student_social_records`
- `student_transaction_summaries`
- `student_medical_summaries`

Each table is keyed by `student_profile_id` and ordered by `created_at`. This
keeps `student_profiles` as identity data while preserving a history of changing
feature inputs.

## Feature Mapping

`FeatureBuilder` converts source records into the existing v1 feature contract
used by `predict_all()`:

- Financial fields: `income_in_rs`, `land_owned_acres`, `vehicles_owned`,
  `electricity_consumption`, `pending_loans`, `business_ownership`
- Social fields: `caste`, `father_caste`, `avg_caste_population_per`,
  `officer_approvals_per_day`
- Transaction fields: `weekly_spending`, `monthly_spending`,
  `transaction_count`, `avg_transaction_value`, `luxury_items_bought`,
  `weekend_spending_ratio`
- Medical fields: `hospital_visits_per_year`, `claim_frequency`,
  `medical_claim_amount`, `avg_claim_amount`, `chronic_disease`

The generated feature dictionary is validated with the existing
`FeatureSnapshotV1` schema before insertion.

## Services

- `FeatureBuilder`: pure conversion from domain records to the canonical
  22-feature payload.
- `SnapshotGenerator`: loads the student profile and source records, builds and
  validates features, and asks the snapshot service to persist them.
- `SnapshotService`: persists validated `feature_snapshots` and computes a
  stable SHA-256 checksum from the feature payload.
- `PredictionService`: remains the inference orchestrator. Existing
  `/predict/profile` behavior still loads the latest snapshot. The generated
  prediction flow uses the same service against the newly created snapshot ID.

## Endpoints

### `POST /snapshot/generate`

Request:

```json
{
  "student_profile_id": "uuid"
}
```

Response includes the generated snapshot ID, schema version, checksum, source,
and validated feature payload.

### `POST /predict/generate`

Request:

```json
{
  "student_profile_id": "uuid"
}
```

Flow:

1. Load `student_profiles`.
2. Load the latest related source records.
3. Build and validate the v1 feature payload.
4. Insert a `feature_snapshots` row.
5. Run inference through `PredictionService`.
6. Store `prediction_records`.
7. Return prediction risks and IDs.

## Error Semantics

- `PROFILE_NOT_FOUND`: no `student_profiles` row exists for the request.
- `MISSING_SOURCE_DATA`: one or more required source tables has no record for
  the profile.
- `FEATURE_GENERATION_FAILED`: generated features do not satisfy the v1 schema.
- `SNAPSHOT_GENERATION_FAILED`: snapshot persistence failed.
- `PREDICTION_FAILED`: legacy model inference raised unexpectedly.

## Backward Compatibility

No model algorithms, training code, preprocessing code, `predict_all()`, or
legacy endpoints were changed. Existing clients can continue using:

- `POST /predict`
- `POST /predict/profile`

