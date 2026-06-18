# CSV Inventory

This document inventories the CSV datasets present in the repository and records their current usage.

## Dataset list

| Path | Row count | Columns | Purpose | Training usage |
|---|---|---|---|---|
| `services/ml/data/income.csv` | 800 | `user_id`, `income_in_rs`, `land_owned_acres`, `vehicles_owned`, `electricity_consumption`, `pending_loans`, `business_ownership` | Income-related numeric features for student financial risk modeling | Used by `services/ml/src/train.py` in `train_income()` only |
| `services/ml/data/caste.csv` | 800 | `user_id`, `caste`, `father_caste`, `state`, `district`, `avg_caste_population_per`, `officer_approvals_per_day` | Caste and demographic features for caste risk modeling | Used by `services/ml/src/train.py` in `train_caste()` only |
| `services/ml/data/transaction.csv` | 800 | `user_id`, `weekly_spending`, `monthly_spending`, `transaction_count`, `avg_transaction_value`, `luxury_items_bought`, `weekend_spending_ratio` | Transaction summary features for transaction risk modeling | Used by `services/ml/src/train.py` in `train_transaction()` only |
| `services/ml/data/medical.csv` | 800 | `user_id`, `hospital_visits_per_year`, `claim_frequency`, `medical_claim_amount`, `avg_claim_amount`, `chronic_disease`, `hospital_type` | Medical history and claims features for medical risk modeling | Used by `services/ml/src/train.py` in `train_medical()` only |

## Notes

- All four CSV files are located under `services/ml/data/`.
- The only code that reads these CSVs is `services/ml/src/train.py`.
- There is no code path in the repository that imports these CSV files into PostgreSQL.
- The `user_id` column is the only common identifier in the raw CSV files and is expected to map to `student_profiles.external_id` in a future ingestion pipeline.
