# Architecture Diagrams

**Audit date:** 2026-06-18  
**Scope:** Text-based and Mermaid diagrams for the ML/AI system as it exists in code

Diagrams distinguish **implemented** (solid lines) from **planned / NOT FOUND** (dashed).

---

## 1. System Architecture

### High-level monorepo layout (as deployed in Docker Compose)

```mermaid
flowchart TB
    subgraph Clients
        Browser[Browser / External Client]
    end

    subgraph apps [Applications]
        Web["apps/web<br/>Next.js :3000<br/>Static landing page"]
        API["apps/api<br/>Bun placeholder<br/>:3001"]
    end

    subgraph services [Services]
        ML["services/ml<br/>FastAPI :8000<br/>IsolationForest inference"]
        Workers["services/workers<br/>NOT IMPLEMENTED"]
    end

    subgraph data [Data Layer]
        PG[(PostgreSQL 16<br/>welfare DB)]
        Redis[(Redis 7<br/>unused by app code)]
    end

    Browser --> Web
    Browser -.->|no ML calls today| ML
    Browser -.->|direct if configured| ML
    API -.->|no routes| ML
    Web -.->|no API routes| API

    ML -->|DATABASE_URL configured<br/>not used by /predict| PG
    API -.-> PG
    Web -.-> PG

    Workers -.-> PG
    Workers -.-> Redis
    API -.-> Redis

    style Workers stroke-dasharray: 5 5
    style API stroke-dasharray: 5 5
```

**Sources:** `docker-compose.yml`, `apps/api/index.ts`, `services/ml/src/app.py`, `apps/web/`

---

### ML service internal architecture

```mermaid
flowchart LR
    subgraph FastAPI["services/ml/src/app.py"]
        Routes["GET /<br/>POST /predict<br/>GET /test"]
        UserData["Pydantic UserData<br/>22 fields"]
    end

    subgraph Inference["services/ml/src/predict.py"]
        PA["predict_all()"]
        NS["normalize_score()"]
        M1[income_model.pkl]
        M2[caste_model.pkl]
        M3[transaction_model.pkl]
        M4[medical_model.pkl]
    end

    subgraph Preprocess["services/ml/src/preprocess.py"]
        PI[preprocess_income]
        PC[preprocess_caste]
        PT[preprocess_transaction]
        PM[preprocess_medical]
        S1[income_scaler]
        S2[caste_scaler + encoder]
        S3[transaction_scaler]
        S4[medical_scaler]
    end

    subgraph DBLayer["services/ml/src/db<br/>NOT USED BY /predict"]
        ORM[SQLAlchemy models]
        Repo[AsyncRepository]
    end

    Routes --> UserData --> PA
    PA --> PI & PC & PT & PM
    PI --> S1 --> M1
    PC --> S2 --> M2
    PT --> S3 --> M3
    PM --> S4 --> M4
    M1 & M2 & M3 & M4 --> NS --> PA

    style DBLayer stroke-dasharray: 5 5
```

**Sources:** `services/ml/src/app.py`, `predict.py`, `preprocess.py`, `db/`

---

## 2. Recommendation Flow

**NOT FOUND IN CURRENT CODEBASE**

This repository does not implement a recommendation engine (collaborative filtering, content-based ranking, hybrid recommenders, or gift suggestions).

### Closest equivalent: Fraud risk aggregation (implemented)

```mermaid
flowchart TD
    A[22 input features] --> B[preprocess_income]
    A --> C[preprocess_caste]
    A --> D[preprocess_transaction]
    A --> E[preprocess_medical]

    B --> F[income_model<br/>IsolationForest]
    C --> G[caste_model]
    D --> H[transaction_model]
    E --> I[medical_model]

    F --> J[income_risk<br/>sigmoid]
    G --> K[caste_risk]
    H --> L[transaction_risk]
    I --> M[medical_risk]

    J & K & L & M --> N["final_risk = mean(4 risks)"]
    N --> O[JSON response]

    style A fill:#e8f4e8
    style O fill:#e8f4e8
```

**Source:** `services/ml/src/predict.py` — `predict_all()`

There is no ranking of items, no candidate retrieval, and no personalization.

---

## 3. Search Flow

**NOT FOUND IN CURRENT CODEBASE**

