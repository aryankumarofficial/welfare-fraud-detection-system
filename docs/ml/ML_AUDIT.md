# ML System Audit

**Audit date:** 2026-06-18  
**Scope:** Read-only analysis of the welfare fraud detection monorepo  
**Auditor role:** Senior ML Architect / AI Systems Auditor

---

## Executive Summary

### Current ML maturity level

**Level: Early prototype (Phase 1–1.1)**

The repository implements a **single-domain ML capability**: unsupervised anomaly detection for welfare fraud risk scoring using four scikit-learn `IsolationForest` models. Inference is exposed via a standalone FastAPI service with a synchronous, stateless `/predict` endpoint.

There is **no** LLM layer, recommendation engine, semantic search, chatbot, vector database, or production MLOps pipeline in application code. Database schema for ML persistence exists but is **not wired** to inference.

| Capability | Status |
| --- | --- |
| Batch model training | Implemented (`services/ml/src/train.py`) |
| Real-time inference API | Implemented (`services/ml/src/app.py`) |
| Feature preprocessing | Implemented (`services/ml/src/preprocess.py`) |
| Prediction persistence | Schema only — NOT wired |
| DB-backed inference | NOT implemented |
| LLM / generative AI | NOT FOUND IN CURRENT CODEBASE |
| Recommendation engine | NOT FOUND IN CURRENT CODEBASE |
| Semantic / vector search | NOT FOUND IN CURRENT CODEBASE |
| Background job processing | Infrastructure stub only (Redis container, empty workers package) |
| Frontend ML integration | Static marketing UI only (hardcoded values) |
| Model explainability (SHAP) | Documented in README only — NOT in code |
| XGBoost classifier | Documented in README only — NOT in code |

### Architecture overview

```text
┌─────────────────────────────────────────────────────────────────┐
│  apps/web (Next.js)          Static landing page                │
│  NO API routes, NO ML fetch                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ (no ML calls today)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  apps/api (Bun)              Placeholder: console.log only      │
│  NO HTTP routes, NO ML proxy                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  services/ml (FastAPI :8000)                                    │
│  POST /predict → predict_all() → 4 IsolationForest models       │
│  SQLAlchemy DB layer present but unused by inference            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  PostgreSQL (welfare)                                             │
│  student_profiles, feature_snapshots, prediction_records,       │
│  model_versions, users, audit_logs                              │
└─────────────────────────────────────────────────────────────────┘
```

**Source:** `docker-compose.yml`, `docs/database-architecture.md`, `services/ml/src/app.py`

### Major strengths

1. **Clear domain decomposition** — Four independent anomaly models (income, caste, transaction, medical) with dedicated preprocessors and scalers.
2. **Separation of concerns in schema** — Phase 1.1 decoupled beneficiary identity (`student_profiles`) from ML inputs (`feature_snapshots`) and outcomes (`prediction_records`). See `docs/database-architecture.md`.
3. **Reproducible training pipeline** — `train.py` reads CSVs from `services/ml/data/`, fits models, and serializes artifacts to `models/*.pkl`.
4. **Typed API contract** — Pydantic `UserData` model enforces request shape at `POST /predict`. Source: `services/ml/src/app.py`.
5. **Dual ORM strategy** — Drizzle (`packages/db`) owns migrations; SQLAlchemy (`services/ml/src/db`) mirrors schema for Python consumers.
6. **CI smoke test** — `.github/workflows/ci.yml` verifies Python ML dependency imports.

### Major weaknesses

1. **No end-to-end integration** — Web and API layers do not call the ML service; predictions are not persisted.
2. **Model artifacts not in repository** — `models/*.pkl` are generated locally; service fails at import if missing. Source: `services/ml/src/predict.py` lines 18–21.
3. **Docker / Makefile path mismatches** — `Dockerfile` CMD references `app.main:app` but entrypoint is `src.app:app`. Source: `services/ml/Dockerfile`, `services/ml/package.json`.
4. **README overstates capabilities** — Claims XGBoost, SHAP, admin dashboard, JWT auth, Redis queues — not implemented in audited code. Source: root `README.md`.
5. **No authentication on ML endpoints** — `/predict` is open. Source: `services/ml/src/app.py`.
6. **No monitoring, logging, or model versioning at runtime** — `model_versions` table unused by inference.
7. **Unused training artifacts** — `*_minmax.pkl` saved by `train.py` but not loaded by `predict.py`.

