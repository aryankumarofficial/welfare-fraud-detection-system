# Startup Flow Audit

This document describes the behavior of `docker compose up --build` and whether startup includes CSV ingestion.

## docker-compose startup sequence

The repository `docker-compose.yml` defines the following services:

1. `postgres`
2. `migrate`
3. `redis`
4. `ml-service`
5. `prediction-queue`
6. `prediction-worker`
7. `prediction-events`
8. `api`
9. `web`

### Startup order and dependencies

- `postgres` starts first and reports healthy via `pg_isready`.
- `migrate` depends on `postgres:healthy`; it runs once and then exits.
- `ml-service` depends on `postgres:healthy` and `migrate` completion.
- `prediction-queue`, `prediction-worker`, and `prediction-events` depend on `redis` and `ml-service`.
- `api` depends on `postgres:healthy`, `migrate` completion, `redis`, and `ml-service`.
- `web` depends on `postgres:healthy`, `migrate` completion, and `api`.

## Commands executed during startup

### `migrate`
- `sh -c "bun install && bun run db:migrate"`
- This installs Bun dependencies and applies Drizzle migrations.

### `ml-service`
- Built from `services/ml/Dockerfile`
- `CMD ["uvicorn","src.app:app","--host","0.0.0.0","--port","8000"]`
- No CSV import command is present.

### `prediction-queue`
- `sh -c "bun install && bun --filter @repo/workers prediction:queue"`
- Starts the queue service; no ingest task is defined here.

### `prediction-worker`
- `sh -c "bun install && bun --filter @repo/workers prediction:worker"`
- Starts the worker; no ingest task is defined here.

### `prediction-events`
- `sh -c "bun install && bun --filter @repo/workers prediction:events"`
- Starts event handling; no ingest task is defined here.

### `api`
- Built from `apps/api`
- Depends on database and migration completion.
- No startup import step is defined in `docker-compose.yml`.

### `web`
- Built from `apps/web/Dockerfile`
- Serves the frontend; no database seeding or CSV loading occurs here.

## Dockerfile review

- `services/ml/Dockerfile`
  - Base image: `python:3.11-slim`
  - Installs Python requirements
  - Runs `uvicorn src.app:app`
  - No CSV ingestion or import command

- `apps/web/Dockerfile`
  - Base image: `oven/bun:1`
  - Runs `bun install` then `bun run dev`
  - No database loading or CSV import logic

## Result

`docker compose up --build` performs schema migration only.

### It does not perform:

- `CSV → PostgreSQL` import
- CSV source table loading
- seed/demo data injection

### It does perform:

- PostgreSQL startup
- schema migrations via `bun run db:migrate`
- service startup for ML, queue, API, and web components

## Conclusion

Startup is currently a schema-only bootstrap. CSV ingestion is not part of the automatic `docker compose up --build` flow.