No semantic search, keyword search, vector retrieval, or embedding pipeline exists.

```mermaid
flowchart LR
    Query[User search query] -.->|NOT IMPLEMENTED| Embed[Embedding model]
    Embed -.-> VectorDB[(Vector index)]
    VectorDB -.-> Results[Ranked results]

    style Query stroke-dasharray: 5 5
    style Embed stroke-dasharray: 5 5
    style VectorDB stroke-dasharray: 5 5
    style Results stroke-dasharray: 5 5
```

**Planned data access pattern (schema only):** profiles could be listed by `external_id` index on `student_profiles` — no search API exposes this.

**Source:** `packages/db/schema/student-profiles.ts`

---

## 4. Chatbot Flow

**NOT FOUND IN CURRENT CODEBASE**

No chat UI, conversation state, LLM calls, or RAG pipeline.

```mermaid
sequenceDiagram
    participant User
    participant UI as Chat UI
    participant API as Chat API
    participant LLM as LLM Provider

    User->>UI: Message
    Note over UI,LLM: NOT IMPLEMENTED
    UI--xAPI: No route
    API--xLLM: No integration
```

---

## 5. Data Flow

### 5a. Current inference data flow (implemented)

```mermaid
flowchart TD
    subgraph Input
        HTTP["POST /predict<br/>JSON body"]
    end

    subgraph Validation
        PYD["Pydantic UserData<br/>app.py"]
    end

    subgraph Processing
        DICT["data.dict()"]
        PRE["preprocess.py<br/>4 domain functions"]
        SCALE["StandardScaler x4<br/>OneHotEncoder x1"]
    end

    subgraph Models
        IF["IsolationForest x4<br/>decision_function"]
        SIG["normalize_score<br/>sigmoid k=5"]
        AVG["Arithmetic mean"]
    end

    subgraph Output
        RESP["{ success, data: risks }"]
    end

    HTTP --> PYD --> DICT --> PRE --> SCALE --> IF --> SIG --> AVG --> RESP

    DB[(PostgreSQL)] -.->|not read/written| PRE

    style DB stroke-dasharray: 5 5
```

**Source:** `services/ml/src/app.py`, `predict.py`, `preprocess.py`

---

### 5b. Training data flow (implemented, offline)

```mermaid
flowchart LR
    CSV1[income.csv] --> T1[train_income]
    CSV2[caste.csv] --> T2[train_caste]
    CSV3[transaction.csv] --> T3[train_transaction]
    CSV4[medical.csv] --> T4[train_medical]

    T1 & T2 & T3 & T4 --> PKL["models/*.pkl"]
    PKL --> INF[predict.py / preprocess.py<br/>at service startup]
```

**Source:** `services/ml/src/train.py`, `services/ml/data/`

---

### 5c. Target production data flow (designed, NOT implemented)

```mermaid
flowchart TD
    ING[CSV ingest / API payload] --> SP[student_profiles]
    ING --> FS[feature_snapshots<br/>features JSONB v1]
    SP --> FS

    REQ["POST /predict<br/>{ profile_id }"] --> LOOKUP[Load latest snapshot]
    LOOKUP --> FS
    LOOKUP --> PRE[preprocess.py]
    PRE --> PA[predict_all]
    PA --> PR[prediction_records]
    PR --> AUD[audit_logs]

    style ING stroke-dasharray: 5 5
    style REQ stroke-dasharray: 5 5
    style LOOKUP stroke-dasharray: 5 5
    style PR stroke-dasharray: 5 5
    style AUD stroke-dasharray: 5 5
```

**Source:** `docs/database-architecture.md`

---

### 5d. Database entity relationships (implemented schema)

```mermaid
erDiagram
    users ||--o{ student_profiles : creates
    users ||--o{ prediction_records : requests
    users ||--o{ audit_logs : acts

    student_profiles ||--o{ feature_snapshots : has
    student_profiles ||--o{ prediction_records : has

    feature_snapshots ||--o{ prediction_records : "inputs (optional FK)"

    model_versions ||--o{ prediction_records : "version (optional FK)"

    student_profiles {
        uuid id PK
        text external_id
        text name
        date date_of_birth
        text gender
        text region
    }

    feature_snapshots {
        uuid id PK
        uuid student_profile_id FK
        jsonb features
        text feature_schema_version
        text checksum
        enum source
    }

    prediction_records {
        uuid id PK
        uuid student_profile_id FK
        uuid feature_snapshot_id FK
        float income_risk
        float caste_risk
        float transaction_risk
        float medical_risk
        float final_risk
        enum inference_source
    }

    model_versions {
        uuid id PK
        text name
        text version
        text artifact_uri
        boolean is_active
    }
```

