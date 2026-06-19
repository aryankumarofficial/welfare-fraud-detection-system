# Build Context Audit

Generated: 2026-06-19

## Goal

Identify why Docker reported `invalid file request node_modules/.bin/eslint` during build and audit COPY/ADD usage.

## Findings

### Offending Dockerfile(s)

- `apps/web/Dockerfile` (line: `COPY . .`)
  - File path: [apps/web/Dockerfile](apps/web/Dockerfile)
  - Docker build context used by compose: `./apps/web` (see `docker-compose.yml`)
  - Problem: `COPY . .` copies _everything_ from the `apps/web` build context into the image. Because there was no `.dockerignore` in `apps/web` previously, `node_modules` in `apps/web` (created by local `bun install`) was included in the build context.
  - Evidence: `apps/web/node_modules/.bin/eslint` exists and is a symlink to `../eslint/bin/eslint.js`. Docker on Windows does not always handle symlinks within the build context well, causing `invalid file request node_modules/.bin/eslint`.

- `services/ml/Dockerfile` (line: `COPY . .`)
  - File path: [services/ml/Dockerfile](services/ml/Dockerfile)
  - Docker build context used by compose: `./services/ml`
  - `services/ml` did not contain `node_modules` in the current tree; but copying the full context is still a broad operation. A per-context `.dockerignore` was added to avoid unnecessary files.

### Other COPY/ADD occurrences

- No other Dockerfiles with `COPY`/`ADD` were found beyond the two above.

## Root cause

- Root cause: The build for `apps/web` used `COPY . .` without a `.dockerignore` in `apps/web` build context. That allowed `apps/web/node_modules` (with many symlinks to host paths created by Bun) to be included in the build context, which leads Docker to error when packaging the build context on Windows.

- Secondary cause: The absence of per-context `.dockerignore` files meant the repository-level `.dockerignore` did not protect subdirectory build contexts (Docker reads `.dockerignore` from the build context root only).

## Fixes applied

- Added `apps/web/.dockerignore` to exclude `node_modules`, build caches, editor files, and environment files but keep package manifests and source directories.
- Rewrote `apps/web/Dockerfile` to copy package manifests first, run `bun install`, copy source, and run build/start (production-friendly). This reduces layer invalidation and prevents copying host `node_modules` into the image.
- Added `services/ml/.dockerignore` to exclude common caches and node_modules in that build context.

## Recommendations

- Prefer granular `COPY` patterns (copy package manifests, install, then copy source) to reduce build context and layer cache invalidation.
- Keep `.dockerignore` in each build context directory referenced by compose (e.g., `apps/web`, `services/ml`, `apps/api` if added later).
- For services that use `image: oven/bun` and `volumes: - .:/app`, avoid mounting host `node_modules` into the container on Windows; instead, let the container run `bun install` inside the container to create its own compatible modules.

---

End of build context audit.
