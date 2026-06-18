# Frontend Integration Audit

## Summary
The web frontend at `apps/web` is now wired end-to-end to the existing ML backend in `services/ml` without dummy placeholders. Authentication, dashboard metrics, analytics, prediction history, model registry, and workflow execution all consume live backend endpoints.

## What is integrated
- `apps/web/src/lib/api.ts` centralizes bearer auth headers and backend request handling for live API calls.
- `apps/web/src/lib/auth.ts` persists JWT-style tokens in `localStorage` and exposes user role decoding for RBAC-aware UI.
- `apps/web/src/components/auth/auth-provider.tsx` provides global auth state and login/logout actions.
- `apps/web/src/app/login/page.tsx` implements the login page, redirecting authenticated users to `/admin/dashboard`.
- `apps/web/src/app/admin/layout.tsx` enforces route guard redirection to `/login` for unauthenticated access.
- `apps/web/src/components/layout/navbar.tsx` now shows authenticated navigation and hides protected links by role.
- Model registry pages, analytics screens, workflow execution pages, and prediction detail pages are wired to actual backend endpoints.

## Backend dependencies
The frontend is integrated with the following ML backend patterns:
- Authentication: `POST /auth/token` using backend credentials entered at login; the client stores the returned JWT-style access token.
- RBAC: frontend navigation adapts based on the decoded user role from the access token.
- Live analytics and data: frontend pages use the ML backend's `/dashboard`, `/analytics`, `/predictions`, `/models`, and `/snapshot` endpoints.

## Current status
- `apps/web` is no longer dependent on `apps/api` at runtime.
- All major admin pages now fetch backend data and render real metrics.
- Auth state is global, and the admin layout blocks unauthenticated access.
- Model registry actions (`promote`, `rollback`, `archive`) are mapped to backend endpoints.
- The dashboard and analytics data are loaded via `useApi` with loading/error handling.

## Remaining considerations
- The login flow still depends on backend-stored environment credentials rather than a production auth provider.
- User roles are derived from token payload only after login; there is no server-side session.
- Some model endpoint actions require admin privileges in the backend; those actions should be restricted in UI if the logged-in user role is not `admin`.
- If the backend accepts different data shapes, the frontend type definitions may need refinement.

## Recommended next steps
1. Validate `services/ml` is running and accessible from `apps/web` using `ML_API_URL` or `NEXT_PUBLIC_API_URL`.
2. Confirm the backend token response shape and any additional protection around `/auth/token`.
3. Add explicit UI role gating for admin-only model actions.
4. Add a logout confirmation or a session expiration handler in `AuthProvider`.
