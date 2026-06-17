# Gap Analysis

**Audit date:** 2026-06-18  
**Comparison:** Current repository state vs production-grade AI/ML platform expectations

This analysis documents gaps only. **No improvements are implemented** as part of this audit.

---

## Executive Gap Summary

| Area | Current state | Production target | Overall gap |
| --- | --- | --- | --- |
| ML inference | Single stateless FastAPI endpoint | Integrated, persisted, versioned inference | **Large** |
| LLM / generative AI | Not present | Optional explanations, case summaries | **N/A or Large** (if desired) |
| Recommendations | Not present | N/A for fraud domain | **N/A** |
| Search | Not present | Beneficiary/case search | **Large** |
| Data pipeline | CSV + schema only | Automated ingestion + validation | **Large** |
| Personalization | Not present | N/A for fraud domain | **N/A** |
| Monitoring | None | Metrics, tracing, alerting | **Critical** |
| Evaluation | None | Offline metrics, drift detection | **Large** |
| Scalability | Single process | Horizontal scale, async jobs | **Large** |
| Security | Open endpoints | AuthN/Z, audit, PII controls | **Critical** |
| Cost optimization | Low (local sklearn) | Managed efficiently at scale | **Low today** |

---

## Architecture Gaps

### GAP-ARCH-001: No service integration layer

| Attribute | Value |
| --- | --- |
| **Description** | `apps/api` is a placeholder; `apps/web` has no API routes. ML service is isolated on port 8000 with no gateway, BFF, or proxy. |
| **Severity** | **High** |
| **Impact** | No unified API surface; clients must call ML service directly; no cross-cutting concerns (auth, rate limits) |
| **Evidence** | `apps/api/index.ts`, absence of `route.ts` in `apps/web` |
| **Recommended future improvement** | Implement API gateway in `apps/api` that proxies `/predict` and adds auth, or add Next.js route handlers |

### GAP-ARCH-002: Database schema not wired to inference

| Attribute | Value |
| --- | --- |
| **Description** | `feature_snapshots`, `prediction_records`, `model_versions` exist but `/predict` neither reads snapshots nor writes outcomes. |
| **Severity** | **High** |
| **Impact** | No reproducibility, no audit trail, schema investment unused |
| **Evidence** | `docs/database-architecture.md` line 64; `services/ml/src/app.py` |
| **Recommended future improvement** | DB-backed inference path: profile ID → snapshot → predict → persist |

### GAP-ARCH-003: Docker / Makefile entrypoint mismatches

| Attribute | Value |
| --- | --- |
| **Description** | `Dockerfile` CMD uses `app.main:app`; actual app is `src.app:app`. Makefile references non-existent `training/train_model.py`. |
| **Severity** | **Medium** |
| **Impact** | Container may fail to start; developer confusion |
| **Evidence** | `services/ml/Dockerfile`, `Makefile`, `services/ml/package.json` |
| **Recommended future improvement** | Align CMD with `src.app:app`; fix Makefile train target |

### GAP-ARCH-004: Workers package is empty

| Attribute | Value |
| --- | --- |
| **Description** | `services/workers/package.json` declares `index.ts` but file does not exist. No BullMQ, Inngest, or cron workers. |
| **Severity** | **Medium** |
| **Impact** | Cannot run batch inference or async pipelines |
| **Evidence** | `services/workers/package.json`, `docs/database-architecture.md` |
| **Recommended future improvement** | Implement worker service with `prediction_jobs` table |

### GAP-ARCH-005: README architecture diverges from code

| Attribute | Value |
| --- | --- |
| **Description** | Root README describes XGBoost, SHAP, admin dashboard, JWT — not implemented. |
| **Severity** | **Medium** |
| **Impact** | Stakeholder misalignment, onboarding confusion |
| **Evidence** | `README.md` lines 36–40, 64–90 |
| **Recommended future improvement** | Update README to match implemented stack or implement claimed features |

---

## Recommendation Quality Gaps

**NOT APPLICABLE — Recommendation engine NOT FOUND IN CURRENT CODEBASE**

This repository targets welfare fraud anomaly detection, not product/gift recommendations. If "recommendation" is interpreted as **prioritizing cases for investigator review**, the following applies:

### GAP-REC-001: No case prioritization / ranking beyond raw risk mean

| Attribute | Value |
| --- | --- |
| **Description** | `final_risk` is unweighted arithmetic mean of four domain scores with no calibration, thresholds, or investigator workflow rules. |
| **Severity** | **Medium** |
| **Impact** | Operators cannot tune sensitivity per domain; no actionable triage labels (e.g., High/Medium/Low) |
| **Evidence** | `services/ml/src/predict.py` line 58 |
| **Recommended future improvement** | Configurable weights, calibrated thresholds, domain-specific alert rules |

