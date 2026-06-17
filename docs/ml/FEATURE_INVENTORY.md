# Feature Inventory

**Audit date:** 2026-06-18  
**Scope:** All AI/ML-related product features in the repository

This project is a **welfare fraud detection system**, not a gift recommendation platform. Features from the generic audit template (AI Gift Finder, gift recommendations, semantic product search, chatbot) are documented as **NOT FOUND** where applicable.

---

## Implemented Features

### Fraud Risk Scoring (Synchronous Inference)

| Attribute | Value |
| --- | --- |
| **Business objective** | Score welfare beneficiary records for fraud/anomaly risk across income, caste administration, transaction, and medical domains |
| **User journey** | External client POSTs 22 numeric/categorical fields → receives 5 risk scores |
| **Backend flow** | `POST /predict` → `UserData` validation → `predict_all()` → JSON response |
| **Frontend flow** | **NOT connected** — no UI calls this endpoint |
| **AI dependencies** | 4× sklearn `IsolationForest`, 4× `StandardScaler`, 1× `OneHotEncoder` |
| **Data dependencies** | Request payload only (no database reads) |
| **Current limitations** | Stateless; no persistence; no auth; requires pre-trained `models/*.pkl` on disk |

**Source:**
- `services/ml/src/app.py` — `predict()`, `UserData`
- `services/ml/src/predict.py` — `predict_all()`
- `services/ml/src/preprocess.py` — domain preprocessors

---

### Offline Model Training

| Attribute | Value |
| --- | --- |
| **Business objective** | Retrain anomaly detection models from CSV datasets |
| **User journey** | Developer runs `python src/train.py` from `services/ml/` |
| **Backend flow** | Read CSV → fit scaler/encoder → fit IsolationForest → dump `.pkl` files |
| **Frontend flow** | N/A |
| **AI dependencies** | sklearn `IsolationForest`, `StandardScaler`, `OneHotEncoder` |
| **Data dependencies** | `services/ml/data/*.csv` (800 rows per domain) |
| **Current limitations** | Manual CLI only; no scheduled retraining; no experiment tracking; no model registry integration |

**Source:** `services/ml/src/train.py`

---

### ML Smoke Test Endpoint

| Attribute | Value |
| --- | --- |
| **Business objective** | Quick verification that models load and produce scores |
| **User journey** | Developer calls `GET /test` |
| **Backend flow** | `run_test_predictions()` iterates 3 hardcoded fixtures → `predict_all()` each |
| **Frontend flow** | N/A |
| **AI dependencies** | Same as fraud risk scoring |
| **Data dependencies** | Hardcoded samples in `services/ml/src/test.py` |
| **Current limitations** | Not a formal test suite; exposed as public HTTP endpoint |

**Source:** `services/ml/src/app.py` — `test()`; `services/ml/src/test.py` — `run_test_predictions()`

---

### Marketing Risk Dashboard (Static UI)

| Attribute | Value |
| --- | --- |
| **Business objective** | Communicate product value on landing page |
| **User journey** | Visitor views homepage hero section |
| **Backend flow** | None |
| **Frontend flow** | React components render hardcoded statistics and risk distribution bars |
| **AI dependencies** | **None** — purely presentational |
| **Data dependencies** | Inline constants in component files |
| **Current limitations** | Misleading "Live" badge; numbers do not reflect real ML output |

**Source files:**
- `apps/web/src/components/home/hero/hero-risk-panel.tsx` — hardcoded `risks` array (72% Low, 18% Medium, 10% High)
- `apps/web/src/components/home/hero/hero-stats-strip.tsx` — static metrics
- `apps/web/src/components/home/hero/hero-content.tsx` — marketing copy referencing AI/ML
- `apps/web/src/components/home/stats/stats-section.tsx` — static stats
- `apps/web/src/components/home/problem-solution/data.ts` — static problem/solution content
- `apps/web/src/app/layout.tsx` — metadata describing "AI-powered fraud detection"

---

## Schema-Only Features (Designed, Not Implemented)

### Beneficiary Profile Management

| Attribute | Value |
| --- | --- |
| **Business objective** | Store beneficiary identity separate from ML features |
| **User journey** | **NOT implemented in application layer** |
| **Backend flow** | Schema exists; no CRUD API found |
| **Frontend flow** | **NOT FOUND** |
| **AI dependencies** | None (identity only) |
| **Data dependencies** | `student_profiles` table |
| **Current limitations** | Table empty without ingestion; no API to create/read profiles |

**Source:** `packages/db/schema/student-profiles.ts`, `services/ml/src/db/models/student_profile.py`

**Fields:** `id`, `external_id`, `name`, `date_of_birth`, `gender`, `region`, `created_by_user_id`, timestamps

---

### Feature Snapshot Storage

| Attribute | Value |
| --- | --- |
| **Business objective** | Immutable, versioned storage of ML input features for reproducible inference |
| **User journey** | **NOT implemented** |
| **Backend flow** | Designed: append-only inserts to `feature_snapshots` |
| **Frontend flow** | **NOT FOUND** |
| **AI dependencies** | Indirect — stores inputs for `predict_all()` |
| **Data dependencies** | `feature_snapshots.features` JSONB, `feature_schema_version` |
| **Current limitations** | No writer service; no JSON schema validation; no ingestion pipeline |