### Technical debt

| Item | Location | Description |
| --- | --- | --- |
| Stale Makefile train path | `Makefile` | References `training/train_model.py` (does not exist); actual trainer is `services/ml/src/train.py` |
| Dockerfile entrypoint | `services/ml/Dockerfile` | `uvicorn app.main:app` — no `app/main.py` |
| Pydantic v1 API | `services/ml/src/app.py:44` | Uses `data.dict()` (deprecated in Pydantic v2) |
| Empty workers package | `services/workers/package.json` | Declares `index.ts` but file does not exist |
| Empty API service | `apps/api/index.ts` | Single `console.log` statement |
| CI references missing app | `.github/workflows/ci.yml:43` | Builds `apps/admin` which is not in monorepo structure |
| README architecture diagram | `README.md` | Shows XGBoost pipeline not present in code |

### Risk assessment

| Risk | Severity | Description |
| --- | --- | --- |
| Unauthenticated inference | **High** | Anyone with network access can POST arbitrary payloads to `/predict` |
| No audit trail | **High** | Predictions are ephemeral; `prediction_records` never written |
| Model artifact absence | **High** | Fresh clone cannot run inference without `python src/train.py` |
| sklearn version drift | **Medium** | Pickle load warnings across sklearn versions (observed 1.8.0 vs 1.9.0) |
| Caste encoding unknowns | **Medium** | `OneHotEncoder(handle_unknown="ignore")` silently zeroes unknown categories |
| Misleading product claims | **Medium** | Marketing UI shows "Live" risk data that is hardcoded |
| No input validation beyond types | **Medium** | No range checks, no schema version enforcement |
| Single-process model loading | **Low** | Models loaded at module import; no hot-reload or A/B testing |

---

## ML Components Inventory

### 1. FastAPI ML Service

| Attribute | Value |
| --- | --- |
| **Name** | ML Inference Service |
| **Purpose** | HTTP API for welfare fraud risk scoring |
| **Location** | `services/ml/src/app.py` |
| **Dependencies** | FastAPI, Pydantic, `src.predict.predict_all` |
| **Inputs** | JSON body matching `UserData` (22 fields) |
| **Outputs** | `{ success: true, data: { income_risk, caste_risk, transaction_risk, medical_risk, final_risk } }` |

**Functions:** `home()`, `predict()`, `test()`

---

### 2. Prediction Engine

| Attribute | Value |
| --- | --- |
| **Name** | `predict_all` |
| **Purpose** | Orchestrate preprocessing, model scoring, normalization, aggregation |
| **Location** | `services/ml/src/predict.py` |
| **Dependencies** | joblib, numpy, sklearn IsolationForest, `src.preprocess` |
| **Inputs** | `dict` with 22 feature keys |
| **Outputs** | `dict` with 5 float risk scores |

**Functions:** `normalize_score(score)`, `predict_all(data: dict)`

**Models loaded at import:**
- `models/income_model.pkl`
- `models/caste_model.pkl`
- `models/transaction_model.pkl`
- `models/medical_model.pkl`

---

### 3. Preprocessing Pipeline

| Attribute | Value |
| --- | --- |
| **Name** | Domain preprocessors |
| **Purpose** | Scale numeric features; one-hot encode caste fields |
| **Location** | `services/ml/src/preprocess.py` |
| **Dependencies** | joblib scalers/encoder |
| **Inputs** | Raw feature `dict` |
| **Outputs** | `numpy` arrays shape `(1, n_features)` per domain |

