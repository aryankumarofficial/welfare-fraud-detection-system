# Production Readiness Audit

## Scope

Reviewed the full repository for production readiness across:
- `apps/web`
- `apps/api`
- `services/ml`
- `services/workers`
- PostgreSQL
- Redis
- BullMQ

Verified:
- startup order
- environment variables
- database migration path
- worker connectivity
- ML service connectivity
- endpoint request/response and auth expectations

> No business logic was modified during this audit.

---

## 1. Integration Audit

### apps/web

Findings:
- `apps/web` is a Next.js frontend, but there is no evidence of backend integration in `apps/web/src`. No `fetch`, `axios`, `NEXT_PUBLIC_*`, or backend URL references were found.
- `apps/web/package.json` declares dependency on `@repo/db`, but actual source files in `apps/web/src` do not import that package.
- This suggests the frontend is currently a static marketing/presentation layer or an incomplete UI integration.

Risk:
- Frontend is not coupled to API/ML services, so users cannot access protected application flows from the browser.
- `@repo/db` is an unused declared dependency in frontend build.

### apps/api

Findings:
- `apps/api/index.ts` contains only:
  - `console.log("Hello via Bun!")`
- There are no HTTP routes, no server logic, and no service handlers.
- The Docker Compose service `api` still builds and exposes port `3000:3000`.

Risk:
- `apps/api` is effectively a dead integration point. The container will start but provide no API endpoints.
- This may hide broken expected API behavior or leave the service orphaned.

### services/ml

Findings:
- The ML service exposes the following verified endpoints:
  - `GET /`
  - `POST /auth/token`
  - `GET /health`
  - `GET /ready`
  - `POST /predict`
  - `POST /predict/profile`
  - `POST /snapshot/generate`
  - `POST /predict/generate`
  - `GET /test`
  - `POST /predictions/queue`
  - `GET /predictions/reviews`
  - `GET /predictions/{student_profile_id}`
  - `GET /predictions/detail/{prediction_id}`
  - `GET /metrics/predictions`
  - `GET /analytics/predictions`
  - `POST /predictions/{prediction_id}/review`
  - `GET /predictions/jobs/{job_id}`
  - `GET /predictions/jobs/{job_id}/result`
  - `GET /analytics/queue`
  - `GET /analytics/model-performance`
  - `GET /analytics/drift`
  - `GET /analytics/alerts`
  - `POST /internal/predictions/jobs/{job_id}/execute`
  - `POST /internal/predictions/jobs/{job_id}/retrying`
  - `POST /internal/predictions/jobs/{job_id}/failed`
  - `GET /dashboard/summary`
  - Model registry endpoints under `/models`
  - `GET /analytics/model-health`

Auth model:
- `POST /auth/token` issues bearer tokens for roles: `admin`, `analyst`, `operator`.
- `require_operator` guard covers prediction and queue operations.
- `require_analyst` guard covers analytics and review endpoints.
- `require_admin` guard covers model registration/lifecycle endpoints.
- Internal queue callbacks require `X-Internal-API-Key`.
- Queue enqueue endpoint requires `X-Queue-API-Key`.

Observation:
- Request validation is implemented through Pydantic models for most endpoints.
- Response models are not consistently declared with `response_model`, so OpenAPI response schema coverage is incomplete.
- `services/ml/src/security.py` implements a custom JWT-like token format. This is a security risk in production because it is homegrown and not standard JWT.

### services/workers

Findings:
- `services/workers/src/predictions/server.ts` exposes:
  - `GET /health`
  - `POST /predictions/enqueue`
- It requires `x-queue-api-key` and matches ML service queue auth.
- `services/workers/src/predictions/handler.ts` calls ML internal endpoints with `X-Internal-API-Key`.
- `services/workers/src/predictions/worker.ts` connects to Redis and processes jobs from BullMQ.
- `services/workers/src/predictions/events.ts` listens to queue events and posts failures to ML internal endpoints.

Broken route:
- `prediction-events` posts to ML internal endpoints but does not include `X-Internal-API-Key`.
- Since ML internal endpoints require that header, `prediction-events` will be unauthorized and cannot update failed jobs as intended.

### PostgreSQL

Findings:
- Docker Compose config uses `postgres:16` and exposes `5432:5432`.
- `migrate` service waits for Postgres health via `pg_isready` before running migrations.
- `packages/db/migrate.ts` uses `drizzle-orm` migrations and exits with failure on migration error.
- `services/ml` uses `DATABASE_URL` with SQLAlchemy async and connection pooling.

