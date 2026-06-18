# Request Flow

This document describes the live request paths and how frontend and worker traffic flows through the repository.

## Frontend API Flow

### Entry point
- `apps/web/src/lib/api.ts`
- Uses `ML_API_URL` or `NEXT_PUBLIC_API_URL` to target the ML backend.
- Uses `ANALYST_USERNAME` / `ANALYST_PASSWORD` to authenticate against `POST /auth/token`.

### Frontend requests

The frontend does not use `apps/api`.
It calls the ML service directly over HTTP.

#### Auth
- `POST /auth/token`

#### Prediction and snapshot workflows
- `POST /snapshot/generate`
- `POST /predict/generate`
- `POST /predictions/queue`
- `POST /predictions/{prediction_id}/review`

#### Analytics and history
- `GET /dashboard/summary`
- `GET /predictions/{student_profile_id}`
- `GET /predictions/detail/{prediction_id}`
- `GET /analytics/predictions`
- `GET /analytics/model-performance`
- `GET /analytics/drift?days=`
- `GET /analytics/alerts`
- `GET /analytics/queue`
- `GET /predictions/jobs/{job_id}`
- `GET /predictions/reviews`

## Backend API Ownership

### `services/ml`
- Owns all HTTP endpoints in the current runtime.
- Exposes both public endpoints and internal endpoints for workers.
- Frontend uses this service directly.

### `apps/api`
- Not part of the current request flow.
- Contains no HTTP request handlers.
- The frontend does not call it.

## Worker Request Flow

### `prediction-queue`
- Runs Bun-based queue API at `services/workers/src/predictions/server.ts`.
- Exposes:
  - `GET /health`
  - `POST /predictions/enqueue`
- Requires `x-queue-api-key`.
- Enqueues jobs into Redis using `bullmq`.

### `prediction-worker`
- Executes queued prediction jobs.
- Does not expose public HTTP endpoints.
- Calls ML service internal endpoints for job execution.
- Uses `process.env.ML_SERVICE_URL`.

### `prediction-events`
- Listens to queue events from Redis.
- Logs queue lifecycle events.
- Calls ML internal endpoint on job failure.

## Worker–ML internal flow

The worker processes talk to `services/ml` internal endpoints:
- `POST /internal/predictions/jobs/{job_id}/execute`
- `POST /internal/predictions/jobs/{job_id}/retrying`
- `POST /internal/predictions/jobs/{job_id}/failed`

These are the only non-frontend HTTP endpoints that the worker subsystem consumes.

## Summary

- `apps/web` => direct HTTP calls to `services/ml`.
- `prediction-queue` => exposes queue enqueue endpoint and uses Redis.
- `prediction-worker` / `prediction-events` => talk to `services/ml` internal endpoints.
- `apps/api` => no request flow at all.
