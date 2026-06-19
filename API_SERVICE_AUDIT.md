# API Service Audit

Generated: 2026-06-19

### Subject: `apps/api`

## Inspect

- Repository current state: there is no `apps/api` directory or code in the workspace.
- Multiple documentation files reference `apps/api` as a Bun placeholder (e.g., `API_OWNERSHIP.md`, `SERVICE_MAP.md`, `docs/PRODUCTION_AUDIT.md`). Those docs state `apps/api` contains only a console.log and no HTTP handlers.
- `docker-compose.yml` in the current repo does not reference `apps/api`.

## Runtime usage analysis

- The frontend (`apps/web`) does not call `apps/api`; it uses `ML_SERVICE_URL`/internal APIs.
- Workers and `services/ml` do not reference `apps/api`.

## Verdict

- Recommendation: `REMOVE` as a runtime service and treat `apps/api` as archival/placeholder documentation.

### Justification

- No code; not referenced in compose; no runtime dependencies.
- Keeping a non-functional service in compose or build pipelines causes confusion and build failures (missing Dockerfile). Removing artifacts and docs references reduces accidental builds.

### Actions

- Remove `apps/api` from any `docker-compose.yml` entries if present in other branches or older versions.
- Update documentation to mark `apps/api` removed or clearly label as deprecated placeholder.
- If in future an API gateway is required, reintroduce it as a separate, fully-implemented service with a proper Dockerfile, tests, and integration points.

End of API service audit.