### GAP-REC-002: No feedback loop for investigator decisions

| Attribute | Value |
| --- | --- |
| **Description** | No storage of confirmed fraud labels or investigator overrides to improve models. |
| **Severity** | **High** |
| **Impact** | Models remain unsupervised anomaly detectors with no supervised refinement |
| **Evidence** | No label tables or feedback APIs in schema |
| **Recommended future improvement** | Add `investigation_outcomes` table and periodic retraining pipeline |

---

## Search Quality Gaps

**Semantic search, keyword search, vector search: NOT FOUND IN CURRENT CODEBASE**

### GAP-SRCH-001: No beneficiary or case search

| Attribute | Value |
| --- | --- |
| **Description** | No API or UI to search profiles by name, region, external_id, or risk level. |
| **Severity** | **High** |
| **Impact** | Investigators cannot discover high-risk cases at scale |
| **Evidence** | No search routes; `student_profiles` has no search indexes beyond `external_id` |
| **Recommended future improvement** | PostgreSQL full-text or dedicated search index on profiles + prediction aggregates |

### GAP-SRCH-002: No semantic / similarity search for fraud patterns

| Attribute | Value |
| --- | --- |
| **Description** | No embedding-based similarity to find beneficiaries with comparable feature vectors. |
| **Severity** | **Low** (optional enhancement) |
| **Impact** | Cannot cluster or find "similar fraud" cases |
| **Evidence** | No embedding models or vector tables |
| **Recommended future improvement** | Optional: embed `feature_snapshots.features` for similarity queries |

---

## Data Collection Gaps

### GAP-DATA-001: No feature snapshot ingestion

| Attribute | Value |
| --- | --- |
| **Description** | No service writes to `feature_snapshots`. CSV training data is not loaded into PostgreSQL. |
| **Severity** | **Critical** |
| **Impact** | DB-backed inference impossible; production data path undefined |
| **Evidence** | `packages/db/schema/feature-snapshots.ts`; no ingest code |
| **Recommended future improvement** | CSV ingest job mapping `user_id` → `student_profiles.external_id` |

### GAP-DATA-002: No feature schema validation

| Attribute | Value |
| --- | --- |
| **Description** | `feature_schema_version` column exists but no JSON schema enforcement for `features` JSONB. |
| **Severity** | **High** |
| **Impact** | Malformed snapshots cause runtime `KeyError` or silent OHE failures |
| **Evidence** | `packages/db/schema/feature-snapshots.ts` |
| **Recommended future improvement** | Publish `feature_schema_v1.json`; validate on insert |

### GAP-DATA-003: Training data not linked to profiles

| Attribute | Value |
| --- | --- |
| **Description** | CSV `user_id` integers are not mapped to `student_profiles.external_id` in any automated flow. |
| **Severity** | **Medium** |
| **Impact** | Cannot replay training data through production pipeline for validation |
| **Evidence** | `services/ml/data/*.csv`, `docs/database-architecture.md` |
| **Recommended future improvement** | Ingestion script with idempotent profile + snapshot creation |

### GAP-DATA-004: No event tracking

| Attribute | Value |
| --- | --- |
| **Description** | No analytics events for predictions, UI interactions, or model performance. |
| **Severity** | **Medium** |
| **Impact** | Cannot measure usage or detection efficacy |
| **Evidence** | No event tables beyond `audit_logs` (unused by ML path) |
| **Recommended future improvement** | Structured logging + `audit_logs` writes on each inference |

---

## Personalization Gaps

**NOT FOUND IN CURRENT CODEBASE** — No user preference storage, behavioral models, or adaptive ranking.

For investigator UX, related gap:

### GAP-PERS-001: No role-based views or saved filters

| Attribute | Value |
| --- | --- |
| **Description** | No auth roles, dashboards, or per-user settings. |
| **Severity** | **Medium** |
| **Impact** | All users would see same static landing page |
| **Evidence** | `docs/UI_ARCHITECTURE.md` (planned, not built) |
| **Recommended future improvement** | Auth + role-based dashboard after API integration |

---

## Monitoring Gaps

### GAP-MON-001: No prediction metrics or logging

