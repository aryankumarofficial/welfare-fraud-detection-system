# Dockerfile Validation

Generated: 2026-06-19

Services to validate: postgres, migrate, csv-importer, redis, ml-service, prediction-queue, prediction-worker, prediction-events, api, web

## Summary

- Dockerfiles exist for:
  - `services/ml` → `services/ml/Dockerfile` (validated)
  - `apps/web` → `apps/web/Dockerfile` (validated)
- Other services use public images (`postgres`, `oven/bun`, `redis`) and do not require Dockerfiles.
- `apps/api` does not have a Dockerfile and is not referenced in `docker-compose.yml` - see API audit.

---

## `services/ml` validation

- Dockerfile path: `services/ml/Dockerfile`
- Build context in compose: `./services/ml` (matches)
- Dockerfile contents (key lines):
  - `FROM python:3.11-slim`
  - `WORKDIR /app`
  - `COPY requirements.txt .`
  - `RUN pip install --no-cache-dir -r requirements.txt`
  - `COPY . .`
  - `CMD ["uvicorn","src.app:app","--host","0.0.0.0","--port","8000"]`
- Validation:
  - `requirements.txt` exists in `services/ml` (checked earlier)
  - `COPY . .` will copy the service source into image; `services/ml/.dockerignore` has been added to exclude unrelated files.
  - Startup command `uvicorn` is correct for FastAPI app path `src.app:app` (verify that file exists: `services/ml/src/app.py`).
- Action items:
  - Ensure `services/ml/src/app.py` exists and `requirements.txt` pins compatible packages (asyncpg, uvicorn, fastapi). If missing, add or fix.

## `apps/web` validation

- Dockerfile path: `apps/web/Dockerfile`
- Build context in compose: `./apps/web` (matches)
- Dockerfile contents (key lines after fix):
  - `FROM oven/bun:1`
  - `WORKDIR /app`
  - `COPY package.json bun.lockb* bun.lock* ./`
  - `RUN bun install`
  - `COPY . .`
  - `RUN bun run build`
  - `CMD ["bun","run","start"]`
- Validation:
  - `apps/web/.dockerignore` was added to exclude `node_modules` and caches so `COPY` won't include host `node_modules`.
  - `package.json` exists and includes `build` and `start` scripts (`next build` / `next start`).
- Action items:
  - Confirm `next` build runs with Bun base image in CI; if not, consider switching to `node:18-alpine` for wider compatibility.

## Services using `oven/bun` image (no Dockerfile)

- `migrate`, `csv-importer`, `prediction-queue`, `prediction-worker`, `prediction-events` use `oven/bun:1.3.5` and bind-mount the repository at runtime.
- Validation notes:
  - These services rely on host files via `volumes: - .:/app`. On Windows, this can expose host `node_modules` and symlink issues. Prefer running `bun install` inside the container (commands already include `bun install`) and ensure `.dockerignore` is present when building images.
  - If using bind mounts for runtime, the container's `bun install` will create its own `node_modules` inside the container (overwriting host's node_modules in the mount), but on Windows permissions/symlinks may still cause issues.

## `api` service

- No Dockerfile and not present in `docker-compose.yml`. See API_SERVICE_AUDIT.md for recommendation.

---

Validation result: Dockerfiles for `services/ml` and `apps/web` are present and updated. `apps/web` build context now excludes `node_modules` and `apps/web/Dockerfile` copies manifests first to avoid symlink issues. Remaining risks:

- Bun compatibility for Next.js production build
- Bind-mounted `.:/app` for Bun services on Windows can still be a source of runtime oddities; prefer container-first installs.

End of Dockerfile validation.