**Sources:** `packages/db/schema/*.ts`, `services/ml/src/db/models/*.py`

---

## 6. Service Communication Flow

### 6a. Docker Compose service dependencies (implemented infrastructure)

```mermaid
flowchart BT
    PG[(postgres)]
    Migrate[migrate<br/>drizzle migrations]
    Redis[(redis)]
    ML[ml-service<br/>:8000]
    API[api<br/>:3001]
    Web[web<br/>:3000]

    PG --> Migrate
    Migrate --> ML
    Migrate --> API
    Migrate --> Web
    PG --> ML
    PG --> API
    PG --> Web
    Redis --> API
    ML --> API
    API --> Web
```

**Source:** `docker-compose.yml`

**Note:** Dependency edges exist in Compose but application-level HTTP calls from `api` → `ml-service` are **NOT FOUND IN CURRENT CODEBASE**.

---

### 6b. Prediction request sequence (implemented path)

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant F as FastAPI app.py
    participant P as predict.py
    participant R as preprocess.py
    participant M as joblib models

  C->>F: POST /predict
  F->>F: Validate UserData
  F->>P: predict_all(dict)
  par Domain preprocessing
    P->>R: preprocess_income
    P->>R: preprocess_caste
    P->>R: preprocess_transaction
    P->>R: preprocess_medical
  end
  R->>M: scaler.transform / encoder.transform
  P->>M: decision_function (x4)
  P->>P: normalize_score + mean
  P-->>F: risk dict
  F-->>C: 200 { success, data }
```

**Source:** `services/ml/src/app.py`, `predict.py`, `preprocess.py`

---

### 6c. Target integrated flow (NOT implemented)

```mermaid
sequenceDiagram
    autonumber
    participant U as Investigator Browser
    participant W as apps/web
    participant A as apps/api
    participant M as ml-service
    participant DB as PostgreSQL

    Note over U,DB: NOT IMPLEMENTED — design target

    U->>W: Request risk for beneficiary
    W->>A: GET /profiles/:id/risk
    A->>DB: SELECT feature_snapshots ORDER BY created_at DESC LIMIT 1
    DB-->>A: features JSONB
    A->>M: POST /predict (features or profile_id)
    M->>M: predict_all
    M-->>A: risks
    A->>DB: INSERT prediction_records
    A-->>W: risk + history
    W-->>U: Dashboard
```

**Sources:** `docs/database-architecture.md`, `docs/UI_ARCHITECTURE.md`

---

## 7. Frontend AI Feature Flow (static UI only)

```mermaid
flowchart LR
    User[Visitor] --> Page[apps/web homepage]
    Page --> Hero[hero-content.tsx]
    Page --> Risk[hero-risk-panel.tsx]
    Page --> Stats[stats-section.tsx]

    Risk --> Hardcoded["Hardcoded arrays<br/>72/18/10% risks<br/>2847 fraud cases"]

    ML[ml-service] -.->|no fetch| Risk

    style ML stroke-dasharray: 5 5
    style Hardcoded fill:#fff3cd
```

**Source:** `apps/web/src/components/home/hero/hero-risk-panel.tsx` lines 7–11

---

## Diagram Legend

| Symbol | Meaning |
| --- | --- |
| Solid arrow | Implemented in current code |
| Dashed arrow / box | Planned, documented, or NOT FOUND |
| Yellow fill | Hardcoded / mock data |

---

## File Reference Index

| Diagram section | Primary source files |
| --- | --- |
| System architecture | `docker-compose.yml`, `apps/*`, `services/*` |
| ML internals | `services/ml/src/*.py` |
| Data flow | `services/ml/src/train.py`, `packages/db/schema/*` |
| Service communication | `docker-compose.yml`, `services/ml/package.json` |
| Frontend | `apps/web/src/components/home/**` |
| Planned flows | `docs/database-architecture.md` |