Observation:
- Migration path exists and is wired into Docker Compose successfully.
- `services/ml` database config supports `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `DB_POOL_TIMEOUT`, and `DB_ECHO`, but these are not set in Compose.

### Redis

Findings:
- Docker Compose uses `redis:7` and exposes `6379:6379`.
- `prediction-queue`, `prediction-worker`, and `prediction-events` depend on Redis.
- Workers convert `REDIS_URL` into a BullMQ connection.

Observation:
- Redis is present and consumed properly by BullMQ worker components.
- `apps/api` depends on Redis in Compose, but no code was found using Redis.

### BullMQ

Findings:
- BullMQ is declared in `services/workers/package.json`.
- The queue is named `prediction-processing`.
- The HTTP bridge enqueues jobs by forwarding to BullMQ.
- Worker processes use `new Worker(...)` and `QueueEvents`.

Risk:
- There is no health or retry logic around the BullMQ HTTP bridge itself. If Redis is unavailable at startup, the queue service may fail silently or crash.

---

## 2. Startup Order Verification

Verified Docker Compose startup order:
- `postgres` starts first.
- `migrate` waits for Postgres health and applies migrations.
- `ml-service` waits for `postgres` healthy and `migrate` completed successfully.
- `prediction-queue`, `prediction-worker`, and `prediction-events` wait for `redis` started and `ml-service` started.
- `api` depends on `postgres` healthy, `migrate` completed, `redis` started, and `ml-service` started.
- `web` depends on `postgres` healthy, `migrate` completed, and `api` started.

Risks:
- `depends_on: service_started` only waits for container startup, not application readiness. `ml-service` may not be ready when workers or `api` begin.
- The queue and worker dependencies should preferably wait for ML readiness, not just container startup.

---

## 3. Environment Variable Audit

Verified environment variables in Docker Compose and code paths.

ML Service expects:
- `DATABASE_URL`
- `PREDICTION_QUEUE_API_URL`
- `JWT_SECRET_KEY`
- `JWT_ACCESS_TOKEN_EXPIRE_SECONDS` (default 3600)
- `INTERNAL_API_KEY`
- `QUEUE_API_KEY`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ANALYST_USERNAME`
- `ANALYST_PASSWORD`
- `OPERATOR_USERNAME`
- `OPERATOR_PASSWORD`

Queue service expects:
- `REDIS_URL`
- `PREDICTION_QUEUE_API_PORT`
- `ML_SERVICE_URL`
- `QUEUE_API_KEY`

Worker expects:
- `REDIS_URL`
- `ML_SERVICE_URL`
- `INTERNAL_API_KEY`
- `QUEUE_API_KEY`
- `PREDICTION_WORKER_CONCURRENCY`

Notes:
- `JWT_ALGORITHM` is supported by settings but not set in Docker Compose; default behavior will still work.
- `DB_*` parameters are supported in ML service but not defined in Compose.
- `apps/api` and `apps/web` have no explicit env vars declared in Compose beyond basic build/deploy values.

---

## 4. Migration Verification

Verified migration architecture:
- `docker-compose.yml` runs `migrate` container with `bun run db:migrate`.
- `packages/db/migrate.ts` uses Drizzle migrator.
- Compose uses `depends_on.migrate.condition: service_completed_successfully` to gate downstream services.

Audit conclusion:
- Migration path is implemented and enforced before primary services start.

---

## 5. Worker Connectivity Verification

Verified worker path:
- `services/workers/src/predictions/server.ts` receives enqueue requests and posts jobs to BullMQ.
- `services/mo/src/services/prediction_queue_client.py` sends `POST /predictions/enqueue` with `X-Queue-API-Key`.
- `services/workers/src/predictions/worker.ts` processes jobs from Redis and calls ML internal execute endpoint.
- `services/workers/src/predictions/handler.ts` includes `X-Internal-API-Key` when posting to ML internal callbacks.

Broken connectivity:
- `services/workers/src/predictions/events.ts` posts failure events to ML internal endpoints without `X-Internal-API-Key`, causing unauthorized callback failures.

---

## 6. ML Connectivity Verification

Verified ML service connectivity:
- `services/ml/src/db/session.py` uses async SQLAlchemy engine with `DATABASE_URL`.
- `services/ml/src/app.py` implements `/health` and `/ready` checks against the database.
- The queue client uses `PREDICTION_QUEUE_API_URL`.

Observation:
- ML service startup warnings log insecure defaults for `JWT_SECRET_KEY`, `INTERNAL_API_KEY`, and `QUEUE_API_KEY`.
- The health endpoints exist and are a good readiness signal.

