# Phase 9: Platform Integration & Production Readiness

## Overview
This phase completes the platform's transition from prototype to production-ready deployment by adding authentication, RBAC, structured logging, health checks, deployment configuration hardening, and operational documentation.

## Service integration audit
- `services/ml` is the primary ML API and orchestration service.
- `services/workers` owns BullMQ queue enqueueing and worker execution.
- `docker-compose.yml` binds `ml-service`, `prediction-queue`, and `prediction-worker` together with Redis and Postgres.
- `apps/api` is currently a placeholder and may be expanded later as an API gateway.

## Authentication and RBAC
- `POST /auth/token` issues bearer tokens for service users.
- Roles supported:
  - `admin` — full model lifecycle, archives, promotions, and review governance.
  - `analyst` — review workflows, analytics, and monitoring.
  - `operator` — inference, snapshot generation, and queue operations.
- Internal machine-to-machine communication is protected using `X-Internal-API-Key` and `X-Queue-API-Key`.

## Health and readiness
- `GET /health` returns service, database, and model readiness state.
- `GET /ready` returns a lightweight readiness check.
- `GET /` remains a welcome endpoint.

## Observability
- Structured request logging is emitted in JSON format.
- Request IDs are assigned with `X-Request-ID` and returned in responses.
- Raw payload content is redacted for sensitive fields.

## Deployment configuration
- `services/ml/Dockerfile` is aligned with the Python app path `src.app:app`.
- Docker compose environment variables are centralized and documented.
- Queue and worker processes use authenticated internal headers.

## Security hardening
- Administrative endpoints are protected by role-based access.
- Queue enqueue and execution callbacks are protected with dedicated API keys.
- The `/test` endpoint is restricted to admin users only.
- Token creation requires valid service account credentials.

## Operations
- Use `docker compose up --build` for local deployment.
- Supply production secrets via environment variables, not in source control.
- Monitor logs via the `welfare_fraud_ml` structured logger.

## Recommended environment variables
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `INTERNAL_API_KEY`
- `QUEUE_API_KEY`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ANALYST_USERNAME`
- `ANALYST_PASSWORD`
- `OPERATOR_USERNAME`
- `OPERATOR_PASSWORD`
