# API Ownership

This document explains which repository component owns HTTP behavior and whether `apps/api` is required.

## Current ownership

### `services/ml`
- Owns the full backend API surface used by the application.
- Source of truth: `services/ml/src/app.py`.
- Exposes:
  - Public ML endpoints for prediction, snapshot generation, analytics, model lifecycle, and auth.
  - Internal worker endpoints under `/internal/predictions/jobs/...`.
- Directly used by:
  - `apps/web` frontend (`apps/web/src/lib/api.ts`).
  - `services/workers` worker code.

### `apps/web`
- Owns the UI and client API wrapper.
- Does not own backend business endpoints.
- Does not implement `route.ts` or any backend route handlers.
- Calls `services/ml` directly using the environment-provided base URL.

### `apps/api`
- Contains only a Bun placeholder at `apps/api/index.ts`:
  - `console.log("Hello via Bun!")`
- No HTTP server is started.
- No route handlers are present.
- No frontend code imports or calls `apps/api`.
- No worker code imports or calls `apps/api`.

## Endpoint ownership matrix

| Component | Owns endpoint | Comment |
|---|---|---|
| `services/ml` | Yes | All runtime REST and internal worker endpoints.
| `apps/web` | No | UI only; uses `services/ml`.
| `apps/api` | No | Placeholder; no routes.
| `services/workers` | Yes, queue API only | `prediction-queue` exposes `/predictions/enqueue` plus `/health`.

## `apps/api` dependency and safety analysis

### Frontend dependencies
- Search results show no `apps/api` import paths in frontend code.
- `apps/web/src/lib/api.ts` resolves to `ML_API_URL` and does not reference `apps/api`.
- The `web` service only depends on `api` in `docker-compose.yml` for startup ordering, not as an API consumer.

### Worker dependencies
- `services/workers` uses `services/ml` internal endpoints and Redis.
- No worker source file imports or references `apps/api`.
- The workers are wired to ML service URLs in `services/workers/src/predictions/config.ts`.

### Business logic
- `apps/api` contains zero business logic.
- The only file is `apps/api/index.ts`, which logs a greeting and exits.
- There are no models, controllers, routes, or data flows in `apps/api`.

### Docker compose evaluation
- `apps/api` is included as a service in `docker-compose.yml`.
- It depends on `postgres`, `migrate`, `redis`, and `ml-service`, though its code does not use those resources.
- There is no `Dockerfile` in `apps/api`, making it nonfunctional as a build context.

## Conclusion

`apps/api` can be removed safely from the current repository as a runtime service.

### Conditions for removal
- Remove `apps/api` service from `docker-compose.yml`.
- Update `apps/web.depends_on` to remove the `api` dependency.
- Remove any documentation mentions of `apps/api` being a live API gateway.

### Remaining owners after removal
- `services/ml` remains the single source of truth for backend APIs.
- `apps/web` remains the frontend client.
- `services/workers` remains the queue and worker subsystem.

## Recommendation

Remove `apps/api` from the service topology unless it is explicitly intended to become a real API gateway in the future.
