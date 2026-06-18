# Authentication Audit

## Auth-related files

- `services/ml/src/security.py`
  - Primary authentication and authorization implementation.
  - Contains JWT token creation/validation, static credential validation, role enforcement, and internal/queue API key checks.
- `services/ml/src/app.py`
  - Defines the login endpoint and all protected API routes.
  - Applies role-based access control via FastAPI dependencies.
- `services/ml/tests/test_security.py`
  - Unit tests for token creation/validation and API key enforcement.
- `apps/web/src/lib/api.ts`
  - Frontend API client that requests a token from `/auth/token` and sends bearer auth headers.
- `apps/web/src/app/unauthorized.tsx`
  - Frontend unauthorized fallback page.
- `packages/db/schema/users.ts`
  - Database schema for a `users` table, but it is not used by the ML auth flow.
- `packages/auth/package.json`
  - Placeholder package with no source code.

## Login endpoints

- `POST /auth/token`
  - Implemented in `services/ml/src/app.py`.
  - Accepts JSON `{ "username": string, "password": string }`.
  - Returns `{ access_token, expires_in, role }` on success.
  - Delegates credential validation to `services/ml/src/security.py`.

## Registration endpoints

- None found.
- There is no user registration API in the current codebase.
- Auth users are defined via environment variables only.

## JWT / token implementation

- Implemented in `services/ml/src/security.py`.
- Token creation uses `create_access_token(username, role)`:
  - Payload contains `sub`, `role`, and `exp`.
  - Payload is JSON-serialized, Base64-url encoded, and signed with HMAC-SHA256.
  - Token format is `base64(payload).base64(signature)`.
- Token validation uses `decode_access_token(token)`:
  - Verifies signature against `JWT_SECRET_KEY`.
  - Validates `exp` expiration.
  - Parses claims into `UserClaims`.
- `TokenResponse` includes `token_type: "bearer"` and `expires_in`.

## User tables and role tables

### `packages/db/schema/users.ts`
- Defines a `users` table:
  - `id`, `external_auth_id`, `created_at`, `updated_at`.
- This table is not used by the runtime auth flow in `services/ml/src/security.py`.

### Role tables
- No dedicated role table exists for authentication.
- System roles are defined in `services/ml/src/security.py` as `SystemRole` enum:
  - `admin`, `analyst`, `operator`, `viewer`.
- Roles are not persisted in the database for auth; they are inferred from environment user credentials and JWT claims.

## Protected routes and RBAC enforcement

- Route protection is applied by FastAPI dependencies in `services/ml/src/app.py`.
- Role enforcement is implemented by `require_minimum_role()` in `services/ml/src/security.py`.
- Available role dependencies:
  - `require_operator`
  - `require_analyst`
  - `require_admin`
- Internal service auth is enforced via `require_internal_service` and header `X-Internal-API-Key`.
- Queue auth is enforced via `require_queue_access` and header `X-Queue-API-Key`.

## Frontend authentication pages

- `apps/web/src/app/unauthorized.tsx`
  - Static page shown for unauthorized access.
- No login page, no registration page, and no user credential form exists in the frontend.
- Frontend auth is instead driven by environment variables in `apps/web/src/lib/api.ts`.

## Session handling

- The frontend does not use browser sessions or cookies.
- `apps/web/src/lib/api.ts` manages an in-memory cached access token:
  - Caches `access_token` and expiry in module variables.
  - Reuses the token until just before expiration.
- This is effectively a service-account-style token cache, not a user session store.
- No refresh token implementation exists.

## Production readiness assessment

### Strengths
- There is a single auth entry point (`POST /auth/token`).
- RBAC enforcement exists via FastAPI dependencies.
- Tokens are signed and expire.
- Internal and queue API keys are separate and validated.

### Weaknesses
- No registration or user management endpoints.
- Credentials are static environment variables, not stored securely in a database.
- No password hashing or user lifecycle management.
- Token implementation is custom and not standard JWT: it omits a header and uses a custom serialization.
- No refresh token support and no session revocation.
- Frontend authentication is not user-facing; it uses env vars and process-level credentials.
- The `users` table schema exists, but it is not used to authenticate system users.
- `packages/auth` is effectively empty and not part of the auth implementation.

### Conclusion
- Authentication is not production-ready in its current state.
- The system supports basic token issuance and role gating, but it lacks user management, registration, secure credential storage, and hardened session/token lifecycle handling.