| Attribute | Value |
| --- | --- |
| **Description** | `/predict` has no structured logs, metrics (latency, throughput), or error tracking. |
| **Severity** | **Critical** |
| **Impact** | Production incidents undetectable; no SLO tracking |
| **Evidence** | `services/ml/src/app.py` — no logging imports |
| **Recommended future improvement** | OpenTelemetry or Prometheus metrics; request/response logging (PII-redacted) |

### GAP-MON-002: No model health checks

| Attribute | Value |
| --- | --- |
| **Description** | `GET /` does not verify model artifacts loaded; no `/health` with model readiness. |
| **Severity** | **High** |
| **Impact** | Orchestrators may route traffic to broken instances |
| **Evidence** | `services/ml/src/app.py` — `home()` |
| **Recommended future improvement** | `/health` returning model load status and sklearn version |

### GAP-MON-003: No alerting on risk distribution drift

| Attribute | Value |
| --- | --- |
| **Description** | No monitoring of score distributions over time. |
| **Severity** | **Medium** |
| **Impact** | Data drift or model degradation goes unnoticed |
| **Evidence** | No monitoring infrastructure |
| **Recommended future improvement** | Batch statistics on `prediction_records.final_risk` |

---

## Evaluation Gaps

### GAP-EVAL-001: No offline evaluation harness

| Attribute | Value |
| --- | --- |
| **Description** | No precision/recall, ROC, or contamination validation against labeled fraud cases. |
| **Severity** | **High** |
| **Impact** | Model quality unknown; IsolationForest contamination is assumed, not validated |
| **Evidence** | `services/ml/src/train.py` — fits without evaluation split |
| **Recommended future improvement** | Evaluation script with held-out labeled set (if labels exist) |

### GAP-EVAL-002: No A/B testing or champion/challenger

| Attribute | Value |
| --- | --- |
| **Description** | `model_versions.is_active` unused; single hardcoded artifact set. |
| **Severity** | **Medium** |
| **Impact** | Cannot safely deploy model updates |
| **Evidence** | `packages/db/schema/model-versions.ts`, `services/ml/src/predict.py` |
| **Recommended future improvement** | Load models by active version; shadow scoring |

### GAP-EVAL-003: No explainability

| Attribute | Value |
| --- | --- |
| **Description** | SHAP claimed in README but not implemented; investigators cannot see which features drove risk. |
| **Severity** | **High** |
| **Impact** | Low trust, regulatory challenges for automated decisions |
| **Evidence** | `README.md`; no SHAP in `requirements.txt` |
| **Recommended future improvement** | Per-domain feature contribution analysis (SHAP or simpler z-score attribution) |

---

## Scalability Gaps

### GAP-SCALE-001: Models loaded once per process at import

| Attribute | Value |
| --- | --- |
| **Description** | `predict.py` and `preprocess.py` load all `.pkl` files at module import. No lazy load or model server. |
| **Severity** | **Low–Medium** |
| **Impact** | Slow cold start; memory per replica; no hot-swap |
| **Evidence** | `services/ml/src/predict.py` lines 18–21 |
| **Recommended future improvement** | Lazy loading, dedicated model server, or object storage-backed artifacts |

### GAP-SCALE-002: Synchronous-only inference

| Attribute | Value |
| --- | --- |
| **Description** | No async batch endpoint; no queue consumer for bulk scoring. |
| **Severity** | **High** |
| **Impact** | Large beneficiary populations cannot be scored efficiently |
| **Evidence** | Only `POST /predict` sync path exists |
| **Recommended future improvement** | `prediction_jobs` + worker pool; Redis already in `docker-compose.yml` |

### GAP-SCALE-003: Redis provisioned but unused

| Attribute | Value |
| --- | --- |
| **Description** | Redis container runs but no application connects. |
| **Severity** | **Low** (wasted resource today) |
| **Impact** | No caching of repeated predictions or job queues |
| **Evidence** | `docker-compose.yml`, `.env.example` |
| **Recommended future improvement** | Cache predictions by `feature_snapshots.checksum`; BullMQ job queue |

### GAP-SCALE-004: No horizontal scaling guidance

| Attribute | Value |
| --- | --- |
| **Description** | Stateless inference allows horizontal scale, but model files must exist on each replica; no shared artifact store integration. |
| **Severity** | **Medium** |
| **Impact** | Deployment friction at scale |
| **Evidence** | Local `models/` path in code |
| **Recommended future improvement** | `model_versions.artifact_uri` → S3/GCS download on startup |

---

## Security Gaps

### GAP-SEC-001: Unauthenticated ML endpoints