**Functions:**
- `preprocess_income(data)` — 6 features → `income_scaler.pkl`
- `preprocess_caste(data)` — 2 numeric + OHE → `caste_scaler.pkl`
- `preprocess_transaction(data)` — 6 features → `transaction_scaler.pkl`
- `preprocess_medical(data)` — 5 features → `medical_scaler.pkl`

**Artifacts loaded at import:**
- `models/income_scaler.pkl`, `caste_scaler.pkl`, `caste_encoder.pkl`, `transaction_scaler.pkl`, `medical_scaler.pkl`

---

### 4. Training Pipeline

| Attribute | Value |
| --- | --- |
| **Name** | Domain trainers |
| **Purpose** | Fit IsolationForest models from CSV training data |
| **Location** | `services/ml/src/train.py` |
| **Dependencies** | pandas, numpy, sklearn, joblib |
| **Inputs** | `services/ml/data/{income,caste,transaction,medical}.csv` |
| **Outputs** | `models/*.pkl` artifacts |

**Functions:** `train_income()`, `train_caste()`, `train_transaction()`, `train_medical()`

---

### 5. Test Fixtures

| Attribute | Value |
| --- | --- |
| **Name** | `run_test_predictions` |
| **Purpose** | Run 3 hardcoded sample payloads through `predict_all` |
| **Location** | `services/ml/src/test.py` |
| **Dependencies** | `src.predict.predict_all` |
| **Inputs** | Inline `data_list` (3 records) |
| **Outputs** | List of prediction dicts |

---

### 6. SQLAlchemy DB Layer (schema consumer, not used by inference)

| Attribute | Value |
| --- | --- |
| **Name** | Async DB session + ORM models |
| **Purpose** | Future persistence for profiles, snapshots, predictions |
| **Location** | `services/ml/src/db/` |
| **Dependencies** | SQLAlchemy 2.x, asyncpg, pydantic-settings |
| **Inputs** | `DATABASE_URL` env var |
| **Outputs** | Async session, ORM entities |

**Key files:**
- `config.py` — `get_database_settings()`
- `session.py` — `get_engine()`, `get_db_session()`, `close_db()`
- `repositories/base.py` — `AsyncRepository` (generic CRUD stub)
- `models/*.py` — `StudentProfile`, `FeatureSnapshot`, `PredictionRecord`, `ModelVersion`, `User`, `AuditLog`

---

### 7. Drizzle Schema (migration owner)

| Attribute | Value |
| --- | --- |
| **Name** | `@repo/db` ML-related tables |
| **Purpose** | Canonical PostgreSQL schema for ML data lifecycle |
| **Location** | `packages/db/schema/` |
| **Dependencies** | Drizzle ORM |
| **Inputs** | Migration SQL |
| **Outputs** | TypeScript types, SQL migrations |

**Tables:** `student_profiles`, `feature_snapshots`, `prediction_records`, `model_versions`, `users`, `audit_logs`

---

### 8. Training Datasets

| Attribute | Value |
| --- | --- |
| **Name** | Domain CSV files |
| **Purpose** | Offline training data (800 rows each) |
| **Location** | `services/ml/data/` |
| **Dependencies** | None (static files) |
| **Inputs** | N/A |
| **Outputs** | Used by `train.py` |

| File | Columns (excl. `user_id`) |
| --- | --- |
| `income.csv` | 6 numeric |
| `caste.csv` | 2 categorical + 2 numeric + `state`, `district` (dropped in training) |
| `transaction.csv` | 6 numeric |
| `medical.csv` | 5 numeric + `hospital_type` (dropped in training) |

---

### 9. Frontend Risk Display (static, not ML-connected)

| Attribute | Value |
| --- | --- |
| **Name** | `HeroRiskPanel` |
| **Purpose** | Marketing UI showing hardcoded risk distribution |
| **Location** | `apps/web/src/components/home/hero/hero-risk-panel.tsx` |
| **Dependencies** | React, shadcn/ui |
| **Inputs** | Hardcoded `risks` array |
| **Outputs** | Rendered card UI |