**Source:** `packages/db/schema/feature-snapshots.ts`, `services/ml/src/db/models/feature_snapshot.py`

**Enum `feature_source`:** `api_payload`, `csv_ingest`, `profile_snapshot` (`packages/db/schema/enums.ts`)

---

### Prediction History / Audit Trail

| Attribute | Value |
| --- | --- |
| **Business objective** | Persist fraud risk outcomes linked to profiles and snapshots |
| **User journey** | **NOT implemented** |
| **Backend flow** | Designed: INSERT into `prediction_records` after inference |
| **Frontend flow** | Planned in `docs/UI_ARCHITECTURE.md` — not built |
| **AI dependencies** | Output of `predict_all()` |
| **Data dependencies** | `prediction_records`, optional `model_version_id`, `job_id` |
| **Current limitations** | `/predict` does not write records; no query API |

**Source:** `packages/db/schema/prediction-records.ts`, `services/ml/src/db/models/prediction_record.py`

---

### Model Version Management

| Attribute | Value |
| --- | --- |
| **Business objective** | Track which model artifacts are deployed and active |
| **User journey** | **NOT implemented** |
| **Backend flow** | Schema only |
| **AI dependencies** | Metadata about `.pkl` artifacts |
| **Current limitations** | Inference loads hardcoded `models/*.pkl` paths; ignores `model_versions` table |

**Source:** `packages/db/schema/model-versions.ts`

---

### Async / Batch Inference

| Attribute | Value |
| --- | --- |
| **Business objective** | Background fraud scoring for large beneficiary batches |
| **User journey** | **NOT implemented** |
| **Backend flow** | Documented future: `prediction_jobs` table, `services/workers`, Redis/BullMQ/Inngest |
| **AI dependencies** | Same models, invoked asynchronously |
| **Current limitations** | Redis container exists (`docker-compose.yml`) but no worker code; `services/workers/package.json` has no `index.ts` |

**Source:** `docs/database-architecture.md` — "Future Phase Tables"

---

## Features NOT FOUND IN CURRENT CODEBASE

The following were in the audit investigation scope but **do not exist** in this repository:

### AI Gift Finder

**NOT FOUND IN CURRENT CODEBASE**

### Recommendation Engine

**NOT FOUND IN CURRENT CODEBASE**

No gift recommendation logic, ranking algorithms, collaborative filtering, or hybrid recommenders.

### Semantic Search

**NOT FOUND IN CURRENT CODEBASE**

No embedding generation, vector indexes, or similarity retrieval.

### Keyword Search

**NOT FOUND IN CURRENT CODEBASE**

No Elasticsearch, PostgreSQL full-text, or application search endpoints.

### Chatbot

**NOT FOUND IN CURRENT CODEBASE**

No chat UI, conversation history, or LLM-backed responses.

### Personalization

**NOT FOUND IN CURRENT CODEBASE**

No user preference storage, behavioral tracking, or adaptive models.

### Preference Learning

**NOT FOUND IN CURRENT CODEBASE**

### Explainable AI (SHAP)

**NOT FOUND IN CURRENT CODEBASE**

Mentioned in root `README.md` ("SHAP (Explainable AI)") but no SHAP dependency or code.

### XGBoost Fraud Classification

**NOT FOUND IN CURRENT CODEBASE**

Mentioned in root `README.md` pipeline diagram but not in `requirements.txt` or Python source.

---

## ML Input Feature Catalog (22 fields)

These are the features required by `predict_all()` today. They are **not** stored on `student_profiles` (removed in migration `0001_phase_1_1_refinements.sql`). Intended future home: `feature_snapshots.features` JSONB.

| Feature | Type | Domain model |
| --- | --- | --- |
| `income_in_rs` | float | income |
| `land_owned_acres` | float | income |
| `vehicles_owned` | int | income |
| `electricity_consumption` | float | income |
| `pending_loans` | int | income |
| `business_ownership` | int (0/1) | income |
| `caste` | string | caste |
| `father_caste` | string | caste |
| `avg_caste_population_per` | float | caste |
| `officer_approvals_per_day` | float | caste |
| `weekly_spending` | float | transaction |
| `monthly_spending` | float | transaction |
| `transaction_count` | int | transaction |
| `avg_transaction_value` | float | transaction |
| `luxury_items_bought` | int | transaction |
| `weekend_spending_ratio` | float | transaction |
| `hospital_visits_per_year` | int | medical |
| `claim_frequency` | int | medical |
| `medical_claim_amount` | float | medical |
| `avg_claim_amount` | float | medical |
| `chronic_disease` | int (0/1) | medical |

**Source:** `services/ml/src/app.py` (`UserData`), `services/ml/src/preprocess.py`

---

## Feature → Data Source Availability

| Feature | `student_profiles` | `feature_snapshots` |
| --- | --- | --- |
| All 22 ML features | **No** (removed Phase 1.1) | **Yes, when populated** |
| `name`, `date_of_birth`, `gender`, `region` | **Yes** | No |
| `external_id` | **Yes** | No |

**Source:** `packages/db/schema/student-profiles.ts`, `packages/db/migrations/0001_phase_1_1_refinements.sql`, `docs/database-architecture.md`
