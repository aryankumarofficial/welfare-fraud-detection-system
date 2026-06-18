# Frontend API Mapping

This document maps frontend pages and components in `apps/web` to the backend ML API endpoints in `services/ml`.

## Authentication
- `apps/web/src/lib/auth.ts` / `login/page.tsx`
  - `POST /auth/token`
  - Stores `access_token` in `localStorage`
  - Decodes role from token payload for RBAC

## Dashboard
- `apps/web/src/app/admin/dashboard/page.tsx`
  - `GET /dashboard/summary`
  - `getDashboardSummary()` in `apps/web/src/lib/api.ts`

## Predictions
- `apps/web/src/app/admin/predictions/page.tsx`
  - `GET /predictions/{student_profile_id}`
  - `getPredictionHistory(studentProfileId)`
- `apps/web/src/app/admin/predictions/detail/[prediction_id]/page.tsx`
  - `GET /predictions/detail/{prediction_id}`
  - `getPredictionDetail(predictionId)`

## Workflows
- `apps/web/src/app/admin/workflows/page.tsx`
  - `POST /snapshot/generate` via `generateSnapshot(studentProfileId)`
  - `POST /predict/generate` via `generatePrediction(studentProfileId)`
  - `POST /predictions/queue` via `queuePrediction(studentProfileId)`
  - `GET /predictions/{student_profile_id}` via `getPredictionHistory(studentProfileId)`
  - `POST /predictions/{prediction_id}/review` via `createPredictionReview(...)`

## Analytics
- `apps/web/src/app/admin/analytics/page.tsx`
  - `GET /analytics/predictions` via `getPredictionAnalytics()`
- `apps/web/src/app/admin/analytics/model-performance/page.tsx`
  - `GET /analytics/model-performance` via `getModelPerformance()`
- `apps/web/src/app/admin/analytics/drift/page.tsx`
  - `GET /analytics/drift?days={n}` via `getDriftAnalytics(days)`
- `apps/web/src/app/admin/analytics/alerts/page.tsx`
  - `GET /analytics/alerts` via `getAlerts()`
- `apps/web/src/app/admin/analytics/queue/page.tsx`
  - `GET /analytics/queue` via `getQueueAnalytics()`
- `apps/web/src/app/admin/analytics/model-health/page.tsx`
  - `GET /analytics/model-health` via `getModelHealth()`

## Model Registry
- `apps/web/src/app/admin/models/page.tsx`
  - `GET /models` via `getModels()`
  - `POST /models/{model_id}/promote` via `promoteModel(modelId)`
  - `POST /models/{model_id}/rollback` via `rollbackModel(modelId)`
  - `POST /models/{model_id}/archive` via `archiveModel(modelId)`
- `apps/web/src/app/admin/models/[model_id]/page.tsx`
  - `GET /models/{model_id}` via `getModelDetail(modelId)`
  - same lifecycle actions as model registry list
- `apps/web/src/app/admin/models/compare/page.tsx`
  - `GET /models/compare?ids={comma-separated}` via `compareModels(ids)`

## API Helper
- `apps/web/src/lib/api.ts`
  - Centralizes all backend calls and bearer auth headers
  - Uses `getStoredAccessToken()` from `apps/web/src/lib/auth.ts`
  - Supports token caching and error normalization

## Route Guard
- `apps/web/src/app/admin/layout.tsx`
  - Redirects unauthenticated users to `/login`
  - Ensures protected admin routes are only accessible after login
- `apps/web/src/components/layout/navbar.tsx`
  - Displays navigation based on authenticated user role

## Notes
- Backend route protection is role-based, so user roles must match the API dependencies.
- The frontend assumes the backend returns JSON and may surface backend error messages directly.