---

## 7. Missing Integrations

- `apps/api` is missing actual route handlers and HTTP functionality.
- `apps/web` does not call backend services; no frontend API integration is present.
- `apps/web` contains an unused dependency on `@repo/db`.
- `apps/api` depends on Redis in Docker Compose despite no code using Redis.

---

## 8. Broken Routes / Issues

1. `services/workers/src/predictions/events.ts`
   - Fails to send `X-Internal-API-Key` to ML internal callbacks.
   - This prevents `failed` job notifications from being accepted by `services/ml`.

2. `apps/api/index.ts`
   - No API endpoints are defined.
   - The service is built and exposed but provides no functionality.

3. `services/ml/src/security.py`
   - Custom JWT-like token generation is implemented instead of a standard library.
   - This is a production risk and should be reviewed or replaced with a well-tested JWT library.

4. `docker-compose.yml`
   - `prediction-queue`, `prediction-worker`, `prediction-events`, and `api` depend on `ml-service` via `service_started` only.
   - This is a weak readiness signal and may allow race conditions.

---

## 9. Dead Code / Unused Components

- `apps/api` contains only a console log and no HTTP handlers.
- `apps/web` contains no backend integration code; its `@repo/db` dependency appears unused.
- `apps/api` Docker Compose definition starts a service that does not currently expose application logic.

---

## 10. Missing Tests

Observed gaps:
- No automated tests for `apps/api` or `apps/web` integration.
- No end-to-end test covering the ML service -> BullMQ queue -> worker -> ML callback cycle.
- No explicit tests for queue API auth header enforcement or internal ML callback auth flow.
- No tests verify `prediction-events` failed-job callback behavior.

Existing tests in `services/ml/tests` cover model monitoring, registry, lifecycle, queue, security, and snapshot pipeline, but they do not appear to cover the full HTTP endpoint contract or worker integration.

---

## 11. Risk Report

High-priority risks:
- `apps/api` is not a functional API service.
- `services/workers/src/predictions/events.ts` is broken by missing internal auth header.
- Startup ordering uses container readiness instead of application readiness.
- `apps/web` is not integrated with backend services.
- Custom JWT implementation in `services/ml` is a security risk.

Medium-priority risks:
- Incomplete OpenAPI response schemas across ML endpoints.
- `apps/api` depends on Redis while not using it.
- Insecure default values are still present in Docker Compose and should be replaced.
- No `DB_*` pool tuning values are set for production.

Lower-priority risks:
- Frontend dead dependency on `@repo/db`.
- `prediction-events` failure callback relies on `fetch(...).catch(() => undefined)` and swallows errors.

---

## 12. Recommended Fixes

1. Fix `apps/api` immediately:
   - Add meaningful route handlers or remove the service from production compose if it is not used.
   - Confirm whether it should proxy to `services/ml` or host separate endpoints.

2. Fix `prediction-events` auth:
   - Add `X-Internal-API-Key` on failure callback requests to ML.
   - Ensure the service can handle retries when ML is temporarily unavailable.

3. Harden startup order:
   - Replace `service_started` dependencies with readiness checks where possible.
   - Add `healthcheck` on `ml-service` and make queue/worker depend on it.
   - Add retry loops for BullMQ/ML connections in startup code.

4. Harden auth and secrets:
   - Replace the homegrown token scheme with a standard JWT solution.
   - Remove insecure default values from production deployments.
   - Add environment validation on startup to fail fast on missing or insecure secrets.

5. Improve test coverage:
   - Add tests for `apps/api` and `apps/web` if they are intended to be live parts of the system.
   - Add end-to-end tests for queue lifecycle and worker callbacks.
   - Add auth tests for queue and internal service headers.

6. Clean dead code:
   - Remove or repurpose `apps/api` if not in use.
   - Remove unused `@repo/db` dependency from `apps/web` if frontend does not require it.
   - Remove stale Redis dependency from `apps/api` Compose config if not used.

7. Validate database schema:
   - All schema modules appear referenced in `services/ml`.
   - Continue verifying that migrations remain aligned with the ActiveRecord model definitions.

---

## 13. Summary

The platform has a largely coherent ML + queue architecture, and the migration path is implemented. However, the current repository contains several production readiness gaps:
- non-functional API service,
- frontend without backend integration,
- broken worker event callback auth,
- weak startup readiness dependencies,
- homegrown auth token logic.

Addressing these findings will be required before this system can be considered production-ready.
