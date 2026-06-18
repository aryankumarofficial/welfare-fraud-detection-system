# Service Map

This document describes the running services defined in the repository and how they are wired together.

## Runtime Services

### postgres
- Role: Primary relational database for `services/ml`.
- Image: `postgres:16`
- Ports: `5432:5432`
- Used by: `migrate`, `ml-service`, and optionally `apps/api` as configured in `docker-compose.yml`.
- Path: `docker-compose.yml`

### redis
- Role: Redis queue backend used by the prediction queue and workers.
- Image: `redis:7`
- Ports: `6379:6379`
- Used by: `prediction-queue`, `prediction-worker`, `prediction-events`.
- Path: `docker-compose.yml`

### migrate
- Role: One-shot database migration runner.
- Image: `oven/bun:1.3.5`
- Command: `bun install && bun run db:migrate`
- Not a persistent runtime service.
- Path: `docker-compose.yml`

### ml-service
- Role: Core ML backend service.
- Runtime: FastAPI via Python / `uvicorn src.app:app`.
- Ports: `8000:8000`
- Path: `services/ml/src/app.py`
- Exposes all backend REST endpoints used by the frontend and workers.

### prediction-queue
- Role: Queue API service for enqueueing prediction jobs.
- Runtime: Bun server in `services/workers/src/predictions/server.ts`.
- Ports: `8010:8010`
- Uses: Redis and the ML backend; accepts `POST /predictions/enqueue`.
- Path: `services/workers/package.json`, `services/workers/src/predictions/server.ts`

### prediction-worker
- Role: Background queue worker that executes prediction jobs.
- Runtime: Bun worker in `services/workers/src/predictions/worker.ts`.
- No exposed HTTP port.
- Uses: Redis and ML backend internal endpoints.
- Path: `services/workers/package.json`, `services/workers/src/predictions/worker.ts`

### prediction-events
- Role: Background event listener for queue lifecycle events.
- Runtime: Bun event listener in `services/workers/src/predictions/events.ts`.
- No exposed HTTP port.
- Uses: Redis and ML backend internal endpoints.
- Path: `services/workers/package.json`, `services/workers/src/predictions/events.ts`

### api
- Role: Placeholder service in `docker-compose.yml`.
- Runtime: Bun `apps/api/index.ts`.
- Ports: `3001:3000`
- Actual content: a single `console.log("Hello via Bun!")` statement.
- No HTTP server, no route handlers, and no business logic.
- Path: `apps/api/index.ts`, `apps/api/package.json`

### web
- Role: Frontend Next.js application.
- Runtime: Next.js via `apps/web/package.json`.
- Ports: `3000:3000`
- Path: `apps/web/src/`.
- Calls the ML backend directly using `apps/web/src/lib/api.ts`.

## Library Packages

These are workspace packages, not standalone runtime services:
- `packages/auth`
- `packages/db`
- `packages/utils`

They provide shared logic, database wiring, or auth helpers for the repository, but are not independent services.

## Notes on apps/api

- `apps/api` is defined as a service in `docker-compose.yml`, but the codebase shows no HTTP server logic.
- There is no `Dockerfile` in `apps/api`, meaning the compose build context is incomplete for an actual service.
- No runtime or request flow in the repo depends on `apps/api`.
- Conclusion: `apps/api` is a placeholder, not a functional service.
