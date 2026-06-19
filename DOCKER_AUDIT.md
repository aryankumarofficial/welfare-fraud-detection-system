# Docker Audit

Repository: d:/ARYAN/welfare-fraud-detection-system

Generated: 2026-06-19

## Summary of services (from `docker-compose.yml`)

- postgres
  - image: `postgres:16`
  - healthcheck: `pg_isready`
- migrate
  - image: `oven/bun:1.3.5`
  - command: `bun install && bun run db:migrate`
  - working_dir: `/app`, volume: `.:/app`
- csv-importer
  - image: `oven/bun:1.3.5`
  - command: `bun install && bun run import:csv`
  - working_dir: `/app`, volume: `.:/app`
- redis
  - image: `redis:7`
- ml-service
  - build context: `./services/ml`
  - Dockerfile: `services/ml/Dockerfile` (Python 3.11)
  - ports: `8000:8000`
  - depends_on: postgres, migrate, csv-importer
- prediction-queue
  - image: `oven/bun:1.3.5`
  - command: `bun install && bun --filter @repo/workers prediction:queue`
  - working_dir: `/app`, volume: `.:/app`
- prediction-worker
  - image: `oven/bun:1.3.5`
  - command: `bun install && bun --filter @repo/workers prediction:worker`
  - working_dir: `/app`, volume: `.:/app`
- prediction-events
  - image: `oven/bun:1.3.5`
  - command: `bun install && bun --filter @repo/workers prediction:events`
  - working_dir: `/app`, volume: `.:/app`
- web
  - build context: `./apps/web`
  - Dockerfile: `apps/web/Dockerfile` (oven/bun)
  - ports: `3000:3000`
  - depends_on: postgres, migrate, ml-service

Total services defined in compose: 10 (matches expected topology except `api` is not present in compose)

## Build contexts and Dockerfiles found

- `services/ml/Dockerfile` (exists)
- `apps/web/Dockerfile` (exists)
- No Dockerfile found under `apps/api` (compose currently does not reference `apps/api`, but earlier errors referenced a missing Dockerfile for `apps/api`).

## Notable Dockerfile instructions (summary)

- `apps/web/Dockerfile`:
  - `COPY . .` (copies entire repo into image context)
  - `RUN bun install` (installs dependencies inside container)
- `services/ml/Dockerfile`:
  - `COPY requirements.txt .`
  - `RUN pip install -r requirements.txt`
  - `COPY . .` (copies entire repo into image context)

## .dockerignore files

- Root `.dockerignore` exists and was created/updated at repository root.
- No other `.dockerignore` files in subfolders were found.

## Expected container graph (high level)

- postgres -> migrate -> csv-importer -> ml-service -> prediction-\* and web
- redis used by prediction-\* services
- web depends on ml-service and postgres

## Missing files and broken references

- `apps/api` has no Dockerfile (present in repo, but not referenced by compose). If `api` is intended to be a service, add a Dockerfile or ensure compose references the correct build context.
- Several services use `image: oven/bun:1.3.5` with `volumes: - .:/app` (migrate/csv-importer/prediction-\*). This mounts host repository into container. If `node_modules` exist on host, bind mount will include them and may contain symlinks that break builds on Windows. Also, using `COPY . .` in `apps/web` and `services/ml` combined with presence of `node_modules` in build context can cause Docker build errors such as `invalid file request node_modules/.bin/eslint`.

## Immediate root causes discovered so far

- Dockerfile `COPY . .` in `apps/web` copies entire repository into image; if `node_modules` exists in context this can cause build failure. Use `.dockerignore` to exclude node_modules or change Dockerfiles to copy only necessary files.
- Bind-mounting the entire repo into Bun-based containers (`.:/app`) relies on host environment. On Windows, symlinked bins in `node_modules/.bin` can be invalid for the container runtime and cause `invalid file request` errors.

## Recommendations (high level)

- Ensure `.dockerignore` excludes `node_modules` (done). Rebuild images after `.dockerignore` is present.
- Change `COPY . .` to more granular COPY patterns in `apps/web/Dockerfile` and `services/ml/Dockerfile` to only include package manifests, lockfiles, source directories, and `prisma`/`migrations`/`data` files.
- For Bun-based ephemeral services that run `bun install` at container startup (migrate, csv-importer, prediction-\*), keep using `image: oven/bun` and `volumes: - .:/app` but avoid copying host `node_modules`; prefer letting container run `bun install` inside its own environment.
- Add a Dockerfile for `apps/api` if that service is intended to run in Docker.

## Next steps

1. Build context investigation: identify every Dockerfile COPY/ADD and confirm whether it references `node_modules` or other host-only paths. (BUILD_CONTEXT_AUDIT.md)
2. Dockerfile validation per-service and create DOCKERFILE_VALIDATION.md
3. Make minimal safe fixes (adjust Dockerfiles, .dockerignore) and run `docker compose build` and `docker compose up` to validate.

---

Audit completed.