**Note:** Displays "Live" badge and fraud statistics that are **not** fetched from ML service.

---

### Components NOT FOUND IN CURRENT CODEBASE

| Component | Notes |
| --- | --- |
| LLM integrations (OpenAI, Anthropic, Gemini) | No imports or API keys in app code |
| Prompt engineering / system prompts | NOT FOUND |
| Tool calling / structured LLM outputs | NOT FOUND |
| Gift recommendation engine | NOT FOUND — project is welfare fraud detection |
| Semantic / keyword / vector search | NOT FOUND |
| Embedding generation | NOT FOUND |
| Chatbot | NOT FOUND |
| Personalization / preference learning | NOT FOUND |
| BullMQ / Inngest workers | Documented only; no implementation |
| Next.js API routes | No `route.ts` files under `apps/web` |
| Redis client usage | Container provisioned; no application code |

---

## End-to-End Data Flow

### Current implemented flow (inference only)

```text
HTTP Client
    │
    ▼
POST /predict  (services/ml/src/app.py :: predict)
    │
    ▼
Pydantic UserData validation (22 required fields)
    │
    ▼
data.dict() → flat Python dict
    │
    ▼
predict_all(data)  (services/ml/src/predict.py)
    │
    ├── preprocess_income(data)   → income_scaler → (1, 6)
    ├── preprocess_caste(data)    → caste_encoder + caste_scaler → (1, 10)
    ├── preprocess_transaction(data) → transaction_scaler → (1, 6)
    └── preprocess_medical(data)  → medical_scaler → (1, 5)
    │
    ▼
Per model: score = -decision_function(X)[0]
    │
    ▼
Per model: risk = 1 / (1 + exp(-5 * score))   [normalize_score]
    │
    ▼
final_risk = mean(income_risk, caste_risk, transaction_risk, medical_risk)
    │
    ▼
JSON response { success, data: { 5 risk floats } }
    │
    ▼
(NOT persisted to database)
```

### Training flow (offline)

```text
services/ml/data/*.csv
    │
    ▼
train.py :: train_{income,caste,transaction,medical}()
    │
    ├── Drop non-feature columns (user_id, state, district, hospital_type)
    ├── StandardScaler.fit_transform (caste: OneHotEncoder first)
    ├── IsolationForest.fit
    └── joblib.dump → models/*.pkl
```

### Documented but NOT implemented flow

```text
User Input (beneficiary UUID)
    │
    ▼
student_profiles lookup          ← NOT wired
    │
    ▼
latest feature_snapshots         ← NOT wired (no ingestion writer)
    │
    ▼
preprocess → predict_all         ← code exists, DB path does not
    │
    ▼
INSERT prediction_records        ← NOT wired
    │
    ▼
Admin Dashboard visualization    ← static UI only
```

**Source:** `docs/database-architecture.md` lines 56–64, 228–239

### LLM / Recommendation / Search flows

**NOT FOUND IN CURRENT CODEBASE**

The investigation scope items (LLM layer, recommendation logic, semantic search, chatbot) have no implementation paths in this repository. See `FEATURE_INVENTORY.md` and `GAP_ANALYSIS.md` for details.

---

## Audit Traceability Index

| Topic | Primary sources |
| --- | --- |
| API endpoints | `services/ml/src/app.py` |
| Inference logic | `services/ml/src/predict.py`, `services/ml/src/preprocess.py` |
| Training | `services/ml/src/train.py` |
| DB schema | `packages/db/schema/*.ts`, `services/ml/src/db/models/*.py` |
| Infrastructure | `docker-compose.yml`, `.env.example` |
| Frontend | `apps/web/src/components/home/` |
| Architecture intent | `docs/database-architecture.md`, `docs/UI_ARCHITECTURE.md` |
| CI | `.github/workflows/ci.yml`, `.github/workflows/docker.yml` |
