# Welfare Fraud Detection System

![CI](https://github.com/AryanKumarOfficial/welfare-fraud-detection-system/actions/workflows/ci.yml/badge.svg)

An **AI-powered fraud detection platform** designed to identify suspicious beneficiaries in government welfare distribution systems using **machine learning anomaly detection and risk scoring**.

The system combines **modern web technologies, scalable microservices, and ML models** to detect fraudulent activities early and improve transparency in welfare programs.

---

# Tech Stack

### Frontend

- Next.js (Admin Dashboard)
- TypeScript
- TailwindCSS
- Chart.js / Recharts

### Backend

- Next.js API Routes
- JWT Authentication
- Redis (Caching + Queue)

### Database

- PostgreSQL
- Drizzle ORM

### Machine Learning

- FastAPI
- Scikit-learn
- Isolation Forest
- XGBoost
- SHAP (Explainable AI)

### Infrastructure

- Bun Monorepo
- Docker
- Docker Compose
- Makefile Automation

---

# System Architecture

```

Admin Dashboard (Next.js)
│
▼
API Layer (Next.js)
│
├── PostgreSQL
├── Redis
│
▼
ML Service (FastAPI)
│
▼
Fraud Detection Models
(Isolation Forest + XGBoost)

```

---

# ML Fraud Detection Pipeline

```

Raw Beneficiary Data
↓
Data Cleaning
↓
Feature Engineering
↓
Isolation Forest (Anomaly Detection)
↓
XGBoost (Fraud Classification)
↓
Risk Score Generation
↓
Admin Dashboard Visualization

```

---

# Monorepo Structure

```

welfare-fraud-detection-system
│
├ apps
│ ├ admin        # Next.js Admin Dashboard
│ └ api          # Next.js Backend API
│
├ packages
│ ├ db           # Drizzle ORM schema
│ ├ auth         # Authentication utilities
│ ├ ui           # Shared UI components
│ └ utils        # Shared utilities
│
├ services
│ ├ ml           # FastAPI ML service
│ └ workers      # Background processing workers
│
├ docker-compose.yml
├ Makefile
└ package.json

```

---

# Setup

## 1. Clone Repository

```bash
git clone https://github.com/AryanKumarOfficial/welfare-fraud-detection-system
cd welfare-fraud-detection-system
```

---

## 2. Install Dependencies

Run the project setup using the Makefile.

```bash
make setup
```

This will automatically:

- Install Bun workspace dependencies
- Create the Python virtual environment
- Install ML dependencies

---

# Development

Start the full development environment:

```bash
make dev
```

This launches:

| Service         | Port |
| --------------- | ---- |
| Admin Dashboard | 3000 |
| API Server      | 3001 |
| ML Service      | 8000 |
| PostgreSQL      | 5432 |
| Redis           | 6379 |

---

# Running Individual Services

Run specific services if needed:

Start Admin Dashboard

```bash
make admin
```

Start API Server

```bash
make api
```

Start ML Service

```bash
make ml
```

Train the ML Model

```bash
make train
```

---

# Docker Setup

Run the entire system using Docker:

```bash
make docker-up
```

Stop all services:

```bash
make docker-down
```

---

# Example API Endpoint

Fraud detection endpoint:

```
POST /fraud/analyze
```

Example request:

```json
{
  "income": 25000,
  "transactions": 12,
  "age": 45
}
```

Response:

```json
{
  "risk_score": 0.82,
  "fraud_label": "HIGH_RISK"
}
```

---

# Future Enhancements

- Real-time fraud alerts
- Graph-based beneficiary relationship analysis
- Deep learning fraud models
- Cross-scheme fraud detection
- Cloud deployment at national scale

---

# Contributors

- [**Aryan Kumar**](https://github.com/AryanKumarOfficial)
- [**Jyoti Patel**](https://github.com/Jyp25070)
- [**Mayank Satpute**](https://github.com/mayanksatpute56-lgtm)
- [**Veer Singh Chauhan**](https://github.com/Veer17104)

Oriental Institute of Science & Technology
Bhopal, India

---

# Contribution Guidelines

See the [Contributing Guide](CONTRIBUTING.md) for details on how to contribute to this project.

---

# Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md).

# License

[MIT License](LICENSE)
