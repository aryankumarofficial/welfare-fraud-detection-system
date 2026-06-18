# Authentication Flow

## Backend auth flow

### Credentials and login
- The only login endpoint is `POST /auth/token` in `services/ml/src/app.py`.
- Payload: `{ "username": string, "password": string }`.
- The request is authenticated by `validate_user_credentials()` in `services/ml/src/security.py`.
- Valid credentials are defined via environment variables:
  - `ADMIN_USERNAME` / `ADMIN_PASSWORD`
  - `ANALYST_USERNAME` / `ANALYST_PASSWORD`
  - `OPERATOR_USERNAME` / `OPERATOR_PASSWORD`
- There is no registration endpoint or user creation flow.

### Token issuance
- Upon successful login, `create_access_token()` is called.
- Token payload includes:
  - `sub` = username
  - `role` = role name
  - `exp` = expiration timestamp
- Tokens are signed with HMAC-SHA256 using `JWT_SECRET_KEY`.
- `JWT_ACCESS_TOKEN_EXPIRE_SECONDS` controls expiry.

### Token validation
- Incoming requests are validated by `get_current_user()` in `services/ml/src/security.py`.
- It reads the bearer token from the `Authorization` header.
- Validation checks:
  - Token format: `payload.signature`
  - Signature matches using `JWT_SECRET_KEY`
  - Token expiration has not passed
- Successful validation returns `UserClaims`.

### Role-based access control
- RBAC is implemented through `require_minimum_role()`.
- Role priority order:
  - `viewer` = 0
  - `operator` = 1
  - `analyst` = 2
  - `admin` = 3
- Protected dependencies:
  - `require_operator`
  - `require_analyst`
  - `require_admin`
- These dependencies are applied directly to FastAPI routes in `services/ml/src/app.py`.

### Internal and queue auth
- Internal ML service calls use `X-Internal-API-Key` and `require_internal_service`.
- Prediction queue access uses `X-Queue-API-Key` and `require_queue_access`.
- These secrets are also environment-configured.

## Frontend auth flow

### Token retrieval
- The frontend API client in `apps/web/src/lib/api.ts` does not present a login UI.
- It calls `POST /auth/token` directly using environment credentials:
  - `ANALYST_USERNAME`
  - `ANALYST_PASSWORD`
- The frontend stores the returned token in module-level cache variables:
  - `cachedToken`
  - `cachedTokenExpiry`

### Authenticated requests
- All backend requests go through `fetchJson()` in `apps/web/src/lib/api.ts`.
- Requests automatically include:
  - `Accept: application/json`
  - `Authorization: Bearer ${token}`
- The token is refreshed when expired.

### Session handling
- There is no browser session or cookie-based auth.
- Session state exists only as an in-memory access token cache in the frontend module.
- If the application restarts or the page refreshes, the token is re-acquired from the backend using env credentials.

## Observations

- The frontend behaves like a service client using one set of credentials, not a multi-user login experience.
- There is no user registration, password reset, or user management flow.
- The auth flow is tightly coupled to environment-managed usernames and passwords.
