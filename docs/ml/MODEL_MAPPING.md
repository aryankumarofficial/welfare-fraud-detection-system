# Model Mapping

**Audit date:** 2026-06-18  
**Scope:** All AI/ML models and external AI services in the repository

---

## Summary Table

| Component | Model | Purpose | Location |
| --- | --- | --- | --- |
| Income anomaly detection | sklearn `IsolationForest` | Detect anomalous income/asset patterns | `services/ml/src/predict.py` (loads `models/income_model.pkl`) |
| Caste anomaly detection | sklearn `IsolationForest` | Detect anomalous caste/administration patterns | `services/ml/src/predict.py` (loads `models/caste_model.pkl`) |
| Transaction anomaly detection | sklearn `IsolationForest` | Detect anomalous spending patterns | `services/ml/src/predict.py` (loads `models/transaction_model.pkl`) |
| Medical anomaly detection | sklearn `IsolationForest` | Detect anomalous medical claim patterns | `services/ml/src/predict.py` (loads `models/medical_model.pkl`) |
| Income feature scaling | sklearn `StandardScaler` | Z-score normalization | `services/ml/src/preprocess.py` (`models/income_scaler.pkl`) |
| Caste feature scaling | sklearn `StandardScaler` | Z-score after OHE | `services/ml/src/preprocess.py` (`models/caste_scaler.pkl`) |
| Caste encoding | sklearn `OneHotEncoder` | Encode `caste`, `father_caste` | `services/ml/src/preprocess.py` (`models/caste_encoder.pkl`) |
| Transaction feature scaling | sklearn `StandardScaler` | Z-score normalization | `services/ml/src/preprocess.py` (`models/transaction_scaler.pkl`) |
| Medical feature scaling | sklearn `StandardScaler` | Z-score normalization | `services/ml/src/preprocess.py` (`models/medical_scaler.pkl`) |
| XGBoost classifier | — | **NOT FOUND IN CURRENT CODEBASE** | Mentioned in root `README.md` only |
| SHAP explainability | — | **NOT FOUND IN CURRENT CODEBASE** | Mentioned in root `README.md` only |
| OpenAI | — | **NOT FOUND IN CURRENT CODEBASE** | — |
| Anthropic | — | **NOT FOUND IN CURRENT CODEBASE** | — |
| Google Gemini | — | **NOT FOUND IN CURRENT CODEBASE** | — |
| Embedding models | — | **NOT FOUND IN CURRENT CODEBASE** | — |
| Vector database | — | **NOT FOUND IN CURRENT CODEBASE** | — |

---

## ML Models (Implemented)

### Income Model

| Attribute | Value |
| --- | --- |
| **Model name** | `income_model.pkl` |
| **Provider** | scikit-learn (local, self-hosted) |
| **Model version** | Not tracked at runtime; `model_versions` table unused |
| **Algorithm** | `IsolationForest(n_estimators=100, contamination=0.05, random_state=42)` |
| **Trained by** | `train_income()` in `services/ml/src/train.py` |
| **Usage location** | `services/ml/src/predict.py` line 46 |
| **Prompt source** | N/A (not an LLM) |
| **Input format** | Scaled array `(1, 6)` from `preprocess_income()` |
| **Output format** | Raw anomaly score via `decision_function`; negated and sigmoid-normalized to `income_risk` float ∈ ~[0, 1] |
| **Cost considerations** | CPU-only; no external API cost; models loaded in-process at startup |
| **Failure handling** | No try/except; missing `.pkl` → import-time crash; invalid input → sklearn/pandas errors propagate as HTTP 500 |
| **Fallback strategy** | None |

**Input features (pre-scaling order):**
1. `income_in_rs`
2. `land_owned_acres`
3. `vehicles_owned`
4. `electricity_consumption`
5. `pending_loans`
6. `business_ownership`

**Training data:** `services/ml/data/income.csv` (800 rows, `user_id` dropped)

**Auxiliary artifact (unused at inference):** `models/income_minmax.pkl`

---

### Caste Model

| Attribute | Value |
| --- | --- |
| **Model name** | `caste_model.pkl` |
| **Provider** | scikit-learn (local) |
| **Algorithm** | `IsolationForest(n_estimators=100, contamination=0.04, random_state=42)` |
| **Trained by** | `train_caste()` in `services/ml/src/train.py` |
| **Usage location** | `services/ml/src/predict.py` line 47 |
| **Encoder** | `caste_encoder.pkl` — `OneHotEncoder(handle_unknown="ignore")` |
| **Scaler** | `caste_scaler.pkl` |
| **Input format** | Scaled array `(1, 10)` |
| **Output format** | `caste_risk` float |
| **Failure handling** | Unknown caste strings → all-zero one-hot (silent degradation) |
| **Fallback strategy** | None |

**Encoder categories (from fitted artifact):**
- `caste`: `General`, `OBC`, `SC`, `ST`
- `father_caste`: `General`, `OBC`, `SC`, `ST`

**Feature vector order (post-preprocessing):**
1. `avg_caste_population_per`
2. `officer_approvals_per_day`
3. `caste_General`, `caste_OBC`, `caste_SC`, `caste_ST`
4. `father_caste_General`, `father_caste_OBC`, `father_caste_SC`, `father_caste_ST`