| Attribute | Value |
| --- | --- |
| **Description** | `/predict` and `/test` are publicly accessible without API keys or JWT. |
| **Severity** | **Critical** |
| **Impact** | Abuse, data injection, resource exhaustion |
| **Evidence** | `services/ml/src/app.py` |
| **Recommended future improvement** | API key or JWT middleware; network policies in Docker |

### GAP-SEC-002: No PII handling policy in ML path

| Attribute | Value |
| --- | --- |
| **Description** | Request payloads contain sensitive socioeconomic/medical data with no encryption-at-rest, redaction, or retention policy in the service. |
| **Severity** | **High** |
| **Impact** | Compliance risk (welfare/medical data) |
| **Evidence** | `UserData` fields in `app.py` |
| **Recommended future improvement** | Persist via encrypted DB only; avoid logging raw payloads |

### GAP-SEC-003: Public test endpoint exposes internal behavior

| Attribute | Value |
| --- | --- |
| **Description** | `GET /test` runs arbitrary bundled fixtures through production models without auth. |
| **Severity** | **Medium** |
| **Impact** | Information disclosure; unnecessary attack surface |
| **Evidence** | `services/ml/src/app.py` — `test()` |
| **Recommended future improvement** | Remove from production builds or protect behind admin auth |

### GAP-SEC-004: Pickle deserialization risk

| Attribute | Value |
| --- | --- |
| **Description** | `joblib.load` on `.pkl` files can execute arbitrary code if artifacts are tampered with. |
| **Severity** | **Medium** |
| **Impact** | Supply chain / artifact integrity risk |
| **Evidence** | `services/ml/src/predict.py`, `preprocess.py` |
| **Recommended future improvement** | Signed artifacts; ONNX export; restricted model storage |

### GAP-SEC-005: Audit logs not written for inference

| Attribute | Value |
| --- | --- |
| **Description** | `audit_logs` table exists but ML service never inserts rows. |
| **Severity** | **High** |
| **Impact** | No forensic trail for who triggered predictions |
| **Evidence** | `services/ml/src/db/models/audit_log.py` (unused) |
| **Recommended future improvement** | Write audit entry on each prediction with actor and resource IDs |

---

## Cost Optimization Gaps

### GAP-COST-001: No external LLM costs (positive)

| Attribute | Value |
| --- | --- |
| **Description** | Current stack is CPU-only sklearn — minimal marginal cost per prediction. |
| **Severity** | **Low** |
| **Impact** | Favorable for high-volume scoring |
| **Evidence** | No cloud AI API usage |
| **Recommended future improvement** | Maintain local inference for bulk scoring; reserve LLMs for optional explanations only |

### GAP-COST-002: No prediction caching

| Attribute | Value |
| --- | --- |
| **Description** | Identical feature payloads recompute full inference every time. |
| **Severity** | **Low** |
| **Impact** | Wasted CPU on duplicate requests |
| **Evidence** | Stateless `predict_all` |
| **Recommended future improvement** | Cache by `feature_snapshots.checksum` in Redis |

### GAP-COST-003: Redis running without utilization

| Attribute | Value |
| --- | --- |
| **Description** | Infrastructure cost with zero application benefit today. |
| **Severity** | **Low** |
| **Impact** | Minor wasted dev resources |
| **Evidence** | `docker-compose.yml` |
| **Recommended future improvement** | Wire Redis or remove from compose until needed |

---

## LLM / Generative AI Gaps

**All NOT FOUND IN CURRENT CODEBASE**

| Gap ID | Description | Severity | Recommended future improvement |
| --- | --- | --- | --- |
| GAP-LLM-001 | No natural language case summaries | Low (optional) | LLM summarizing prediction + profile for investigators |
| GAP-LLM-002 | No conversational assistant | Low (optional) | RAG over policy docs + case data |
| GAP-LLM-003 | No prompt management / versioning | N/A until LLMs added | Prompt registry with eval harness |

---

## Gap Priority Matrix

| Priority | Gap IDs |
| --- | --- |
| **P0 — Block production** | GAP-ARCH-002, GAP-DATA-001, GAP-MON-001, GAP-SEC-001, GAP-SEC-002 |
| **P1 — High value** | GAP-ARCH-001, GAP-EVAL-001, GAP-EVAL-003, GAP-SCALE-002, GAP-SRCH-001, GAP-REC-002 |
| **P2 — Operational maturity** | GAP-ARCH-003, GAP-ARCH-004, GAP-DATA-002, GAP-MON-002, GAP-EVAL-002, GAP-SEC-003 |
| **P3 — Nice to have** | GAP-SRCH-002, GAP-SCALE-003, GAP-COST-002, GAP-LLM-* |
