# Protected Endpoints

This document lists all auth-protected endpoints in `services/ml/src/app.py` and their required access control.

## Public endpoints

- `GET /`
  - No auth required.
- `GET /health`
  - No auth required.
- `GET /ready`
  - No auth required.
- `POST /auth/token`
  - Login endpoint; no bearer auth required.

## Operator-protected endpoints

- `POST /predict`
- `POST /predict/profile`
- `POST /snapshot/generate`
- `POST /predict/generate`
- `POST /predictions/queue`
- `GET /predictions/{student_profile_id}`
- `GET /predictions/detail/{prediction_id}`
- `GET /predictions/jobs/{job_id}`
- `GET /predictions/jobs/{job_id}/result`

## Analyst-protected endpoints

- `GET /dashboard/summary`
- `GET /metrics/predictions`
- `GET /analytics/predictions`
- `GET /analytics/model-performance`
- `GET /analytics/drift`
- `GET /analytics/alerts`
- `GET /models`
- `GET /models/compare`
- `GET /models/{model_id}`
- `POST /models/{model_id}/evaluate`
- `GET /analytics/model-health`
- `GET /predictions/reviews`

## Admin-protected endpoints

- `GET /test`
- `POST /models`
- `POST /models/{model_id}/promote`
- `POST /models/{model_id}/rollback`
- `POST /models/{model_id}/archive`

## Internal service endpoints

- `POST /internal/predictions/jobs/{job_id}/execute`
- `POST /internal/predictions/jobs/{job_id}/retrying`
- `POST /internal/predictions/jobs/{job_id}/failed`

## Error handling and auth failure responses

- Missing or invalid bearer token returns HTTP 401.
- Insufficient role returns HTTP 403.
- Invalid internal API key returns HTTP 401.
- Invalid queue API key returns HTTP 401.

## Notes

- Route protection is enforced by FastAPI dependencies in `services/ml/src/app.py`.
- Role hierarchies are determined by `services/ml/src/security.py`.
- There is no unprotected route for user registration or user profile management.