**Training drops:** `user_id`, `state`, `district` from `services/ml/data/caste.csv`

**Auxiliary artifact (unused):** `models/caste_minmax.pkl`

---

### Transaction Model

| Attribute | Value |
| --- | --- |
| **Model name** | `transaction_model.pkl` |
| **Provider** | scikit-learn (local) |
| **Algorithm** | `IsolationForest(n_estimators=100, contamination=0.036, random_state=42)` |
| **Trained by** | `train_transaction()` in `services/ml/src/train.py` |
| **Usage location** | `services/ml/src/predict.py` line 48 |
| **Scaler** | `transaction_scaler.pkl` |
| **Input format** | Scaled array `(1, 6)` |
| **Output format** | `transaction_risk` float |
| **Failure handling** | None explicit |
| **Fallback strategy** | None |

**Input features:**
1. `weekly_spending`
2. `monthly_spending`
3. `transaction_count`
4. `avg_transaction_value`
5. `luxury_items_bought`
6. `weekend_spending_ratio`

**Training data:** `services/ml/data/transaction.csv`

**Auxiliary artifact (unused):** `models/transaction_minmax.pkl`

---

### Medical Model

| Attribute | Value |
| --- | --- |
| **Model name** | `medical_model.pkl` |
| **Provider** | scikit-learn (local) |
| **Algorithm** | `IsolationForest(n_estimators=100, contamination=0.036, random_state=42)` |
| **Trained by** | `train_medical()` in `services/ml/src/train.py` |
| **Usage location** | `services/ml/src/predict.py` line 49 |
| **Scaler** | `medical_scaler.pkl` |
| **Input format** | Scaled array `(1, 5)` |
| **Output format** | `medical_risk` float |
| **Failure handling** | None explicit |
| **Fallback strategy** | None |

**Input features:**
1. `hospital_visits_per_year`
2. `claim_frequency`
3. `medical_claim_amount`
4. `avg_claim_amount`
5. `chronic_disease`

**Training drops:** `user_id`, `hospital_type` from `services/ml/data/medical.csv`

**Auxiliary artifact (unused):** `models/medical_minmax.pkl`

---

## Score Aggregation Model

| Attribute | Value |
| --- | --- |
| **Name** | `normalize_score` + arithmetic mean |
| **Provider** | Custom (numpy) |
| **Location** | `services/ml/src/predict.py` |
| **Formula** | `risk = 1 / (1 + exp(-5 * (-decision_function)))` per domain |
| **Final risk** | `(income_risk + caste_risk + transaction_risk + medical_risk) / 4` |
| **Prompt source** | N/A |
| **Cost** | Negligible CPU |
| **Failure handling** | None |
| **Fallback** | None |

**Note:** `train.py` saves per-domain min/max score ranges (`*_minmax.pkl`) but `predict.py` uses sigmoid normalization instead. This is an inconsistency between training metadata and inference code.

---

## Database Model Version Registry (schema only)

| Attribute | Value |
| --- | --- |
| **Table** | `model_versions` |
| **Schema** | `packages/db/schema/model-versions.ts` |
| **ORM** | `services/ml/src/db/models/model_version.py` |
| **Purpose** | Track deployed artifact URIs and configuration |
| **Runtime usage** | **NOT wired** — `predict.py` does not query this table |
| **Fields** | `name`, `version`, `artifact_uri`, `configuration`, `is_active`, `deployed_at` |

---

## LLM / External AI Services

### OpenAI

**NOT FOUND IN CURRENT CODEBASE**

No `openai` package in `services/ml/requirements.txt` or root `package.json`. No API key references in application source.

### Anthropic

**NOT FOUND IN CURRENT CODEBASE**

No application code references. Tangential hit: `skills-lock.json` references `anthropics/skills` (Cursor agent tooling metadata, not product code).

### Google Gemini

**NOT FOUND IN CURRENT CODEBASE**

### LangChain / LlamaIndex / Ollama

**NOT FOUND IN CURRENT CODEBASE**

---

## Model Artifact Inventory

| Artifact | Created by | Loaded at inference | In git repo |
| --- | --- | --- | --- |
| `income_model.pkl` | `train_income()` | Yes | No (generated) |
| `income_scaler.pkl` | `train_income()` | Yes | No |
| `income_minmax.pkl` | `train_income()` | **No** | No |
| `caste_model.pkl` | `train_caste()` | Yes | No |
| `caste_scaler.pkl` | `train_caste()` | Yes | No |
| `caste_encoder.pkl` | `train_caste()` | Yes | No |
| `caste_minmax.pkl` | `train_caste()` | **No** | No |
| `transaction_model.pkl` | `train_transaction()` | Yes | No |
| `transaction_scaler.pkl` | `train_transaction()` | Yes | No |
| `transaction_minmax.pkl` | `train_transaction()` | **No** | No |
| `medical_model.pkl` | `train_medical()` | Yes | No |
| `medical_scaler.pkl` | `train_medical()` | Yes | No |
| `medical_minmax.pkl` | `train_medical()` | **No** | No |

**Source:** `services/ml/src/train.py`, `services/ml/src/predict.py`, `services/ml/src/preprocess.py`

`.gitignore` ignores `*.joblib`; `*.pkl` is not ignored (commented out) but artifacts are absent from the repository snapshot audited.
